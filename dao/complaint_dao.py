# Component 3 | Author: Talal Esbaitah (23077550)

from database.db_setup import get_connection
from datetime import datetime


class ComplaintDAO:

    @staticmethod
    def get_complaints_for_tenant(tenant_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, mr.description as request_description
            FROM complaints c
            LEFT JOIN maintenance_requests mr
                ON c.linked_request_id = mr.request_id
            WHERE c.tenant_id = ?
            ORDER BY c.created_at DESC
        """, (tenant_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def log_complaint(tenant_id, description, linked_request_id=None):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO complaints (tenant_id, description, linked_request_id)
            VALUES (?,?,?)
        """, (tenant_id, description, linked_request_id))
        complaint_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return complaint_id

    @staticmethod
    def get_open_requests_for_tenant(tenant_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT mr.request_id, mr.description, a.apartment_name
            FROM maintenance_requests mr
            JOIN apartments a ON mr.apartment_id = a.apartment_id
            WHERE mr.tenant_id = ? AND mr.status != 'Resolved'
            ORDER BY mr.created_at DESC
        """, (tenant_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
