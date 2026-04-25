# Component: Components 1/3/4 - Database, Tenant & Apartment, Payment & Maintenance

import sqlite3
import os
import bcrypt

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pams.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # ── Cities ──────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            city_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    # ── Users ───────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN (
                'Front-Desk Staff','Finance Manager',
                'Maintenance Staff','Administrator','Manager'
            )),
            assigned_city INTEGER,
            FOREIGN KEY (assigned_city) REFERENCES cities(city_id)
        )
    """)

    # ── Tenants ─────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            tenant_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ni_number TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            occupation TEXT,
            reference_info TEXT,
            apartment_requirements TEXT,
            emergency_contact TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ── Apartments ──────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS apartments (
            apartment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_id INTEGER NOT NULL,
            apartment_name TEXT NOT NULL,
            type TEXT NOT NULL,
            rent_amount REAL NOT NULL,
            number_of_rooms INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Vacant'
                CHECK(status IN ('Vacant','Occupied','Under Maintenance')),
            is_active INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (city_id) REFERENCES cities(city_id)
        )
    """)

    # ── Leases ──────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leases (
            lease_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id INTEGER NOT NULL,
            apartment_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            monthly_rent REAL NOT NULL,
            penalty_rate REAL NOT NULL DEFAULT 0.05,
            deposit_amount REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Active'
                CHECK(status IN ('Active','Expired','Terminated','Pending')),
            termination_notice_date TEXT,
            FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
            FOREIGN KEY (apartment_id) REFERENCES apartments(apartment_id)
        )
    """)

    # ── Invoices ────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
            lease_id INTEGER NOT NULL,
            tenant_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            due_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
                CHECK(status IN ('Pending','Paid','Overdue','Partial')),
            description TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (lease_id) REFERENCES leases(lease_id),
            FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
        )
    """)

    # ── Payments ────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            tenant_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_date TEXT NOT NULL,
            method TEXT NOT NULL DEFAULT 'Cash'
                CHECK(method IN ('Cash','Bank Transfer','Card','Cheque')),
            status TEXT NOT NULL DEFAULT 'Completed'
                CHECK(status IN ('Completed','Refunded')),
            FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id),
            FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
        )
    """)

    # ── Maintenance Requests ────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS maintenance_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            apartment_id INTEGER NOT NULL,
            tenant_id INTEGER,
            description TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'Medium'
                CHECK(priority IN ('Low','Medium','High','Urgent')),
            status TEXT NOT NULL DEFAULT 'Pending'
                CHECK(status IN ('Pending','In Progress','Resolved','Cancelled')),
            cost REAL NOT NULL DEFAULT 0,
            time_to_fix INTEGER NOT NULL DEFAULT 0,
            resolution_notes TEXT,
            scheduled_date TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            resolved_at TEXT,
            FOREIGN KEY (apartment_id) REFERENCES apartments(apartment_id),
            FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
        )
    """)

    # ── Complaints ──────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            linked_request_id INTEGER,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
            FOREIGN KEY (linked_request_id)
                REFERENCES maintenance_requests(request_id)
        )
    """)

    conn.commit()
    conn.close()


def seed_data():
    conn = get_connection()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM cities")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    # ── Seed Cities ─────────────────────────────────────
    cities = ["Bristol", "Cardiff", "London", "Manchester"]
    for city in cities:
        cursor.execute("INSERT INTO cities (name) VALUES (?)", (city,))

    # ── Seed Users ──────────────────────────────────────
    users = [
        ("manager1", "Manager123!", "Manager", None),
        ("admin1", "Admin123!", "Administrator", 1),
        ("frontdesk1", "Frontdesk123!", "Front-Desk Staff", 3),
        ("finance1", "Finance123!", "Finance Manager", 4),
        ("maintenance1", "Maintenance123!", "Maintenance Staff", 2),
    ]
    for username, password, role, city_id in users:
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        cursor.execute(
            "INSERT INTO users (username, password, role, assigned_city) VALUES (?,?,?,?)",
            (username, hashed, role, city_id)
        )

    # ── Seed Tenants ────────────────────────────────────
    tenants = [
        ("AB123456C", "John Smith", "07700900001", "john.smith@email.com",
         "Engineer", "Dr. Jane Doe", "2 Bedroom", "Mary Smith - 07700900099"),
        ("CD789012E", "Sarah Johnson", "07700900002", "sarah.j@email.com",
         "Teacher", "Prof. Alan Green", "1 Bedroom", "Tom Johnson - 07700900098"),
        ("EF345678G", "Ahmed Hassan", "07700900003", "ahmed.h@email.com",
         "Accountant", "Lisa White", "3 Bedroom", "Fatima Hassan - 07700900097"),
        ("GH901234I", "Emma Wilson", "07700900004", "emma.w@email.com",
         "Nurse", "Dr. Peter Brown", "Studio", "David Wilson - 07700900096"),
        ("IJ567890K", "James Taylor", "07700900005", "james.t@email.com",
         "Solicitor", "Margaret Davis", "2 Bedroom", "Claire Taylor - 07700900095"),
        ("KL234567M", "Priya Patel", "07700900006", "priya.p@email.com",
         "Software Developer", "Raj Kumar", "1 Bedroom", "Vikram Patel - 07700900094"),
    ]
    for t in tenants:
        cursor.execute("""
            INSERT INTO tenants (ni_number, name, phone, email, occupation,
                reference_info, apartment_requirements, emergency_contact)
            VALUES (?,?,?,?,?,?,?,?)
        """, t)

    # ── Seed Apartments ─────────────────────────────────
    apartments = [
        (1, "Flat 1A", "1 Bedroom", 850.00, 1, "Occupied"),
        (1, "Flat 1B", "2 Bedroom", 1200.00, 2, "Occupied"),
        (1, "Flat 2A", "Studio", 650.00, 1, "Vacant"),
        (1, "Flat 2B", "3 Bedroom", 1500.00, 3, "Under Maintenance"),
        (2, "Unit 101", "2 Bedroom", 950.00, 2, "Occupied"),
        (2, "Unit 102", "1 Bedroom", 750.00, 1, "Vacant"),
        (3, "Suite 1", "2 Bedroom", 1800.00, 2, "Occupied"),
        (3, "Suite 2", "3 Bedroom", 2200.00, 3, "Occupied"),
        (3, "Suite 3", "Studio", 1100.00, 1, "Vacant"),
        (4, "Room 301", "1 Bedroom", 900.00, 1, "Occupied"),
        (4, "Room 302", "2 Bedroom", 1150.00, 2, "Vacant"),
        (4, "Room 303", "3 Bedroom", 1400.00, 3, "Vacant"),
    ]
    for a in apartments:
        cursor.execute("""
            INSERT INTO apartments (city_id, apartment_name, type, rent_amount,
                number_of_rooms, status) VALUES (?,?,?,?,?,?)
        """, a)

    # ── Seed Leases ─────────────────────────────────────
    leases = [
        (1, 1, "2025-01-01", "2026-01-01", 850.00, 0.05, 850.00, "Active"),
        (2, 2, "2025-03-01", "2026-03-01", 1200.00, 0.05, 1200.00, "Active"),
        (3, 5, "2025-02-01", "2026-02-01", 950.00, 0.05, 950.00, "Active"),
        (4, 7, "2025-06-01", "2026-06-01", 1800.00, 0.05, 1800.00, "Active"),
        (5, 8, "2025-04-01", "2026-04-01", 2200.00, 0.05, 2200.00, "Active"),
        (6, 10, "2025-05-01", "2026-05-01", 900.00, 0.05, 900.00, "Active"),
    ]
    for l in leases:
        cursor.execute("""
            INSERT INTO leases (tenant_id, apartment_id, start_date, end_date,
                monthly_rent, penalty_rate, deposit_amount, status)
            VALUES (?,?,?,?,?,?,?,?)
        """, l)

    # ── Seed Invoices ───────────────────────────────────
    invoices = [
        (1, 1, 850.00, "2026-04-01", "Paid", "April 2026 Rent"),
        (2, 2, 1200.00, "2026-04-01", "Paid", "April 2026 Rent"),
        (3, 3, 950.00, "2026-04-01", "Pending", "April 2026 Rent"),
        (4, 4, 1800.00, "2026-04-01", "Overdue", "April 2026 Rent"),
        (5, 5, 2200.00, "2026-04-01", "Paid", "April 2026 Rent"),
        (6, 6, 900.00, "2026-04-01", "Partial", "April 2026 Rent"),
        (1, 1, 850.00, "2026-03-01", "Paid", "March 2026 Rent"),
        (2, 2, 1200.00, "2026-03-01", "Paid", "March 2026 Rent"),
    ]
    for inv in invoices:
        cursor.execute("""
            INSERT INTO invoices (lease_id, tenant_id, amount, due_date, status, description)
            VALUES (?,?,?,?,?,?)
        """, inv)

    # ── Seed Payments ───────────────────────────────────
    payments = [
        (1, 1, 850.00, "2026-03-28", "Bank Transfer"),
        (2, 2, 1200.00, "2026-03-30", "Card"),
        (5, 5, 2200.00, "2026-04-01", "Bank Transfer"),
        (6, 6, 500.00, "2026-04-05", "Cash"),
        (7, 1, 850.00, "2026-02-28", "Bank Transfer"),
        (8, 2, 1200.00, "2026-02-27", "Card"),
    ]
    for p in payments:
        cursor.execute("""
            INSERT INTO payments (invoice_id, tenant_id, amount, payment_date, method)
            VALUES (?,?,?,?,?)
        """, p)

    # ── Seed Maintenance Requests ───────────────────────
    maintenance = [
        (4, 3, "Leaking pipe in bathroom", "High", "In Progress", 0, 0,
         None, "2026-04-18", "2026-04-10"),
        (2, 2, "Broken window lock", "Medium", "Resolved", 120.00, 90,
         "Replaced window lock mechanism", None, "2026-03-15"),
        (7, 4, "Heating not working", "Urgent", "Pending", 0, 0,
         None, None, "2026-04-12"),
        (10, 6, "Door handle loose", "Low", "Resolved", 35.00, 30,
         "Tightened and replaced screws", None, "2026-03-20"),
    ]
    for m in maintenance:
        cursor.execute("""
            INSERT INTO maintenance_requests (apartment_id, tenant_id, description,
                priority, status, cost, time_to_fix, resolution_notes,
                scheduled_date, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, m)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    seed_data()
    print("Database initialized and seeded successfully.")
