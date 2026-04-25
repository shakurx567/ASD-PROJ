# Component 3 | Author: Talal Esbaitah (23077550)

from database.db_setup import get_connection


class ApartmentDAO:

    @staticmethod
    def add_apartment(city_id, apartment_name, apt_type, rent_amount,
                      number_of_rooms, status="Vacant"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO apartments (city_id, apartment_name, type, rent_amount,
                number_of_rooms, status)
            VALUES (?,?,?,?,?,?)
        """, (city_id, apartment_name, apt_type, rent_amount,
              number_of_rooms, status))
        apt_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return apt_id

    @staticmethod
    def get_apartment(apartment_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, c.name as city_name
            FROM apartments a
            JOIN cities c ON a.city_id = c.city_id
            WHERE a.apartment_id = ?
        """, (apartment_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_all_apartments(city_id=None):
        conn = get_connection()
        cursor = conn.cursor()
        if city_id:
            cursor.execute("""
                SELECT a.*, c.name as city_name
                FROM apartments a JOIN cities c ON a.city_id = c.city_id
                WHERE a.city_id = ? ORDER BY c.name, a.apartment_name
            """, (city_id,))
        else:
            cursor.execute("""
                SELECT a.*, c.name as city_name
                FROM apartments a JOIN cities c ON a.city_id = c.city_id
                ORDER BY c.name, a.apartment_name
            """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def update_apartment(apartment_id, **kwargs):
        allowed = {"apartment_name", "type", "rent_amount",
                    "number_of_rooms", "status", "city_id"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return False
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [apartment_id]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE apartments SET {set_clause} WHERE apartment_id = ?", values)
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    @staticmethod
    def update_status(apartment_id, status):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE apartments SET status = ? WHERE apartment_id = ?",
            (status, apartment_id))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    @staticmethod
    def deactivate_apartment(apartment_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE apartments SET is_active = 0 WHERE apartment_id = ?",
            (apartment_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    @staticmethod
    def reactivate_apartment(apartment_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE apartments SET is_active = 1 WHERE apartment_id = ?",
            (apartment_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    @staticmethod
    def get_vacant_apartments(city_id=None):
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT a.*, c.name as city_name
            FROM apartments a JOIN cities c ON a.city_id = c.city_id
            WHERE a.status = 'Vacant'
        """
        params = ()
        if city_id:
            sql += " AND a.city_id = ?"
            params = (city_id,)
        sql += " ORDER BY c.name, a.apartment_name"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_occupancy_stats(city_id=None):
        conn = get_connection()
        cursor = conn.cursor()
        if city_id:
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM apartments WHERE city_id = ? GROUP BY status
            """, (city_id,))
        else:
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM apartments GROUP BY status
            """)
        rows = cursor.fetchall()
        conn.close()
        stats = {"Vacant": 0, "Occupied": 0, "Under Maintenance": 0}
        for r in rows:
            stats[r["status"]] = r["count"]
        stats["total"] = sum(stats.values())
        if stats["total"] > 0:
            stats["occupancy_rate"] = round(
                stats["Occupied"] / stats["total"] * 100, 1)
        else:
            stats["occupancy_rate"] = 0
        return stats

    @staticmethod
    def get_occupancy_by_city():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.name as city_name, c.city_id,
                   COUNT(a.apartment_id) as total,
                   SUM(CASE WHEN a.status = 'Occupied' THEN 1 ELSE 0 END) as occupied,
                   SUM(CASE WHEN a.status = 'Vacant' THEN 1 ELSE 0 END) as vacant,
                   SUM(CASE WHEN a.status = 'Under Maintenance' THEN 1 ELSE 0 END) as maintenance
            FROM cities c
            LEFT JOIN apartments a ON c.city_id = a.city_id
            GROUP BY c.city_id, c.name
            ORDER BY c.name
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def filter_apartments(city_id=None, status=None, apt_type=None,
                          min_rent=None, max_rent=None, show_inactive=False):
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT a.*, c.name as city_name,
                   COALESCE(a.is_active, 1) as is_active
            FROM apartments a JOIN cities c ON a.city_id = c.city_id
            WHERE 1=1
        """
        params = []
        if not show_inactive:
            sql += " AND COALESCE(a.is_active, 1) = 1"
        if city_id:
            sql += " AND a.city_id = ?"
            params.append(city_id)
        if status:
            sql += " AND a.status = ?"
            params.append(status)
        if apt_type:
            sql += " AND a.type = ?"
            params.append(apt_type)
        if min_rent is not None:
            sql += " AND a.rent_amount >= ?"
            params.append(min_rent)
        if max_rent is not None:
            sql += " AND a.rent_amount <= ?"
            params.append(max_rent)
        sql += " ORDER BY COALESCE(a.is_active, 1) DESC, c.name, a.apartment_name"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_cities():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cities ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_apartment_history(apartment_id):
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
