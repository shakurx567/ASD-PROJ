# Component 4 | Author: Abdulmalik Altaleb (23061771)

from database.db_setup import get_connection
from datetime import datetime


class InvoiceDAO:

    @staticmethod
    def create_invoice(lease_id, tenant_id, amount, due_date, description=""):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO invoices (lease_id, tenant_id, amount, due_date, description)
            VALUES (?,?,?,?,?)
        """, (lease_id, tenant_id, amount, due_date, description))
        invoice_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return invoice_id

    @staticmethod
    def get_invoice(invoice_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.*, t.name as tenant_name, t.email,
                   a.apartment_name, c.name as city_name
            FROM invoices i
            JOIN tenants t ON i.tenant_id = t.tenant_id
            JOIN leases l ON i.lease_id = l.lease_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
            JOIN cities c ON a.city_id = c.city_id
            WHERE i.invoice_id = ?
        """, (invoice_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_all_invoices(status=None, tenant_id=None):
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT i.*, t.name as tenant_name,
                   a.apartment_name, c.name as city_name
            FROM invoices i
            JOIN tenants t ON i.tenant_id = t.tenant_id
            JOIN leases l ON i.lease_id = l.lease_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
            JOIN cities c ON a.city_id = c.city_id
            WHERE 1=1
        """
        params = []
        if status:
            sql += " AND i.status = ?"
            params.append(status)
        if tenant_id:
            sql += " AND i.tenant_id = ?"
            params.append(tenant_id)
        sql += " ORDER BY i.due_date DESC"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def update_invoice_status(invoice_id, status):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE invoices SET status = ? WHERE invoice_id = ?",
            (status, invoice_id))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    @staticmethod
    def generate_monthly_invoices():
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now()
        due_date = now.strftime("%Y-%m-01")
        month_desc = now.strftime("%B %Y")

        cursor.execute("""
            SELECT l.lease_id, l.tenant_id, l.monthly_rent
            FROM leases l
            WHERE l.status = 'Active'
            AND l.lease_id NOT IN (
                SELECT lease_id FROM invoices
                WHERE due_date LIKE ?
            )
        """, (now.strftime("%Y-%m") + "%",))
        leases = cursor.fetchall()

        count = 0
        for lease in leases:
            cursor.execute("""
                INSERT INTO invoices (lease_id, tenant_id, amount, due_date, description)
                VALUES (?,?,?,?,?)
            """, (lease["lease_id"], lease["tenant_id"],
                  lease["monthly_rent"], due_date,
                  f"{month_desc} Rent"))
            count += 1

        conn.commit()
        conn.close()
        return count

    @staticmethod
    def detect_overdue_invoices():
        conn = get_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            UPDATE invoices SET status = 'Overdue'
            WHERE status = 'Pending' AND due_date < ?
        """, (today,))
        count = cursor.rowcount
        conn.commit()
        conn.close()
        return count

    @staticmethod
    def get_overdue_invoices():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.*, t.name as tenant_name, t.email,
                   a.apartment_name, c.name as city_name
            FROM invoices i
            JOIN tenants t ON i.tenant_id = t.tenant_id
            JOIN leases l ON i.lease_id = l.lease_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
            JOIN cities c ON a.city_id = c.city_id
            WHERE i.status IN ('Overdue')
            ORDER BY i.due_date ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_tenant_invoices(tenant_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.*, a.apartment_name, c.name as city_name
            FROM invoices i
            JOIN leases l ON i.lease_id = l.lease_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
            JOIN cities c ON a.city_id = c.city_id
            WHERE i.tenant_id = ?
            ORDER BY i.due_date DESC
        """, (tenant_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_financial_summary(city_id=None):
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT
                COALESCE(SUM(CASE WHEN i.status = 'Paid' THEN i.amount ELSE 0 END), 0) as total_collected,
                COALESCE(SUM(CASE WHEN i.status = 'Pending' THEN i.amount ELSE 0 END), 0) as total_pending,
                COALESCE(SUM(CASE WHEN i.status = 'Overdue' THEN i.amount ELSE 0 END), 0) as total_overdue,
                COALESCE(SUM(CASE WHEN i.status = 'Partial' THEN i.amount ELSE 0 END), 0) as total_partial,
                COUNT(*) as total_invoices
            FROM invoices i
            JOIN leases l ON i.lease_id = l.lease_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
        """
        params = ()
        if city_id:
            sql += " WHERE a.city_id = ?"
            params = (city_id,)
        cursor.execute(sql, params)
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}

    @staticmethod
    def apply_late_fee(invoice_id, fee_amount):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT lease_id, tenant_id FROM invoices WHERE invoice_id = ?",
            (invoice_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        due_date = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            INSERT INTO invoices (lease_id, tenant_id, amount, due_date, description)
            VALUES (?,?,?,?,?)
        """, (row["lease_id"], row["tenant_id"], fee_amount, due_date,
              f"Late fee for invoice #{invoice_id}"))
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return new_id

    @staticmethod
    def get_financial_by_city():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.name as city_name,
                COALESCE(SUM(CASE WHEN i.status = 'Paid' THEN i.amount ELSE 0 END), 0) as collected,
                COALESCE(SUM(CASE WHEN i.status IN ('Pending','Overdue','Partial') THEN i.amount ELSE 0 END), 0) as pending,
                COUNT(i.invoice_id) as invoice_count
            FROM cities c
            LEFT JOIN apartments a ON c.city_id = a.city_id
            LEFT JOIN leases l ON a.apartment_id = l.apartment_id
            LEFT JOIN invoices i ON l.lease_id = i.lease_id
            GROUP BY c.city_id, c.name
            ORDER BY c.name
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
