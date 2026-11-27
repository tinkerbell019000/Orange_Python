import os
import random
import string
import uuid
import pytest
from config.config import Config

USER_ROLES = ("Admin", "ESS")
USER_STATUSES = ("Enabled", "Disabled")
EMPLOYEE_SEARCH_LETTERS = ("a",)

def unique_username(prefix: str = "user") -> str:
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "master")
    random_letters = "".join(random.choices(string.ascii_lowercase, k=4))
    short_uuid = uuid.uuid4().hex[:4]
    return f"{prefix}_{worker_id}_{random_letters}{short_uuid}"

def random_user_role(exclude: str | None = None) -> str:
    choices = [r for r in USER_ROLES if r != exclude]
    return random.choice(choices)

def random_user_status(exclude: str | None = None) -> str:
    choices = [s for s in USER_STATUSES if s != exclude]
    return random.choice(choices)

def random_employee_query() -> str:
    return random.choice(EMPLOYEE_SEARCH_LETTERS)

def random_valid_password(length: int = 12) -> str:
    upper = random.choice(string.ascii_uppercase)
    lower = random.choice(string.ascii_lowercase)
    digit = random.choice(string.digits)
    special = random.choice("@#$%&*!")
    remaining = "".join(random.choices(string.ascii_letters + string.digits, k=max(length - 4, 4)))
    chars = list(upper + lower + digit + special + remaining)
    random.shuffle(chars)
    return "".join(chars)

def random_short_username() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=random.randint(1, 4)))

def random_short_password() -> str:
    return (random.choice(string.ascii_uppercase) + random.choice(string.ascii_lowercase) + random.choice(string.digits) + "".join(random.choices(string.ascii_lowercase, k=random.randint(1, 3))))

def random_letters_only_password(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters, k=length))

def random_invalid_employee() -> str:
    return f"InvalidEmp_{uuid.uuid4().hex[:6]}"

def get_user_lookup_payload(username: str) -> dict:
    return {"username": username}

def get_valid_add_user_payload(username: str | None = None,role: str | None = None,status: str | None = None,password: str | None = None,) -> dict:
    pwd = password or random_valid_password()
    return {
        "role": role or random_user_role(),
        "employee": random_employee_query(),
        "pick_emp": True,
        "status": status or "Enabled",
        "username": username or unique_username("add"),
        "password": pwd,
        "confirm_password": pwd,
    }

def get_valid_edit_user_payload(current_username: str,updated_username: str | None = None,role: str | None = None,status: str | None = None,password: str | None = None,) -> dict:
    pwd = password or random_valid_password()
    return {
        "current_username": current_username,
        "role": role or random_user_role(),
        "status": status or random_user_status(),
        "username": updated_username or unique_username("edit"),
        "change_password": True,
        "password": pwd,
        "confirm_password": pwd,
    }

ADD_USER_NEGATIVE_VALIDATIONS = [
    pytest.param({"role": ""}, "User Role", "Required", id="add-role-required"),
    pytest.param({"employee": "", "pick_emp": False}, "Employee Name", "Required", id="add-employee-required"),
    pytest.param({"employee": random_invalid_employee(), "pick_emp": False}, "Employee Name", "Invalid", id="add-employee-invalid"),
    pytest.param({"status": ""}, "Status", "Required", id="add-status-required"),
    pytest.param({"username": ""}, "Username", "Required", id="add-username-required"),
    pytest.param({"username": random_short_username()}, "Username", "Should be at least 5 characters", id="add-username-min-length"),
    pytest.param({"username": Config.USERNAME}, "Username", "Already exists", id="add-username-duplicate"),
    pytest.param({"password": ""}, "Password", "Required", id="add-password-required"),
    pytest.param({"password": random_short_password()}, "Password", "Should have at least 7 characters", id="add-password-min-length"),
    pytest.param({"password": random_letters_only_password()}, "Password", "minimum 1 number", id="add-password-missing-number"),
    pytest.param({"password": random_valid_password(), "confirm_password": random_valid_password()},"Confirm Password","Passwords do not match",id="add-confirm-password-mismatch",),
]

EDIT_USER_NEGATIVE_VALIDATIONS = [
    pytest.param({"username": ""}, "Username", "Required", id="edit-username-required"),
    pytest.param({"employee": random_invalid_employee(), "pick_emp": False}, "Employee Name", "Invalid", id="edit-employee-invalid"),
    pytest.param({"username": random_short_username()}, "Username", "Should be at least 5 characters", id="edit-username-min-length"),
    pytest.param({"username": Config.USERNAME}, "Username", "Already exists", id="edit-username-duplicate"),
    pytest.param({"change_password": True, "password": ""}, "Password", "Required", id="edit-password-required"),
    pytest.param({"change_password": True, "password": random_short_password()}, "Password", "Should have at least 7 characters", id="edit-password-min-length"),
    pytest.param({"change_password": True, "password": random_letters_only_password()}, "Password", "minimum 1 number", id="edit-password-missing-number"),
    pytest.param({"change_password": True,"password": random_valid_password(),"confirm_password": random_valid_password(),},"Confirm Password","Passwords do not match",id="edit-confirm-password-mismatch",),
]
