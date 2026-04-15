# Student ID: 24000310
# Student Name: Mzamil Ahmed
# Component: Component 1 - Database Design & Project Infrastructure

from datetime import datetime

def get_date_today():
    return datetime.now().strftime("%Y-%m-%d")

def format_date(date_obj):
    return date_obj.strftime("%Y-%m-%d")

