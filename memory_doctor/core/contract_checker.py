
"""OpenAPI validation and static Python SDK route inspection."""

import ast
import json
import re
from urllib.parse import urlsplit


HTTP_METHODS = {
    "get", "post", "put", "patch",
    "delete", "options", "head", "trace",
}


def load_spec(data: bytes) -> dict:
    """Load and validate an OpenAPI JSON document."""
    try:
        spec = json.loads(data.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc

    if not isinstance(spec, dict):
        raise ValueError("The JSON root must be an object.")

    if not isinstance(spec.get("paths"), dict):
        raise ValueError("No valid 'paths' object was found.")

    return spec


def get_operations(paths: dict) -> list[dict]:
    """Return all documented HTTP operations."""
    operations = []

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue

        for method in sorted(HTTP_METHODS):
            operation = path_item.get(method)

            if isinstance(operation, dict):
                operations.append({
                    "Method": method.upper(),
                    "Path": path,
                    "Summary": operation.get("summary", ""),
                    "Operation ID": operation.get("operationId", ""),
                })

    return operations


def normalize_path(path: str) -> str:
    """Normalize a route or absolute URL to its path."""
    path = path.strip()

    if "://" in path:
        path = urlsplit(path).path

    return path.split("?", 1)[0]


def check_route(paths: dict, method: str, path: str) -> dict:
    """Check whether an HTTP method and path are documented."""
    method = method.strip().lower()
    path = normalize_path(path)

    if method not in HTTP_METHODS:
        return {
            "Status": "Invalid method",
            "Details": f"Unsupported HTTP method: {method.upper()}",
        }

    if (
        not path.startswith("/")
        or any(char.isspace() for char in path)
    ):
        return {
            "Status": "Invalid path",
            "Details": "The route must start with / and contain no spaces.",
        }

    path_item = paths.get(path)

    if path_item is None:
        return {
            "Status": "Not in specification",
            "Details": "Exact path not found in the uploaded specification.",
        }

    if not isinstance(path_item, dict):
        return {
            "Status": "Unresolved path",
            "Details": "The path definition could not be inspected.",
        }

    if method not in path_item:
        return {
            "Status": "Method not found",
            "Details": (
                f"The path exists, but {method.upper()} "
                "is not documented."
            ),
        }

    if not isinstance(path_item[method], dict):
        return {
            "Status": "Unresolved operation",
            "Details": "The operation definition could not be inspected.",
        }

    return {
        "Status": "Found",
        "Details": "Path and HTTP method are documented.",
    }


# --------------------------------------------------
# STATIC PYTHON SOURCE INSPECTION
# --------------------------------------------------

def _resolve_string(node, constants: dict) -> str | None:
    """Resolve simple string expressions without executing code."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value

    if isinstance(node, ast.Name):
        return constants.get(node.id)

    if isinstance(node, ast.Attribute):
        return constants.get(node.attr)

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _resolve_string(node.left, constants)
        right = _resolve_string(node.right, constants)

        if left is not None and right is not None:
            return left + right

    if isinstance(node, ast.JoinedStr):
        parts = []

        for value in node.values:
            if isinstance(value, ast.Constant):
                if not isinstance(value.value, str):
                    return None
                parts.append(value.value)

            elif isinstance(value, ast.FormattedValue):
                expr = value.value

                if isinstance(expr, ast.Name):
                    parts.append("{" + expr.id + "}")
                elif isinstance(expr, ast.Attribute):
                    parts.append("{" + expr.attr + "}")
                else:
                    return None

            else:
                return None

        return "".join(parts)

    return None


def _collect_constants(tree: ast.AST) -> dict:
    """Collect simple string assignments for route resolution."""
    constants = {}

    for _ in range(8):
        changed = False

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                value_node = node.value
                targets = node.targets
            elif isinstance(node, ast.AnnAssign):
                value_node = node.value
                targets = [node.target]
            else:
                continue

            if value_node is None:
                continue

            value = _resolve_string(value_node, constants)
            if value is None:
                continue

            for target in targets:
                if isinstance(target, ast.Name):
                    name = target.id
                elif isinstance(target, ast.Attribute):
                    name = target.attr
                else:
                    continue

                if constants.get(name) != value:
                    constants[name] = value
                    changed = True

        if not changed:
            break

    return constants


def _is_route_candidate(value: str | None) -> bool:
    """Return True for a literal route or URL."""
    if not value:
        return False

    if "://" in value:
        return bool(urlsplit(value).scheme and urlsplit(value).netloc)

    if value.startswith("{") and "}/" in value:
        value = value[value.find("}/") + 1:]

    return value.startswith("/")


def extract_sdk_routes(
    source: str,
    source_name: str = "uploaded.py",
) -> list[dict]:
    """
    Statically identify likely HTTP routes in Python source.

    This function never executes uploaded code. It can miss routes
    that are constructed dynamically at runtime.
    """
    try:
        tree = ast.parse(source, filename=source_name)
    except SyntaxError as exc:
        raise ValueError(
            f"Cannot parse {source_name}: {exc}"
        ) from exc

    constants = _collect_constants(tree)
    found = []

    request_names = {
        "request", "request_json", "request_raw",
        "make_request", "api_call", "fetch",
    }

    def add(method, path, line, confidence="static"):
        if not _is_route_candidate(path):
            return

        normalized = normalize_path(path)

        if not normalized.startswith("/"):
            return

        item = {
            "Method": method or "Unknown",
            "Path": normalized,
            "Source": source_name,
            "Line": line,
            "Detection": confidence,
        }

        if item not in found:
            found.append(item)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func = node.func
        name = (
            func.attr if isinstance(func, ast.Attribute)
            else func.id if isinstance(func, ast.Name)
            else ""
        )
        clean_name = name.lstrip("_").lower()

        method = None
        if clean_name in HTTP_METHODS:
            method = clean_name.upper()

        # Resolve positional and keyword string arguments.
        args = [
            _resolve_string(arg, constants)
            for arg in node.args
        ]
        kwargs = {
            kw.arg: _resolve_string(kw.value, constants)
            for kw in node.keywords
            if kw.arg is not None
        }

        if method is None:
            possible_methods = [
                kwargs.get("method"),
                kwargs.get("http_method"),
                *args[:2],
            ]
            for value in possible_methods:
                if value and value.lower() in HTTP_METHODS:
                    method = value.upper()
                    break

        is_request_call = (
            clean_name in HTTP_METHODS
            or clean_name in request_names
            or "request" in clean_name
            or "api_call" in clean_name
            or any(key in kwargs for key in (
                "path", "url", "endpoint", "route"
            ))
        )

        if not is_request_call:
            continue

        candidates = [
            kwargs.get(key)
            for key in ("path", "url", "endpoint", "route")
        ]

        # For request("POST", path), don't mistake "POST" for a route.
        candidates.extend(
            value for value in args
            if not (value and value.lower() in HTTP_METHODS)
        )

        path = next(
            (value for value in candidates
             if _is_route_candidate(value)),
            None,
        )

        if path is not None:
            add(method, path, node.lineno)

    return sorted(
        found,
        key=lambda route: (
            route["Path"],
            route["Method"],
            route["Line"],
        ),
    )

def compare_routes(paths: dict, routes: list[dict]) -> list[dict]:
    """Compare extracted routes against the OpenAPI paths."""
    results = []

    def canonical(path):
        return re.sub(r"\{[^{}]+\}", "{}", path)

    def find_match(path):
        if path in paths:
            return path

        matches = [
            spec_path for spec_path in paths
            if canonical(spec_path) == canonical(path)
        ]
        return matches[0] if len(matches) == 1 else None

    for route in routes:
        method = str(route.get("Method") or "Unknown").upper()
        path = route.get("Path")
        source = route.get("Source", "Manual")

        if not isinstance(path, str):
            result = {
                "Status": "Invalid path",
                "Details": "Route path must be a string.",
            }
            path = ""
        else:
            path = normalize_path(path)

            if method == "UNKNOWN":
                match = find_match(path) if path.startswith("/") else None

                if match:
                    result = {
                        "Status": "Path found; method unknown",
                        "Details": (
                            f"Matching OpenAPI path: {match}. "
                            "The HTTP method could not be inferred."
                        ),
                    }
                else:
                    result = check_route(paths, "GET", path)
                    if result["Status"] == "Method not found":
                        result["Status"] = "Not in specification"

            else:
                match = find_match(path)
                result = check_route(
                    paths, method, match or path
                )

        results.append({
            **route,
            "Path": path,
            "Source": source,
            "Status": result["Status"],
            "Details": result["Details"],
        })

    return results