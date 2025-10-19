import logging
from typing import Optional

# -----------------------
# Module-Level Imports and Configuration
# -----------------------

# ES utilities (index/get/delete/bulk)
try:
    from services.es_client import (
        get_es_client,
        ensure_ticket_index,
        index_ticket,
        delete_ticket,
    )
    ES_AVAILABLE = True
except Exception as e:
    ES_AVAILABLE = False

# DB helpers to fetch flattened ticket docs
try:
    from db.db import get_flat_ticket_by_id
except Exception as e:
    # If import fails at module load (e.g., circulars in some environments),
    # you can lazy-import inside functions instead.
    get_flat_ticket_by_id = None  # type: ignore

logger = logging.getLogger(__name__)


# -----------------------
# Utility Functions
# -----------------------
def _es_ready() -> bool:
    """
    Returns True if ES is available and reachable; False otherwise.
    Does not raise exceptions.
    """
    if not ES_AVAILABLE:
        logger.debug("Elasticsearch not available (import-time).")
        return False
    try:
        es = get_es_client()
        if not es:
            return False
        # Optional: es.ping() is relatively cheap; comment out if too chatty.
        es.ping()
        return True
    except Exception as e:
        logger.warning(f"Elasticsearch not ready: {e}")
        return False


def _ensure_index_safe() -> None:
    """
    Ensures the ticket index exists; swallows exceptions and logs.
    """
    try:
        ensure_ticket_index()
    except Exception as e:
        logger.warning(f"Failed to ensure ES ticket index (non-fatal): {e}")


# -----------------------
# Core Sync Functions
# -----------------------
def on_ticket_created(ticket_id: int) -> None:
    """
    Should be called after a ticket is inserted in SQL.
    Pulls the latest row from SQL and indexes it into ES.
    Safe no-op if ES isn't available.
    """
    if not _es_ready():
        return
    _ensure_index_safe()

    try:
        # Lazy import fallback
        global get_flat_ticket_by_id
        if get_flat_ticket_by_id is None:
            from db.db import get_flat_ticket_by_id  # type: ignore

        doc = get_flat_ticket_by_id(ticket_id)
        if not doc:
            logger.warning(f"[ticket_sync] Created ticket {ticket_id} not found in DB; skipping ES index.")
            return

        ok, err = index_ticket(doc)
        if not ok:
            logger.error(f"[ticket_sync] Indexing ticket {ticket_id} failed: {err}")
        else:
            logger.info(f"[ticket_sync] Indexed new ticket {ticket_id} into ES.")
    except Exception as e:
        logger.error(f"[ticket_sync] on_ticket_created({ticket_id}) error: {e}")


def on_ticket_updated(ticket_id: int) -> None:
    """
    Should be called after a ticket is updated in SQL.
    Fetches fresh data from SQL and upserts to ES.
    Safe no-op if ES isn't available.
    """
    if not _es_ready():
        return
    _ensure_index_safe()

    try:
        global get_flat_ticket_by_id
        if get_flat_ticket_by_id is None:
            from db.db import get_flat_ticket_by_id  # type: ignore

        doc = get_flat_ticket_by_id(ticket_id)
        if not doc:
            logger.warning(f"[ticket_sync] Updated ticket {ticket_id} missing in DB; deleting from ES just in case.")
            ok, err = delete_ticket(ticket_id)
            if not ok:
                logger.error(f"[ticket_sync] Deleting missing ticket {ticket_id} from ES failed: {err}")
            return

        ok, err = index_ticket(doc)
        if not ok:
            logger.error(f"[ticket_sync] Re-indexing ticket {ticket_id} failed: {err}")
        else:
            logger.info(f"[ticket_sync] Re-indexed ticket {ticket_id} into ES.")
    except Exception as e:
        logger.error(f"[ticket_sync] on_ticket_updated({ticket_id}) error: {e}")


def on_ticket_deleted(ticket_id: int) -> None:
    """
    Should be called after a ticket is deleted in SQL.
    Removes the corresponding document from ES if present.
    Safe no-op if ES isn't available.
    """
    if not _es_ready():
        return

    try:
        ok, err = delete_ticket(ticket_id)
        if not ok:
            logger.error(f"[ticket_sync] Deleting ticket {ticket_id} from ES failed: {err}")
        else:
            logger.info(f"[ticket_sync] Deleted ticket {ticket_id} from ES.")
    except Exception as e:
        logger.error(f"[ticket_sync] on_ticket_deleted({ticket_id}) error: {e}")


# -----------------------
# Convenience Functions
# -----------------------
def upsert_ticket(ticket_id: int) -> None:
    """
    Convenience: read the ticket from SQL and index it into ES (create or update).
    Use when you don't know if the change was create or update.
    """
    on_ticket_updated(ticket_id)


def resync_ticket(ticket_id: int) -> None:
    """
    Force a fresh read from SQL and re-index into ES, logging any issues.
    Alias for on_ticket_updated for clarity.
    """
    on_ticket_updated(ticket_id)