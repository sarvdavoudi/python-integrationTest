import pytest
import os
import requests
from decorators.captcha_handler_decorator import captcha_handler_decorator


@pytest.fixture(scope='module')
def api_url():
    return os.getenv("API_URL")


@captcha_handler_decorator
def test_login(api_url, captcha_key, captcha_response):
    login_url = f"{api_url}/user/login/"
    payload = {
        'username': 'admin',
        'password': 'adminadmin',
        'captcha_key': captcha_key,
        'captcha_response': captcha_response,
    }

    response = requests.post(login_url, json=payload)
    assert response.status_code == 200, "Login failed"
    print('Login Response:', response.json())
