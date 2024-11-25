import pytest
import requests
import os

@pytest.fixture(scope='module')
def api_url():
    return os.getenv("API_URL")

def test_get_captcha(api_url):
    response = requests.get(f"{api_url}/user/captcha/")
    
    # Print the entire response 
    print('Response:', response.json())
    
    # Ensure the response status is 200
    assert response.status_code == 200, "Failed to retrieve captcha"
    
    # Parse the JSON response to have access to the data objects
    response_data = response.json()
    
    # Extract the captcha_key
    captcha_key = response_data.get('data', {}).get('captcha_key')
    
    # Print the captcha_key
    print('Captcha Key:', captcha_key)

    # Optionally, assert that the captcha_key is not None
    assert captcha_key is not None, "Captcha key is missing in the response"

   
   # Step 2: Use the captcha_key to request the captcha image
    image_response = requests.get(f"{api_url}/captcha/image/{captcha_key}/")
    
    # Print the image response
    print('Image Response:', image_response.json())
    
    # Ensure the image response status is 200
    assert image_response.status_code == 200, "Failed to retrieve captcha image"
