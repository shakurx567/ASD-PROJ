# Student ID: 24000310
# Student Name: Mzamil Ahmed
# Component: Component 1 - Database Design & Project Infrastructure

#Run this code to DROP a table
#Replace [TABLENAME] with the actual name of the table

import sqlite3
conn = sqlite3.connect('paragon.db')
cursor = conn.cursor()

cursor.execute("DROP TABLE [TABLENAME]")
conn.commit()

print("Success!")

conn.close()


#TABLE NAMES:
#system_users
#cities
#tenants
#apartments
#leases
#maintenance_requests
#invoices