from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object('config.Config')

    # Import and register blueprints
    from api.auth import auth_bp
    from api.user import user_bp
    from api.ticket import ticket_bp
    from api.admin import admin_bp
    from api.cities import cities_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(ticket_bp, url_prefix='/api/ticket')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(cities_bp, url_prefix='/api/cities')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
