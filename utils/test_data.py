import random
import string
from config.config import Config


def unique_username(prefix: str = "admin_user") -> str:
    random_suffix = "".join(random.choices(string.ascii_lowercase, k=5))
    return f"{prefix}_{random_suffix}"


def get_valid_add_user_payload(username: str | None = None) -> dict:
    return {
        "role": "ESS",
        "employee": "a",
        "pick_emp": True,
        "status": "Enabled",
        "username": username or unique_username(),
        "password": "Password@123",
        "confirm_password": "Password@123",
    }


def get_valid_edit_user_payload(updated_username: str | None = None) -> dict:
    return {
        "role": "Admin",
        "status": "Disabled",
        "username": updated_username or unique_username(),
        "change_password": True,
        "password": "NewPassword@123",
        "confirm_password": "NewPassword@123",
    }


ADD_USER_NEGATIVE_VALIDATIONS = [
    ({"employee": "InvalidEmp999", "pick_emp": False}, "Employee Name", "Invalid"),
    ({"username": "usr"}, "Username", "Should be at least 5 characters"),
    ({"username": Config.USERNAME}, "Username", "Already exists"),
    ({"password": "Pass1"}, "Password", "Should have at least 7 characters"),
    ({"password": "PasswordOnly"}, "Password", "minimum 1 number"),
    ({"password": "Password@123", "confirm_password": "Password@999"}, "Confirm Password", "Passwords do not match"),
]

EDIT_USER_NEGATIVE_VALIDATIONS = [
    ({"username": ""}, "Username", "Required"),
    ({"employee": "InvalidEmp999", "pick_emp": False}, "Employee Name", "Invalid"),
    ({"username": "usr"}, "Username", "Should be at least 5 characters"),
    ({"username": "EXISTING_USER"}, "Username", "Already exists"),
    ({"change_password": True, "password": ""}, "Password", "Required"),
    ({"change_password": True, "password": "Pass1"}, "Password", "Should have at least 7 characters"),
    ({"change_password": True, "password": "PasswordOnly"}, "Password", "minimum 1 number"),
    (
        {"change_password": True, "password": "Password@123", "confirm_password": "Password@999"},
        "Confirm Password",
        "Passwords do not match",
    ),
]
