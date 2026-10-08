from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity

def roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                role = claims.get("role")
                if role not in roles:
                    return jsonify({"success": False, "error": "Access denied"}), 403
                return fn(*args, **kwargs)
            except Exception:
                return jsonify({"success": False, "error": "Authentication required"}), 401
        return wrapper
    return decorator

def current_user_id():
    return int(get_jwt_identity())

def current_role():
    return get_jwt().get("role")
