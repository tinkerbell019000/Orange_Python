import uuid
from config.config import Config


def unique_username(prefix: str = "qauser") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:6]}"


ADD_USER_NEGATIVE_VALIDATIONS = [
    ({"employee": "InvalidEmp999", "pick_emp": False}, "Employee Name", "Invalid"),
    ({"username": "usr"}, "Username", "Should be at least 5 characters"),
    ({"username": Config.USERNAME}, "Username", "Already exists"),
    ({"password": "Pass1"}, "Password", "Should have at least 7 characters"),
    ({"password": "PasswordOnly"}, "Password", "minimum 1 number"),
    ({"password": "Password@123", "confirm_password": "Password@999"}, "Confirm Password", "Passwords do not match"),
]


EDIT_USERNAME_VALIDATIONS = [("", "Required")] + [
    (payload["username"], expected_msg)
    for payload, error_label, expected_msg in ADD_USER_NEGATIVE_VALIDATIONS
    if error_label == "Username"
]
