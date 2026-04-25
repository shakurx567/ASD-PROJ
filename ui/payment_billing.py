# Component 4 | Author: Abdulmalik Altaleb (23061771)

import tkinter as tk
from tkinter import messagebox, ttk
from ui.ui_helpers import *
from dao.invoice_dao import InvoiceDAO
from dao.payment_dao import PaymentDAO
from dao.tenant_dao import TenantDAO
from datetime import datetime


class PaymentBillingScreen:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.view_mode = "invoices"
        self.build()

    def build(self):
        clear_frame(self.parent)

        header = page_header(self.parent, "Payment & Billing",
                             "Manage invoices, record payments and track finances")

        btn_row = tk.Frame(self.parent, bg=BG_DARK)
        btn_row.pack(fill="x", padx=36, pady=(0, 8))

        gold_button(btn_row, "+  Record Payment", self.open_record_payment, side="right")
        secondary_button(btn_row, "Generate Monthly Invoices", self.generate_invoices, side="right")
        secondary_button(btn_row, "Detect Overdue", self.detect_overdue, side="right")

        tab_bar = tk.Frame(self.parent, bg=BG_DARK)
        tab_bar.pack(fill="x", padx=36, pady=(0, 16))

        self.tab_btns = {}
        for label in ["Invoices", "Payments", "Overdue"]:
            btn = tk.Button(tab_bar, text=label, bg=BG_CARD, fg=TEXT_MUTED,
                            relief="flat", padx=20, pady=8, cursor="hand2",
                            font=FONT_BODY,
                            command=lambda l=label: self.switch_tab(l))
            btn.pack(side="left", padx=(0, 4))
            self.tab_btns[label] = btn

        self.stats_frame = tk.Frame(self.parent, bg=BG_DARK)
        self.stats_frame.pack(fill="x", padx=36, pady=(0, 16))
        self.refresh_stats()

        self.content_frame = tk.Frame(self.parent, bg=BG_DARK)
        self.content_frame.pack(fill="both", expand=True, padx=36)

        self._scroll_canvas = None
        self._scroll_window = None

        self.switch_tab("Invoices")

    def refresh_stats(self):
        clear_frame(self.stats_frame)
        summary = InvoiceDAO.get_financial_summary()
        stat_card(self.stats_frame, "Coll", "Collected",
                  f"£{summary.get('total_collected', 0):,.0f}", GREEN, 0)
        stat_card(self.stats_frame, "Pend", "Pending",
                  f"£{summary.get('total_pending', 0):,.0f}", GOLD, 1)
        stat_card(self.stats_frame, "Over", "Overdue",
                  f"£{summary.get('total_overdue', 0):,.0f}", RED, 2)
        stat_card(self.stats_frame, "Inv", "Total Invoices",
                  summary.get("total_invoices", 0), BLUE, 3)

    def switch_tab(self, tab):
        self.view_mode = tab.lower()
        for label, btn in self.tab_btns.items():
            if label == tab:
                btn.config(bg=GOLD, fg=BG_DARK, font=("Helvetica", 10, "bold"))
            else:
                btn.config(bg=BG_CARD, fg=TEXT_MUTED, font=FONT_BODY)

        clear_frame(self.content_frame)

        if self.view_mode == "invoices":
            self.show_invoices()
        elif self.view_mode == "payments":
            self.show_payments()
        elif self.view_mode == "overdue":
            self.show_overdue()

    def _make_scrollable_rows(self):
        scroll_container = tk.Frame(self.content_frame, bg=BG_DARK)
        scroll_container.pack(fill="both", expand=True)

        canvas = tk.Canvas(scroll_container, bg=BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical",
                                  command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        rows_frame = tk.Frame(canvas, bg=BG_DARK)
        win_id = canvas.create_window((0, 0), window=rows_frame, anchor="nw")

        rows_frame.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(
            int(-1*(e.delta/120)), "units"))

        self._scroll_canvas = canvas
        return rows_frame

    def show_invoices(self):
        cols = [("ID", 4), ("Tenant", 14), ("Apartment", 12), ("Amount", 10),
                ("Due Date", 10), ("Status", 10), ("Actions", 12)]
        table_header(self.content_frame, cols)

        rows_frame = self._make_scrollable_rows()

        invoices = InvoiceDAO.get_all_invoices()
        widths = [4, 14, 12, 10, 10]

        for i, inv in enumerate(invoices):
            bg = BG_CARD if i % 2 == 0 else BG_DARK
            row = tk.Frame(rows_frame, bg=bg)
            row.pack(fill="x")

            values = [inv["invoice_id"], inv["tenant_name"],
                      inv["apartment_name"], f"£{inv['amount']:,.2f}",
                      inv["due_date"]]
            for val, w in zip(values, widths):
                tk.Label(row, text=str(val), bg=bg, fg=TEXT_WHITE,
                         font=FONT_BODY, width=w, anchor="w",
                         padx=12, pady=10).pack(side="left")

            badge = status_badge(row, inv["status"], bg)
            badge.config(width=10, anchor="w", padx=12, pady=10)
            badge.pack(side="left")

            actions = tk.Frame(row, bg=bg)
            actions.pack(side="left", padx=8)

            if inv["status"] in ("Pending", "Overdue", "Partial"):
                tk.Button(actions, text="Pay", bg=BG_ACCENT, fg=TEXT_WHITE,
                          relief="flat", padx=10, pady=4, cursor="hand2",
                          font=FONT_SMALL,
                          command=lambda iid=inv["invoice_id"], tid=inv["tenant_id"],
                          amt=inv["amount"]: self.quick_pay(iid, tid, amt)
                          ).pack(side="left")

    def show_payments(self):
        cols = [("ID", 4), ("Tenant", 14), ("Amount", 10), ("Date", 10),
                ("Method", 12), ("Invoice", 20)]
        table_header(self.content_frame, cols)

        rows_frame = self._make_scrollable_rows()

        payments = PaymentDAO.get_all_payments()
        widths = [4, 14, 10, 10, 12, 20]

        for i, p in enumerate(payments):
            bg = BG_CARD if i % 2 == 0 else BG_DARK
            row = tk.Frame(rows_frame, bg=bg)
            row.pack(fill="x")

            values = [p["payment_id"], p["tenant_name"],
                      f"£{p['amount']:,.2f}", p["payment_date"],
                      p["method"], p.get("invoice_desc", "")]
            for val, w in zip(values, widths):
                tk.Label(row, text=str(val), bg=bg, fg=TEXT_WHITE,
                         font=FONT_BODY, width=w, anchor="w",
                         padx=12, pady=10).pack(side="left")

    def show_overdue(self):
        cols = [("ID", 4), ("Tenant", 14), ("Apartment", 12),
                ("Amount", 10), ("Due Date", 10), ("City", 10), ("Actions", 12)]
        table_header(self.content_frame, cols)

        rows_frame = self._make_scrollable_rows()

        overdue = InvoiceDAO.get_overdue_invoices()
        widths = [4, 14, 12, 10, 10, 10]

        if not overdue:
            tk.Label(rows_frame, text="No overdue invoices.",
                     bg=BG_DARK, fg=GREEN, font=FONT_BODY).pack(pady=40)
            return

        for i, inv in enumerate(overdue):
            bg = BG_CARD if i % 2 == 0 else BG_DARK
            row = tk.Frame(rows_frame, bg=bg)
            row.pack(fill="x")

            values = [inv["invoice_id"], inv["tenant_name"],
                      inv["apartment_name"], f"£{inv['amount']:,.2f}",
                      inv["due_date"], inv["city_name"]]
            for val, w in zip(values, widths):
                tk.Label(row, text=str(val), bg=bg, fg=TEXT_WHITE,
                         font=FONT_BODY, width=w, anchor="w",
                         padx=12, pady=10).pack(side="left")

            tk.Button(row, text="Pay", bg=BG_ACCENT, fg=TEXT_WHITE,
                      relief="flat", padx=10, pady=4, cursor="hand2",
                      font=FONT_SMALL,
                      command=lambda iid=inv["invoice_id"], tid=inv["tenant_id"],
                      amt=inv["amount"]: self.quick_pay(iid, tid, amt)
                      ).pack(side="left", padx=8)

    def open_record_payment(self):
        dialog = tk.Toplevel()
        dialog.title("Record Payment")
        dialog.geometry("440x480")
        dialog.configure(bg=BG_CARD)
        dialog.grab_set()
        dialog.resizable(False, False)

        dh = tk.Frame(dialog, bg=BG_ACCENT, padx=24, pady=16)
        dh.pack(fill="x")
        tk.Label(dh, text="+  Record Payment",
                 bg=BG_ACCENT, fg=TEXT_WHITE, font=FONT_HEADING).pack(anchor="w")

        form = tk.Frame(dialog, bg=BG_CARD, padx=28, pady=20)
        form.pack(fill="both", expand=True)

        field_label(form, "TENANT")
        tenants = TenantDAO.get_all_tenants()
        tenant_names = [f"{t['name']} (ID: {t['tenant_id']})" for t in tenants]
        tenant_dd, tenant_var = make_dropdown(form, tenant_names)
        tenant_dd.pack(fill="x", pady=(4, 14))

        field_label(form, "INVOICE")
        inv_dd_var = tk.StringVar()
        inv_dd = ttk.Combobox(form, textvariable=inv_dd_var, state="readonly",
                              font=FONT_BODY)
        inv_dd.pack(fill="x", pady=(4, 14))
        invoice_cache = []

        def on_tenant_select(event):
            idx = tenant_dd.current()
            if idx < 0:
                return
            tid = tenants[idx]["tenant_id"]
            invs = InvoiceDAO.get_all_invoices(tenant_id=tid)
            unpaid = [iv for iv in invs if iv["status"] in ("Pending", "Overdue", "Partial")]
            invoice_cache.clear()
            invoice_cache.extend(unpaid)
            labels = [f"INV-{iv['invoice_id']} | £{iv['amount']:,.2f} | {iv['due_date']} | {iv['status']}" for iv in unpaid]
            inv_dd["values"] = labels if labels else ["No unpaid invoices"]
            if labels:
                inv_dd.current(0)

        tenant_dd.bind("<<ComboboxSelected>>", on_tenant_select)

        field_label(form, "AMOUNT (GBP)")
        amount_e = make_entry(form)
        amount_e.pack(fill="x", pady=(4, 14), ipady=6)

        field_label(form, "PAYMENT METHOD")
        methods = ["Cash", "Bank Transfer", "Card", "Cheque"]
        method_dd, method_var = make_dropdown(form, methods)
        method_dd.pack(fill="x", pady=(4, 14))

        field_label(form, "PAYMENT DATE")
        date_e = make_entry(form)
        date_e.pack(fill="x", pady=(4, 14), ipady=6)
        date_e.insert(0, datetime.now().strftime("%Y-%m-%d"))

        err = tk.Label(form, text="", bg=BG_CARD, fg=RED, font=FONT_SMALL)
        err.pack(anchor="w")

        def save():
            t_idx = tenant_dd.current()
            i_idx = inv_dd.current()
            if t_idx < 0 or i_idx < 0 or not invoice_cache:
                err.config(text="Please select tenant and invoice.")
                return
            try:
                amount = float(amount_e.get().strip())
            except ValueError:
                err.config(text="Invalid amount.")
                return

            invoice = invoice_cache[i_idx]
            tenant = tenants[t_idx]
            pay_id = PaymentDAO.record_payment(
                invoice["invoice_id"], tenant["tenant_id"],
                amount, method_var.get(), date_e.get().strip())
            dialog.destroy()
            self.refresh_stats()
            self.switch_tab("Payments" if self.view_mode == "payments" else "Invoices")
            self._show_receipt(pay_id)

        btn_row = tk.Frame(form, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(8, 0))
        tk.Button(btn_row, text="Cancel", bg=BG_DARK, fg=TEXT_MUTED,
                  relief="flat", padx=16, pady=8, command=dialog.destroy
                  ).pack(side="right", padx=(8, 0))
        tk.Button(btn_row, text="Record Payment", bg=GOLD, fg=BG_DARK,
                  relief="flat", padx=16, pady=8, font=("Helvetica", 10, "bold"),
                  activebackground=GOLD_HOVER, command=save).pack(side="right")

    def quick_pay(self, invoice_id, tenant_id, amount):
        dialog = tk.Toplevel()
        dialog.title("Quick Payment")
        dialog.geometry("380x280")
        dialog.configure(bg=BG_CARD)
        dialog.grab_set()

        dh = tk.Frame(dialog, bg=BG_ACCENT, padx=24, pady=16)
        dh.pack(fill="x")
        tk.Label(dh, text=f"Pay Invoice #{invoice_id}",
                 bg=BG_ACCENT, fg=TEXT_WHITE, font=FONT_HEADING).pack(anchor="w")

        form = tk.Frame(dialog, bg=BG_CARD, padx=28, pady=20)
        form.pack(fill="both", expand=True)

        tk.Label(form, text=f"Invoice Amount: £{amount:,.2f}",
                 bg=BG_CARD, fg=TEXT_WHITE, font=FONT_BODY).pack(anchor="w", pady=(0, 14))

        field_label(form, "AMOUNT TO PAY")
        amt_e = make_entry(form)
        amt_e.pack(fill="x", pady=(4, 14), ipady=6)
        amt_e.insert(0, str(amount))

        field_label(form, "METHOD")
        methods = ["Cash", "Bank Transfer", "Card", "Cheque"]
        m_dd, m_var = make_dropdown(form, methods)
        m_dd.pack(fill="x", pady=(4, 14))

        def pay():
            try:
                pay_amount = float(amt_e.get().strip())
            except ValueError:
                return
            pay_id = PaymentDAO.record_payment(invoice_id, tenant_id, pay_amount, m_var.get())
            dialog.destroy()
            self.refresh_stats()
            self.switch_tab(self.view_mode.capitalize())
            self._show_receipt(pay_id)

        btn_row = tk.Frame(form, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(8, 0))
        tk.Button(btn_row, text="Cancel", bg=BG_DARK, fg=TEXT_MUTED,
                  relief="flat", padx=16, pady=8, command=dialog.destroy
                  ).pack(side="right", padx=(8, 0))
        tk.Button(btn_row, text="Pay", bg=GOLD, fg=BG_DARK,
                  relief="flat", padx=16, pady=8, font=("Helvetica", 10, "bold"),
                  activebackground=GOLD_HOVER, command=pay).pack(side="right")

    def _show_receipt(self, payment_id):
        receipt = PaymentDAO.get_receipt_data(payment_id)
        if not receipt:
            return

        win = tk.Toplevel()
        win.title(f"Receipt — Payment #{payment_id}")
        win.geometry("420x480")
        win.configure(bg="#16213e")
        win.grab_set()
        win.resizable(False, False)

        hdr = tk.Frame(win, bg="#0f3460", padx=24, pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text="PARAGON  ·  Payment Receipt",
                 bg="#0f3460", fg="#e2b96f",
                 font=("Georgia", 13, "bold")).pack(anchor="w")
        tk.Label(hdr, text=f"Receipt #{payment_id:05d}",
                 bg="#0f3460", fg="#7a9cc4",
                 font=("Helvetica", 9)).pack(anchor="w", pady=(2, 0))

        body = tk.Frame(win, bg="#16213e", padx=28, pady=20)
        body.pack(fill="both", expand=True)

        def row(label, value, value_color="white"):
            r = tk.Frame(body, bg="#16213e")
            r.pack(fill="x", pady=5)
            tk.Label(r, text=label, bg="#16213e", fg="#555e7a",
                     font=("Helvetica", 8, "bold"), width=20,
                     anchor="w").pack(side="left")
            tk.Label(r, text=str(value), bg="#16213e", fg=value_color,
                     font=("Helvetica", 10), anchor="w").pack(side="left")

        tk.Frame(body, bg="#0f3460", height=1).pack(fill="x", pady=(0, 12))

        row("Tenant", receipt["tenant_name"])
        row("Apartment", receipt.get("apartment_name", "—"))
        row("City", receipt.get("city_name", "—"))

        tk.Frame(body, bg="#0f3460", height=1).pack(fill="x", pady=10)

        row("Amount Paid", f"£{receipt['amount']:,.2f}", "#e2b96f")
        row("Payment Date", receipt["payment_date"])
        row("Method", receipt["method"])
        row("Invoice Amount", f"£{receipt.get('invoice_amount', 0):,.2f}")

        paid_total = PaymentDAO.get_payments_for_invoice(receipt["invoice_id"])
        total_paid = sum(p["amount"] for p in paid_total)
        remaining = receipt.get("invoice_amount", 0) - total_paid
        if remaining > 0.005:
            tk.Frame(body, bg="#0f3460", height=1).pack(fill="x", pady=10)
            row("Remaining Balance", f"£{remaining:,.2f}", "#e05c5c")

        tk.Frame(body, bg="#0f3460", height=1).pack(fill="x", pady=(12, 0))

        tk.Label(body,
                 text="Thank you for your payment.",
                 bg="#16213e", fg="#555e7a",
                 font=("Helvetica", 9, "italic")).pack(pady=(10, 0))

        tk.Button(body, text="Close", bg="#e2b96f", fg="#1a1a2e",
                  font=("Helvetica", 10, "bold"), relief="flat",
                  padx=20, pady=8, cursor="hand2",
                  activebackground="#c9a45a",
                  command=win.destroy).pack(pady=(16, 0))

    def generate_invoices(self):
        count = InvoiceDAO.generate_monthly_invoices()
        if count > 0:
            messagebox.showinfo("Invoices Generated",
                                f"{count} invoice(s) generated for this month.")
        else:
            messagebox.showinfo("Info", "All invoices for this month already exist.")
        self.refresh_stats()
        self.switch_tab("Invoices")

    def detect_overdue(self):
        count = InvoiceDAO.detect_overdue_invoices()
        messagebox.showinfo("Overdue Detection",
                            f"{count} invoice(s) marked as overdue.")
        self.refresh_stats()
        self.switch_tab("Overdue")
