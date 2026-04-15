# Student ID: 24000310
# Student Name: Mzamil Ahmed
# Component: Component 1 - Database Design & Project Infrastructure

def is_email_valid(email):
    return "@" in email and "." in email

def is_phone_valid(phone):
    return phone.isdigit() and len(phone) >= 10