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
    app.register_blueprint(cities_bp, url_prefix='/api')

    from api.ticket import ticket_bp
    app.register_blueprint(ticket_bp, url_prefix='/api')

    from api.reservation import reservation_bp
    app.register_blueprint(reservation_bp, url_prefix='/api')


    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
