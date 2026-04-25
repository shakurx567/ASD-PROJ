# Component 3 | Author: Talal Esbaitah (23077550)

from database.db_setup import get_connection
from datetime import datetime, timedelta


class LeaseDAO:

    @staticmethod
    def create_lease(tenant_id, apartment_id, start_date, end_date,
                     monthly_rent, deposit_amount=0, penalty_rate=0.05):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE apartments SET status = 'Occupied' WHERE apartment_id = ?",
            (apartment_id,))

        cursor.execute("""
            INSERT INTO leases (tenant_id, apartment_id, start_date, end_date,
                monthly_rent, deposit_amount, penalty_rate, status)
            VALUES (?,?,?,?,?,?,?,'Active')
        """, (tenant_id, apartment_id, start_date, end_date,
              monthly_rent, deposit_amount, penalty_rate))
        lease_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return lease_id

    @staticmethod
    def get_lease(lease_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.*, t.name as tenant_name, t.ni_number,
                   a.apartment_name, c.name as city_name
            FROM leases l
            JOIN tenants t ON l.tenant_id = t.tenant_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
            JOIN cities c ON a.city_id = c.city_id
            WHERE l.lease_id = ?
        """, (lease_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_all_leases(status=None):
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT l.*, t.name as tenant_name,
                   a.apartment_name, c.name as city_name
            FROM leases l
            JOIN tenants t ON l.tenant_id = t.tenant_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
            JOIN cities c ON a.city_id = c.city_id
        """
        params = ()
        if status:
            sql += " WHERE l.status = ?"
            params = (status,)
        sql += " ORDER BY l.start_date DESC"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_active_lease_for_tenant(tenant_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.*, a.apartment_name, c.name as city_name
            FROM leases l
            JOIN apartments a ON l.apartment_id = a.apartment_id
            JOIN cities c ON a.city_id = c.city_id
            WHERE l.tenant_id = ? AND l.status = 'Active'
        """, (tenant_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_expiring_leases(days=30):
        conn = get_connection()
        cursor = conn.cursor()
        threshold = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT l.*, t.name as tenant_name,
                   a.apartment_name, c.name as city_name
            FROM leases l
            JOIN tenants t ON l.tenant_id = t.tenant_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
            JOIN cities c ON a.city_id = c.city_id
            WHERE l.status = 'Active' AND l.end_date BETWEEN ? AND ?
            ORDER BY l.end_date ASC
        """, (today, threshold))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def renew_lease(lease_id, new_end_date, new_monthly_rent=None):
        conn = get_connection()
        cursor = conn.cursor()
        if new_monthly_rent:
            cursor.execute("""
                UPDATE leases SET end_date = ?, monthly_rent = ?
                WHERE lease_id = ? AND status = 'Active'
            """, (new_end_date, new_monthly_rent, lease_id))
        else:
            cursor.execute("""
                UPDATE leases SET end_date = ?
                WHERE lease_id = ? AND status = 'Active'
            """, (new_end_date, lease_id))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    @staticmethod
    def calculate_early_termination_penalty(lease_id):
        lease = LeaseDAO.get_lease(lease_id)
        if not lease:
            return None
        penalty = lease["monthly_rent"] * lease["penalty_rate"]
        return {
            "lease_id": lease_id,
            "monthly_rent": lease["monthly_rent"],
            "penalty_rate": lease["penalty_rate"],
            "penalty_amount": round(penalty, 2),
            "notice_required_days": 30,
            "tenant_name": lease["tenant_name"]
        }

    @staticmethod
    def terminate_lease(lease_id):
        conn = get_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")

        cursor.execute(
            "SELECT apartment_id FROM leases WHERE lease_id = ?", (lease_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False

        apartment_id = row["apartment_id"]

        cursor.execute("""
            UPDATE leases SET status = 'Terminated', termination_notice_date = ?
            WHERE lease_id = ?
        """, (today, lease_id))

        cursor.execute(
            "UPDATE apartments SET status = 'Vacant' WHERE apartment_id = ?",
            (apartment_id,))

        conn.commit()
        conn.close()
        return True

    @staticmethod
    def expire_lease(lease_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT apartment_id FROM leases WHERE lease_id = ?", (lease_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False
        apartment_id = row["apartment_id"]
        cursor.execute(
            "UPDATE leases SET status = 'Expired' WHERE lease_id = ?",
            (lease_id,))
        cursor.execute(
            "UPDATE apartments SET status = 'Vacant' WHERE apartment_id = ?",
            (apartment_id,))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_leases_for_apartment_by_tenant(tenant_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.*, a.apartment_name, c.name as city_name
            FROM leases l
            JOIN apartments a ON l.apartment_id = a.apartment_id
            JOIN cities c ON a.city_id = c.city_id
            WHERE l.tenant_id = ?
            ORDER BY l.start_date DESC
        """, (tenant_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_leases_for_apartment(apartment_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.*, t.name as tenant_name
            FROM leases l
            JOIN tenants t ON l.tenant_id = t.tenant_id
            WHERE l.apartment_id = ?
            ORDER BY l.start_date DESC
        """, (apartment_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
