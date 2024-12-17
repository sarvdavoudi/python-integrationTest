import requests
from PIL import Image
from io import BytesIO
import numpy as np
import pytesseract
import cv2
import os

def pre_process_image(image_data):
    # Create a directory for saving images
    image_dir = "images_login_captcha"
    os.makedirs(image_dir, exist_ok=True)

    received_image_path = os.path.join(image_dir, "received_captcha.png")
    image_data.save(received_image_path)

    image = np.array(image_data)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((3, 3), np.uint8)
    morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    processed_image_path = os.path.join(image_dir, "final_processed_captcha.png")
    cv2.imwrite(processed_image_path, morphed)

    return morphed

def captcha_handler_decorator(func):
    def wrapper(api_url,*args, **kwargs):
        # Step 1: Get the captcha_key from the /user/captcha/ endpoint
        response = requests.get(f"{api_url}/user/captcha/")
        assert response.status_code == 200, "Failed to retrieve captcha"

        response_data = response.json()
        captcha_key = response_data.get('data', {}).get('captcha_key')
        assert captcha_key is not None, "Captcha key is missing in the response"

        # Attempt to login with the captcha until successful
        max_retries = 20
        retry_count = 0
        successful_login = False

        while retry_count < max_retries and not successful_login:
            # Step 2: Get the captcha image
            image_response = requests.get(f"{api_url}/captcha/image/{captcha_key}/")
            assert image_response.status_code == 200, "Failed to retrieve captcha image"

            # Step 3: Pre-process the image
            image = Image.open(BytesIO(image_response.content))
            pre_processed_image = pre_process_image(image)
            processed_image = Image.fromarray(pre_processed_image)

            # Step 4: Use Tesseract to extract captcha text
            custom_config = r'--psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            raw_captcha_response = pytesseract.image_to_string(processed_image, config=custom_config).strip()

            if not raw_captcha_response:
                raise ValueError("Tesseract returned an empty response. Check the captcha image and Tesseract installation.")

            captcha_response = raw_captcha_response.lower()

            # Call the wrapped function with captcha data
            try:
                return func(api_url, captcha_key, captcha_response)
            except AssertionError as e:
                print(f"Login attempt {retry_count + 1} failed: {e}")
                # Fetch a new captcha if login fails
                response = requests.get(f"{api_url}/user/captcha/")
                assert response.status_code == 200, "Failed to retrieve new captcha"
                response_data = response.json()
                captcha_key = response_data.get('data', {}).get('captcha_key')
                assert captcha_key is not None, "Captcha key is missing in the new response"
                retry_count += 1

        assert successful_login, "Login failed after multiple attempts."
    return wrapper
