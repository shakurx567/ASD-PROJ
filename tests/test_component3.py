# Component 3 | Author: Talal Esbaitah (23077550)

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_setup import get_connection, init_db, DB_PATH
from dao.tenant_dao import TenantDAO
from dao.apartment_dao import ApartmentDAO
from dao.lease_dao import LeaseDAO
from datetime import datetime, timedelta


class BaseDBTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import database.db_setup as db_mod
        cls._orig_path = db_mod.DB_PATH
        db_mod.DB_PATH = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "test_pams.db")
        if os.path.exists(db_mod.DB_PATH):
            os.remove(db_mod.DB_PATH)
        init_db()
        conn = get_connection()
        conn.execute("INSERT OR IGNORE INTO cities (name) VALUES ('Bristol')")
        conn.execute("INSERT OR IGNORE INTO cities (name) VALUES ('London')")
        conn.commit()
        conn.close()

    @classmethod
    def tearDownClass(cls):
        import database.db_setup as db_mod
        if os.path.exists(db_mod.DB_PATH):
            os.remove(db_mod.DB_PATH)
        db_mod.DB_PATH = cls._orig_path


class TestTenantDAO(BaseDBTest):

    def test_add_tenant_returns_id(self):
        tid = TenantDAO.add_tenant(
            "ZZ111111A", "Test User", "07000000001",
            "test@email.com", "Tester")
        self.assertIsNotNone(tid)
        self.assertGreater(tid, 0)

    def test_get_tenant_returns_correct_data(self):
        tid = TenantDAO.add_tenant(
            "ZZ222222B", "Jane Doe", "07000000002",
            "jane@email.com", "Doctor")
        tenant = TenantDAO.get_tenant(tid)
        self.assertEqual(tenant["name"], "Jane Doe")
        self.assertEqual(tenant["ni_number"], "ZZ222222B")
        self.assertEqual(tenant["email"], "jane@email.com")

    def test_get_nonexistent_tenant_returns_none(self):
        result = TenantDAO.get_tenant(99999)
        self.assertIsNone(result)

    def test_update_tenant(self):
        tid = TenantDAO.add_tenant(
            "ZZ333333C", "Old Name", "07000000003", "old@email.com")
        TenantDAO.update_tenant(tid, name="New Name", phone="07999999999")
        tenant = TenantDAO.get_tenant(tid)
        self.assertEqual(tenant["name"], "New Name")
        self.assertEqual(tenant["phone"], "07999999999")

    def test_deactivate_tenant(self):
        tid = TenantDAO.add_tenant(
            "ZZ444444D", "Deactivate Me", "07000000004", "deact@email.com")
        result = TenantDAO.deactivate_tenant(tid)
        self.assertTrue(result)
        tenant = TenantDAO.get_tenant(tid)
        self.assertEqual(tenant["is_active"], 0)

    def test_reactivate_tenant(self):
        tid = TenantDAO.add_tenant(
            "ZZ555555E", "Reactivate Me", "07000000005", "react@email.com")
        TenantDAO.deactivate_tenant(tid)
        TenantDAO.reactivate_tenant(tid)
        tenant = TenantDAO.get_tenant(tid)
        self.assertEqual(tenant["is_active"], 1)

    def test_search_tenants_by_name(self):
        TenantDAO.add_tenant(
            "ZZ666666F", "Unique SearchName", "07000000006", "search@email.com")
        results = TenantDAO.search_tenants("Unique SearchName")
        self.assertTrue(len(results) >= 1)
        self.assertEqual(results[0]["name"], "Unique SearchName")

    def test_search_tenants_by_ni(self):
        TenantDAO.add_tenant(
            "XX999999Z", "NI Search Test", "07000000007", "ni@email.com")
        results = TenantDAO.search_tenants("XX999999Z")
        self.assertTrue(len(results) >= 1)

    def test_duplicate_ni_number_raises(self):
        ni = "DUP00001A"
        try:
            TenantDAO.add_tenant(ni, "First", "07000000008", "first@email.com")
        except Exception:
            pass
        with self.assertRaises(Exception):
            TenantDAO.add_tenant(ni, "Second", "07000000009", "second@email.com")

    def test_pagination(self):
        for i in range(5):
            TenantDAO.add_tenant(
                f"PG{i:06d}X", f"Page User {i}", f"0700{i:07d}",
                f"page{i}@email.com")
        page1, total = TenantDAO.get_tenants_paginated(page=1, per_page=3)
        self.assertLessEqual(len(page1), 3)
        self.assertGreater(total, 0)


