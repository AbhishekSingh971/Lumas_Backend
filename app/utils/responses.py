from flask import jsonify


def ok(data=None, message=None, status=200):
    payload = {"success": True}
    if message is not None:
        payload["message"] = message
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status

def fail(message, status=400, code="bad_request", details=None):
    payload = {"success": False, "error": {"code": code, "message": message}}
    if details:
        payload["error"]["details"] = details
    return jsonify(payload), status
