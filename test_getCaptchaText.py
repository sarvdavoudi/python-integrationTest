import pytest
import requests
import os
from PIL import Image
import pytesseract
from io import BytesIO

@pytest.fixture(scope='module')
def api_url():
    return os.getenv("API_URL")

def test_get_captcha(api_url):
    # Specify the path to the Tesseract executable
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update the path if necessary

    # Step 1: Get the captcha_key from the /user/captcha/ endpoint
    response = requests.get(f"{api_url}/user/captcha/")
    
    # Print the entire response
    print('Response Status:', response.status_code)
    print('Response Content:', response.content)

    # Ensure the response status is 200
    assert response.status_code == 200, "Failed to retrieve captcha"
    
    # Parse the JSON response
    response_data = response.json()  # This may raise an error if not valid JSON
    
    # Extract the captcha_key
    captcha_key = response_data.get('data', {}).get('captcha_key')
    
    # Print the captcha_key
    print('Captcha_Key:', captcha_key)

    # Optionally, assert that the captcha_key is not None
    assert captcha_key is not None, "Captcha key is missing in the response"

    # Step 2: Use the captcha_key to request the captcha image
    image_response = requests.get(f"{api_url}/captcha/image/{captcha_key}/")
    
    # Ensure the image response status is 200
    assert image_response.status_code == 200, "Failed to retrieve captcha image"
    
    # Step 3: Convert the image response to text using Tesseract
    image = Image.open(BytesIO(image_response.content))  # Open the image from bytes
    captcha_response = pytesseract.image_to_string(image)    # Use Tesseract to extract text
    
    # Print the extracted text
    print('captcha_response is', captcha_response.strip())