from flask import Blueprint, request, jsonify
from . import db
from sqlalchemy import or_
from .models import User, Task, Item, Comment, RefreshToken
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity
)

api_bp = Blueprint('api', __name__)

# ✅ Auth routes
@api_bp.route('/register', methods=['POST'])
def register_user():  # renamed to avoid conflicts
    print("🔥 REGISTER ROUTE HIT")
    data = request.get_json()
    if not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'error': 'Missing fields'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username exists'}), 400

    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@api_bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    identifier = data.get('username') or data.get('email') or data.get('identifier')
    password = data.get('password')

    print("📥 Login with:", identifier)

    user = User.query.filter(
        or_(
            User.username == identifier,
            User.email == identifier
        )
    ).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        db.session.add(RefreshToken(token=refresh_token, user_id=user.id))
        db.session.commit()
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200

    return jsonify({'error': 'Invalid credentials'}), 40