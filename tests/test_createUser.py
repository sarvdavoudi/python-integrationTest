import pytest
import requests
import os
from decorators.admin_login_decorator import admin_login_decorator

@pytest.fixture(scope="module")
def api_url():
    return os.getenv("API_URL")


@admin_login_decorator
def test_create_user(api_url, token):
    create_user_payload = {
        "username": "test3",
        "email": "test3@gmail.com",
        "password": "123456789",
        "password_again": "123456789",
        "role": "base"
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
    }

  
    response = requests.post(f"{api_url}/user/create/", json=create_user_payload, headers=headers)
    
    # بررسی وضعیت پاسخ
    assert response.status_code == 200, "User creation failed"
    response_data = response.json()

    # نمایش داده‌های پاسخ در صورت نیاز
    print("Created User Data:", response_data)
