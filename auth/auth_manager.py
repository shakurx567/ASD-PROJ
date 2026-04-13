# Student ID: 24019989
# Student Name: Abdishakur Hasan
# Component: Component 2 - User Authentication, RBAC & Desktop UI Framework

import bcrypt
import os
from models.user import User
from utils.session import Session

CITIES = ["Bristol", "Cardiff", "London", "Manchester", "All"]

MOCK_USERS = [
    {
        "user_id": 1,
        "username": "manager1",
        "password": bcrypt.hashpw("Manager123!".encode(), bcrypt.gensalt()),
        "role": "Manager",
        "city": "All"
    },
    {
        "user_id": 2,
        "username": "admin1",
        "password": bcrypt.hashpw("Admin123!".encode(), bcrypt.gensalt()),
        "role": "Administrator",
        "city": "Bristol"
    },
    {
        "user_id": 3,
        "username": "frontdesk1",
        "password": bcrypt.hashpw("Frontdesk123!".encode(), bcrypt.gensalt()),
        "role": "Front-Desk Staff",
        "city": "London"
    },
    {
        "user_id": 4,
        "username": "finance1",
        "password": bcrypt.hashpw("Finance123!".encode(), bcrypt.gensalt()),
        "role": "Finance Manager",
        "city": "Manchester"
    },
    {
        "user_id": 5,
        "username": "maintenance1",
        "password": bcrypt.hashpw("Maintenance123!".encode(), bcrypt.gensalt()),
        "role": "Maintenance Staff",
        "city": "Cardiff"
    }
]

failed_attempts = {}
MAX_ATTEMPTS = 3
REMEMBER_ME_FILE = "remember_me.txt"

def is_password_strong(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not any(c.isupper() for c in password):
        return False, "Password must contain an uppercase letter."
    if not any(c.islower() for c in password):
        return False, "Password must contain a lowercase letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain a number."
    return True, "OK"

def attempt_login(username, password):
    if failed_attempts.get(username, 0) >= MAX_ATTEMPTS:
        return False, "Account locked. Too many failed attempts."

    user_data = next((u for u in MOCK_USERS if u["username"] == username), None)

    if user_data and bcrypt.checkpw(password.encode(), user_data["password"]):
        failed_attempts[username] = 0
        user = User(
            user_data["user_id"],
            user_data["username"],
            user_data["role"],
            user_data["city"]
        )
        Session.login(user)
        return True, "Login successful."
    else:
        failed_attempts[username] = failed_attempts.get(username, 0) + 1
        remaining = MAX_ATTEMPTS - failed_attempts[username]
        if remaining <= 0:
            return False, "Account locked. Too many failed attempts."
        return False, f"Invalid credentials. {remaining} attempt(s) remaining."

def logout():
    Session.logout()

def save_remember_me(username):
    with open(REMEMBER_ME_FILE, "w") as f:
        f.write(username)

def load_remember_me():
    if os.path.exists(REMEMBER_ME_FILE):
        with open(REMEMBER_ME_FILE, "r") as f:
            return f.read().strip()
    return ""

def clear_remember_me():
    if os.path.exists(REMEMBER_ME_FILE):
        os.remove(REMEMBER_ME_FILE)