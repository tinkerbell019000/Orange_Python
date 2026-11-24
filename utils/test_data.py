import uuid
from config.config import Config


def unique_username(prefix: str = "qauser") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:6]}"


DEFAULT_USER_PAYLOAD = {
    "role": "ESS",
    "status": "Enabled",
    "employee_hint": "a",
    "password": "Password@123",
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
