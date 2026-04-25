# Component 4 | Author: Abdulmalik Altaleb (23061771)

from database.db_setup import get_connection
from datetime import datetime


class MaintenanceDAO:

    @staticmethod
    def create_request(apartment_id, tenant_id, description,
                       priority="Medium"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO maintenance_requests
                (apartment_id, tenant_id, description, priority)
            VALUES (?,?,?,?)
        """, (apartment_id, tenant_id, description, priority))
        request_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return request_id

    @staticmethod
    def get_request(request_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT mr.*, a.apartment_name, c.name as city_name,
                   t.name as tenant_name
            FROM maintenance_requests mr
            JOIN apartments a ON mr.apartment_id = a.apartment_id
            JOIN cities c ON a.city_id = c.city_id
            LEFT JOIN tenants t ON mr.tenant_id = t.tenant_id
            WHERE mr.request_id = ?
        """, (request_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_all_requests(status=None, priority=None, city_id=None):
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT mr.*, a.apartment_name, c.name as city_name,
                   t.name as tenant_name
            FROM maintenance_requests mr
            JOIN apartments a ON mr.apartment_id = a.apartment_id
            JOIN cities c ON a.city_id = c.city_id
            LEFT JOIN tenants t ON mr.tenant_id = t.tenant_id
            WHERE 1=1
        """
        params = []
        if status:
            sql += " AND mr.status = ?"
            params.append(status)
        if priority:
            sql += " AND mr.priority = ?"
            params.append(priority)
        if city_id:
            sql += " AND a.city_id = ?"
            params.append(city_id)
        sql += " ORDER BY CASE mr.priority WHEN 'Urgent' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END, mr.created_at DESC"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def update_status(request_id, status):
        conn = get_connection()
        cursor = conn.cursor()
        resolved_at = None
        if status == "Resolved":
            resolved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE maintenance_requests SET status = ?, resolved_at = ?
            WHERE request_id = ?
        """, (status, resolved_at, request_id))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    @staticmethod
    def update_priority(request_id, priority):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE maintenance_requests SET priority = ? WHERE request_id = ?",
            (priority, request_id))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    @staticmethod
    def log_resolution(request_id, resolution_notes, cost, time_to_fix):
        conn = get_connection()
        cursor = conn.cursor()
        resolved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE maintenance_requests
            SET resolution_notes = ?, cost = ?, time_to_fix = ?,
                status = 'Resolved', resolved_at = ?
            WHERE request_id = ?
        """, (resolution_notes, cost, time_to_fix, resolved_at, request_id))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    @staticmethod
    def schedule_maintenance(request_id, scheduled_date):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE maintenance_requests
            SET scheduled_date = ?, status = 'In Progress'
            WHERE request_id = ?
        """, (scheduled_date, request_id))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    @staticmethod
    def get_maintenance_costs(city_id=None):
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT
                COALESCE(SUM(mr.cost), 0) as total_cost,
                COUNT(*) as total_requests,
                COALESCE(AVG(mr.time_to_fix), 0) as avg_time_to_fix,
                SUM(CASE WHEN mr.status = 'Resolved' THEN 1 ELSE 0 END) as resolved,
                SUM(CASE WHEN mr.status = 'Pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN mr.status = 'In Progress' THEN 1 ELSE 0 END) as in_progress
            FROM maintenance_requests mr
            JOIN apartments a ON mr.apartment_id = a.apartment_id
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
    def get_costs_by_city():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.name as city_name,
                COALESCE(SUM(mr.cost), 0) as total_cost,
                COUNT(mr.request_id) as request_count
            FROM cities c
            LEFT JOIN apartments a ON c.city_id = a.city_id
            LEFT JOIN maintenance_requests mr ON a.apartment_id = mr.apartment_id
            GROUP BY c.city_id, c.name
            ORDER BY c.name
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_requests_for_apartment(apartment_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT mr.*, t.name as tenant_name
            FROM maintenance_requests mr
            LEFT JOIN tenants t ON mr.tenant_id = t.tenant_id
            WHERE mr.apartment_id = ?
            ORDER BY mr.created_at DESC
        """, (apartment_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
