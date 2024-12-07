import requests
from .captcha_handler_decorator import captcha_handler_decorator


def admin_login_decorator(func):
    @captcha_handler_decorator
    def wrapper(api_url, captcha_key, captcha_response, *args, **kwargs):
        payload = {
            'username': 'admin',
            'password': 'adminadmin',
            'captcha_key': captcha_key,
            'captcha_response': captcha_response,
        }

        response = requests.post(f"{api_url}/user/login/", json=payload)
        assert response.status_code == 200, "Login failed"
        
        # Extract token or handle response as needed
        token = response.json().get('data', {}).get('token')
        assert token, "Token missing in the login response"
        print('Login successful. Token:', token)

        # Pass the token to the decorated function
        return func(api_url, token, *args, **kwargs)

    return wrapper
