# Component 3 | Author: Talal Esbaitah (23077550)

import tkinter as tk
from tkinter import messagebox, ttk
from ui.ui_helpers import *
from dao.tenant_dao import TenantDAO
from dao.lease_dao import LeaseDAO
from dao.payment_dao import PaymentDAO
from dao.complaint_dao import ComplaintDAO
from dao.maintenance_dao import MaintenanceDAO


class TenantManagementScreen:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.page = 1
        self.per_page = 15
        self.search_query = ""
        self.build()

    def build(self):
        clear_frame(self.parent)

        header = page_header(self.parent, "Tenant Management",
                             "Add, edit and manage tenant records")
        gold_button(header, "+  Register Tenant", self.open_add_dialog)

        search_frame = tk.Frame(self.parent, bg=BG_DARK)
        search_frame.pack(fill="x", padx=36, pady=(0, 16))

        self.search_entry = make_entry(search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=6)
        self.search_entry.insert(0, "")
        self.search_entry.bind("<Return>", lambda e: self.do_search())

        tk.Button(search_frame, text="Search", bg=BG_ACCENT, fg=TEXT_WHITE,
                  font=FONT_BODY, relief="flat", padx=16, pady=6,
                  cursor="hand2", command=self.do_search
                  ).pack(side="left", padx=(8, 0))

        tk.Button(search_frame, text="Clear", bg=BG_CARD, fg=TEXT_MUTED,
                  font=FONT_BODY, relief="flat", padx=12, pady=6,
                  cursor="hand2", command=self.clear_search
                  ).pack(side="left", padx=(8, 0))

        cols = [("ID", 5), ("NI Number", 12), ("Name", 16), ("Phone", 14),
                ("Email", 20), ("Status", 8), ("Actions", 14)]
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

        self.page_frame = tk.Frame(self.parent, bg=BG_DARK)
        self.page_frame.pack(fill="x", padx=36, pady=(8, 16))

        self.refresh_table()

    def refresh_table(self):
        clear_frame(self.rows_frame)
        clear_frame(self.page_frame)

        if self.search_query:
            tenants = TenantDAO.search_tenants(self.search_query, active_only=False)
            total = len(tenants)
        else:
            tenants, total = TenantDAO.get_tenants_paginated(
                self.page, self.per_page, active_only=False)

        widths = [5, 12, 16, 14, 20]

        if not tenants:
            tk.Label(self.rows_frame, text="No tenants found.",
                     bg=BG_DARK, fg=TEXT_MUTED, font=FONT_BODY
                     ).pack(pady=40)
            return

        overdue_ids = TenantDAO.get_overdue_tenant_ids()

        for i, t in enumerate(tenants):
            bg = BG_CARD if i % 2 == 0 else BG_DARK
            row = tk.Frame(self.rows_frame, bg=bg)
            row.pack(fill="x")

            values = [t["tenant_id"], t["ni_number"], t["name"],
                      t["phone"], t["email"]]
            for val, w in zip(values, widths):
                tk.Label(row, text=str(val), bg=bg, fg=TEXT_WHITE,
                         font=FONT_BODY, width=w, anchor="w",
                         padx=12, pady=10).pack(side="left")

            is_overdue = t["tenant_id"] in overdue_ids and t["is_active"]
            if not t["is_active"]:
                status_text = "Inactive"
            elif is_overdue:
                status_text = "Overdue"
            else:
                status_text = "Active"
            badge = status_badge(row, status_text, bg)
            badge.config(width=8, anchor="w", padx=12, pady=10)
            badge.pack(side="left")

            actions = tk.Frame(row, bg=bg)
            actions.pack(side="left", padx=8)

            tk.Button(actions, text="Edit", bg=BG_ACCENT, fg=TEXT_WHITE,
                      relief="flat", padx=10, pady=4, cursor="hand2",
                      font=FONT_SMALL,
                      command=lambda tid=t["tenant_id"]: self.open_edit_dialog(tid)
                      ).pack(side="left", padx=(0, 4))

            if t["is_active"]:
                tk.Button(actions, text="Deactivate", bg="#2a1a1a", fg=RED,
                          relief="flat", padx=10, pady=4, cursor="hand2",
                          font=FONT_SMALL,
                          command=lambda tid=t["tenant_id"]: self.deactivate(tid)
                          ).pack(side="left")
            else:
                tk.Button(actions, text="Reactivate", bg="#1a2a1a", fg=GREEN,
                          relief="flat", padx=10, pady=4, cursor="hand2",
                          font=FONT_SMALL,
                          command=lambda tid=t["tenant_id"]: self.reactivate(tid)
                          ).pack(side="left")

            tk.Button(actions, text="History", bg=BG_CARD if bg == BG_DARK else BG_DARK,
                      fg=BLUE, relief="flat", padx=10, pady=4, cursor="hand2",
                      font=FONT_SMALL,
                      command=lambda tid=t["tenant_id"], tname=t["name"]: self.show_history(tid, tname)
                      ).pack(side="left", padx=(4, 0))

        if not self.search_query:
            total_pages = max(1, (total + self.per_page - 1) // self.per_page)
            tk.Label(self.page_frame,
                     text=f"Page {self.page} of {total_pages}  ({total} tenants)",
                     bg=BG_DARK, fg=TEXT_MUTED, font=FONT_SMALL
                     ).pack(side="left")

            if self.page > 1:
                tk.Button(self.page_frame, text="< Prev", bg=BG_ACCENT,
                          fg=TEXT_WHITE, relief="flat", padx=10, pady=4,
                          cursor="hand2", font=FONT_SMALL,
                          command=self.prev_page).pack(side="right", padx=4)
            if self.page < total_pages:
                tk.Button(self.page_frame, text="Next >", bg=BG_ACCENT,
                          fg=TEXT_WHITE, relief="flat", padx=10, pady=4,
                          cursor="hand2", font=FONT_SMALL,
                          command=self.next_page).pack(side="right", padx=4)

    def do_search(self):
        self.search_query = self.search_entry.get().strip()
        self.refresh_table()

    def clear_search(self):
        self.search_query = ""
        self.search_entry.delete(0, tk.END)
        self.page = 1
        self.refresh_table()

    def next_page(self):
        self.page += 1
        self.refresh_table()

    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            self.refresh_table()

    def open_add_dialog(self):
        self._open_dialog(mode="add")

    def open_edit_dialog(self, tenant_id):
        tenant = TenantDAO.get_tenant(tenant_id)
        if tenant:
            self._open_dialog(mode="edit", tenant=tenant)

    def _open_dialog(self, mode="add", tenant=None):
        dialog = tk.Toplevel()
        dialog.title("Register Tenant" if mode == "add" else "Edit Tenant")
        dialog.geometry("500x680")
        dialog.configure(bg=BG_CARD)
        dialog.grab_set()
        dialog.resizable(False, False)

        dh = tk.Frame(dialog, bg=BG_ACCENT, padx=24, pady=16)
        dh.pack(fill="x")
        tk.Label(dh, text="+  Register Tenant" if mode == "add" else "Edit Tenant",
                 bg=BG_ACCENT, fg=TEXT_WHITE, font=FONT_HEADING).pack(anchor="w")

        canvas = tk.Canvas(dialog, bg=BG_CARD, highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        form = tk.Frame(canvas, bg=BG_CARD, padx=28, pady=20)

        form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=form, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        entries = {}
        fields = [
            ("NI NUMBER *", "ni_number"),
            ("FULL NAME *", "name"),
            ("PHONE *", "phone"),
            ("EMAIL *", "email"),
            ("OCCUPATION", "occupation"),
            ("REFERENCES", "reference_info"),
            ("APARTMENT REQUIREMENTS", "apartment_requirements"),
            ("EMERGENCY CONTACT", "emergency_contact"),
        ]

        for label_text, key in fields:
            field_label(form, label_text)
            e = make_entry(form)
            e.pack(fill="x", pady=(4, 14), ipady=6)
            if tenant and key in tenant:
                e.insert(0, tenant[key] or "")
            entries[key] = e

        err = tk.Label(form, text="", bg=BG_CARD, fg=RED, font=FONT_SMALL)
        err.pack(anchor="w", pady=(4, 8))

        def save():
            data = {k: entries[k].get().strip() for k in entries}
            if not data["ni_number"] or not data["name"] or \
               not data["phone"] or not data["email"]:
                err.config(text="Please fill in all required fields (*)")
                return

            if mode == "add":
                try:
                    TenantDAO.add_tenant(**data)
                    dialog.destroy()
                    messagebox.showinfo("Success", "Tenant registered successfully.")
                    self.refresh_table()
                except Exception as ex:
                    if "UNIQUE" in str(ex):
                        err.config(text="NI Number already exists.")
                    else:
                        err.config(text=str(ex))
            else:
                TenantDAO.update_tenant(tenant["tenant_id"], **data)
                dialog.destroy()
                messagebox.showinfo("Success", "Tenant updated successfully.")
                self.refresh_table()

        btn_row = tk.Frame(form, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(8, 0))
        tk.Button(btn_row, text="Cancel", bg=BG_DARK, fg=TEXT_MUTED,
                  relief="flat", padx=16, pady=8, cursor="hand2",
                  font=FONT_BODY, command=dialog.destroy).pack(side="right", padx=(8, 0))
        tk.Button(btn_row, text="Save" if mode == "edit" else "Register",
                  bg=GOLD, fg=BG_DARK, relief="flat", padx=16, pady=8,
                  cursor="hand2", font=("Helvetica", 10, "bold"),
                  activebackground=GOLD_HOVER, command=save).pack(side="right")

    def show_history(self, tenant_id, tenant_name):
        win = tk.Toplevel()
        win.title(f"History — {tenant_name}")
        win.geometry("680x560")
        win.configure(bg="#16213e")
        win.grab_set()
        win.resizable(False, False)

        hdr = tk.Frame(win, bg="#0f3460", padx=24, pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"Tenant History  —  {tenant_name}",
                 bg="#0f3460", fg="white",
                 font=("Georgia", 14, "bold")).pack(anchor="w")

        body = tk.Frame(win, bg="#16213e", padx=20, pady=16)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="LEASE HISTORY",
                 bg="#16213e", fg="#3a4a6b",
                 font=("Helvetica", 8, "bold")).pack(anchor="w", pady=(0, 6))

        lease_hdr = tk.Frame(body, bg="#0f3460")
        lease_hdr.pack(fill="x")
        for col, w in [("Apartment", 16), ("City", 10), ("Start", 10), ("End", 10), ("Rent", 10), ("Status", 10)]:
            tk.Label(lease_hdr, text=col, bg="#0f3460", fg="#e2b96f",
                     font=("Helvetica", 8, "bold"), width=w,
                     anchor="w", padx=10, pady=8).pack(side="left")

        leases = LeaseDAO.get_leases_for_apartment_by_tenant(tenant_id)
        if leases:
            for i, l in enumerate(leases):
                bg = "#16213e" if i % 2 == 0 else "#1a1a2e"
                row = tk.Frame(body, bg=bg)
                row.pack(fill="x")
                for val, w in [
                    (l.get("apartment_name", "—"), 16),
                    (l.get("city_name", "—"), 10),
                    (l["start_date"], 10),
                    (l["end_date"], 10),
                    (f"£{l['monthly_rent']:,.0f}", 10),
                    (l["status"], 10),
                ]:
                    tk.Label(row, text=str(val), bg=bg, fg="white",
                             font=("Helvetica", 10), width=w,
                             anchor="w", padx=10, pady=8).pack(side="left")
        else:
            tk.Label(body, text="No lease history.", bg="#16213e",
                     fg="#555e7a", font=("Helvetica", 10)).pack(anchor="w", pady=8)

        tk.Frame(body, bg="#0f3460", height=1).pack(fill="x", pady=(12, 8))

        tk.Label(body, text="PAYMENT HISTORY",
                 bg="#16213e", fg="#3a4a6b",
                 font=("Helvetica", 8, "bold")).pack(anchor="w", pady=(0, 6))

        pay_hdr = tk.Frame(body, bg="#0f3460")
        pay_hdr.pack(fill="x")
        for col, w in [("Payment ID", 10), ("Amount", 10), ("Date", 12), ("Method", 14), ("Invoice", 20)]:
            tk.Label(pay_hdr, text=col, bg="#0f3460", fg="#e2b96f",
                     font=("Helvetica", 8, "bold"), width=w,
                     anchor="w", padx=10, pady=8).pack(side="left")

        payments = PaymentDAO.get_tenant_payment_history(tenant_id)
        if payments:
            for i, p in enumerate(payments):
                bg = "#16213e" if i % 2 == 0 else "#1a1a2e"
                row = tk.Frame(body, bg=bg)
                row.pack(fill="x")
                for val, w in [
                    (p["payment_id"], 10),
                    (f"£{p['amount']:,.2f}", 10),
                    (p["payment_date"], 12),
                    (p["method"], 14),
                    (p.get("invoice_desc", "—") or "—", 20),
                ]:
                    tk.Label(row, text=str(val), bg=bg, fg="white",
                             font=("Helvetica", 10), width=w,
                             anchor="w", padx=10, pady=8).pack(side="left")
        else:
            tk.Label(body, text="No payment history.", bg="#16213e",
                     fg="#555e7a", font=("Helvetica", 10)).pack(anchor="w", pady=8)

        tk.Frame(body, bg="#0f3460", height=1).pack(fill="x", pady=(12, 8))

        complaint_header_row = tk.Frame(body, bg="#16213e")
        complaint_header_row.pack(fill="x", pady=(0, 6))

        tk.Label(complaint_header_row, text="COMPLAINT LOG",
                 bg="#16213e", fg="#3a4a6b",
                 font=("Helvetica", 8, "bold")).pack(side="left")

        tk.Button(complaint_header_row, text="+  Log Complaint",
                  bg="#0f3460", fg="#e2b96f",
                  font=("Helvetica", 8, "bold"), relief="flat",
                  padx=10, pady=4, cursor="hand2",
                  activebackground="#1a4a7a",
                  command=lambda: self._open_complaint_dialog(tenant_id, win, complaints_frame)
                  ).pack(side="right")

        comp_hdr = tk.Frame(body, bg="#0f3460")
        comp_hdr.pack(fill="x")
        for col, w in [("ID", 6), ("Description", 30), ("Linked Request", 18), ("Date", 14)]:
            tk.Label(comp_hdr, text=col, bg="#0f3460", fg="#e2b96f",
                     font=("Helvetica", 8, "bold"), width=w,
                     anchor="w", padx=10, pady=8).pack(side="left")

        complaints_frame = tk.Frame(body, bg="#16213e")
        complaints_frame.pack(fill="x")
        self._render_complaints(tenant_id, complaints_frame)

        tk.Button(body, text="Close", bg="#e2b96f", fg="#1a1a2e",
                  font=("Helvetica", 10, "bold"), relief="flat",
                  padx=20, pady=8, cursor="hand2",
                  activebackground="#c9a45a",
                  command=win.destroy).pack(pady=(16, 0), anchor="e")

    def _render_complaints(self, tenant_id, frame):
        for w in frame.winfo_children():
            w.destroy()
        complaints = ComplaintDAO.get_complaints_for_tenant(tenant_id)
        if complaints:
            for i, c in enumerate(complaints):
                bg = "#16213e" if i % 2 == 0 else "#1a1a2e"
                row = tk.Frame(frame, bg=bg)
                row.pack(fill="x")
                linked = c.get("request_description") or "—"
                if linked != "—" and len(linked) > 22:
                    linked = linked[:22] + "…"
                desc = c["description"]
                if len(desc) > 35:
                    desc = desc[:35] + "…"
                for val, w in [
                    (c["complaint_id"], 6),
                    (desc, 30),
                    (linked, 18),
                    (c["created_at"][:10], 14),
                ]:
                    tk.Label(row, text=str(val), bg=bg, fg="white",
                             font=("Helvetica", 10), width=w,
                             anchor="w", padx=10, pady=8).pack(side="left")
        else:
            tk.Label(frame, text="No complaints logged.", bg="#16213e",
                     fg="#555e7a", font=("Helvetica", 10)).pack(anchor="w", pady=8)

    def _open_complaint_dialog(self, tenant_id, parent_win, complaints_frame):
        dialog = tk.Toplevel(parent_win)
        dialog.title("Log Complaint")
        dialog.geometry("420x340")
        dialog.configure(bg="#16213e")
        dialog.grab_set()
        dialog.resizable(False, False)

        dh = tk.Frame(dialog, bg="#0f3460", padx=24, pady=16)
        dh.pack(fill="x")
        tk.Label(dh, text="+  Log Complaint",
                 bg="#0f3460", fg="white",
                 font=("Georgia", 14, "bold")).pack(anchor="w")

        form = tk.Frame(dialog, bg="#16213e", padx=24, pady=20)
        form.pack(fill="both", expand=True)

        tk.Label(form, text="DESCRIPTION", bg="#16213e", fg="#555e7a",
                 font=("Helvetica", 8, "bold")).pack(anchor="w")
        desc_text = tk.Text(form, bg="#1a1a2e", fg="white",
                            insertbackground="#e2b96f", relief="flat",
                            font=("Helvetica", 10), height=4, bd=10,
                            highlightthickness=1, highlightcolor="#e2b96f",
                            highlightbackground="#0f3460")
        desc_text.pack(fill="x", pady=(4, 14))

        link_var = tk.BooleanVar(value=False)
        open_requests = MaintenanceDAO.get_all_requests(
            status=None, priority=None)
        tenant_requests = [r for r in open_requests
                           if r.get("tenant_name") and
                           r["status"] != "Resolved"]

        link_row = tk.Frame(form, bg="#16213e")
        link_row.pack(fill="x", pady=(0, 8))
        tk.Checkbutton(
            link_row, text="Link to maintenance request",
            variable=link_var,
            bg="#16213e", fg="#7a9cc4",
            selectcolor="#1a1a2e",
            activebackground="#16213e",
            activeforeground="#e2b96f",
            font=("Helvetica", 9),
            cursor="hand2",
            relief="flat", bd=0
        ).pack(side="left")

        req_labels = [f"#{r['request_id']} — {r['apartment_name']}: {r['description'][:30]}"
                      for r in tenant_requests]
        req_var = tk.StringVar(value=req_labels[0] if req_labels else "")
        req_dd = tk.OptionMenu(link_row, req_var,
                               *req_labels if req_labels else ["No open requests"])
        req_dd.config(bg="#1a1a2e", fg="white", relief="flat",
                      font=("Helvetica", 9), activebackground="#0f3460")
        req_dd["menu"].config(bg="#1a1a2e", fg="white")
        req_dd.pack(side="left", padx=(8, 0))

        err = tk.Label(form, text="", bg="#16213e", fg="#e05c5c",
                       font=("Helvetica", 9))
        err.pack(anchor="w")

        def save():
            desc = desc_text.get("1.0", tk.END).strip()
            if not desc:
                err.config(text="Description is required.")
                return
            linked_id = None
            if link_var.get() and tenant_requests:
                idx = req_labels.index(req_var.get()) if req_var.get() in req_labels else -1
                if idx >= 0:
                    linked_id = tenant_requests[idx]["request_id"]
            ComplaintDAO.log_complaint(tenant_id, desc, linked_id)
            dialog.destroy()
            self._render_complaints(tenant_id, complaints_frame)

        btn_row = tk.Frame(form, bg="#16213e")
        btn_row.pack(fill="x", pady=(8, 0))
        tk.Button(btn_row, text="Cancel", bg="#1a1a2e", fg="#555e7a",
                  relief="flat", padx=16, pady=8, cursor="hand2",
                  font=("Helvetica", 10),
                  command=dialog.destroy).pack(side="right", padx=(8, 0))
        tk.Button(btn_row, text="Log Complaint", bg="#e2b96f", fg="#1a1a2e",
                  relief="flat", padx=16, pady=8, cursor="hand2",
                  font=("Helvetica", 10, "bold"),
                  activebackground="#c9a45a",
                  command=save).pack(side="right")

    def deactivate(self, tenant_id):
        if messagebox.askyesno("Confirm", "Deactivate this tenant?\nThey will be marked as inactive."):
            TenantDAO.deactivate_tenant(tenant_id)
            self.refresh_table()

    def reactivate(self, tenant_id):
        TenantDAO.reactivate_tenant(tenant_id)
        self.refresh_table()
