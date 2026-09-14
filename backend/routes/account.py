from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from auth import current_user
from extensions import db

account_bp = Blueprint('account', __name__)


@account_bp.route('/account', methods=['GET'])
@jwt_required()
def get_account():
    return jsonify(current_user().to_dict()), 200


@account_bp.route('/account', methods=['PUT'])
@jwt_required()
def update_account():
    user = current_user()
    model = type(user)
    data = request.get_json(silent=True) or {}
    full_name = (data.get('full_name') or '').strip()
    email = (data.get('email') or '').strip()
    new_password = data.get('new_password') or ''

    if full_name and len(full_name) < 2:
        return jsonify({'error': 'Full name must be at least 2 characters'}), 400
    if email and model.query.filter(model.email == email, model.id != user.id).first():
        return jsonify({'error': 'Email already in use'}), 400

    if new_password:
        if not data.get('current_password'):
            return jsonify({'error': 'Current password is required to set a new password'}), 400
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters'}), 400
        user.set_password(new_password)

    user.full_name = full_name or user.full_name
    user.email = email or user.email
    db.session.commit()
    return jsonify({'message': 'Account updated successfully', **user.to_dict()}), 200
