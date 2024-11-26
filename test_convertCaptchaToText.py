import pytest
import requests
import os
from PIL import Image
import pytesseract
from io import BytesIO

@pytest.fixture(scope='module')
def api_url():
    return os.getenv("API_URL")

def test_get_captcha_and_login(api_url):
    # Specify the path to the Tesseract executable
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update the path if necessary

    # Step 1: Get the captcha_key from the /user/captcha/ endpoint
    response = requests.get(f"{api_url}/user/captcha/")
    
    # Ensure the response status is 200
    assert response.status_code == 200, "Failed to retrieve captcha"
    
    # Parse the JSON response
    response_data = response.json()
    
    # Extract the captcha_key
    captcha_key = response_data.get('data', {}).get('captcha_key')
    assert captcha_key is not None, "Captcha key is missing in the response"

    # Step 2: Use the captcha_key to request the captcha image
    image_response = requests.get(f"{api_url}/captcha/image/{captcha_key}/")
    assert image_response.status_code == 200, "Failed to retrieve captcha image"
    
    # Step 3: Convert the image response to text using Tesseract
    image = Image.open(BytesIO(image_response.content))
    captcha_response = pytesseract.image_to_string(image).strip()  # Use Tesseract to extract text

    # Check if the captcha_response is empty
    if not captcha_response:
        raise ValueError("Tesseract returned an empty response. Please check the captcha image and Tesseract installation.")

    # Print for debugging
    print('Captcha Key:', captcha_key)
    print('Captcha Response:', captcha_response)
