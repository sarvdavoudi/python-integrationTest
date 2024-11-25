import os
import requests
import pytest

# Test to create a user, using the admin_token fixture to get the token
def test_create_user(admin_token):
    base_url = os.getenv("API_URL")
    assert base_url, "API_URL is not set in the environment variables."

    endpoint = "/user/create"
    url = f"{base_url}{endpoint}"

    user_data = {
        "username": "test_user",
        "email": "test_user@example.com",
        "password": "secure_password123"
    }

    headers = {
        "Authorization": f"Bearer {admin_token}"
    }

    # Send the POST request to create a user
    response = requests.post(url, json=user_data, headers=headers)
    response.raise_for_status()

    # Validate the response status and body
    assert response.status_code in [200, 201], f"Failed to create user. Status code: {response.status_code}"
    response_data = response.json()
    assert response_data.get("message") == "User created successfully", "User creation failed!"
