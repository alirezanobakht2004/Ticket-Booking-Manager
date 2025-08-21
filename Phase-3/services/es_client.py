import logging
from typing import Any, Dict, Iterable, List, Optional, Tuple

from elasticsearch import ApiError, Elasticsearch, NotFoundError, TransportError
from elasticsearch.helpers import bulk

from config import Config

_logger = logging.getLogger(__name__)

# Singleton client cache
_es_client: Optional[Elasticsearch] = None


def build_ticket_search_query(params: Dict[str, Any], from_: int = 0, size: int = 20) -> Dict[str, Any]:
    """
    Construct a bool query for tickets based on params:
      origin_id, destination_id, travel_date (YYYY-MM-DD),
      vehicle_type, min_price, max_price, company_name,
      departure_start (HH:MM), departure_end (HH:MM),
      travel_class
    Note: This is a query builder; the execution should live in ticket_service.
    """
    must = []
    filters = []

    origin_id = params.get("origin_id")
    destination_id = params.get("destination_id")
    travel_date = params.get("travel_date")  # YYYY-MM-DD
    vehicle_type = params.get("vehicle_type")
    min_price = params.get("min_price")
    max_price = params.get("max_price")
    company_name = params.get("company_name")
    dep_start = params.get("departure_start")  # HH:MM
    dep_end = params.get("departure_end")      # HH:MM
    travel_class = params.get("travel_class")

    # Required constraints
    if origin_id is not None:
        filters.append({"term": {"origin_id": origin_id}})
    if destination_id is not None:
        filters.append({"term": {"destination_id": destination_id}})

    # Date range for a given day (UTC)
    if travel_date:
        filters.append({
            "range": {
                "departure_time": {
                    "gte": f"{travel_date}T00:00:00Z",
                    "lt": f"{travel_date}T23:59:59Z"
                }
            }
        })

    # Vehicle type
    if vehicle_type:
        filters.append({"term": {"vehicle_type": vehicle_type}})

    # Price range
    price_range = {}
    if min_price is not None:
        price_range["gte"] = min_price
    if max_price is not None:
        price_range["lte"] = max_price
    if price_range:
        filters.append({"range": {"price": price_range}})

    # Travel class
    if travel_class is not None:
        filters.append({"term": {"class_code": travel_class}})

    # Company name: match phrase prefix for simple autocomplete-like behavior
    if company_name:
        must.append({
            "match_phrase_prefix": {
                "company_name": {
                    "query": company_name
                }
            }
        })

    # Departure time window (HH:MM) — approximate via script or derived field
    # Best practice: index hour/minute fields and use range on them.
    # If you have derived fields like departure_hour, you can filter here.
    # Example (if you later add departure_hour int field):
    # if dep_start or dep_end:
    #     hour_range = {}
    #     if dep_start:
    #         hour_range["gte"] = int(dep_start[:2])
    #     if dep_end:
    #         hour_range["lte"] = int(dep_end[:2])
    #     filters.append({"range": {"departure_hour": hour_range}})

    query = {
        "from": from_,
        "size": size,
        "query": {
            "bool": {
                "must": must if must else [{"match_all": {}}],
                "filter": filters
            }
        },
        "sort": [
            {"departure_time": {"order": "asc"}}
        ]
    }
    return query


