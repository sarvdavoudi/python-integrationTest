import os
import requests
import pytest
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image
import pytesseract

load_dotenv()

# Make sure Tesseract is in your PATH, otherwise specify the path here
# For example: pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

@pytest.fixture(scope="session")
def admin_token():
    base_url = os.getenv("API_URL")
    login_endpoint = "/user/login"
    login_url = f"{base_url}{login_endpoint}"

    admin_credentials = {
        "username": "admin",  # Replace with actual admin username
        "password": "adminadmin"  # Replace with actual admin password
    }

    # Send login request to get the token
    response = requests.post(login_url, json=admin_credentials)
    assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
    
    response_data = response.json()
    token = response_data.get("token")
    assert token, "Failed to obtain token"

    return token

@pytest.fixture(scope="session")
def captcha_image():
    base_url = os.getenv("API_URL")
    captcha_endpoint = "/user/captcha"
    captcha_url = f"{base_url}{captcha_endpoint}"

    # Fetch the CAPTCHA image
    response = requests.get(captcha_url)
    response.raise_for_status()  # Ensure we got a valid response

    # Return the image as a BytesIO object
    return BytesIO(response.content)

@pytest.fixture(scope="session")
def captcha_text(captcha_image):
    # Open the CAPTCHA image from the BytesIO object
    image = Image.open(captcha_image)
    
    # Use Tesseract OCR to extract text from the image
    captcha_text = pytesseract.image_to_string(image, config="--psm 6")
    
    # Clean the extracted text (removing unwanted characters)
    captcha_text = captcha_text.strip()
    
    return captcha_text
