import os
import requests


def test_api_connection():
    url = os.getenv("API_URL")
    assert url, "API_URL.is not loaded from environment variables"
    response = requests.get(url)
    response_data = response.json()
    assert response_data["code"] != 1000, f"Test failed:internal server error"
    print("Test passed successfully!")
