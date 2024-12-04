import requests
from captcha_handler import captcha_handler


def admin_login_decorator(func):
    @captcha_handler
    def wrapper(api_url, captcha_key, captcha_response, *args, **kwargs):
        login_url = f"{api_url}/user/login/"
        payload = {
            'username': 'admin',
            'password': 'adminadmin',
            'captcha_key': captcha_key,
            'captcha_response': captcha_response,
        }

        response = requests.post(login_url, json=payload)
        assert response.status_code == 200, "Login failed"
        
        # Extract token or handle response as needed
        token = response.json().get('data', {}).get('token')
        assert token, "Token missing in the login response"
        print('Login successful. Token:', token)

        # Pass the token to the decorated function
        return func(api_url, token, *args, **kwargs)

    return wrapper
