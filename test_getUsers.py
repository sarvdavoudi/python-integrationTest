import pytest
import requests
import os
from PIL import Image
import pytesseract
from io import BytesIO
import cv2
import numpy as np
import time

@pytest.fixture(scope='module')
def api_url():
    return os.getenv("API_URL")

def pre_process_image(image_data):
    # Create a directory for saving images
    image_dir = "images_login_captcha"
    
    # Create directory if it doesn't exist
    os.makedirs(image_dir, exist_ok=True)
    
    # Save the received image in its original form
    received_image_path = os.path.join(image_dir, "received_captcha.png")
    image_data.save(received_image_path)  # Save the received image
    print(f"Received image saved at: {received_image_path}")

    # Convert the image to a NumPy array for processing
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
    
    # Save the final processed image
    processed_image_path = os.path.join(image_dir, "final_processed_captcha.png")
    cv2.imwrite(processed_image_path, morphed)  # Save the processed image
    print(f"Processed captcha image saved at: {processed_image_path}")

    # Return the processed image
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
    captcha_key = response_data.get('data', {}).get('captcha_key')
    assert captcha_key is not None, "Captcha key is missing in the response"
    print('Captcha_Key is:', captcha_key)

    #####################################################################
    # Step 5: Perform login using username, password, captcha_key, and captcha_response
    login_url = f"{api_url}/user/login/"

    # Initialize variables
    max_retries = 5  # Max number of retries
    retry_count = 0
    successful_login = False
    token = None  

    # Retry loop until successful login with proccessed captcha
    while retry_count < max_retries and not successful_login:
        # Step 2: Use the captcha_key to request the captcha image
        image_response = requests.get(f"{api_url}/captcha/image/{captcha_key}/")
        assert image_response.status_code == 200, "Failed to retrieve captcha image"

        # Step 3: Pre-process the image to improve OCR accuracy
        image = Image.open(BytesIO(image_response.content))
        pre_processed_image = pre_process_image(image)

        # Convert pre-processed image back to a PIL image for Tesseract
        processed_image = Image.fromarray(pre_processed_image)

        # Step 4: Use Tesseract to extract text with character whitelist to avoid unwanted characters
        custom_config = r'--psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        raw_captcha_response = pytesseract.image_to_string(processed_image, config=custom_config).strip()
        print('Raw Captcha Response is:', raw_captcha_response)

        if not raw_captcha_response:
            raise ValueError("Tesseract returned an empty response. Check the captcha image and Tesseract installation.")

        # Convert to lowercase for processing if needed
        captcha_response = raw_captcha_response.lower()
        print('Processed Captcha Response from upperCase to lowerCase is:', captcha_response)

        payload = {
            'username': 'admin',
            'password': 'adminadmin',
            'captcha_key': captcha_key,
            'captcha_response': captcha_response
        }

        login_response = requests.post(login_url, json=payload)

        # Add debug prints and checks here
        print('Login Response:', login_response.json())  # Print the full login response for debugging

        if login_response.status_code == 200:
            successful_login = True  # Exit the loop if login is successful
            token = login_response.json().get('token')  # Extract the token
            
            # Adjust the path based on the actual response structure
            token = login_response.json().get('data', {}).get('token')  # Ensure you're getting the token from the correct path
            
            if token:
                print('Received Token:', token)
            else:
                print("Token is missing in the login response.")
                print('Full Response:', login_response.json())  # Print full response if token is missing
        else:
            print(f"Login attempt {retry_count + 1} failed with status code {login_response.status_code}. Requesting new captcha...")
            print('Response Content:', login_response.text)  # Print response content for further diagnosis
            
            # Request a new captcha if login fails
            response = requests.get(f"{api_url}/user/captcha/")

            # Ensure the response status is 200
            assert response.status_code == 200, "Failed to retrieve new captcha"

            # Parse the new captcha_key
            response_data = response.json()
            captcha_key = response_data.get('data', {}).get('captcha_key')
            assert captcha_key is not None, "Captcha key is missing in the new response"
            print('New Captcha_Key is:', captcha_key)

            retry_count += 1
            time.sleep(2)  # Sleep for a short duration before retrying

    # Ensure login was successful after retries
    assert successful_login, "Login failed after multiple attempts."

    return token  # Return the token for further use

####################################################################
def test_get_user_data(api_url):
    token = test_get_captcha_and_login(api_url)  # Call the login test to get the token

    # Define headers with the token
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Send GET request with headers
    response = requests.get(f"{api_url}/user/get/", headers=headers)

    # Ensure the response status is 200
    assert response.status_code == 200, "Failed to retrieve user data"

    # Parse the response data
    response_data = response.json()
    print("User Data:", response_data)

    