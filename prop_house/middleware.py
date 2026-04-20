import json
import os
from django.http import HttpRequest


class HeaderDebugMiddleware:
    def __init__(self, get_response):

        self.get_response = get_response
        self.log_file = "request_debug.log"

    def __call__(self, request: HttpRequest):

        # Collect Headers, build to dictionary
        headers = {k: v for k, v in request.headers.items()}

        session_key = getattr(request.session, "session_key", "No Session Key")
        cookie_session_id = request.COOKIES.get("sessionid", "No Cookie Found")

        # 3. Write to file
        with open(self.log_file, "a") as f:
            f.write(f"\n--- [{request.method}] {request.path} ---\n")
            f.write(f"Session Key in Django: {session_key}\n")
            f.write(f"Session ID in Cookie: {cookie_session_id}\n")
            f.write("Full Headers:\n")
            f.write(json.dumps(headers, indent=4))
            f.write(f"\n{'-' * 40}\n")

        response = self.get_response(request)
        return response
