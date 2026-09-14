from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from extensions import db
from models import ROLE_MODELS


def role_required(role):
    def decorator(view):
        @wraps(view)
        @jwt_required()
        def wrapper(*args, **kwargs):
            if get_jwt().get('role') != role:
                return jsonify({'error': f'{role.capitalize()}s only'}), 403
            return view(*args, **kwargs)
        return wrapper
    return decorator


def current_user_id():
    return int(get_jwt_identity())


def current_user():
    return db.get_or_404(ROLE_MODELS[get_jwt()['role']], current_user_id(), description='User not found')
