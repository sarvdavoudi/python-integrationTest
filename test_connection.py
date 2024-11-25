import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

def test_api_connection():
    url = os.getenv("API_URL")
    response = requests.get(url)
    assert response.status_code == 200, f"Failed to connect to API. Status code: {response.status_code}"
