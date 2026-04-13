# Student ID: 24019989
# Student Name: Abdishakur Hasan
# Component: Component 2 - User Authentication, RBAC & Desktop UI Framework



import tkinter as tk
from utils.session import Session
from auth.auth_manager import logout

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.current_user = Session.get_current_user()
        self.notifications = [
            {"priority": "🔴 URGENT", "message": "Lease expiring: Flat 4B Bristol", "read": False},
            {"priority": "🟡 NORMAL", "message": "Payment overdue: John Smith", "read": False},
            {"priority": "🔵 INFO",   "message": "Maintenance completed: Flat 2A",  "read": True},
        ]
        self.active_btn = None
        self.build()

    def build(self):
        self.root.configure(bg="#1a1a2e")

        # ── TOP BAR ──────────────────────────────────────────
        topbar = tk.Frame(self.root, bg="#16213e", height=56)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        # Logo area
        logo_frame = tk.Frame(topbar, bg="#0f3460", width=220)
        logo_frame.pack(side="left", fill="y")
        logo_frame.pack_propagate(False)

        tk.Label(
            logo_frame, text="⬡  PARAGON",
            bg="#0f3460", fg="#e2b96f",
            font=("Georgia", 13, "bold")
        ).pack(side="left", padx=20)

        # Right side of topbar
        right_bar = tk.Frame(topbar, bg="#16213e")
        right_bar.pack(side="right", fill="y", padx=16)

        # Notification bell
        unread = sum(1 for n in self.notifications if not n["read"])
        self.notif_btn = tk.Button(
            right_bar,
            text=f"🔔  {unread}" if unread > 0 else "🔔",
            bg="#0f3460", fg="#e2b96f",
            relief="flat", font=("Helvetica", 10, "bold"),
            cursor="hand2", padx=12, pady=6,
            activebackground="#1a3a5c",
            command=self.show_notifications
        )
        self.notif_btn.pack(side="right", pady=12, padx=(8, 0))

        # User pill
        user_pill = tk.Frame(right_bar, bg="#0f3460")
        user_pill.pack(side="right", pady=12)

        tk.Label(
            user_pill,
            text=f"  {self.current_user.username}",
            bg="#0f3460", fg="white",
            font=("Helvetica", 10, "bold")
        ).pack(side="left", padx=(12, 4))

        tk.Label(
            user_pill,
            text=f"{self.current_user.role}  ·  {self.current_user.city}  ",
            bg="#0f3460", fg="#7a9cc4",
            font=("Helvetica", 8)
        ).pack(side="left")

        # ── BODY ─────────────────────────────────────────────
        body = tk.Frame(self.root, bg="#1a1a2e")
        body.pack(fill="both", expand=True)

        # ── SIDEBAR ──────────────────────────────────────────
        sidebar = tk.Frame(body, bg="#16213e", width=220)
        sidebar.pack(fill="y", side="left")
        sidebar.pack_propagate(False)

        # Sidebar section label
        tk.Label(
            sidebar, text="MAIN MENU",
            bg="#16213e", fg="#3a4a6b",
            font=("Helvetica", 8, "bold")
        ).pack(pady=(24, 8), padx=20, anchor="w")

        self.sidebar_buttons = []
        menu_items = self.get_menu_items()
        for item in menu_items:
            cmd = self.get_command(item)
            btn = tk.Button(
                sidebar, text=item,
                bg="#16213e", fg="#aaaaaa",
                relief="flat", anchor="w",
                font=("Helvetica", 10),
                padx=20, pady=10,
                cursor="hand2",
                activebackground="#0f3460",
                activeforeground="white",
                command=lambda c=cmd, b=None: self._sidebar_click(c, b)
            )
            btn.pack(fill="x")
            self.sidebar_buttons.append(btn)

            # Fix late binding issue
            btn.config(command=lambda c=cmd, b=btn: self._sidebar_click(c, b))

        # Divider before logout
        tk.Frame(sidebar, bg="#0f3460", height=1).pack(
            fill="x", padx=20, pady=12, side="bottom"
        )

        tk.Button(
            sidebar, text="⎋   Logout",
            bg="#16213e", fg="#e05c5c",
            relief="flat", anchor="w",
            font=("Helvetica", 10),
            padx=20, pady=10,
            cursor="hand2",
            activebackground="#2a1a1a",
            activeforeground="#e05c5c",
            command=self.logout
        ).pack(fill="x", side="bottom")

        tk.Label(
            sidebar, text="ACCOUNT",
            bg="#16213e", fg="#3a4a6b",
            font=("Helvetica", 8, "bold")
        ).pack(side="bottom", padx=20, anchor="w", pady=(0, 4))

        # ── CONTENT AREA ─────────────────────────────────────
        self.content = tk.Frame(body, bg="#1a1a2e")
        self.content.pack(fill="both", expand=True)

        # ── STATUS BAR ───────────────────────────────────────
        statusbar = tk.Frame(self.root, bg="#0f3460", height=28)
        statusbar.pack(fill="x", side="bottom")
        statusbar.pack_propagate(False)

        tk.Label(
            statusbar, text="●  System Ready",
            bg="#0f3460", fg="#5cb85c",
            font=("Helvetica", 8)
        ).pack(side="left", padx=16, pady=6)

        tk.Label(
            statusbar, text="PAMS  v1.0  ·  Paragon Apartment Management System",
            bg="#0f3460", fg="#3a4a6b",
            font=("Helvetica", 8)
        ).pack(side="right", padx=16, pady=6)

        self.show_dashboard()

    def _sidebar_click(self, cmd, btn):
        # Reset all buttons
        for b in self.sidebar_buttons:
            b.config(bg="#16213e", fg="#aaaaaa")
        # Highlight active
        if btn:
            btn.config(bg="#0f3460", fg="white")
            self.active_btn = btn
        cmd()

    def get_menu_items(self):
        role = self.current_user.role
        if role == "Front-Desk Staff":
            return ["🏠   Dashboard", "👤   Register Tenant", "🔍   View Tenants", "🔧   Maintenance Request"]
        elif role == "Finance Manager":
            return ["🏠   Dashboard", "💳   Record Payment", "🧾   Generate Invoice", "📊   Financial Reports"]
        elif role == "Maintenance Staff":
            return ["🏠   Dashboard", "🔧   Maintenance Requests", "✅   Update Status", "💰   Log Costs"]
        elif role == "Administrator":
            return ["🏠   Dashboard", "👤   Tenants", "🏢   Apartments", "💳   Payments", "🔧   Maintenance", "📊   Reports", "👥   Manage Users"]
        elif role == "Manager":
            return ["🏠   Dashboard", "👤   Tenants", "🏢   Apartments", "💳   Payments", "🔧   Maintenance", "📊   Reports", "👥   Manage Users", "🌍   All Locations", "➕   Add City"]
        return ["🏠   Dashboard"]

    def get_command(self, item):
        if "Manage Users" in item:
            return self.show_user_management
        elif "Dashboard" in item:
            return self.show_dashboard
        elif "Add City" in item:
            return self.show_add_city
        else:
            return lambda i=item: self.show_placeholder(i)

    def show_user_management(self):
        from ui.user_management import UserManagementScreen
        UserManagementScreen(self.content)

    def show_add_city(self):
        from ui.add_city import AddCityScreen
        AddCityScreen(self.content)

    def show_dashboard(self):
        for w in self.content.winfo_children():
            w.destroy()

        # Page header
        header = tk.Frame(self.content, bg="#1a1a2e")
        header.pack(fill="x", padx=36, pady=(32, 0))

        tk.Label(
            header,
            text=f"Good day, {self.current_user.username} 👋",
            bg="#1a1a2e", fg="white",
            font=("Georgia", 22, "bold")
        ).pack(anchor="w")

        tk.Label(
            header,
            text=f"{self.current_user.role}  ·  {self.current_user.city} Office",
            bg="#1a1a2e", fg="#555e7a",
            font=("Helvetica", 10)
        ).pack(anchor="w", pady=(4, 0))

        # Divider
        tk.Frame(self.content, bg="#16213e", height=2).pack(
            fill="x", padx=36, pady=20
        )

        # Stat cards
        cards_frame = tk.Frame(self.content, bg="#1a1a2e")
        cards_frame.pack(fill="x", padx=36)

        stats = self._get_stats()
        for i, (icon, label, value, color) in enumerate(stats):
            self._stat_card(cards_frame, icon, label, value, color, i)

        # Recent activity section
        tk.Label(
            self.content, text="RECENT ACTIVITY",
            bg="#1a1a2e", fg="#3a4a6b",
            font=("Helvetica", 8, "bold")
        ).pack(anchor="w", padx=36, pady=(32, 8))

        activity_items = [
            ("🔴", "Lease expiring soon", "Flat 4B — Bristol", "2 hours ago"),
            ("🟡", "Payment overdue", "John Smith — £1,200", "5 hours ago"),
            ("🟢", "Maintenance resolved", "Flat 2A — Boiler fixed", "Yesterday"),
        ]

        for icon, title, detail, time in activity_items:
            row = tk.Frame(self.content, bg="#16213e")
            row.pack(fill="x", padx=36, pady=3)

            tk.Label(row, text=icon, bg="#16213e",
                    font=("Helvetica", 12)).pack(side="left", padx=16, pady=12)

            info = tk.Frame(row, bg="#16213e")
            info.pack(side="left", fill="x", expand=True, pady=10)

            tk.Label(info, text=title, bg="#16213e", fg="white",
                    font=("Helvetica", 10, "bold"), anchor="w").pack(anchor="w")
            tk.Label(info, text=detail, bg="#16213e", fg="#555e7a",
                    font=("Helvetica", 9), anchor="w").pack(anchor="w")

            tk.Label(row, text=time, bg="#16213e", fg="#3a4a6b",
                    font=("Helvetica", 8)).pack(side="right", padx=16)

    def _get_stats(self):
        role = self.current_user.role
        if role in ("Administrator", "Manager"):
            return [
                ("🏢", "Total Apartments", "48", "#e2b96f"),
                ("👤", "Active Tenants",   "41", "#5cb85c"),
                ("💳", "Pending Payments", "7",  "#e05c5c"),
                ("🔧", "Open Requests",    "3",  "#7a9cc4"),
            ]
        elif role == "Finance Manager":
            return [
                ("💰", "Collected This Month", "£38,400", "#5cb85c"),
                ("⏳", "Pending",              "£8,400",  "#e2b96f"),
                ("🚨", "Overdue",              "£2,100",  "#e05c5c"),
                ("🧾", "Invoices Issued",      "48",      "#7a9cc4"),
            ]
        elif role == "Maintenance Staff":
            return [
                ("📋", "Open Requests",    "3",  "#e2b96f"),
                ("⚙️", "In Progress",      "2",  "#7a9cc4"),
                ("✅", "Resolved Today",   "1",  "#5cb85c"),
                ("💰", "Costs This Month", "£840", "#aaaaaa"),
            ]
        else:
            return [
                ("👤", "Tenants",          "41", "#e2b96f"),
                ("🏢", "Apartments",       "48", "#7a9cc4"),
                ("🔧", "Open Requests",    "3",  "#5cb85c"),
                ("📋", "My Tasks Today",   "5",  "#aaaaaa"),
            ]

    def _stat_card(self, parent, icon, label, value, color, col):
        card = tk.Frame(parent, bg="#16213e", padx=20, pady=20)
        card.grid(row=0, column=col, padx=(0, 12), sticky="ew")
        parent.grid_columnconfigure(col, weight=1)

        top = tk.Frame(card, bg="#16213e")
        top.pack(fill="x")

        tk.Label(top, text=icon, bg="#16213e",
                font=("Helvetica", 18)).pack(side="left")

        # Colored dot indicator
        tk.Label(top, text="●", bg="#16213e", fg=color,
                font=("Helvetica", 8)).pack(side="right")

        tk.Label(card, text=value, bg="#16213e", fg=color,
                font=("Georgia", 26, "bold")).pack(anchor="w", pady=(8, 2))

        tk.Label(card, text=label, bg="#16213e", fg="#555e7a",
                font=("Helvetica", 9)).pack(anchor="w")

    def show_placeholder(self, item):
        for w in self.content.winfo_children():
            w.destroy()

        name = item.strip().split("   ")[-1] if "   " in item else item.strip()

        tk.Label(
            self.content, text=name,
            bg="#1a1a2e", fg="white",
            font=("Georgia", 22, "bold")
        ).pack(pady=(60, 8), padx=36, anchor="w")

        tk.Frame(self.content, bg="#e2b96f", height=3, width=48).pack(
            padx=36, anchor="w"
        )

        tk.Label(
            self.content,
            text="This module is being developed by another team member.\nIt will be integrated here once complete.",
            bg="#1a1a2e", fg="#555e7a",
            font=("Helvetica", 11),
            justify="left"
        ).pack(pady=20, padx=36, anchor="w")

        # Under construction card
        card = tk.Frame(self.content, bg="#16213e", padx=24, pady=24)
        card.pack(padx=36, anchor="w")

        tk.Label(
            card, text="🔨  Under Construction",
            bg="#16213e", fg="#e2b96f",
            font=("Helvetica", 11, "bold")
        ).pack(anchor="w")

        tk.Label(
            card, text="Component integration pending.",
            bg="#16213e", fg="#555e7a",
            font=("Helvetica", 9)
        ).pack(anchor="w", pady=(4, 0))

    def update_bell(self):
        unread = sum(1 for n in self.notifications if not n["read"])
        self.notif_btn.config(
            text=f"🔔  {unread}" if unread > 0 else "🔔"
        )

    def show_notifications(self):
        win = tk.Toplevel(self.root)
        win.title("Notifications")
        win.geometry("420x520")
        win.configure(bg="#16213e")
        win.grab_set()
        win.resizable(False, False)

        # Header
        header = tk.Frame(win, bg="#0f3460", padx=24, pady=16)
        header.pack(fill="x")

        tk.Label(
            header, text="🔔  Notifications",
            bg="#0f3460", fg="white",
            font=("Georgia", 14, "bold")
        ).pack(side="left")

        unread_count = sum(1 for n in self.notifications if not n["read"])
        self.badge = tk.Label(
            header,
            text=f"  {unread_count} unread  " if unread_count > 0 else "  All read  ",
            bg="#e2b96f" if unread_count > 0 else "#16213e",
            fg="#1a1a2e" if unread_count > 0 else "#555e7a",
            font=("Helvetica", 8, "bold")
        )
        self.badge.pack(side="right")

        container = tk.Frame(win, bg="#16213e")
        container.pack(fill="both", expand=True, padx=16, pady=16)

        def render():
            for w in container.winfo_children():
                w.destroy()

            unread = sum(1 for n in self.notifications if not n["read"])
            self.badge.config(
                text=f"  {unread} unread  " if unread > 0 else "  All read  ",
                bg="#e2b96f" if unread > 0 else "#16213e",
                fg="#1a1a2e" if unread > 0 else "#555e7a"
            )

            for i, notif in enumerate(self.notifications):
                is_read = notif["read"]
                card_bg = "#1a2a4a" if not is_read else "#1a1a2e"
                fg = "white" if not is_read else "#444f6b"
                pri_fg = "#e2b96f" if not is_read else "#3a4a6b"

                card = tk.Frame(container, bg=card_bg)
                card.pack(fill="x", pady=4)

                # Left accent bar
                accent_color = "#e05c5c" if "URGENT" in notif["priority"] else \
                               "#e2b96f" if "NORMAL" in notif["priority"] else "#7a9cc4"
                tk.Frame(card, bg=accent_color if not is_read else "#2a2a3a",
                        width=4).pack(side="left", fill="y")

                inner = tk.Frame(card, bg=card_bg, padx=14, pady=12)
                inner.pack(side="left", fill="both", expand=True)

                tk.Label(inner, text=notif["priority"],
                        bg=card_bg, fg=pri_fg,
                        font=("Helvetica", 8, "bold")).pack(anchor="w")

                tk.Label(inner, text=notif["message"],
                        bg=card_bg, fg=fg,
                        font=("Helvetica", 10)).pack(anchor="w", pady=(2, 6))

                btn_text = "Mark as read" if not is_read else "Mark as unread"

                def toggle(idx=i):
                    self.notifications[idx]["read"] = not self.notifications[idx]["read"]
                    self.update_bell()
                    render()

                tk.Button(
                    inner, text=btn_text,
                    bg=card_bg, fg="#555e7a",
                    relief="flat", font=("Helvetica", 8),
                    cursor="hand2", anchor="w",
                    activebackground=card_bg,
                    activeforeground="#e2b96f",
                    command=toggle
                ).pack(anchor="w")

            # Mark all read
            unread2 = sum(1 for n in self.notifications if not n["read"])
            if unread2 > 0:
                def mark_all():
                    for n in self.notifications:
                        n["read"] = True
                    self.update_bell()
                    render()

                tk.Button(
                    container, text="✓  Mark all as read",
                    bg="#16213e", fg="#e2b96f",
                    relief="flat", font=("Helvetica", 9, "bold"),
                    cursor="hand2",
                    activebackground="#16213e",
                    activeforeground="white",
                    command=mark_all
                ).pack(pady=(8, 0), anchor="e")

        render()

    def logout(self):
        logout()
        self.root.destroy()
        import main
        main.main()