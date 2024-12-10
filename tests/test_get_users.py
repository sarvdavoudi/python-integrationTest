import pytest
import requests
import os
from decorators.admin_login_decorator import admin_login_decorator


@pytest.fixture(scope="module")
def api_url():
    return os.getenv("API_URL")


@admin_login_decorator

def test_getUsers(api_url, token):
    headers = {
        "Authorization": f"Bearer {token}",
    }

    response = requests.get(f"{api_url}/user/get/", headers=headers)
    assert response.status_code == 200, "Failed to retrieve user data"
    response_data = response.json()
    print("User Data:", response_data)
