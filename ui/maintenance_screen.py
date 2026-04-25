# Component 4 | Author: Abdulmalik Altaleb (23061771)

import tkinter as tk
from tkinter import messagebox, ttk
from ui.ui_helpers import *
from dao.maintenance_dao import MaintenanceDAO
from dao.apartment_dao import ApartmentDAO
from dao.tenant_dao import TenantDAO
from datetime import datetime


class MaintenanceScreen:
    def __init__(self, parent_frame, main_window=None):
        self.parent = parent_frame
        self.main_window = main_window
        self.filter_status = None
        self.filter_priority = None
        self.build()

    def build(self):
        clear_frame(self.parent)

        header = page_header(self.parent, "Maintenance Requests",
                             "Create, track and resolve maintenance issues")
        gold_button(header, "+  New Request", self.open_create_dialog)

        # Filters
        filter_frame = tk.Frame(self.parent, bg=BG_DARK)
        filter_frame.pack(fill="x", padx=36, pady=(0, 16))

        tk.Label(filter_frame, text="Status:", bg=BG_DARK, fg=TEXT_MUTED,
                 font=FONT_SMALL).pack(side="left", padx=(0, 4))
        statuses = ["All", "Pending", "In Progress", "Resolved", "Cancelled"]
        self.stat_dd, self.stat_var = make_dropdown(filter_frame, statuses, "All")
        self.stat_dd.pack(side="left", padx=(0, 16))
        self.stat_dd.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        tk.Label(filter_frame, text="Priority:", bg=BG_DARK, fg=TEXT_MUTED,
                 font=FONT_SMALL).pack(side="left", padx=(0, 4))
        priorities = ["All", "Urgent", "High", "Medium", "Low"]
        self.pri_dd, self.pri_var = make_dropdown(filter_frame, priorities, "All")
        self.pri_dd.pack(side="left")
        self.pri_dd.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        # Stats
        self.stats_frame = tk.Frame(self.parent, bg=BG_DARK)
        self.stats_frame.pack(fill="x", padx=36, pady=(0, 16))
        self.refresh_stats()

        # Table
        cols = [("ID", 4), ("Apartment", 12), ("City", 10), ("Tenant", 12),
                ("Description", 18), ("Priority", 8), ("Status", 10), ("Actions", 16)]
        table_frame = tk.Frame(self.parent, bg=BG_DARK)
        table_frame.pack(fill="both", expand=True, padx=36)
        table_header(table_frame, cols)

        scroll_container = tk.Frame(table_frame, bg=BG_DARK)
        scroll_container.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(scroll_container, bg=BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical",
                                  command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self.rows_frame = tk.Frame(self._canvas, bg=BG_DARK)
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self.rows_frame, anchor="nw")

        self.rows_frame.bind("<Configure>", lambda e: self._canvas.configure(
            scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>", lambda e: self._canvas.itemconfig(
            self._canvas_window, width=e.width))
        self._canvas.bind("<MouseWheel>", lambda e: self._canvas.yview_scroll(
            int(-1*(e.delta/120)), "units"))

        self.refresh_table()

    def refresh_stats(self):
        clear_frame(self.stats_frame)
        costs = MaintenanceDAO.get_maintenance_costs()
        stat_card(self.stats_frame, "Tot", "Total Requests",
                  costs.get("total_requests", 0), BLUE, 0)
        stat_card(self.stats_frame, "Pen", "Pending",
                  costs.get("pending", 0), GOLD, 1)
        stat_card(self.stats_frame, "Prog", "In Progress",
                  costs.get("in_progress", 0), BLUE, 2)
        stat_card(self.stats_frame, "Cost", "Total Cost",
                  f"£{costs.get('total_cost', 0):,.0f}", RED, 3)

    def refresh_table(self):
        clear_frame(self.rows_frame)

        status = None if self.stat_var.get() == "All" else self.stat_var.get()
        priority = None if self.pri_var.get() == "All" else self.pri_var.get()
        requests = MaintenanceDAO.get_all_requests(status=status, priority=priority)
        widths = [4, 12, 10, 12]

        if not requests:
            tk.Label(self.rows_frame, text="No maintenance requests found.",
                     bg=BG_DARK, fg=TEXT_MUTED, font=FONT_BODY).pack(pady=40)
            return

        for i, req in enumerate(requests):
            bg = BG_CARD if i % 2 == 0 else BG_DARK
            row = tk.Frame(self.rows_frame, bg=bg)
            row.pack(fill="x")

            values = [req["request_id"], req["apartment_name"],
                      req["city_name"], req.get("tenant_name", "-")]
            for val, w in zip(values, widths):
                tk.Label(row, text=str(val) if val else "-", bg=bg,
                         fg=TEXT_WHITE, font=FONT_BODY, width=w,
                         anchor="w", padx=12, pady=10).pack(side="left")

            desc = (req["description"][:30] + "...") if len(req["description"]) > 30 else req["description"]
            tk.Label(row, text=desc, bg=bg, fg=TEXT_WHITE,
                     font=FONT_BODY, width=18, anchor="w",
                     padx=12, pady=10).pack(side="left")

            pri_badge = status_badge(row, req["priority"], bg)
            pri_badge.config(width=8, anchor="w", padx=12, pady=10)
            pri_badge.pack(side="left")

            st_badge = status_badge(row, req["status"], bg)
            st_badge.config(width=10, anchor="w", padx=12, pady=10)
            st_badge.pack(side="left")

            actions = tk.Frame(row, bg=bg)
            actions.pack(side="left", padx=8)

            if req["status"] in ("Pending", "In Progress"):
                if req["status"] == "Pending":
                    tk.Button(actions, text="Schedule", bg=BG_ACCENT, fg=TEXT_WHITE,
                              relief="flat", padx=8, pady=4, cursor="hand2",
                              font=FONT_SMALL,
                              command=lambda rid=req["request_id"]: self.schedule(rid)
                              ).pack(side="left", padx=(0, 4))

                tk.Button(actions, text="Resolve", bg="#1a2a1a", fg=GREEN,
                          relief="flat", padx=8, pady=4, cursor="hand2",
                          font=FONT_SMALL,
                          command=lambda rid=req["request_id"]: self.open_resolve_dialog(rid)
                          ).pack(side="left")

    def open_create_dialog(self):
        dialog = tk.Toplevel()
        dialog.title("New Maintenance Request")
        dialog.geometry("460x440")
        dialog.configure(bg=BG_CARD)
        dialog.grab_set()
        dialog.resizable(False, False)

        dh = tk.Frame(dialog, bg=BG_ACCENT, padx=24, pady=16)
        dh.pack(fill="x")
        tk.Label(dh, text="+  New Maintenance Request",
                 bg=BG_ACCENT, fg=TEXT_WHITE, font=FONT_HEADING).pack(anchor="w")

        form = tk.Frame(dialog, bg=BG_CARD, padx=28, pady=20)
        form.pack(fill="both", expand=True)

        field_label(form, "APARTMENT")
        apartments = ApartmentDAO.get_all_apartments()
        apt_labels = [f"{a['apartment_name']} - {a['city_name']}" for a in apartments]
        apt_dd, apt_var = make_dropdown(form, apt_labels)
        apt_dd.pack(fill="x", pady=(4, 14))

        field_label(form, "TENANT (Optional)")
        tenants = TenantDAO.get_all_tenants()
        tenant_labels = ["-- None --"] + [f"{t['name']} (ID: {t['tenant_id']})" for t in tenants]
        t_dd, t_var = make_dropdown(form, tenant_labels, "-- None --")
        t_dd.pack(fill="x", pady=(4, 14))

        field_label(form, "PRIORITY")
        priorities = ["Low", "Medium", "High", "Urgent"]
        pri_dd, pri_var = make_dropdown(form, priorities, "Medium")
        pri_dd.pack(fill="x", pady=(4, 14))

        field_label(form, "DESCRIPTION")
        desc_text = tk.Text(form, bg=BG_DARK, fg=TEXT_WHITE,
                            insertbackground=GOLD, relief="flat",
                            font=("Helvetica", 10), height=4, bd=10,
                            highlightthickness=1, highlightcolor=GOLD,
                            highlightbackground=BG_ACCENT)
        desc_text.pack(fill="x", pady=(4, 14))

        err = tk.Label(form, text="", bg=BG_CARD, fg=RED, font=FONT_SMALL)
        err.pack(anchor="w")

        def save():
            apt_idx = apt_dd.current()
            if apt_idx < 0:
                err.config(text="Please select an apartment.")
                return
            desc = desc_text.get("1.0", tk.END).strip()
            if not desc:
                err.config(text="Description is required.")
                return

            apartment = apartments[apt_idx]
            t_idx = t_dd.current()
            tenant_id = None
            if t_idx > 0:
                tenant_id = tenants[t_idx - 1]["tenant_id"]

            MaintenanceDAO.create_request(
                apartment["apartment_id"], tenant_id,
                desc, pri_var.get())
            dialog.destroy()
            messagebox.showinfo("Success", "Maintenance request created.")
            self.refresh_stats()
            self.refresh_table()

        btn_row = tk.Frame(form, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(8, 0))
        tk.Button(btn_row, text="Cancel", bg=BG_DARK, fg=TEXT_MUTED,
                  relief="flat", padx=16, pady=8, command=dialog.destroy
                  ).pack(side="right", padx=(8, 0))
        tk.Button(btn_row, text="Create Request", bg=GOLD, fg=BG_DARK,
                  relief="flat", padx=16, pady=8, font=("Helvetica", 10, "bold"),
                  activebackground=GOLD_HOVER, command=save).pack(side="right")

    def schedule(self, request_id):
        dialog = tk.Toplevel()
        dialog.title("Schedule Maintenance")
        dialog.geometry("360x200")
        dialog.configure(bg=BG_CARD)
        dialog.grab_set()

        form = tk.Frame(dialog, bg=BG_CARD, padx=28, pady=20)
        form.pack(fill="both", expand=True)

        field_label(form, "SCHEDULED DATE (YYYY-MM-DD)")
        date_e = make_entry(form)
        date_e.pack(fill="x", pady=(4, 14), ipady=6)
        date_e.insert(0, datetime.now().strftime("%Y-%m-%d"))

        def save():
            MaintenanceDAO.schedule_maintenance(request_id, date_e.get().strip())
            dialog.destroy()
            messagebox.showinfo("Scheduled", "Maintenance scheduled. Status set to In Progress.")
            self.refresh_stats()
            self.refresh_table()

        btn_row = tk.Frame(form, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(8, 0))
        tk.Button(btn_row, text="Cancel", bg=BG_DARK, fg=TEXT_MUTED,
                  relief="flat", padx=16, pady=8, command=dialog.destroy
                  ).pack(side="right", padx=(8, 0))
        tk.Button(btn_row, text="Schedule", bg=GOLD, fg=BG_DARK,
                  relief="flat", padx=16, pady=8, font=("Helvetica", 10, "bold"),
                  activebackground=GOLD_HOVER, command=save).pack(side="right")

    def open_resolve_dialog(self, request_id):
        req = MaintenanceDAO.get_request(request_id)
        if not req:
            return

        dialog = tk.Toplevel()
        dialog.title("Resolve Maintenance Request")
        dialog.geometry("460x420")
        dialog.configure(bg=BG_CARD)
        dialog.grab_set()

        dh = tk.Frame(dialog, bg=BG_ACCENT, padx=24, pady=16)
        dh.pack(fill="x")
        tk.Label(dh, text=f"Resolve Request #{request_id}",
                 bg=BG_ACCENT, fg=TEXT_WHITE, font=FONT_HEADING).pack(anchor="w")

        form = tk.Frame(dialog, bg=BG_CARD, padx=28, pady=20)
        form.pack(fill="both", expand=True)

        tk.Label(form, text=f"Apartment: {req['apartment_name']} ({req['city_name']})",
                 bg=BG_CARD, fg=TEXT_WHITE, font=FONT_BODY).pack(anchor="w", pady=(0, 4))
        tk.Label(form, text=f"Issue: {req['description']}",
                 bg=BG_CARD, fg=TEXT_MUTED, font=FONT_SMALL).pack(anchor="w", pady=(0, 16))

        field_label(form, "RESOLUTION NOTES")
        notes_text = tk.Text(form, bg=BG_DARK, fg=TEXT_WHITE,
                             insertbackground=GOLD, relief="flat",
                             font=("Helvetica", 10), height=3, bd=10,
                             highlightthickness=1, highlightcolor=GOLD,
                             highlightbackground=BG_ACCENT)
        notes_text.pack(fill="x", pady=(4, 14))

        field_label(form, "COST (GBP)")
        cost_e = make_entry(form)
        cost_e.pack(fill="x", pady=(4, 14), ipady=6)
        cost_e.insert(0, "0")

        field_label(form, "TIME TO FIX (minutes)")
        time_e = make_entry(form)
        time_e.pack(fill="x", pady=(4, 14), ipady=6)
        time_e.insert(0, "0")

        err = tk.Label(form, text="", bg=BG_CARD, fg=RED, font=FONT_SMALL)
        err.pack(anchor="w")

        def resolve():
            notes = notes_text.get("1.0", tk.END).strip()
            try:
                cost = float(cost_e.get().strip())
                time_fix = int(time_e.get().strip())
            except ValueError:
                err.config(text="Cost and time must be valid numbers.")
                return

            MaintenanceDAO.log_resolution(request_id, notes, cost, time_fix)
            dialog.destroy()
            messagebox.showinfo("Resolved", "Maintenance request resolved and logged.")
            if self.main_window is not None:
                msg = f"Maintenance resolved: {req['apartment_name']}"
                self.main_window.notifications.append(
                    {"priority": "🟢 INFO", "message": msg, "read": False})
                self.main_window.update_bell()
            self.refresh_stats()
            self.refresh_table()

        btn_row = tk.Frame(form, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(8, 0))
        tk.Button(btn_row, text="Cancel", bg=BG_DARK, fg=TEXT_MUTED,
                  relief="flat", padx=16, pady=8, command=dialog.destroy
                  ).pack(side="right", padx=(8, 0))
        tk.Button(btn_row, text="Mark Resolved", bg=GREEN, fg=TEXT_WHITE,
                  relief="flat", padx=16, pady=8, font=("Helvetica", 10, "bold"),
                  command=resolve).pack(side="right")