def bulk_index_tickets(tickets: Iterable[Dict[str, Any]], chunk_size: int = 500) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Bulk index a sequence of ticket dicts. Each dict will be normalized.
    Returns (success_count, errors_list)
    """
    es = get_es_client()
    index = get_ticket_index_name()

    def _actions():
        for t in tickets:
            doc = normalize_ticket_doc(t)
            doc_id = str(doc.get("ticket_id"))
            if not doc_id or doc_id == "None":
                _logger.warning(f"Skipping ticket without ticket_id: {t}")
                continue
            yield {
                "_op_type": "index",
                "_index": index,
                "_id": doc_id,
                "_source": doc,
            }

    try:
        success_count, errors = bulk(es, _actions(), chunk_size=chunk_size, refresh=False)
        if errors:
            _logger.error(f"Bulk index had errors (showing first 3): {errors[:3]}")
        _logger.info(f"Bulk indexed {success_count} ticket docs into '{index}'")
        return success_count, errors
    except Exception as e:
        _logger.error(f"Bulk index failed: {e}")
        return 0, [{"exception": str(e)}]


def delete_ticket(ticket_id: int) -> Tuple[bool, Optional[str]]:
    """
    Delete a ticket document by ID.
    Returns (ok, error_message)
    """
    es = get_es_client()
    index = get_ticket_index_name()
    try:
        es.delete(index=index, id=str(ticket_id), refresh="false")
        return True, None
    except NotFoundError:
        # Not present is okay for idempotency
        return True, None
    except TransportError as e:
        _logger.error(f"TransportError deleting ticket {ticket_id}: {e}")
        return False, str(e)
    except Exception as e:
        _logger.error(f"Unexpected error deleting ticket {ticket_id}: {e}")
        return False, str(e)


def ensure_ticket_index() -> None:
    """
    Ensures the tickets index exists with appropriate mappings/settings.
    Safe to call multiple times at startup.
    """
    es = get_es_client()
    index = get_ticket_index_name()

    try:
        if es.indices.exists(index=index):
            return
    except Exception as e:
        _logger.error(f"Failed checking index existence for '{index}': {e}")
        raise

    # Settings and mappings
    # Adjust analyzers or add completion fields if you plan autocomplete
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "analyzer": {
                    "edge_ngram_analyzer": {
                        "type": "custom",
                        "tokenizer": "edge_ngram_tokenizer",
                        "filter": ["lowercase"]
                    }
                },
                "tokenizer": {
                    "edge_ngram_tokenizer": {
                        "type": "edge_ngram",
                        "min_gram": 2,
                        "max_gram": 15,
                        "token_chars": ["letter", "digit"]
                    }
                }
            }
        },
        "mappings": {
            "dynamic": "false",
            "properties": {
                # Identifiers
                "ticket_id": {"type": "keyword"},
                "vehicle_id": {"type": "integer"},
                "reservation_id": {"type": "integer"},

                # Locations
                "origin_id": {"type": "integer"},
                "destination_id": {"type": "integer"},
                "origin_city": {
                    "type": "text",
                    "fields": {"raw": {"type": "keyword"}},
                    "analyzer": "edge_ngram_analyzer",
                    "search_analyzer": "standard"
                },
                "destination_city": {
                    "type": "text",
                    "fields": {"raw": {"type": "keyword"}},
                    "analyzer": "edge_ngram_analyzer",
                    "search_analyzer": "standard"
                },

                # Times
                "departure_time": {"type": "date"},  # ISO8601 strings
                "arrival_time": {"type": "date"},

                # Pricing and class
                "price": {"type": "double"},
                "class_code": {"type": "integer"},

                # Vehicle metadata
                "vehicle_type": {"type": "keyword"},  # plane|bus|train
                "brand": {
                    "type": "text",
                    "fields": {"raw": {"type": "keyword"}}
                },
                "model": {
                    "type": "text",
                    "fields": {"raw": {"type": "keyword"}}
                },

                # Company naming variants (one of these will be present per type)
                "company_name": {
                    "type": "text",
                    "fields": {"raw": {"type": "keyword"}},
                    "analyzer": "edge_ngram_analyzer",
                    "search_analyzer": "standard"
                },

                # Capacity
                "capacity": {"type": "integer"},
                "reserved_number": {"type": "integer"},

                # Misc flags
                "has_internet": {"type": "boolean"},
                "snack_service": {"type": "boolean"},
            }
        }
    }

    try:
        es.indices.create(index=index, body=settings)
        _logger.info(f"Created Elasticsearch index '{index}'")
    except ApiError as e:
        if getattr(e, "error", "") == "resource_already_exists_exception":
            _logger.info(f"Index '{index}' already exists")
        else:
            _logger.error(f"Failed creating index '{index}': {e}")
            raise
    except Exception as e:
        _logger.error(f"Unexpected error creating index '{index}': {e}")
        raise


def get_es_client() -> Elasticsearch:
    """
    Returns a singleton Elasticsearch client configured from Config.
    """
    global _es_client
    if _es_client is not None:
        return _es_client

    # Build hosts arg based on Config
    host = getattr(Config, "ELASTICSEARCH_HOST", "localhost")
    port = int(getattr(Config, "ELASTICSEARCH_PORT", 9200))
    scheme = getattr(Config, "ELASTICSEARCH_SCHEME", "http")

    # If you require auth/SSL, extend here:
    # user = getattr(Config, "ELASTICSEARCH_USER", None)
    # password = getattr(Config, "ELASTICSEARCH_PASSWORD", None)
    # verify_certs = getattr(Config, "ELASTICSEARCH_VERIFY_CERTS", True)

    _es_client = Elasticsearch(
        hosts=[{"host": host, "port": port, "scheme": scheme}],
        # basic_auth=(user, password) if user and password else None,
        # verify_certs=verify_certs,
        request_timeout=10,
        retry_on_timeout=True,
        max_retries=3,
    )
    try:
        ping_ok = _es_client.ping()
        if not ping_ok:
            _logger.warning("Elasticsearch ping failed, but proceeding with client creation")
    except Exception as e:
        _logger.error(f"Error pinging Elasticsearch: {e}")

    return _es_client


def get_ticket(ticket_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a single ticket document by ID from ES.
    Returns the _source dict or None if not found.
    """
    es = get_es_client()
    index = get_ticket_index_name()
    try:
        resp = es.get(index=index, id=str(ticket_id))
        return resp.get("_source")
    except NotFoundError:
        return None
    except Exception as e:
        _logger.error(f"Error getting ticket {ticket_id}: {e}")
        return None


