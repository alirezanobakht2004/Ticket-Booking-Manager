import logging
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object('config.Config')

    # Set up logging for debugging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)  # Set logging level to DEBUG for verbose output

    # Import and register blueprints
    from api.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    from api.cities import cities_bp
    app.register_blueprint(cities_bp, url_prefix='/api/cities')

    from api.ticket import ticket_bp
    app.register_blueprint(ticket_bp, url_prefix='/api/tickets')

    from api.reservation import reservation_bp
    app.register_blueprint(reservation_bp, url_prefix='/api/reservations')
    
    from api.payment import payment_bp
    app.register_blueprint(payment_bp, url_prefix='/api/payments')

    from api.admin import admin_bp
    app.register_blueprint(admin_bp,url_prefix = '/api/admin')

    from api.user import user_bp
    app.register_blueprint(user_bp, url_prefix='/api/user')

    from api.report import report_bp
    app.register_blueprint(report_bp, url_prefix='/api/report')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0',debug=True)
