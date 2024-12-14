import pytest
import os
import requests
from decorators.captcha_handler_decorator import captcha_handler_decorator


@pytest.fixture(scope='module')
def api_url():
    return os.getenv("API_URL")


@captcha_handler_decorator
def test_admin_login(api_url, captcha_key, captcha_response):
    payload = {
        'username': 'admin',
        'password': 'adminadmin',
        'captcha_key': captcha_key,
        'captcha_response': captcha_response,
    }

    response = requests.post(f"{api_url}/user/login/", json=payload)
    assert response.status_code == 200, "Login failed"
    print('Login Response:', response.json())
