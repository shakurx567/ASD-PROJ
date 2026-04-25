# Component 4 | Author: Abdulmalik Altaleb (23061771)

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_setup import get_connection, init_db
from dao.tenant_dao import TenantDAO
from dao.apartment_dao import ApartmentDAO
from dao.lease_dao import LeaseDAO
from dao.invoice_dao import InvoiceDAO
from dao.payment_dao import PaymentDAO
from dao.maintenance_dao import MaintenanceDAO
from datetime import datetime


class BaseDBTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import database.db_setup as db_mod
        cls._orig_path = db_mod.DB_PATH
        db_mod.DB_PATH = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "test_pams_c4.db")
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

    def _setup_lease(self, suffix):
        tid = TenantDAO.add_tenant(
            f"C4{suffix}01A", f"C4 Tenant {suffix}",
            f"0700{suffix}01", f"c4{suffix}@email.com")
        aid = ApartmentDAO.add_apartment(
            1, f"C4 Flat {suffix}", "2 Bedroom", 1000.00, 2, "Vacant")
        lid = LeaseDAO.create_lease(tid, aid, "2026-01-01", "2027-01-01", 1000.00)
        return tid, aid, lid


# ── Invoice Tests ───────────────────────────────────────
class TestInvoiceDAO(BaseDBTest):

    def test_create_invoice(self):
        tid, aid, lid = self._setup_lease("INV1")
        inv_id = InvoiceDAO.create_invoice(lid, tid, 1000.00, "2026-04-01", "April Rent")
        self.assertIsNotNone(inv_id)
        self.assertGreater(inv_id, 0)

    def test_get_invoice(self):
        tid, aid, lid = self._setup_lease("INV2")
        inv_id = InvoiceDAO.create_invoice(lid, tid, 1000.00, "2026-04-01", "April Rent")
        inv = InvoiceDAO.get_invoice(inv_id)
        self.assertEqual(inv["amount"], 1000.00)
        self.assertEqual(inv["status"], "Pending")
        self.assertEqual(inv["tenant_name"], "C4 Tenant INV2")

    def test_update_invoice_status(self):
        tid, aid, lid = self._setup_lease("INV3")
        inv_id = InvoiceDAO.create_invoice(lid, tid, 1000.00, "2026-04-01")
        InvoiceDAO.update_invoice_status(inv_id, "Paid")
        inv = InvoiceDAO.get_invoice(inv_id)
        self.assertEqual(inv["status"], "Paid")

    def test_get_all_invoices_filter_by_status(self):
        tid, aid, lid = self._setup_lease("INV4")
        InvoiceDAO.create_invoice(lid, tid, 500.00, "2026-04-01")
        InvoiceDAO.create_invoice(lid, tid, 600.00, "2026-05-01")
        results = InvoiceDAO.get_all_invoices(status="Pending")
        self.assertTrue(len(results) >= 2)

    def test_detect_overdue_invoices(self):
        tid, aid, lid = self._setup_lease("INV5")
        InvoiceDAO.create_invoice(lid, tid, 1000.00, "2020-01-01", "Old invoice")
        count = InvoiceDAO.detect_overdue_invoices()
        self.assertGreater(count, 0)

    def test_get_financial_summary(self):
        summary = InvoiceDAO.get_financial_summary()
        self.assertIn("total_collected", summary)
        self.assertIn("total_pending", summary)
        self.assertIn("total_overdue", summary)
        self.assertIn("total_invoices", summary)

    def test_financial_by_city(self):
        by_city = InvoiceDAO.get_financial_by_city()
        self.assertIsInstance(by_city, list)
        self.assertTrue(len(by_city) >= 1)


