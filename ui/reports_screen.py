# Component 4 | Author: Abdulmalik Altaleb (23061771)

import tkinter as tk
from tkinter import ttk
from ui.ui_helpers import *
from dao.apartment_dao import ApartmentDAO
from dao.invoice_dao import InvoiceDAO
from dao.maintenance_dao import MaintenanceDAO


class ReportsScreen:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.build()

    def build(self):
        clear_frame(self.parent)
        page_header(self.parent, "Reports & Analytics",
                    "Occupancy, financial and maintenance insights")

        # Tab bar
        tab_bar = tk.Frame(self.parent, bg=BG_DARK)
        tab_bar.pack(fill="x", padx=36, pady=(0, 16))

        self.tab_btns = {}
        for label in ["Occupancy", "Financial", "Maintenance"]:
            btn = tk.Button(tab_bar, text=label, bg=BG_CARD, fg=TEXT_MUTED,
                            relief="flat", padx=20, pady=8, cursor="hand2",
                            font=FONT_BODY,
                            command=lambda l=label: self.switch_tab(l))
            btn.pack(side="left", padx=(0, 4))
            self.tab_btns[label] = btn

        self.content_frame = tk.Frame(self.parent, bg=BG_DARK)
        self.content_frame.pack(fill="both", expand=True, padx=36)

        self.switch_tab("Occupancy")

    def switch_tab(self, tab):
        for label, btn in self.tab_btns.items():
            if label == tab:
                btn.config(bg=GOLD, fg=BG_DARK, font=("Helvetica", 10, "bold"))
            else:
                btn.config(bg=BG_CARD, fg=TEXT_MUTED, font=FONT_BODY)

        clear_frame(self.content_frame)

        if tab == "Occupancy":
            self.show_occupancy()
        elif tab == "Financial":
            self.show_financial()
        elif tab == "Maintenance":
            self.show_maintenance()

    def show_occupancy(self):
        stats = ApartmentDAO.get_occupancy_stats()
        stats_row = tk.Frame(self.content_frame, bg=BG_DARK)
        stats_row.pack(fill="x", pady=(0, 20))
        stat_card(stats_row, "Tot", "Total", stats["total"], BLUE, 0)
        stat_card(stats_row, "Occ", "Occupied", stats["Occupied"], GREEN, 1)
        stat_card(stats_row, "Vac", "Vacant", stats["Vacant"], GOLD, 2)
        stat_card(stats_row, "%", "Rate", f"{stats['occupancy_rate']}%", BLUE, 3)

        body = tk.Frame(self.content_frame, bg=BG_DARK)
        body.pack(fill="both", expand=True)

        table_left = tk.Frame(body, bg=BG_DARK)
        table_left.pack(side="left", fill="both", expand=True, padx=(0, 16))

        cols = [("City", 14), ("Total", 6), ("Occupied", 8),
                ("Vacant", 6), ("Maint.", 6), ("Rate", 8)]
        table_header(table_left, cols)
        by_city = ApartmentDAO.get_occupancy_by_city()

        for i, c in enumerate(by_city):
            bg = BG_CARD if i % 2 == 0 else BG_DARK
            row = tk.Frame(table_left, bg=bg)
            row.pack(fill="x")
            total = c["total"] or 0
            occupied = c["occupied"] or 0
            rate = f"{round(occupied / total * 100, 1)}%" if total > 0 else "0%"
            vals = [c["city_name"], total, occupied,
                    c["vacant"] or 0, c["maintenance"] or 0, rate]
            widths = [14, 6, 8, 6, 6, 8]
            for val, w in zip(vals, widths):
                tk.Label(row, text=str(val), bg=bg, fg=TEXT_WHITE,
                         font=FONT_BODY, width=w, anchor="w",
                         padx=12, pady=10).pack(side="left")

        chart_right = tk.Frame(body, bg=BG_CARD, padx=20, pady=20)
        chart_right.pack(side="right", fill="y", padx=(0, 0))

        tk.Label(chart_right, text="OCCUPANCY BY CITY",
                 bg=BG_CARD, fg=TEXT_DIM, font=FONT_LABEL).pack(anchor="w", pady=(0, 12))

        canvas = tk.Canvas(chart_right, width=280, height=200,
                           bg=BG_CARD, highlightthickness=0)
        canvas.pack()

        if by_city:
            max_total = max((c["total"] or 1) for c in by_city)
            bar_width = 40
            spacing = 20
            x = 30
            colors = [GOLD, BLUE, GREEN, RED, "#aaaaaa"]

            for idx, c in enumerate(by_city):
                total = c["total"] or 0
                occupied = c["occupied"] or 0
                h_total = (total / max_total) * 150 if max_total > 0 else 0
                h_occ = (occupied / max_total) * 150 if max_total > 0 else 0

                canvas.create_rectangle(x, 180 - h_total, x + bar_width, 180,
                                        fill=BG_ACCENT, outline="")
                canvas.create_rectangle(x, 180 - h_occ, x + bar_width, 180,
                                        fill=colors[idx % len(colors)], outline="")
                canvas.create_text(x + bar_width // 2, 192,
                                   text=c["city_name"][:6], fill=TEXT_MUTED,
                                   font=("Helvetica", 8))
                canvas.create_text(x + bar_width // 2, 180 - h_occ - 10,
                                   text=str(occupied), fill=TEXT_WHITE,
                                   font=("Helvetica", 9, "bold"))
                x += bar_width + spacing

    def show_financial(self):
        summary = InvoiceDAO.get_financial_summary()
        stats_row = tk.Frame(self.content_frame, bg=BG_DARK)
        stats_row.pack(fill="x", pady=(0, 20))
        stat_card(stats_row, "Coll", "Collected",
                  f"£{summary.get('total_collected', 0):,.0f}", GREEN, 0)
        stat_card(stats_row, "Pend", "Pending",
                  f"£{summary.get('total_pending', 0):,.0f}", GOLD, 1)
        stat_card(stats_row, "Over", "Overdue",
                  f"£{summary.get('total_overdue', 0):,.0f}", RED, 2)
        stat_card(stats_row, "Part", "Partial",
                  f"£{summary.get('total_partial', 0):,.0f}", BLUE, 3)

        body = tk.Frame(self.content_frame, bg=BG_DARK)
        body.pack(fill="both", expand=True)

        table_left = tk.Frame(body, bg=BG_DARK)
        table_left.pack(side="left", fill="both", expand=True, padx=(0, 16))

        cols = [("City", 14), ("Collected", 12), ("Pending", 12), ("Invoices", 8)]
        table_header(table_left, cols)

        by_city = InvoiceDAO.get_financial_by_city()
        for i, c in enumerate(by_city):
            bg = BG_CARD if i % 2 == 0 else BG_DARK
            row = tk.Frame(table_left, bg=bg)
            row.pack(fill="x")
            vals = [c["city_name"], f"£{c['collected']:,.0f}",
                    f"£{c['pending']:,.0f}", c["invoice_count"]]
            widths = [14, 12, 12, 8]
            for val, w in zip(vals, widths):
                tk.Label(row, text=str(val), bg=bg, fg=TEXT_WHITE,
                         font=FONT_BODY, width=w, anchor="w",
                         padx=12, pady=10).pack(side="left")

        chart_right = tk.Frame(body, bg=BG_CARD, padx=20, pady=20)
        chart_right.pack(side="right", fill="y")

        tk.Label(chart_right, text="REVENUE BREAKDOWN",
                 bg=BG_CARD, fg=TEXT_DIM, font=FONT_LABEL).pack(anchor="w", pady=(0, 12))

        canvas = tk.Canvas(chart_right, width=220, height=220,
                           bg=BG_CARD, highlightthickness=0)
        canvas.pack()

        total = max(summary.get("total_collected", 0) +
                    summary.get("total_pending", 0) +
                    summary.get("total_overdue", 0) +
                    summary.get("total_partial", 0), 1)

        slices = [
            (summary.get("total_collected", 0), GREEN, "Collected"),
            (summary.get("total_pending", 0), GOLD, "Pending"),
            (summary.get("total_overdue", 0), RED, "Overdue"),
            (summary.get("total_partial", 0), BLUE, "Partial"),
        ]

        start = 0
        cx, cy, r = 110, 100, 80
        for val, color, label in slices:
            if val <= 0:
                continue
            extent = (val / total) * 360
            canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                              start=start, extent=extent,
                              fill=color, outline=BG_CARD, width=2)
            start += extent

        ly = 200
        for val, color, label in slices:
            if val <= 0:
                continue
            pct = round(val / total * 100, 1)
            canvas.create_rectangle(10, ly, 22, ly + 10, fill=color, outline="")
            canvas.create_text(28, ly + 5, text=f"{label} ({pct}%)",
                               fill=TEXT_MUTED, font=("Helvetica", 8), anchor="w")
            ly += 16

    def show_maintenance(self):
        costs = MaintenanceDAO.get_maintenance_costs()
        stats_row = tk.Frame(self.content_frame, bg=BG_DARK)
        stats_row.pack(fill="x", pady=(0, 20))
        stat_card(stats_row, "Tot", "Total Requests",
                  costs.get("total_requests", 0), BLUE, 0)
        stat_card(stats_row, "Res", "Resolved",
                  costs.get("resolved", 0), GREEN, 1)
        stat_card(stats_row, "Cost", "Total Cost",
                  f"£{costs.get('total_cost', 0):,.0f}", RED, 2)
        stat_card(stats_row, "Avg", "Avg Fix Time",
                  f"{costs.get('avg_time_to_fix', 0):.0f} min", GOLD, 3)

        body = tk.Frame(self.content_frame, bg=BG_DARK)
        body.pack(fill="both", expand=True)

        table_left = tk.Frame(body, bg=BG_DARK)
        table_left.pack(side="left", fill="both", expand=True, padx=(0, 16))

        cols = [("City", 14), ("Requests", 10), ("Total Cost", 12)]
        table_header(table_left, cols)

        by_city = MaintenanceDAO.get_costs_by_city()
        for i, c in enumerate(by_city):
            bg = BG_CARD if i % 2 == 0 else BG_DARK
            row = tk.Frame(table_left, bg=bg)
            row.pack(fill="x")
            vals = [c["city_name"], c["request_count"], f"£{c['total_cost']:,.0f}"]
            widths = [14, 10, 12]
            for val, w in zip(vals, widths):
                tk.Label(row, text=str(val), bg=bg, fg=TEXT_WHITE,
                         font=FONT_BODY, width=w, anchor="w",
                         padx=12, pady=10).pack(side="left")

        chart_right = tk.Frame(body, bg=BG_CARD, padx=20, pady=20)
        chart_right.pack(side="right", fill="y")

        tk.Label(chart_right, text="COSTS BY CITY",
                 bg=BG_CARD, fg=TEXT_DIM, font=FONT_LABEL).pack(anchor="w", pady=(0, 12))

        canvas = tk.Canvas(chart_right, width=280, height=200,
                           bg=BG_CARD, highlightthickness=0)
        canvas.pack()

        if by_city:
            max_cost = max((c["total_cost"] or 1) for c in by_city)
            bar_width = 40
            spacing = 20
            x = 30
            colors = [RED, GOLD, BLUE, GREEN, "#aaaaaa"]

            for idx, c in enumerate(by_city):
                cost = c["total_cost"] or 0
                h = (cost / max_cost) * 150 if max_cost > 0 else 0
                canvas.create_rectangle(x, 180 - h, x + bar_width, 180,
                                        fill=colors[idx % len(colors)], outline="")
                canvas.create_text(x + bar_width // 2, 192,
                                   text=c["city_name"][:6], fill=TEXT_MUTED,
                                   font=("Helvetica", 8))
                if cost > 0:
                    canvas.create_text(x + bar_width // 2, 180 - h - 10,
                                       text=f"£{cost:,.0f}", fill=TEXT_WHITE,
                                       font=("Helvetica", 8, "bold"))
                x += bar_width + spacing
