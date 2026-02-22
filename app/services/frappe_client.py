import requests


class FrappeClient:
    def __init__(self, frappe_url: str, api_key: str, api_secret: str):
        self.frappe_url = frappe_url
        self.headers = {
            "Authorization": f"token {api_key}:{api_secret}",
            "Content-Type": "application/json"
        }

    def post(self, resource: str, payload: dict) -> dict:
        response = requests.post(
            f"{self.frappe_url}/api/resource/{resource}",
            json=payload,
            headers=self.headers
        )
        if response.status_code not in (200, 201):
            raise Exception(response.text)
        return response.json().get("data", {})

    def get(self, resource: str, name: str) -> dict:
        response = requests.get(
            f"{self.frappe_url}/api/resource/{resource}/{name}",
            headers=self.headers
        )
        if response.status_code != 200:
            raise Exception(response.text)
        return response.json().get("data", {})

    def list(self, resource: str) -> list:
        response = requests.get(
            f"{self.frappe_url}/api/resource/{resource}",
            headers=self.headers
        )
        if response.status_code != 200:
            raise Exception(response.text)
        return response.json().get("data", [])

    def delete(self, resource: str, name: str) -> None:
        response = requests.delete(
            f"{self.frappe_url}/api/resource/{resource}/{name}",
            headers=self.headers
        )
        if response.status_code != 202:
            raise Exception(response.text)
