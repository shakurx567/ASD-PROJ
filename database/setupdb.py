# Student ID: 24000310
# Student Name: Mzamil Ahmed
# Component: Component 1 - Database Design & Project Infrastructure


#SQL TO CREATE THE DATABASE

#RUN THIS **ONCE**

#Then you won't need this anymore. A separate file can then be created to
#add the data into the database

import sqlite3

conn = sqlite3.connect('paragon.db')

cursor = conn.cursor()


cursor.execute("PRAGMA foreign_keys = ON;")

cursor.execute("""CREATE TABLE system_users (
        userID INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(50), 
        passwd VARCHAR(255), 
        roleOfUser VARCHAR(50), 
        assignedCity INTEGER,
        FOREIGN KEY (assignedCity) REFERENCES cities(cityID)  
               )""")

cursor.execute("""CREATE TABLE cities (
    cityID INTEGER PRIMARY KEY AUTOINCREMENT,
    cityName VARCHAR(100) 
               )""")

cursor.execute("""CREATE TABLE tenants (
    tenantID INTEGER PRIMARY KEY AUTOINCREMENT,
    tenantName VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100)  
               )""")

cursor.execute("""CREATE TABLE apartments (
    apartmentID INTEGER PRIMARY KEY AUTOINCREMENT,
    apartmentType VARCHAR(50),
    rentAmount DECIMAL(10,2),
    numberOfRooms INT,
    apartmentStatus VARCHAR(20)
               )""")

cursor.execute("""CREATE TABLE leases (
    leaseID INTEGER PRIMARY KEY AUTOINCREMENT,
    tenantID INTEGER,
    apartmentID INTEGER,
    startDate DATE,
    endDate DATE,
    monthlyRent DECIMAL(10,2),
    penaltyRate DECIMAL(5,2),
    FOREIGN KEY (tenantID) REFERENCES tenants(tenantID),
    FOREIGN KEY (apartmentID) REFERENCES apartments(apartmentID))
               """)

cursor.execute("""CREATE TABLE maintenance_requests (
    requestID INTEGER PRIMARY KEY AUTOINCREMENT,
    apartmentID INTEGER,
    requestDetails TEXT, 
    priorityLevel VARCHAR(20), 
    requestStatus VARCHAR(20),
    totalCost DECIMAL(10,2),  
    timeToFix INTEGER,
    FOREIGN KEY (apartmentID) REFERENCES apartments(apartmentID))
               """)

cursor.execute("""CREATE TABLE invoices (
    invoiceID INTEGER PRIMARY KEY AUTOINCREMENT,
    leaseID INTEGER,
    dueDate DATE,
    amount DECIMAL(10,2),
    invoiceStatus VARCHAR(20), 
    FOREIGN KEY (leaseID) REFERENCES leases(leaseID))
               """)

cursor.execute("""CREATE TABLE payments (
    paymentID INTEGER PRIMARY KEY AUTOINCREMENT,
    invoiceID INTEGER,
    amount DECIMAL (10,2),
    paymentDate DATE,
    paymentStatus VARCHAR(20), 
    FOREIGN KEY (invoiceID) REFERENCES invoices(invoiceID)

               )""")

conn.commit()

conn.close()