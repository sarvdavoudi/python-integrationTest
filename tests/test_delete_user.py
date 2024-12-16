import pytest
import requests
import os
import json
from pathlib import Path
from decorators.get_user_decorator import get_user_decorator
from decorators.user_creation_decorator import user_creation_decorator
from decorators.admin_login_decorator import admin_login_decorator

@pytest.fixture(scope="module")
def api_url():
    return os.getenv("API_URL")

@admin_login_decorator
@user_creation_decorator
@get_user_decorator
def test_delete_user(api_url, token, get_user_data, user_creation_data):
    headers = {
        "Authorization": f"Bearer {token}",
    }

    # Step 1: Load existing users from the JSON file
    json_file_path = Path("generated_users/users.json")
    if not json_file_path.exists():
        pytest.fail("Users file not found. Please create users first.")

    with open(json_file_path, "r") as json_file:
        users_data = json.load(json_file)

    if not users_data:
        pytest.fail("No users found in the JSON file.")

    # Step 2: Find the recently created user in server response
    if get_user_data.get("success") and get_user_data["data"]["Total"] > 0:
        server_users = get_user_data["data"]["Data"]

        for server_user in server_users:
            # Compare server user with `user_creation_data` by email (unique identifier)
            if server_user['email'] == user_creation_data['email']:  # Match by email
                user_id = server_user['id']  # Get user_id from server response
                print(f"Deleting user: {user_creation_data['username']} with ID: {user_id}")

                # Step 3: Send DELETE request to the server
                delete_response = requests.delete(f"{api_url}/user/delete/{user_id}/", headers=headers)
                assert delete_response.status_code == 200, "Failed to delete user data"
                delete_response_data=delete_response.json()
                print(delete_response_data,"User deleted successfully.")

                # Remove user from the local JSON data
                users_data = [user for user in users_data if user["email"] != user_creation_data["email"]]
                break  # Exit the loop after deleting to avoid multiple deletions for the same user

    else:
        print("No users found to delete.")

    # Step 4: Save updated JSON data back to the file
    with open(json_file_path, "w") as json_file:
        json.dump(users_data, json_file, indent=4)
        print(f"Users data deleted in JSON file: {json_file_path}")