def get_ticket_index_name() -> str:
    return getattr(Config, "ELASTICSEARCH_INDEX_TICKETS", "tickets")


def index_ticket(ticket: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Index or update a single ticket document by ticket_id.
    Returns (ok, error_message)
    """
    es = get_es_client()
    index = get_ticket_index_name()
    doc = normalize_ticket_doc(ticket)
    doc_id = str(doc.get("ticket_id"))

    if not doc_id or doc_id == "None":
        return False, "ticket_id missing in document"

    try:
        es.index(index=index, id=doc_id, document=doc, refresh="false")
        return True, None
    except TransportError as e:
        _logger.error(f"TransportError indexing ticket {doc_id}: {e}")
        return False, str(e)
    except Exception as e:
        _logger.error(f"Unexpected error indexing ticket {doc_id}: {e}")
        return False, str(e)


def normalize_ticket_doc(ticket: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize your SQL ticket row into an ES document shape that matches the mappings.
    Call this before indexing. Adjust keys to match your DB schema.
    Expected keys available from your current queries (tweak as needed):
      - ticket_id, vehicle_id, price, class_code
      - source (origin_id), destination (destination_id)
      - departure_time, arrival_time (ISO strings)
      - brand, model
      - bus_company / airline_name / train_type (map into company_name)
      - origin (city title), destination (city title) from details query if available
      - capacity, reserved_number
    """
    doc = {
        "ticket_id": ticket.get("ticket_id"),
        "vehicle_id": ticket.get("vehicle_id"),
        "reservation_id": ticket.get("reservation_id"),

        "origin_id": ticket.get("source") or ticket.get("origin_id"),
        "destination_id": ticket.get("destination") or ticket.get("destination_id"),
        "origin_city": ticket.get("origin"),
        "destination_city": ticket.get("destination"),

        "departure_time": ticket.get("departure_time"),
        "arrival_time": ticket.get("arrival_time"),

        "price": ticket.get("price"),
        "class_code": ticket.get("class_code"),

        "brand": ticket.get("brand"),
        "model": ticket.get("model"),
        "vehicle_type": ticket.get("vehicle_type"),

        "company_name": ticket.get("bus_company") or ticket.get("airline_name") or ticket.get("train_type"),

        "capacity": ticket.get("capacity"),
        "reserved_number": ticket.get("reserved_number"),

        # Example flag normalization if present in your details
        "has_internet": ticket.get("internet_connection") or ticket.get("plane_internet_connection") or ticket.get("train_internet_connection"),
        "snack_service": ticket.get("snack_service"),
    }
    # Optional cleanup: remove None values to reduce index size
    return {k: v for k, v in doc.items() if v is not None}


def search_tickets_es(params: Dict[str, Any], page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    Execute an ES search built from provided params.
    Returns dict with hits and total for the API/service layer to transform.
    """
    es = get_es_client()
    index = get_ticket_index_name()

    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20

    from_ = (page - 1) * page_size
    body = build_ticket_search_query(params, from_=from_, size=page_size)

    try:
        resp = es.search(index=index, body=body)
        hits = resp.get("hits", {}).get("hits", [])
        total_val = resp.get("hits", {}).get("total", {})
        total = total_val.get("value", 0) if isinstance(total_val, dict) else total_val

        results = [h.get("_source", {}) for h in hits]
        return {
            "results": results,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        _logger.error(f"Elasticsearch search failed: {e}")
        return {"results": [], "total": 0, "page": page, "page_size": page_size}