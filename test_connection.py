import os
import requests

def test_api_connection():
    url = os.getenv("API_URL")    
    assert url, "API_URL.is not loaded from environment variables"    
    response = requests.get(url)
    assert response.status_code == 200, f"Failed to connect to API. Status code: {response.status_code}"
