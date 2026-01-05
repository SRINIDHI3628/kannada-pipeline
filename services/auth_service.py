from flask import request, jsonify
from functools import wraps
from models import User

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = request.headers.get("X-User-Id")
            user = User.query.get(user_id)

            if not user or user.role not in allowed_roles:
                return jsonify({"error": "Access denied"}), 403

            return f(*args, **kwargs)
        return wrapper
    return decorator
