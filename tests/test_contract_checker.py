
import unittest
import json

from memory_doctor.core.contract_checker import (
    load_spec,
    get_operations,
    check_route,
    extract_sdk_routes,
    compare_routes,
)


class TestContractChecker(unittest.TestCase):

    def setUp(self):
        self.spec = {
            "openapi": "3.0.0",
            "paths": {
                "/memory/experience": {
                    "post": {
                        "summary": "Store a memory",
                        "operationId": "storeMemory",
                    }
                },
                "/memory/recall": {
                    "post": {
                        "summary": "Recall a memory",
                    }
                },
                "/memory/events": {
                    "get": {
                        "summary": "List events",
                    }
                },
            },
        }
        self.paths = self.spec["paths"]

    def test_load_valid_spec(self):
        data = json.dumps(self.spec).encode("utf-8")
        self.assertEqual(load_spec(data)["openapi"], "3.0.0")

    def test_reject_invalid_json(self):
        with self.assertRaises(ValueError):
            load_spec(b"{invalid json}")

    def test_reject_missing_paths(self):
        data = json.dumps({"openapi": "3.0.0"}).encode()
        with self.assertRaises(ValueError):
            load_spec(data)

    def test_get_operations(self):
        self.assertEqual(len(get_operations(self.paths)), 3)

    def test_existing_route(self):
        result = check_route(
            self.paths, "POST", "/memory/experience"
        )
        self.assertEqual(result["Status"], "Found")

    def test_missing_route(self):
        result = check_route(
            self.paths, "POST", "/memory/documents"
        )
        self.assertEqual(
            result["Status"], "Not in specification"
        )

    def test_wrong_method(self):
        result = check_route(
            self.paths, "GET", "/memory/experience"
        )
        self.assertEqual(
            result["Status"], "Method not found"
        )

    def test_invalid_method(self):
        result = check_route(
            self.paths, "CONNECT", "/memory/experience"
        )
        self.assertEqual(
            result["Status"], "Invalid method"
        )

    def test_full_url_with_query(self):
        result = check_route(
            self.paths,
            "POST",
            "https://api.example.com/memory/experience?test=1",
        )
        self.assertEqual(result["Status"], "Found")

    def test_extract_requests_post(self):
        source = '''
import requests

def save():
    requests.post("/memory/documents")
'''
        routes = extract_sdk_routes(source)
        self.assertTrue(any(
            r["Method"] == "POST"
            and r["Path"] == "/memory/documents"
            for r in routes
        ))

    def test_extract_request_method_and_path(self):
        source = '''
class Client:
    def save(self):
        self._request("POST", "/memory/insert")
'''
        routes = extract_sdk_routes(source)
        self.assertTrue(any(
            r["Method"] == "POST"
            and r["Path"] == "/memory/insert"
            for r in routes
        ))

    def test_extract_route_constant(self):
        source = '''
BASE_URL = "https://api.example.com"

def save():
    requests.post(BASE_URL + "/memory/documents")
'''
        routes = extract_sdk_routes(source)
        self.assertTrue(any(
            r["Path"] == "/memory/documents"
            for r in routes
        ))

    def test_extract_dynamic_path_template(self):
        source = '''
class Client:
    def recall(self, memory_id):
        self._request("GET", f"/memory/{memory_id}")
'''
        routes = extract_sdk_routes(source)
        self.assertTrue(any(
            r["Path"] == "/memory/{memory_id}"
            for r in routes
        ))

    def test_invalid_python_source(self):
        with self.assertRaises(ValueError):
            extract_sdk_routes("def broken(")

    def test_compare_routes(self):
        routes = [{
            "Method": "POST",
            "Path": "/memory/experience",
            "Source": "client.py",
        }]
        result = compare_routes(self.paths, routes)
        self.assertEqual(result[0]["Status"], "Found")

    def test_compare_parameter_names(self):
        paths = {"/memory/{id}": {"get": {}}}
        routes = [{
            "Method": "GET",
            "Path": "/memory/{memory_id}",
            "Source": "client.py",
        }]
        result = compare_routes(paths, routes)
        self.assertEqual(result[0]["Status"], "Found")


if __name__ == "__main__":
    unittest.main()