from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies

from extensions import db, limiter
from models import ROLE_MODELS, Doctor

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@limiter.limit('5/minute')
def register():
    data = request.get_json(silent=True) or {}
    model = ROLE_MODELS.get(data.get('role'))
    if not model:
        return jsonify({'error': 'Invalid role'}), 400

    missing = [f for f in ('full_name', 'username', 'email', 'password') if not str(data.get(f) or '').strip()]
    if missing:
        return jsonify({'error': f"Missing required fields: {', '.join(missing)}"}), 400
    if len(data['password']) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    if model is Doctor and not data.get('specialization'):
        return jsonify({'error': 'Specialization is required for doctors'}), 400
    if model.query.filter((model.email == data['email']) | (model.username == data['username'])).first():
        return jsonify({'error': 'Email or Username already registered'}), 400

    user = model(full_name=data['full_name'], username=data['username'], email=data['email'])
    if model is Doctor:
        user.specialization = data['specialization']
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    message = 'Doctor registered successfully' if model is Doctor else 'Account registered successfully'
    return jsonify({'message': message}), 201


@auth_bp.route('/login', methods=['POST'])
@limiter.limit('10/minute')
def login():
    data = request.get_json(silent=True) or {}
    model = ROLE_MODELS.get(data.get('role'))
    if not model:
        return jsonify({'error': 'Invalid role'}), 400

    user = model.query.filter_by(email=data.get('email')).first()
    if not user or not user.check_password(data.get('password') or ''):
        return jsonify({'error': 'The email, password or role you entered is incorrect!'}), 401

    token = create_access_token(identity=str(user.id), additional_claims={'role': data['role']})
    response = jsonify({'message': 'Login successful', **user.to_dict()})
    set_access_cookies(response, token)
    return response, 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    response = jsonify({'message': 'Logged out successfully'})
    unset_jwt_cookies(response)
    return response, 200
