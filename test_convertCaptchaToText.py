import pytest
import requests
import os
from PIL import Image
import pytesseract
from io import BytesIO
import cv2
import numpy as np

@pytest.fixture(scope='module')
def api_url():
    return os.getenv("API_URL")

def pre_process_image(image_data):
    # Convert the image to a NumPy array
    image = np.array(image_data)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Remove noise using GaussianBlur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply binary thresholding (Otsu's method)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Use morphological transformations to clean the text
    kernel = np.ones((3, 3), np.uint8)
    morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    return morphed

def test_get_captcha_and_login(api_url):
    # Specify the path to Tesseract executable
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update path if necessary

    # Step 1: Get the captcha_key from the /user/captcha/ endpoint
    response = requests.get(f"{api_url}/user/captcha/")

    # Ensure the response status is 200
    assert response.status_code == 200, "Failed to retrieve captcha"
    
    # Parse the JSON response
    response_data = response.json()
    
    # Extract the captcha_key
    captcha_key = response_data.get('data', {}).get('captcha_key')
    assert captcha_key is not None, "Captcha key is missing in the response"
    
    # Print the captcha_key for debugging
    print('Captcha_Key is:', captcha_key)

    # Step 2: Use the captcha_key to request the captcha image
    image_response = requests.get(f"{api_url}/captcha/image/{captcha_key}/")
    assert image_response.status_code == 200, "Failed to retrieve captcha image"
    
    # Step 3: Pre-process the image to improve OCR accuracy
    image = Image.open(BytesIO(image_response.content))
    pre_processed_image = pre_process_image(image)
    
    # Convert pre-processed image back to a PIL image for Tesseract
    processed_image = Image.fromarray(pre_processed_image)

    # Use Tesseract to extract text with character whitelist to avoid unwanted characters
    custom_config = r'--psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    raw_captcha_response = pytesseract.image_to_string(processed_image, config=custom_config).strip()  # Raw OCR result
    
    # Print raw captcha response for debugging
    print('Raw Captcha Response is :', raw_captcha_response)

    # Check if the raw_captcha_response is empty
    if not raw_captcha_response:
        raise ValueError("Tesseract returned an empty response. Please check the captcha image and Tesseract installation.")
    
    # If needed, convert to lowercase
    captcha_response = raw_captcha_response.lower()  # Optional: Adjust if captcha expects lowercase text

    # Print the final processed captcha response
    print('Processed Captcha Response from upperCase to lowerCase is:', captcha_response)

    # You can add additional checks to verify the correctness of the captcha_response