# ── Payment Tests ───────────────────────────────────────
class TestPaymentDAO(BaseDBTest):

    def test_record_payment(self):
        tid, aid, lid = self._setup_lease("PAY1")
        inv_id = InvoiceDAO.create_invoice(lid, tid, 1000.00, "2026-04-01")
        pay_id = PaymentDAO.record_payment(inv_id, tid, 1000.00, "Cash")
        self.assertIsNotNone(pay_id)
        self.assertGreater(pay_id, 0)

    def test_full_payment_marks_invoice_paid(self):
        tid, aid, lid = self._setup_lease("PAY2")
        inv_id = InvoiceDAO.create_invoice(lid, tid, 1000.00, "2026-04-01")
        PaymentDAO.record_payment(inv_id, tid, 1000.00, "Bank Transfer")
        inv = InvoiceDAO.get_invoice(inv_id)
        self.assertEqual(inv["status"], "Paid")

    def test_partial_payment_marks_invoice_partial(self):
        tid, aid, lid = self._setup_lease("PAY3")
        inv_id = InvoiceDAO.create_invoice(lid, tid, 1000.00, "2026-04-01")
        PaymentDAO.record_payment(inv_id, tid, 500.00, "Cash")
        inv = InvoiceDAO.get_invoice(inv_id)
        self.assertEqual(inv["status"], "Partial")

    def test_two_partial_payments_complete_invoice(self):
        tid, aid, lid = self._setup_lease("PAY4")
        inv_id = InvoiceDAO.create_invoice(lid, tid, 1000.00, "2026-04-01")
        PaymentDAO.record_payment(inv_id, tid, 600.00, "Cash")
        PaymentDAO.record_payment(inv_id, tid, 400.00, "Card")
        inv = InvoiceDAO.get_invoice(inv_id)
        self.assertEqual(inv["status"], "Paid")

    def test_get_payment(self):
        tid, aid, lid = self._setup_lease("PAY5")
        inv_id = InvoiceDAO.create_invoice(lid, tid, 800.00, "2026-04-01")
        pay_id = PaymentDAO.record_payment(inv_id, tid, 800.00, "Card")
        payment = PaymentDAO.get_payment(pay_id)
        self.assertEqual(payment["amount"], 800.00)
        self.assertEqual(payment["method"], "Card")

    def test_get_tenant_payment_history(self):
        tid, aid, lid = self._setup_lease("PAY6")
        inv_id = InvoiceDAO.create_invoice(lid, tid, 900.00, "2026-04-01")
        PaymentDAO.record_payment(inv_id, tid, 900.00, "Cash")
        history = PaymentDAO.get_tenant_payment_history(tid)
        self.assertTrue(len(history) >= 1)

    def test_get_receipt_data(self):
        tid, aid, lid = self._setup_lease("PAY7")
        inv_id = InvoiceDAO.create_invoice(lid, tid, 750.00, "2026-04-01", "Test receipt")
        pay_id = PaymentDAO.record_payment(inv_id, tid, 750.00, "Cheque")
        receipt = PaymentDAO.get_receipt_data(pay_id)
        self.assertIsNotNone(receipt)
        self.assertEqual(receipt["amount"], 750.00)
        self.assertIn("apartment_name", receipt)
        self.assertIn("city_name", receipt)

    def test_outstanding_balance(self):
        tid, aid, lid = self._setup_lease("PAY8")
        InvoiceDAO.create_invoice(lid, tid, 1000.00, "2026-04-01")
        balance = PaymentDAO.get_outstanding_balance(tid)
        self.assertEqual(balance, 1000.00)


# ── Maintenance Tests ───────────────────────────────────
class TestMaintenanceDAO(BaseDBTest):

    def _setup_apartment(self, suffix):
        return ApartmentDAO.add_apartment(
            1, f"Maint Flat {suffix}", "1 Bedroom", 700.00, 1)

    def test_create_request(self):
        aid = self._setup_apartment("MR1")
        rid = MaintenanceDAO.create_request(aid, None, "Broken tap", "High")
        self.assertIsNotNone(rid)
        self.assertGreater(rid, 0)

    def test_get_request(self):
        aid = self._setup_apartment("MR2")
        rid = MaintenanceDAO.create_request(aid, None, "Leaking roof", "Urgent")
        req = MaintenanceDAO.get_request(rid)
        self.assertEqual(req["description"], "Leaking roof")
        self.assertEqual(req["priority"], "Urgent")
        self.assertEqual(req["status"], "Pending")

    def test_update_status(self):
        aid = self._setup_apartment("MR3")
        rid = MaintenanceDAO.create_request(aid, None, "Flickering light")
        MaintenanceDAO.update_status(rid, "In Progress")
        req = MaintenanceDAO.get_request(rid)
        self.assertEqual(req["status"], "In Progress")

    def test_update_priority(self):
        aid = self._setup_apartment("MR4")
        rid = MaintenanceDAO.create_request(aid, None, "Squeaky door", "Low")
        MaintenanceDAO.update_priority(rid, "High")
        req = MaintenanceDAO.get_request(rid)
        self.assertEqual(req["priority"], "High")

    def test_log_resolution(self):
        aid = self._setup_apartment("MR5")
        rid = MaintenanceDAO.create_request(aid, None, "Broken window")
        MaintenanceDAO.log_resolution(rid, "Replaced glass pane", 150.00, 120)
        req = MaintenanceDAO.get_request(rid)
        self.assertEqual(req["status"], "Resolved")
        self.assertEqual(req["cost"], 150.00)
        self.assertEqual(req["time_to_fix"], 120)
        self.assertEqual(req["resolution_notes"], "Replaced glass pane")
        self.assertIsNotNone(req["resolved_at"])

    def test_schedule_maintenance(self):
        aid = self._setup_apartment("MR6")
        rid = MaintenanceDAO.create_request(aid, None, "Paint peeling")
        MaintenanceDAO.schedule_maintenance(rid, "2026-04-20")
        req = MaintenanceDAO.get_request(rid)
        self.assertEqual(req["status"], "In Progress")
        self.assertEqual(req["scheduled_date"], "2026-04-20")

    def test_get_maintenance_costs(self):
        costs = MaintenanceDAO.get_maintenance_costs()
        self.assertIn("total_cost", costs)
        self.assertIn("total_requests", costs)
        self.assertIn("resolved", costs)

    def test_costs_by_city(self):
        by_city = MaintenanceDAO.get_costs_by_city()
        self.assertIsInstance(by_city, list)
        self.assertTrue(len(by_city) >= 1)

    def test_filter_by_status(self):
        aid = self._setup_apartment("MR7")
        MaintenanceDAO.create_request(aid, None, "Filter test", "Medium")
        results = MaintenanceDAO.get_all_requests(status="Pending")
        self.assertTrue(len(results) >= 1)

    def test_filter_by_priority(self):
        aid = self._setup_apartment("MR8")
        MaintenanceDAO.create_request(aid, None, "Priority filter", "Urgent")
        results = MaintenanceDAO.get_all_requests(priority="Urgent")
        self.assertTrue(len(results) >= 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
