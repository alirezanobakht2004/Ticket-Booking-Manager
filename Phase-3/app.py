import logging
from flask import Flask
from flask_cors import CORS


def create_app():
    """
    Flask application factory function.
    Initializes the application with configuration, logging, and all extensions.
    """
    # -----------------------
    # Initial Configuration
    # -----------------------
    app = Flask(__name__)
    CORS(app)
    app.config.from_object('config.Config')

    # -----------------------
    # Logging Configuration
    # -----------------------
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logger = logging.getLogger("app")

    # Increase Flask app logger verbosity if configured
    if getattr(app.config, "FLASK_DEBUG_LOG", True):
        app.logger.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    # -----------------------
    # Elasticsearch Initialization
    # -----------------------
    if getattr(app.config, "ELASTICSEARCH_ENABLE", True):
        try:
            from services.es_client import get_es_client, ensure_ticket_index
            es = get_es_client()
            ensure_ticket_index()
            logger.info("Elasticsearch initialized and ticket index ensured")
        except Exception as e:
            logger.error(f"Elasticsearch initialization failed: {e}")

        # -----------------------
        # Optional ES Backfill on Startup
        # -----------------------
        if getattr(app.config, "ELASTICSEARCH_BACKFILL_ON_START", False):
            try:
                from db.db import get_all_tickets_for_indexing
                from services.es_client import bulk_index_tickets
                rows = get_all_tickets_for_indexing()
                if rows:
                    logger.info(f"Backfilling {len(rows)} tickets into Elasticsearch...")
                    success, errors = bulk_index_tickets(rows, chunk_size=500)
                    if errors:
                        logger.warning(f"ES backfill completed with errors (sample): {errors[:2]}")
                    logger.info(f"ES backfill success count: {success}")
                else:
                    logger.info("No tickets found for ES backfill.")
            except Exception as e:
                logger.error(f"ES backfill failed: {e}")

    # -----------------------
    # Blueprint Registration
    # -----------------------
    # Authentication
    from api.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # Cities
    from api.cities import cities_bp
    app.register_blueprint(cities_bp, url_prefix='/api/cities')

    # Tickets
    from api.ticket import ticket_bp
    app.register_blueprint(ticket_bp, url_prefix='/api/tickets')

    # Reservations
    from api.reservation import reservation_bp
    app.register_blueprint(reservation_bp, url_prefix='/api/reservations')

    # Payments
    from api.payment import payment_bp
    app.register_blueprint(payment_bp, url_prefix='/api/payments')

    # Admin
    from api.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # Users
    from api.user import user_bp
    app.register_blueprint(user_bp, url_prefix='/api/user')

    # Reports
    from api.report import report_bp
    app.register_blueprint(report_bp, url_prefix='/api/report')

    # -----------------------
    # Final Initialization
    # -----------------------
    logger.info("Application initialized")
    return app


# -----------------------
# Main Entry Point
# -----------------------
if __name__ == '__main__':
    app = create_app()
    # Host/port/debug can also be driven by config
    app.run(
        host='0.0.0.0', 
        port=getattr(app.config, "PORT", 5000), 
        debug=True
    )