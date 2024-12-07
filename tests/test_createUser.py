import pytest
import requests
import os
import random
import string
import json
from pathlib import Path
from decorators.admin_login_decorator import admin_login_decorator

@pytest.fixture(scope="module")
def api_url():
    return os.getenv("API_URL")


def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def get_or_create_json_file(folder_name="generated_users", file_name="users.json"):
    folder_path = Path(folder_name)
    folder_path.mkdir(parents=True, exist_ok=True)  
    file_path = folder_path / file_name
    if not file_path.exists():  
        with open(file_path, "w") as json_file:
            json.dump([], json_file)
    return file_path

@admin_login_decorator
def test_create_user(api_url, token):
    random_username = f"user_{generate_random_string()}"
    random_email = f"{generate_random_string()}@example.com"
    random_password = generate_random_string(8)
    
    create_user_payload = {
        "username": random_username,
        "email": random_email,
        "password": random_password,
        "password_again": random_password,
        "role": "base"  
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
    }

    response = requests.post(f"{api_url}/user/create/", json=create_user_payload, headers=headers)
    
    
    assert response.status_code == 200, "User creation failed"
    response_data = response.json()

    
    user_data = {
        "username": random_username,
        "email": random_email,
        "password": random_password,
        "response": response_data
    }
    
    json_file_path = get_or_create_json_file()
    
    with open(json_file_path, "r+") as json_file:
        existing_data = json.load(json_file)
        existing_data.append(user_data)  
        json_file.seek(0)  
        json.dump(existing_data, json_file, indent=4)

    print(f"User data added to: {json_file_path}")
    
    assert response.status_code == 200, "User creation failed"
    response_data = response.json()

    print("Created User Data:", response_data)