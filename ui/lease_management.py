# Component 3 | Author: Talal Esbaitah (23077550)

import tkinter as tk
from tkinter import messagebox, ttk
from ui.ui_helpers import *
from dao.lease_dao import LeaseDAO
from dao.tenant_dao import TenantDAO
from dao.apartment_dao import ApartmentDAO
from datetime import datetime, timedelta


class LeaseManagementScreen:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.filter_status = None
        self.build()

    def build(self):
        clear_frame(self.parent)

        header = page_header(self.parent, "Lease Agreements",
                             "Track and manage lease contracts")
        gold_button(header, "+  New Lease", self.open_create_dialog)

        filter_frame = tk.Frame(self.parent, bg=BG_DARK)
        filter_frame.pack(fill="x", padx=36, pady=(0, 16))

        tk.Label(filter_frame, text="Status:", bg=BG_DARK, fg=TEXT_MUTED,
                 font=FONT_SMALL).pack(side="left", padx=(0, 8))
        statuses = ["All", "Active", "Expired", "Terminated", "Pending"]
        self.stat_dd, self.stat_var = make_dropdown(filter_frame, statuses, "All")
        self.stat_dd.pack(side="left", padx=(0, 16))
        self.stat_dd.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        expiring = LeaseDAO.get_expiring_leases(30)
        if expiring:
            warn = tk.Frame(filter_frame, bg="#2a2a1a", padx=12, pady=4)
            warn.pack(side="right")
            tk.Label(warn, text=f"! {len(expiring)} lease(s) expiring within 30 days",
                     bg="#2a2a1a", fg=GOLD, font=FONT_SMALL).pack()

        cols = [("ID", 4), ("Tenant", 14), ("Apartment", 12), ("City", 10),
                ("Start", 10), ("End", 10), ("Rent", 10), ("Status", 10), ("Actions", 16)]
        table_frame = tk.Frame(self.parent, bg=BG_DARK)
        table_frame.pack(fill="both", expand=True, padx=36)
        table_header(table_frame, cols)

        scroll_container = tk.Frame(table_frame, bg=BG_DARK)
        scroll_container.pack(fill="both", expand=True)
        canvas = tk.Canvas(scroll_container, bg=BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        self.rows_frame = tk.Frame(canvas, bg=BG_DARK)
        self.rows_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        self.refresh_table()

    def refresh_table(self):
        clear_frame(self.rows_frame)

        status_filter = self.stat_var.get()
        status = None if status_filter == "All" else status_filter
        leases = LeaseDAO.get_all_leases(status=status)
        widths = [4, 14, 12, 10, 10, 10, 10]

        if not leases:
            tk.Label(self.rows_frame, text="No leases found.",
                     bg=BG_DARK, fg=TEXT_MUTED, font=FONT_BODY).pack(pady=40)
            return

        for i, lease in enumerate(leases):
            bg = BG_CARD if i % 2 == 0 else BG_DARK
            row = tk.Frame(self.rows_frame, bg=bg)
            row.pack(fill="x")

            values = [lease["lease_id"], lease["tenant_name"],
                      lease["apartment_name"], lease["city_name"],
                      lease["start_date"], lease["end_date"],
                      f"£{lease['monthly_rent']:,.2f}"]
            for val, w in zip(values, widths):
                tk.Label(row, text=str(val), bg=bg, fg=TEXT_WHITE,
                         font=FONT_BODY, width=w, anchor="w",
                         padx=12, pady=10).pack(side="left")

            badge = status_badge(row, lease["status"], bg)
            badge.config(width=10, anchor="w", padx=12, pady=10)
            badge.pack(side="left")

            actions = tk.Frame(row, bg=bg)
            actions.pack(side="left", padx=8)

            if lease["status"] == "Active":
                tk.Button(actions, text="Renew", bg=BG_ACCENT, fg=TEXT_WHITE,
                          relief="flat", padx=8, pady=4, cursor="hand2",
                          font=FONT_SMALL,
                          command=lambda lid=lease["lease_id"]: self.open_renew_dialog(lid)
                          ).pack(side="left", padx=(0, 4))
                tk.Button(actions, text="Terminate", bg="#2a1a1a", fg=RED,
                          relief="flat", padx=8, pady=4, cursor="hand2",
                          font=FONT_SMALL,
                          command=lambda lid=lease["lease_id"]: self.terminate(lid)
                          ).pack(side="left")

    def open_create_dialog(self):
        dialog = tk.Toplevel()
        dialog.title("Create Lease Agreement")
        dialog.geometry("460x560")
        dialog.configure(bg=BG_CARD)
        dialog.grab_set()
        dialog.resizable(False, False)

        dh = tk.Frame(dialog, bg=BG_ACCENT, padx=24, pady=16)
        dh.pack(fill="x")
        tk.Label(dh, text="+  New Lease Agreement",
                 bg=BG_ACCENT, fg=TEXT_WHITE, font=FONT_HEADING).pack(anchor="w")

        form = tk.Frame(dialog, bg=BG_CARD, padx=28, pady=20)
        form.pack(fill="both", expand=True)

        field_label(form, "TENANT")
        tenants = TenantDAO.get_all_tenants()
        tenant_names = [f"{t['name']} ({t['ni_number']})" for t in tenants]
        tenant_dd, tenant_var = make_dropdown(form, tenant_names)
        tenant_dd.pack(fill="x", pady=(4, 14))

        field_label(form, "APARTMENT (Vacant Only)")
        vacant = ApartmentDAO.get_vacant_apartments()
        apt_labels = [f"{a['apartment_name']} - {a['city_name']} (£{a['rent_amount']:,.0f}/mo)" for a in vacant]
        apt_dd, apt_var = make_dropdown(form, apt_labels if apt_labels else ["No vacant apartments"])
        apt_dd.pack(fill="x", pady=(4, 14))

        field_label(form, "START DATE (YYYY-MM-DD)")
        start_e = make_entry(form)
        start_e.pack(fill="x", pady=(4, 14), ipady=6)
        start_e.insert(0, datetime.now().strftime("%Y-%m-%d"))

        field_label(form, "END DATE (YYYY-MM-DD)")
        end_e = make_entry(form)
        end_e.pack(fill="x", pady=(4, 14), ipady=6)
        end_e.insert(0, (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"))

        field_label(form, "DEPOSIT AMOUNT (GBP)")
        deposit_e = make_entry(form)
        deposit_e.pack(fill="x", pady=(4, 14), ipady=6)
        deposit_e.insert(0, "0")

        err = tk.Label(form, text="", bg=BG_CARD, fg=RED, font=FONT_SMALL)
        err.pack(anchor="w")

        def save():
            if not tenant_names or not apt_labels:
                err.config(text="No tenants or vacant apartments available.")
                return

            tenant_idx = tenant_dd.current()
            apt_idx = apt_dd.current()
            if tenant_idx < 0 or apt_idx < 0:
                err.config(text="Please select a tenant and apartment.")
                return

            tenant = tenants[tenant_idx]
            apartment = vacant[apt_idx]

            try:
                start = start_e.get().strip()
                end = end_e.get().strip()
                datetime.strptime(start, "%Y-%m-%d")
                datetime.strptime(end, "%Y-%m-%d")
                deposit = float(deposit_e.get().strip())
            except ValueError:
                err.config(text="Invalid date format or deposit value.")
                return

            existing = LeaseDAO.get_active_lease_for_tenant(tenant["tenant_id"])
            if existing:
                err.config(text=f"Tenant already has an active lease at {existing['apartment_name']}.")
                return

            LeaseDAO.create_lease(
                tenant["tenant_id"], apartment["apartment_id"],
                start, end, apartment["rent_amount"], deposit)
            dialog.destroy()
            messagebox.showinfo("Success", "Lease created successfully.")
            self.refresh_table()

        btn_row = tk.Frame(form, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(8, 0))
        tk.Button(btn_row, text="Cancel", bg=BG_DARK, fg=TEXT_MUTED,
                  relief="flat", padx=16, pady=8, cursor="hand2",
                  font=FONT_BODY, command=dialog.destroy).pack(side="right", padx=(8, 0))
        tk.Button(btn_row, text="Create Lease", bg=GOLD, fg=BG_DARK,
                  relief="flat", padx=16, pady=8, cursor="hand2",
                  font=("Helvetica", 10, "bold"), activebackground=GOLD_HOVER,
                  command=save).pack(side="right")

    def open_renew_dialog(self, lease_id):
        lease = LeaseDAO.get_lease(lease_id)
        if not lease:
            return

        dialog = tk.Toplevel()
        dialog.title("Renew Lease")
        dialog.geometry("400x320")
        dialog.configure(bg=BG_CARD)
        dialog.grab_set()

        dh = tk.Frame(dialog, bg=BG_ACCENT, padx=24, pady=16)
        dh.pack(fill="x")
        tk.Label(dh, text="Renew Lease",
                 bg=BG_ACCENT, fg=TEXT_WHITE, font=FONT_HEADING).pack(anchor="w")

        form = tk.Frame(dialog, bg=BG_CARD, padx=28, pady=20)
        form.pack(fill="both", expand=True)

        tk.Label(form, text=f"Tenant: {lease['tenant_name']}", bg=BG_CARD,
                 fg=TEXT_WHITE, font=FONT_BODY).pack(anchor="w", pady=(0, 4))
        tk.Label(form, text=f"Apartment: {lease['apartment_name']}", bg=BG_CARD,
                 fg=TEXT_MUTED, font=FONT_SMALL).pack(anchor="w", pady=(0, 16))

        field_label(form, "NEW END DATE (YYYY-MM-DD)")
        end_e = make_entry(form)
        end_e.pack(fill="x", pady=(4, 14), ipady=6)
        current_end = datetime.strptime(lease["end_date"], "%Y-%m-%d")
        new_end = (current_end + timedelta(days=365)).strftime("%Y-%m-%d")
        end_e.insert(0, new_end)

        field_label(form, "NEW MONTHLY RENT (leave blank to keep current)")
        rent_e = make_entry(form)
        rent_e.pack(fill="x", pady=(4, 14), ipady=6)

        err = tk.Label(form, text="", bg=BG_CARD, fg=RED, font=FONT_SMALL)
        err.pack(anchor="w")

        def renew():
            new_end_date = end_e.get().strip()
            try:
                datetime.strptime(new_end_date, "%Y-%m-%d")
            except ValueError:
                err.config(text="Invalid date format.")
                return
            new_rent = None
            rent_str = rent_e.get().strip()
            if rent_str:
                try:
                    new_rent = float(rent_str)
                except ValueError:
                    err.config(text="Invalid rent value.")
                    return
            LeaseDAO.renew_lease(lease_id, new_end_date, new_rent)
            dialog.destroy()
            messagebox.showinfo("Success", "Lease renewed successfully.")
            self.refresh_table()

        btn_row = tk.Frame(form, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(8, 0))
        tk.Button(btn_row, text="Cancel", bg=BG_DARK, fg=TEXT_MUTED,
                  relief="flat", padx=16, pady=8, command=dialog.destroy
                  ).pack(side="right", padx=(8, 0))
        tk.Button(btn_row, text="Renew", bg=GOLD, fg=BG_DARK,
                  relief="flat", padx=16, pady=8, font=("Helvetica", 10, "bold"),
                  activebackground=GOLD_HOVER, command=renew).pack(side="right")

    def terminate(self, lease_id):
        penalty = LeaseDAO.calculate_early_termination_penalty(lease_id)
        if not penalty:
            return
        msg = (f"Terminate lease for {penalty['tenant_name']}?\n\n"
               f"Early termination penalty: £{penalty['penalty_amount']:,.2f}\n"
               f"(5% of £{penalty['monthly_rent']:,.2f} monthly rent)\n"
               f"30-day notice period required.")
        if messagebox.askyesno("Confirm Early Termination", msg):
            LeaseDAO.terminate_lease(lease_id)
            messagebox.showinfo("Terminated", "Lease terminated. Apartment marked as vacant.")
            self.refresh_table()
