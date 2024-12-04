import requests
from PIL import Image
import pytesseract
from io import BytesIO
import cv2
import numpy as np
import os


def pre_process_image(image_data):
    # Create directory for saving images
    image_dir = "images_captcha_test"
    os.makedirs(image_dir, exist_ok=True)
    
    # Save the original image
    main_image_path = os.path.join(image_dir, "received_captcha.png")
    image_data.save(main_image_path)
    
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
    cv2.imwrite(processed_image_path, morphed)
    
    # Return the processed image
    return morphed


def captcha_handler_decorator(func):
    def wrapper(api_url, *args, **kwargs):
        # Step 1: Get the captcha_key
        response = requests.get(f"{api_url}/user/captcha/")
        assert response.status_code == 200, "Failed to retrieve captcha"

        response_data = response.json()
        captcha_key = response_data.get('data', {}).get('captcha_key')
        assert captcha_key is not None, "Captcha key is missing in the response"
        print('Captcha_Key is:', captcha_key)

        # Step 2: Use the captcha_key to request the captcha image
        image_response = requests.get(f"{api_url}/captcha/image/{captcha_key}/")
        assert image_response.status_code == 200, "Failed to retrieve captcha image"

        # Step 3: Pre-process the image to improve OCR accuracy
        image = Image.open(BytesIO(image_response.content))
        pre_processed_image = pre_process_image(image)

        # Convert pre-processed image back to a PIL image for Tesseract
        processed_image = Image.fromarray(pre_processed_image)

        # Step 4: Use Tesseract to extract text
        custom_config = r'--psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        raw_captcha_response = pytesseract.image_to_string(processed_image, config=custom_config).strip()
        print('Raw Captcha Response is:', raw_captcha_response)

        if not raw_captcha_response:
            raise ValueError("Tesseract returned an empty response. Check the captcha image and Tesseract installation.")

        captcha_response = raw_captcha_response.lower()
        print('Processed Captcha Response:', captcha_response)

        # Pass the captcha_key and captcha_response to the test function
        return func(api_url, captcha_key, captcha_response, *args, **kwargs)
    return wrapper
