# Student ID: 24019989
# Student Name: Abdishakur Hasan
# Component: Component 2 - User Authentication, RBAC & Desktop UI Framework

class User:
    def __init__(self, user_id, username, role, city):
        self.user_id = user_id
        self.username = username
        self.role = role
        self.city = city

    def has_permission(self, action):
        permissions = {
            "Front-Desk Staff": [
                "register_tenant",
                "view_tenant",
                "create_maintenance_request"
            ],
            "Finance Manager": [
                "record_payment",
                "generate_invoice",
                "view_financial_reports"
            ],
            "Maintenance Staff": [
                "view_maintenance_requests",
                "update_maintenance_status",
                "log_costs"
            ],
            "Administrator": [
                "register_tenant",
                "view_tenant",
                "create_maintenance_request",
                "record_payment",
                "generate_invoice",
                "view_financial_reports",
                "view_maintenance_requests",
                "update_maintenance_status",
                "log_costs",
                "manage_users",
                "manage_apartments",
                "generate_reports"
            ],
            "Manager": [
                "register_tenant",
                "view_tenant",
                "create_maintenance_request",
                "record_payment",
                "generate_invoice",
                "view_financial_reports",
                "view_maintenance_requests",
                "update_maintenance_status",
                "log_costs",
                "manage_users",
                "manage_apartments",
                "generate_reports",
                "add_city",
                "view_all_locations"
            ]
        }
        return action in permissions.get(self.role, [])

    def __str__(self):
        return f"User({self.username}, {self.role}, {self.city})"