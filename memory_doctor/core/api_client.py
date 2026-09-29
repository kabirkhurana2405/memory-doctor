
"""Read-only TinyHumans API diagnostics."""

import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import (
    HTTPRedirectHandler,
    Request,
    build_opener,
)

BASE_URL = "https://api.tinyhumans.ai"
TIMEOUT = 10
USER_AGENT = "MemoryDoctor/0.1"


class NoRedirect(HTTPRedirectHandler):
    """Prevent credentials from being forwarded on redirects."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _redact(text, api_key=None):
    """Remove credentials from diagnostic messages."""
    if api_key:
        text = text.replace(api_key.strip(), "[REDACTED]")
    return text[:300]


def _safe_error_message(exc, api_key=None):
    """Extract a useful error without exposing credentials."""
    try:
        body = exc.read(4096).decode("utf-8", errors="replace")

        try:
            data = json.loads(body)
        except (ValueError, TypeError):
            data = None

        if isinstance(data, dict):
            title = data.get("title")
            detail = data.get("detail")
            message = data.get("error") or data.get("message")

            if isinstance(title, str) and isinstance(detail, str):
                message = f"{title}: {detail}"
            elif not isinstance(message, str):
                message = (
                    title
                    or detail
                    or data.get("error_name")
                    or data.get("error_category")
                )

            if isinstance(message, str):
                return _redact(message, api_key)

        # Preserve a useful plain-text error, if present.
        if body.strip():
            return _redact(body.strip(), api_key)

    except (ValueError, OSError):
        pass

    return f"HTTP {exc.code} response received."


def _request(method, path, api_key=None, auth_style="bearer"):
    """Send a read-only request to the fixed TinyHumans API host."""

    if (
        not isinstance(path, str)
        or not path.startswith("/")
        or path.startswith("//")
        or any(ord(char) < 32 for char in path)
    ):
        raise ValueError("Invalid API path.")

    headers = {
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }

    if api_key:
        key = api_key.strip()

        if auth_style == "bearer":
            headers["Authorization"] = f"Bearer {key}"
        elif auth_style == "x-api-key":
            headers["x-api-key"] = key
        else:
            raise ValueError(
                "auth_style must be 'bearer' or 'x-api-key'."
            )

    request = Request(
        BASE_URL + path,
        headers=headers,
        method=method,
    )

    started = time.perf_counter()

    def elapsed():
        return round((time.perf_counter() - started) * 1000)

    try:
        opener = build_opener(NoRedirect)

        with opener.open(request, timeout=TIMEOUT) as response:
            return {
                "reachable": True,
                "ok": 200 <= response.status < 300,
                "status_code": response.status,
                "latency_ms": elapsed(),
                "message": f"HTTP {response.status} response received.",
            }

    except HTTPError as exc:
        return {
            # An HTTP response means the server was reachable.
            "reachable": True,
            "ok": False,
            "status_code": exc.code,
            "latency_ms": elapsed(),
            "message": _safe_error_message(exc, api_key),
        }

    except (URLError, TimeoutError, OSError):
        return {
            "reachable": False,
            "ok": False,
            "status_code": None,
            "latency_ms": elapsed(),
            "message": (
                "Could not connect. Check internet connectivity, "
                "DNS and TLS configuration."
            ),
        }


def check_api_reachability():
    """Check the public health endpoint without an API key."""
    return _request("GET", "/health")


def check_memory_access(api_key, auth_style="bearer"):
    """Perform a read-only check of the memory events endpoint."""
    if not isinstance(api_key, str) or not api_key.strip():
        raise ValueError("An API key is required.")

    return _request(
        "GET",
        "/memory/events",
        api_key=api_key,
        auth_style=auth_style,
    )