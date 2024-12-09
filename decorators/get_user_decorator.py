import pytest
import os
import requests



@pytest.fixture(scope="module")
def api_url():
    return os.getenv("API_URL")

def get_user_decorator(func):
    def wrapper(api_url, token, *args, **kwargs):
        headers = {
            "Authorization": f"Bearer {token}",
        }
        response = requests.get(f"{api_url}/user/get/", headers=headers)
        assert response.status_code == 200, "Failed to retrieve user data"
        get_user_data = response.json()
        print("User Data:", get_user_data)
        return func(api_url, token, get_user_data, *args, **kwargs)

    return wrapper