import pytest
import requests
import os
import json
from pathlib import Path
from decorators.admin_login_decorator import admin_login_decorator
from decorators.captcha_handler_decorator import captcha_handler_decorator

def read_last_user_from_json(file_name="users.json"):
    """Reads the last user data from the JSON file."""
    json_file_path = Path("generated_users") / file_name
    if json_file_path.exists():
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
            if data:
                return data[-1]  # Get the last user
    raise FileNotFoundError("No user data found in the JSON file.")

@pytest.fixture(scope="module")
def api_url():
    return os.getenv("API_URL")

@captcha_handler_decorator
def test_login_user(api_url, captcha_key, captcha_response):
    """Test user login with the last record from the JSON file."""
    
    def perform_login(api_url, payload):
        """Handles the login process."""
        response = requests.post(f"{api_url}/user/login/", json=payload)
        assert response.status_code == 200, "Login failed"
        print("Login successful:", response.json())

    # Read the last user data from the JSON file
    user_data = read_last_user_from_json()
    username = user_data["username"]
    password = user_data["password"]

    # Create the login payload
    payload = {
        "username": username,
        "password": password,
        "captcha_key": captcha_key,  
        "captcha_response": captcha_response, 
    }

    perform_login(api_url, payload)
