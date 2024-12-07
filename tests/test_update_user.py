import pytest
import requests
import os
import json
from pathlib import Path
from decorators.admin_login_decorator import admin_login_decorator

@pytest.fixture(scope="module")
def api_url():
    return os.getenv("API_URL")

@admin_login_decorator
def test_get_and_update_user(api_url, token):
    headers = {
        "Authorization": f"Bearer {token}",
    }

    # Step 1: Get the list of users from the server
    response = requests.get(f"{api_url}/user/get/", headers=headers)
    assert response.status_code == 200, "Failed to retrieve user data"
    response_data = response.json()
    print("User Data from server:", response_data)

    # Step 2: Load existing users from the JSON file
    json_file_path = Path("generated_users/users.json")
    if not json_file_path.exists():
        pytest.fail("Users file not found. Please create users first.")

    with open(json_file_path, "r") as json_file:
        users_data = json.load(json_file)

    # Step 3: Compare and find matches
    if response_data.get("success") and response_data["data"]["Total"] > 0:
        server_users = response_data["data"]["Data"]
        
        for server_user in server_users:
            # Find matching user in JSON data by email
            for json_user in users_data:
                if server_user['email'] == json_user['email']:  # Match by email
                    user_id = server_user['id']  # Get user_id from server response
                    print(f"Updating user: {json_user['username']} with ID: {user_id}")

                    # Check if the username already has an update suffix
                    if "_updated" not in json_user["username"]:
                        updated_username = f"{json_user['username']}_updated"  # First update
                    else:
                        # Extract the existing version number if present, or start with 2
                        if "_updated" in json_user["username"]:
                            base_username = json_user["username"].split("_updated")[0]
                            suffix = json_user["username"].split("_updated")[1]
                            update_count = int(suffix) if suffix.isdigit() else 1
                            updated_username = f"{base_username}_updated{update_count + 1}"
                        else:
                            updated_username = f"{json_user['username']}_updated2"  # Default second update

                    # Prepare updated data
                    update_data = {
                        "username": updated_username,
                        "email": f"{updated_username}@example.com"  # Updated email for clarity
                    }

                    # Step 4: Update user data on the server
                    update_response = requests.patch(f"{api_url}/user/update/{user_id}/", headers=headers, json=update_data)
                    assert update_response.status_code == 200, "Failed to update user data"
                    updated_user_data = update_response.json()
                    print("Updated User Data from server:", updated_user_data)

                    # Update the JSON file with new information
                    json_user.update(update_data)
                    break  # Exit the loop after updating to avoid multiple updates for the same user

    else:
        print("No users found to update.")
    
    # Step 5: Save updated JSON data back to the file
    with open(json_file_path, "w") as json_file:
        json.dump(users_data, json_file, indent=4)
        print(f"Users data updated in JSON file: {json_file_path}")
