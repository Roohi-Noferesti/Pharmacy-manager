# adapters/external_api_adapter.py
import requests

class ExternalAPIAdapter:
    def __init__(self, base_url):
        self.base_url = base_url

    def make_request(self, endpoint, method='GET', params=None, data=None, headers=None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.request(method, url, params=params, data=data, headers=headers)
        return response.json() if response.status_code == 200 else None
