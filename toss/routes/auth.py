from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app import db
from models.models import User

# Initialize a clean Flask Blueprint cluster for security tasks
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Missing required username or password fields!"}), 400

    # Ensure this profile doesn't collide with an existing account record
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "This username is already taken!"}), 400

    # Turn the plain text password into a secure cryptographic hash string
    hashed_password = generate_password_hash(password)

    # Initialize a new User row based on player.py specifications (starting with 0 coins/0 xp)
    new_user = User(
        username=username,
        password_hash=hashed_password,
        coins=0,
        xp=0
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"Account '{username}' successfully registered!"}), 201


@auth_bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Please provide both username and password!"}), 400

    user = User.query.filter_by(username=username).first()

    # Compare the provided plain text password with the encrypted database hash
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid username or password!"}), 401

    # Issue a secure JWT string identifying this specific user instance session
    token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful!",
        "access_token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "coins": user.coins,
            "xp": user.xp
        }
    }), 200