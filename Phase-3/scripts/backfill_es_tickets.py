import logging
import sys
from typing import List, Dict, Any

# Ensure package imports work when running as a module
# e.g., python -m scripts.backfill_es_tickets
try:
    from services.es_client import (
        get_es_client,
        ensure_ticket_index,
        bulk_index_tickets,
    )
    from db.db import get_all_tickets_for_indexing
except Exception as e:
    print(f"Import error: {e}", file=sys.stderr)
    raise

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("backfill_es_tickets")


# -----------------------
# Utility Functions
# -----------------------
def chunked(iterable, size):
    """Yield successive chunks from iterable of given size."""
    it = iter(iterable)
    while True:
        chunk = []
        try:
            for _ in range(size):
                chunk.append(next(it))
        except StopIteration:
            if chunk:
                yield chunk
            break
        yield chunk


# -----------------------
# Main Backfill Function
# -----------------------
def main(batch_size: int = 1000) -> int:
    """
    Backfill all tickets from SQL into Elasticsearch.
    - Ensures index exists
    - Reads flattened ticket rows
    - Bulk indexes in batches
    Returns exit code 0 on success, >0 on partial/failed.
    """
    logger.info("Starting ES backfill for tickets...")

    # Ensure ES connection and index
    es = get_es_client()
    if not es:
        logger.error("Failed to get Elasticsearch client.")
        return 2

    ensure_ticket_index()
    logger.info("Index ensured.")

    # Load all tickets from DB in memory; if dataset is very large, add server-side pagination
    try:
        rows: List[Dict[str, Any]] = get_all_tickets_for_indexing()
    except Exception as e:
        logger.error(f"Failed to fetch tickets from DB: {e}")
        return 3

    total = len(rows)
    if total == 0:
        logger.info("No tickets found in DB to index. Nothing to do.")
        return 0

    logger.info(f"Fetched {total} tickets from DB. Beginning bulk index in batches of {batch_size}...")

    indexed = 0
    had_errors = False

    for i, batch in enumerate(chunked(rows, batch_size), start=1):
        try:
            success_count, errors = bulk_index_tickets(batch, chunk_size=min(batch_size, 500))
            indexed += success_count
            if errors:
                had_errors = True
                # Log a small sample, not the entire error payload
                logger.error(f"Batch {i}: bulk index reported {len(errors)} errors. Sample: {errors[:2]}")
        except Exception as e:
            had_errors = True
            logger.error(f"Batch {i}: bulk index failed: {e}")

        logger.info(f"Progress: {indexed}/{total} indexed ({indexed/total:.1%})")

    if had_errors:
        logger.warning("Backfill completed with some errors. Check logs for details.")
        return 4

    logger.info("Backfill completed successfully.")
    return 0


# -----------------------
# Entry Point
# -----------------------
if __name__ == "__main__":
    # Optional: allow batch size override from CLI
    # Usage: python -m scripts.backfill_es_tickets 2000
    bs = 1000
    if len(sys.argv) > 1:
        try:
            bs = int(sys.argv[1])
        except ValueError:
            print(f"Ignoring invalid batch size '{sys.argv[1]}', using default {bs}.", file=sys.stderr)
    
    sys.exit(main(batch_size=bs))