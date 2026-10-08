from functools import wraps
from flask import request
from pydantic import ValidationError
from app.utils.responses import fail

def validate_json(schema_cls):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                parsed = schema_cls.model_validate(request.get_json(silent=True) or {})
            except ValidationError as exc:
                return fail("Validation failed", 422, "validation_error", exc.errors(include_url=False))
            return fn(parsed, *args, **kwargs)
        return wrapper
    return decorator
