import pytest
import requests
import os
import json
from pathlib import Path
from decorators.admin_login_decorator import admin_login_decorator
from decorators.user_creation_decorator import user_creation_decorator
from decorators.captcha_handler_decorator import captcha_handler_decorator


def read_last_user_from_json(file_name="users.json"):
    """Reads the last user data from the JSON file."""
    json_file_path = Path("generated_users") / file_name
    if json_file_path.exists():
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
            if data:
                return data[-1]  # Get the last user
    raise FileNotFoundError("No user data found in the JSON file.")


@pytest.fixture(scope="module")
def api_url():
    return os.getenv("API_URL")


@admin_login_decorator
@user_creation_decorator
@captcha_handler_decorator
def test_login_user(api_url, captcha_key, captcha_response):
    """Test user login with the last record from the JSON file."""

    def perform_login(api_url, payload):
        """Handles the login process."""
        response = requests.post(f"{api_url}/user/login/", json=payload)
        if response.status_code != 200:
            print("Login failed:", response.status_code, response.json())
        assert response.status_code == 200, "Login failed"
        print("Login successful:", response.json())
        return response.json()

    # Read the last user data from the JSON file
    user_data = read_last_user_from_json()
    username = user_data["username"]
    password = user_data["password"]

    # Create the login payload
    payload = {
        "username": username,
        "password": password,
        "captcha_key": captcha_key,
        "captcha_response": captcha_response,
    }

    # Perform login and get the response
    login_response = perform_login(api_url, payload)

    if 'data' not in login_response or 'token' not in login_response['data']:
        print("Login response does not contain a token.")
        return  # Exit if login is not successful

    token = login_response["data"]["token"]  # Extract the token from the login response

    # Set the headers with the token
    headers = {
        "Authorization": f"Bearer {token}",
    }

    # Send a GET request to fetch security questions with headers
    response = requests.get(f"{api_url}/user/security_questions/get/", headers=headers)
    assert response.status_code == 200, "Failed to fetch security questions"

    # Extract security questions from the response
    response_data = response.json()
    questions = response_data.get("data", {})

    # Debugging output to inspect the response structure
    print("Security questions response data:", response_data)

    # Check if questions are structured as expected
    if not isinstance(questions, dict) or not questions:
        print("No security questions found or questions is not a dictionary.")
        return  # Exit if no questions are found

    # Prepare the answers for the security questions
    questions_and_answers = []
    for question_key, question_value in questions.items():
        questions_and_answers.append(
            {
                "question": question_value,
                "answer": "x1",  # Replace with the actual answer
            }
        )

    # Create the payload for the security questions
    security_payload = {
        "username": username,
        "questions_and_answers": questions_and_answers,
    }

    # Send the POST request to answer the security questions with headers
    security_response = requests.post(
        f"{api_url}/user/security_questions/", json=security_payload, headers=headers
    )

    # Check the response
    assert security_response.status_code == 200, "Failed to answer security questions"
    print("Security questions answered successfully:", security_response.json())