class TestApartmentDAO(BaseDBTest):

    def test_add_apartment(self):
        aid = ApartmentDAO.add_apartment(1, "Test Flat A", "2 Bedroom", 1000.00, 2)
        self.assertIsNotNone(aid)
        self.assertGreater(aid, 0)

    def test_get_apartment(self):
        aid = ApartmentDAO.add_apartment(1, "Test Flat B", "Studio", 650.00, 1)
        apt = ApartmentDAO.get_apartment(aid)
        self.assertEqual(apt["apartment_name"], "Test Flat B")
        self.assertEqual(apt["type"], "Studio")
        self.assertEqual(apt["rent_amount"], 650.00)

    def test_update_apartment(self):
        aid = ApartmentDAO.add_apartment(1, "Old Flat", "1 Bedroom", 800.00, 1)
        ApartmentDAO.update_apartment(aid, apartment_name="New Flat", rent_amount=900.00)
        apt = ApartmentDAO.get_apartment(aid)
        self.assertEqual(apt["apartment_name"], "New Flat")
        self.assertEqual(apt["rent_amount"], 900.00)

    def test_update_status(self):
        aid = ApartmentDAO.add_apartment(1, "Status Flat", "1 Bedroom", 700.00, 1)
        ApartmentDAO.update_status(aid, "Occupied")
        apt = ApartmentDAO.get_apartment(aid)
        self.assertEqual(apt["status"], "Occupied")

    def test_get_vacant_apartments(self):
        ApartmentDAO.add_apartment(1, "Vacant Flat", "1 Bedroom", 600.00, 1, "Vacant")
        vacant = ApartmentDAO.get_vacant_apartments()
        self.assertTrue(any(a["apartment_name"] == "Vacant Flat" for a in vacant))

    def test_occupancy_stats(self):
        stats = ApartmentDAO.get_occupancy_stats()
        self.assertIn("total", stats)
        self.assertIn("occupancy_rate", stats)
        self.assertIn("Vacant", stats)

    def test_filter_apartments_by_status(self):
        ApartmentDAO.add_apartment(2, "Filter Test", "2 Bedroom", 1000.00, 2, "Vacant")
        results = ApartmentDAO.filter_apartments(status="Vacant")
        self.assertTrue(len(results) >= 1)

    def test_get_cities(self):
        cities = ApartmentDAO.get_cities()
        self.assertTrue(len(cities) >= 2)
        names = [c["name"] for c in cities]
        self.assertIn("Bristol", names)


class TestLeaseDAO(BaseDBTest):

    def _create_tenant_and_apartment(self, suffix=""):
        tid = TenantDAO.add_tenant(
            f"LS{suffix}001A", f"Lease Tenant {suffix}",
            f"0700{suffix}001", f"lease{suffix}@email.com")
        aid = ApartmentDAO.add_apartment(
            1, f"Lease Flat {suffix}", "2 Bedroom", 1000.00, 2, "Vacant")
        return tid, aid

    def test_create_lease(self):
        tid, aid = self._create_tenant_and_apartment("CL")
        lid = LeaseDAO.create_lease(tid, aid, "2026-01-01", "2027-01-01", 1000.00)
        self.assertIsNotNone(lid)
        apt = ApartmentDAO.get_apartment(aid)
        self.assertEqual(apt["status"], "Occupied")

    def test_get_lease(self):
        tid, aid = self._create_tenant_and_apartment("GL")
        lid = LeaseDAO.create_lease(tid, aid, "2026-01-01", "2027-01-01", 1000.00, 500.00)
        lease = LeaseDAO.get_lease(lid)
        self.assertEqual(lease["monthly_rent"], 1000.00)
        self.assertEqual(lease["deposit_amount"], 500.00)
        self.assertEqual(lease["status"], "Active")

    def test_early_termination_penalty(self):
        tid, aid = self._create_tenant_and_apartment("ET")
        lid = LeaseDAO.create_lease(tid, aid, "2026-01-01", "2027-01-01", 1200.00)
        penalty = LeaseDAO.calculate_early_termination_penalty(lid)
        self.assertIsNotNone(penalty)
        self.assertEqual(penalty["penalty_amount"], 60.00)
        self.assertEqual(penalty["penalty_rate"], 0.05)

    def test_terminate_lease_frees_apartment(self):
        tid, aid = self._create_tenant_and_apartment("TL")
        lid = LeaseDAO.create_lease(tid, aid, "2026-01-01", "2027-01-01", 900.00)
        LeaseDAO.terminate_lease(lid)
        lease = LeaseDAO.get_lease(lid)
        self.assertEqual(lease["status"], "Terminated")
        apt = ApartmentDAO.get_apartment(aid)
        self.assertEqual(apt["status"], "Vacant")

    def test_renew_lease(self):
        tid, aid = self._create_tenant_and_apartment("RL")
        lid = LeaseDAO.create_lease(tid, aid, "2026-01-01", "2027-01-01", 800.00)
        LeaseDAO.renew_lease(lid, "2028-01-01", 850.00)
        lease = LeaseDAO.get_lease(lid)
        self.assertEqual(lease["end_date"], "2028-01-01")
        self.assertEqual(lease["monthly_rent"], 850.00)

    def test_get_active_lease_for_tenant(self):
        tid, aid = self._create_tenant_and_apartment("AL")
        LeaseDAO.create_lease(tid, aid, "2026-01-01", "2027-01-01", 700.00)
        active = LeaseDAO.get_active_lease_for_tenant(tid)
        self.assertIsNotNone(active)
        self.assertEqual(active["status"], "Active")

    def test_expire_lease(self):
        tid, aid = self._create_tenant_and_apartment("EX")
        lid = LeaseDAO.create_lease(tid, aid, "2025-01-01", "2025-12-31", 600.00)
        LeaseDAO.expire_lease(lid)
        lease = LeaseDAO.get_lease(lid)
        self.assertEqual(lease["status"], "Expired")
        apt = ApartmentDAO.get_apartment(aid)
        self.assertEqual(apt["status"], "Vacant")


if __name__ == '__main__':
    unittest.main(verbosity=2)
