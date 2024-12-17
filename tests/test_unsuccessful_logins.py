import pytest
import requests
import os
from decorators.admin_login_decorator import admin_login_decorator


@pytest.fixture(scope="module")
def api_url():
    return os.getenv("API_URL")


@admin_login_decorator

def test_unsuccessful_logins(api_url, token):
    headers = {
        "Authorization": f"Bearer {token}",
    }

    response = requests.get(f"{api_url}/user/unsuccessful_logins/", headers=headers)
    assert response.status_code == 200, "Failed to retrieve unsuccessful logins"
    response_data = response.json()
    print("unsuccessful logins are:", response_data)
