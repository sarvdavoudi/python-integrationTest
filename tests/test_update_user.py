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

def test_update_user(api_url, token, response_data,user_data):
    headers = {
        "Authorization": f"Bearer {token}",
    }

    # Step 1: Load existing users from the JSON file
    json_file_path = Path("generated_users/users.json")
    if not json_file_path.exists():
        pytest.fail("Users file not found. Please create users first.")

    with open(json_file_path, "r") as json_file:
        users_data = json.load(json_file)

    # Check if there are any users in the JSON file
    if not users_data:
        pytest.fail("No users found in the JSON file.")

    # Get the first user from the JSON data
    first_json_user = users_data[0]

    # Step 2: Compare the first JSON user with server users
    if response_data.get("success") and response_data["data"]["Total"] > 0:
        server_users = response_data["data"]["Data"]
        
        for server_user in server_users:
            # Compare the first JSON user with the server user by email
            if server_user['email'] == first_json_user['email']:  # Match by email
                user_id = server_user['id']  # Get user_id from server response
                print(f"Updating user: {first_json_user['username']} with ID: {user_id}")

                # Check if the username already has an update suffix
                if "_updated" not in first_json_user["username"]:
                    updated_username = f"{first_json_user['username']}_updated"  # First update
                else:
                    # Extract the existing version number if present, or start with 2
                    if "_updated" in first_json_user["username"]:
                        base_username = first_json_user["username"].split("_updated")[0]
                        suffix = first_json_user["username"].split("_updated")[1]
                        update_count = int(suffix) if suffix.isdigit() else 1
                        updated_username = f"{base_username}_updated{update_count + 1}"
                    else:
                        updated_username = f"{first_json_user['username']}_updated2"  # Default second update

                # Prepare updated data
                update_data = {
                    "username": updated_username,
                    "email": f"{updated_username}@example.com"  # Updated email for clarity
                }

                # Step 3: Update user data on the server
                update_response = requests.patch(f"{api_url}/user/update/{user_id}/", headers=headers, json=update_data)
                assert update_response.status_code == 200, "Failed to update user data"
                updated_user_data = update_response.json()
                print("Updated User Data from server:", updated_user_data)

                # Update the JSON file with new information
                first_json_user.update(update_data)
                break  # Exit the loop after updating to avoid multiple updates for the same user

    else:
        print("No users found to update.")
    
    # Step 4: Save updated JSON data back to the file
    with open(json_file_path, "w") as json_file:
        json.dump(users_data, json_file, indent=4)
        print(f"Users data updated in JSON file: {json_file_path}")
