# Student ID: 24019989
# Student Name: Abdishakur Hasan
# Component: Component 2 - User Authentication, RBAC & Desktop UI Framework



import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.user import User
from utils.session import Session
from auth.auth_manager import is_password_strong

class TestUser(unittest.TestCase):

    def setUp(self):
        self.manager = User(1, "manager1", "Manager", "All")
        self.admin = User(2, "admin1", "Administrator", "Bristol")
        self.frontdesk = User(3, "frontdesk1", "Front-Desk Staff", "London")
        self.finance = User(4, "finance1", "Finance Manager", "Manchester")
        self.maintenance = User(5, "maintenance1", "Maintenance Staff", "Cardiff")

    def test_manager_can_add_city(self):
        self.assertTrue(self.manager.has_permission("add_city"))

    def test_manager_can_view_all_locations(self):
        self.assertTrue(self.manager.has_permission("view_all_locations"))

    def test_manager_can_manage_users(self):
        self.assertTrue(self.manager.has_permission("manage_users"))

    def test_admin_can_manage_users(self):
        self.assertTrue(self.admin.has_permission("manage_users"))

    def test_admin_cannot_add_city(self):
        self.assertFalse(self.admin.has_permission("add_city"))

    def test_admin_cannot_view_all_locations(self):
        self.assertFalse(self.admin.has_permission("view_all_locations"))

    def test_frontdesk_can_register_tenant(self):
        self.assertTrue(self.frontdesk.has_permission("register_tenant"))

    def test_frontdesk_cannot_record_payment(self):
        self.assertFalse(self.frontdesk.has_permission("record_payment"))

    def test_frontdesk_cannot_manage_users(self):
        self.assertFalse(self.frontdesk.has_permission("manage_users"))

    def test_finance_can_record_payment(self):
        self.assertTrue(self.finance.has_permission("record_payment"))

    def test_finance_can_generate_invoice(self):
        self.assertTrue(self.finance.has_permission("generate_invoice"))

    def test_finance_cannot_manage_users(self):
        self.assertFalse(self.finance.has_permission("manage_users"))

    def test_maintenance_can_view_requests(self):
        self.assertTrue(self.maintenance.has_permission("view_maintenance_requests"))

    def test_maintenance_cannot_record_payment(self):
        self.assertFalse(self.maintenance.has_permission("record_payment"))

    def test_maintenance_cannot_register_tenant(self):
        self.assertFalse(self.maintenance.has_permission("register_tenant"))

    def test_user_str(self):
        result = str(self.manager)
        self.assertEqual(result, "User(manager1, Manager, All)")


class TestSession(unittest.TestCase):

    def setUp(self):
        Session.logout()

    def test_session_initially_empty(self):
        self.assertIsNone(Session.get_current_user())

    def test_is_logged_in_false_initially(self):
        self.assertFalse(Session.is_logged_in())

    def test_login_sets_current_user(self):
        user = User(1, "admin1", "Administrator", "Bristol")
        Session.login(user)
        self.assertEqual(Session.get_current_user(), user)

    def test_is_logged_in_true_after_login(self):
        user = User(1, "admin1", "Administrator", "Bristol")
        Session.login(user)
        self.assertTrue(Session.is_logged_in())

    def test_logout_clears_session(self):
        user = User(1, "admin1", "Administrator", "Bristol")
        Session.login(user)
        Session.logout()
        self.assertIsNone(Session.get_current_user())

    def test_is_logged_in_false_after_logout(self):
        user = User(1, "admin1", "Administrator", "Bristol")
        Session.login(user)
        Session.logout()
        self.assertFalse(Session.is_logged_in())


class TestPasswordStrength(unittest.TestCase):

    def test_valid_password_passes(self):
        result, _ = is_password_strong("Admin123!")
        self.assertTrue(result)

    def test_too_short_password_fails(self):
        result, msg = is_password_strong("Ab1")
        self.assertFalse(result)
        self.assertIn("8 characters", msg)

    def test_no_uppercase_fails(self):
        result, msg = is_password_strong("admin123!")
        self.assertFalse(result)
        self.assertIn("uppercase", msg)

    def test_no_lowercase_fails(self):
        result, msg = is_password_strong("ADMIN123!")
        self.assertFalse(result)
        self.assertIn("lowercase", msg)

    def test_no_number_fails(self):
        result, msg = is_password_strong("AdminPass!")
        self.assertFalse(result)
        self.assertIn("number", msg)

    def test_empty_password_fails(self):
        result, _ = is_password_strong("")
        self.assertFalse(result)

    def test_exactly_8_chars_passes(self):
        result, _ = is_password_strong("Admin12!")
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main(verbosity=2)