# Component 4 | Author: Abdulmalik Altaleb (23061771)

from database.db_setup import get_connection
from datetime import datetime


class PaymentDAO:

    @staticmethod
    def record_payment(invoice_id, tenant_id, amount, method="Cash",
                       payment_date=None):
        if not payment_date:
            payment_date = datetime.now().strftime("%Y-%m-%d")
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO payments (invoice_id, tenant_id, amount, payment_date, method)
            VALUES (?,?,?,?,?)
        """, (invoice_id, tenant_id, amount, payment_date, method))
        payment_id = cursor.lastrowid

        cursor.execute("""
            SELECT COALESCE(SUM(p.amount), 0) as total_paid, i.amount as invoice_amount
            FROM invoices i
            LEFT JOIN payments p ON i.invoice_id = p.invoice_id
                AND p.status = 'Completed'
            WHERE i.invoice_id = ?
            GROUP BY i.invoice_id
        """, (invoice_id,))
        row = cursor.fetchone()
        if row:
            if row["total_paid"] >= row["invoice_amount"]:
                cursor.execute(
                    "UPDATE invoices SET status = 'Paid' WHERE invoice_id = ?",
                    (invoice_id,))
            else:
                cursor.execute(
                    "UPDATE invoices SET status = 'Partial' WHERE invoice_id = ?",
                    (invoice_id,))

        conn.commit()
        conn.close()
        return payment_id

    @staticmethod
    def get_payment(payment_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, t.name as tenant_name, i.amount as invoice_amount,
                   i.due_date, i.description as invoice_description
            FROM payments p
            JOIN tenants t ON p.tenant_id = t.tenant_id
            JOIN invoices i ON p.invoice_id = i.invoice_id
            WHERE p.payment_id = ?
        """, (payment_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_all_payments(tenant_id=None):
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT p.*, t.name as tenant_name,
                   i.amount as invoice_amount, i.description as invoice_desc
            FROM payments p
            JOIN tenants t ON p.tenant_id = t.tenant_id
            JOIN invoices i ON p.invoice_id = i.invoice_id
        """
        params = ()
        if tenant_id:
            sql += " WHERE p.tenant_id = ?"
            params = (tenant_id,)
        sql += " ORDER BY p.payment_date DESC"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_tenant_payment_history(tenant_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, i.amount as invoice_amount, i.due_date,
                   i.description as invoice_desc, i.status as invoice_status
            FROM payments p
            JOIN invoices i ON p.invoice_id = i.invoice_id
            WHERE p.tenant_id = ?
            ORDER BY p.payment_date DESC
        """, (tenant_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_outstanding_balance(tenant_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COALESCE(SUM(i.amount), 0) as total_invoiced,
                COALESCE((SELECT SUM(p.amount) FROM payments p
                          WHERE p.tenant_id = ? AND p.status = 'Completed'), 0) as total_paid
            FROM invoices i
            WHERE i.tenant_id = ? AND i.status IN ('Pending', 'Overdue', 'Partial')
        """, (tenant_id, tenant_id))
        row = cursor.fetchone()
        conn.close()
        if row:
            return round(row["total_invoiced"] - row["total_paid"], 2)
        return 0

    @staticmethod
    def get_payments_for_invoice(invoice_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, t.name as tenant_name
            FROM payments p
            JOIN tenants t ON p.tenant_id = t.tenant_id
            WHERE p.invoice_id = ?
            ORDER BY p.payment_date DESC
        """, (invoice_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_receipt_data(payment_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, t.name as tenant_name, t.email, t.phone,
                   i.amount as invoice_amount, i.due_date, i.description,
                   a.apartment_name, c.name as city_name
            FROM payments p
            JOIN tenants t ON p.tenant_id = t.tenant_id
            JOIN invoices i ON p.invoice_id = i.invoice_id
            JOIN leases l ON i.lease_id = l.lease_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
            JOIN cities c ON a.city_id = c.city_id
            WHERE p.payment_id = ?
        """, (payment_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
