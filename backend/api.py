import os

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import InternalServerError, NotFound

from config import Config
from extensions import bcrypt, db, jwt, limiter
from routes.account import account_bp
from routes.appointments import appointments_bp
from routes.auth import auth_bp
from routes.doctors import doctors_bp


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    CORS(app, origins=[os.getenv('FRONTEND_URL', 'http://localhost:3000')], supports_credentials=True)

    app.register_blueprint(auth_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(account_bp)

    @app.errorhandler(NotFound)
    def not_found(error):
        return jsonify({'error': error.description}), 404

    @app.errorhandler(InternalServerError)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Something went wrong. Please try again.'}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')
