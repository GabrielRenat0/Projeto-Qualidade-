import json
import pytest
import requests
from pathlib import Path

class APIClient:
    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url
        self.timeout = 10
        
    def _request(self, method, route, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, f"{self.base_url}{route}", **kwargs)
        
    def get(self, route, **kwargs): return self._request("GET", route, **kwargs)
    def post(self, route, **kwargs): return self._request("POST", route, **kwargs)
    def put(self, route, **kwargs): return self._request("PUT", route, **kwargs)
    def patch(self, route, **kwargs): return self._request("PATCH", route, **kwargs)
    def delete(self, route, **kwargs): return self._request("DELETE", route, **kwargs)

@pytest.fixture(scope="session")
def api():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return APIClient(session, "https://jsonplaceholder.typicode.com")

@pytest.fixture(scope="session")
def massa():
    payloads_path = Path(__file__).parent / "data" / "payloads.json"
    if payloads_path.exists():
        with open(payloads_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}
