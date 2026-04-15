# Student ID: 24000310
# Student Name: Mzamil Ahmed
# Component: Component 1 - Database Design & Project Infrastructure

# Run this code to get the names of all the tables

import sqlite3
conn = sqlite3.connect('paragon.db')
cursor = conn.cursor()


#UNCOMMENT CODE TO CHECK THE TABLE NAMES IN DATABASE
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

tables = cursor.fetchall()

for table in tables:
    print(table[0])