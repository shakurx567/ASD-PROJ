# Component 3 | Author: Talal Esbaitah (23077550)

from database.db_setup import get_connection


class TenantDAO:

    @staticmethod
    def add_tenant(ni_number, name, phone, email, occupation="",
                   reference_info="", apartment_requirements="",
                   emergency_contact=""):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tenants (ni_number, name, phone, email, occupation,
                    reference_info, apartment_requirements, emergency_contact)
                VALUES (?,?,?,?,?,?,?,?)
            """, (ni_number, name, phone, email, occupation,
                  reference_info, apartment_requirements, emergency_contact))
            tenant_id = cursor.lastrowid
            conn.commit()
            return tenant_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def get_tenant(tenant_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tenants WHERE tenant_id = ?", (tenant_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_all_tenants(active_only=True):
        conn = get_connection()
        cursor = conn.cursor()
        if active_only:
            cursor.execute("SELECT * FROM tenants WHERE is_active = 1 ORDER BY name")
        else:
            cursor.execute("SELECT * FROM tenants ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def update_tenant(tenant_id, **kwargs):
        allowed = {"ni_number", "name", "phone", "email", "occupation",
                    "reference_info", "apartment_requirements", "emergency_contact"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return False
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [tenant_id]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE tenants SET {set_clause} WHERE tenant_id = ?", values)
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    @staticmethod
    def deactivate_tenant(tenant_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE tenants SET is_active = 0 WHERE tenant_id = ?", (tenant_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    @staticmethod
    def reactivate_tenant(tenant_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE tenants SET is_active = 1 WHERE tenant_id = ?", (tenant_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    @staticmethod
    def search_tenants(query, active_only=True):
        conn = get_connection()
        cursor = conn.cursor()
        pattern = f"%{query}%"
        sql = """
            SELECT * FROM tenants
            WHERE (name LIKE ? OR ni_number LIKE ? OR email LIKE ? OR phone LIKE ?)
        """
        if active_only:
            sql += " AND is_active = 1"
        sql += " ORDER BY name"
        cursor.execute(sql, (pattern, pattern, pattern, pattern))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_tenant_with_lease(tenant_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.*, l.lease_id, l.start_date, l.end_date, l.monthly_rent,
                   l.status as lease_status, a.apartment_name, c.name as city_name
            FROM tenants t
            LEFT JOIN leases l ON t.tenant_id = l.tenant_id AND l.status = 'Active'
            LEFT JOIN apartments a ON l.apartment_id = a.apartment_id
            LEFT JOIN cities c ON a.city_id = c.city_id
            WHERE t.tenant_id = ?
        """, (tenant_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_overdue_tenant_ids():
        """Return a set of tenant_ids that have at least one overdue or past-due invoice."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT tenant_id FROM invoices
            WHERE status = 'Overdue'
               OR (status = 'Pending' AND due_date < date('now'))
        """)
        rows = cursor.fetchall()
        conn.close()
        return {row[0] for row in rows}

    @staticmethod
    def get_tenants_paginated(page=1, per_page=20, active_only=True):
        conn = get_connection()
        cursor = conn.cursor()
        offset = (page - 1) * per_page

        count_sql = "SELECT COUNT(*) FROM tenants"
        if active_only:
            count_sql += " WHERE is_active = 1"
        cursor.execute(count_sql)
        total = cursor.fetchone()[0]

        sql = "SELECT * FROM tenants"
        if active_only:
            sql += " WHERE is_active = 1"
        sql += " ORDER BY name LIMIT ? OFFSET ?"
        cursor.execute(sql, (per_page, offset))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows], total
