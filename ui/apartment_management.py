# Component 3 | Author: Talal Esbaitah (23077550)

import tkinter as tk
from tkinter import messagebox, ttk
from ui.ui_helpers import *
from dao.apartment_dao import ApartmentDAO
from dao.lease_dao import LeaseDAO


class ApartmentManagementScreen:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.filter_city = None
        self.filter_status = None
        self.show_inactive = False
        self.build()

    def build(self):
        clear_frame(self.parent)

        header = page_header(self.parent, "Apartment Management",
                             "Register, manage and track apartment occupancy")
        gold_button(header, "+  Register Apartment", self.open_add_dialog)

        filter_frame = tk.Frame(self.parent, bg=BG_DARK)
        filter_frame.pack(fill="x", padx=36, pady=(0, 16))

        tk.Label(filter_frame, text="Filter:", bg=BG_DARK, fg=TEXT_MUTED,
                 font=FONT_SMALL).pack(side="left", padx=(0, 8))

        cities = ApartmentDAO.get_cities()
        city_names = ["All Cities"] + [c["name"] for c in cities]
        self.city_dd, self.city_var = make_dropdown(filter_frame, city_names, "All Cities")
        self.city_dd.pack(side="left", padx=(0, 8))
        self.city_dd.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        statuses = ["All Status", "Vacant", "Occupied", "Under Maintenance"]
        self.status_dd, self.status_var = make_dropdown(filter_frame, statuses, "All Status")
        self.status_dd.pack(side="left", padx=(0, 8))
        self.status_dd.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        self._inactive_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            filter_frame, text="Show Inactive",
            variable=self._inactive_var,
            bg=BG_DARK, fg=TEXT_MUTED,
            selectcolor=BG_CARD,
            activebackground=BG_DARK,
            activeforeground=GOLD,
            font=FONT_SMALL,
            cursor="hand2",
            relief="flat", bd=0,
            command=self.apply_filters
        ).pack(side="left", padx=(8, 0))

        stats_frame = tk.Frame(self.parent, bg=BG_DARK)
        stats_frame.pack(fill="x", padx=36, pady=(0, 16))
        self.stats_frame = stats_frame
        self.refresh_stats()

        cols = [("ID", 4), ("Name", 12), ("City", 12), ("Type", 10),
                ("Rooms", 6), ("Rent (GBP)", 10), ("Status", 14), ("Actions", 14)]
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

    def refresh_stats(self):
        clear_frame(self.stats_frame)
        stats = ApartmentDAO.get_occupancy_stats()
        stat_card(self.stats_frame, "Total", "Total Apartments",
                  stats["total"], BLUE, 0)
        stat_card(self.stats_frame, "Occ", "Occupied",
                  stats["Occupied"], GREEN, 1)
        stat_card(self.stats_frame, "Vac", "Vacant",
                  stats["Vacant"], GOLD, 2)
        stat_card(self.stats_frame, "%", "Occupancy Rate",
                  f"{stats['occupancy_rate']}%", BLUE, 3)

    def apply_filters(self):
        city_name = self.city_var.get()
        status_name = self.status_var.get()

        self.filter_city = None
        if city_name != "All Cities":
            cities = ApartmentDAO.get_cities()
            for c in cities:
                if c["name"] == city_name:
                    self.filter_city = c["city_id"]
                    break

        self.filter_status = None if status_name == "All Status" else status_name
        self.show_inactive = self._inactive_var.get()
        self.refresh_table()

    def refresh_table(self):
        clear_frame(self.rows_frame)

        apartments = ApartmentDAO.filter_apartments(
            city_id=self.filter_city, status=self.filter_status,
            show_inactive=self.show_inactive)
        widths = [4, 12, 12, 10, 6, 10]

        if not apartments:
            tk.Label(self.rows_frame, text="No apartments found.",
                     bg=BG_DARK, fg=TEXT_MUTED, font=FONT_BODY).pack(pady=40)
            return

        for i, apt in enumerate(apartments):
            is_active = apt.get("is_active", 1)
            if is_active:
                bg = BG_CARD if i % 2 == 0 else BG_DARK
                text_fg = TEXT_WHITE
            else:
                bg = "#131325" if i % 2 == 0 else "#111120"
                text_fg = TEXT_DIM

            row = tk.Frame(self.rows_frame, bg=bg)
            row.pack(fill="x")

            values = [apt["apartment_id"], apt["apartment_name"],
                      apt["city_name"], apt["type"],
                      apt["number_of_rooms"], f"£{apt['rent_amount']:,.2f}"]
            for val, w in zip(values, widths):
                tk.Label(row, text=str(val), bg=bg, fg=text_fg,
                         font=FONT_BODY, width=w, anchor="w",
                         padx=12, pady=10).pack(side="left")

            if is_active:
                badge = status_badge(row, apt["status"], bg)
            else:
                badge = tk.Label(row, text="Inactive", bg=bg, fg=TEXT_DIM,
                                 font=("Helvetica", 9, "bold"))
            badge.config(width=14, anchor="w", padx=12, pady=10)
            badge.pack(side="left")

            actions = tk.Frame(row, bg=bg)
            actions.pack(side="left", padx=8)

            if is_active:
                tk.Button(actions, text="Edit", bg=BG_ACCENT, fg=TEXT_WHITE,
                          relief="flat", padx=10, pady=4, cursor="hand2",
                          font=FONT_SMALL,
                          command=lambda a=apt["apartment_id"]: self.open_edit_dialog(a)
                          ).pack(side="left", padx=(0, 4))

                tk.Button(actions, text="History", bg=BG_CARD if bg == BG_DARK else BG_DARK,
                          fg=BLUE, relief="flat", padx=10, pady=4,
                          cursor="hand2", font=FONT_SMALL,
                          command=lambda a=apt["apartment_id"]: self.show_history(a)
                          ).pack(side="left", padx=(0, 4))

                tk.Button(actions, text="Deactivate", bg="#2a1a1a", fg=RED,
                          relief="flat", padx=10, pady=4, cursor="hand2",
                          font=FONT_SMALL,
                          command=lambda a=apt["apartment_id"]: self.deactivate(a)
                          ).pack(side="left")
            else:
                tk.Button(actions, text="Reactivate", bg="#1a2a1a", fg=GREEN,
                          relief="flat", padx=10, pady=4, cursor="hand2",
                          font=FONT_SMALL,
                          command=lambda a=apt["apartment_id"]: self.reactivate(a)
                          ).pack(side="left")

    def open_add_dialog(self):
        self._open_dialog(mode="add")

    def open_edit_dialog(self, apartment_id):
        apt = ApartmentDAO.get_apartment(apartment_id)
        if apt:
            self._open_dialog(mode="edit", apartment=apt)

    def _open_dialog(self, mode="add", apartment=None):
        dialog = tk.Toplevel()
        dialog.title("Register Apartment" if mode == "add" else "Edit Apartment")
        dialog.geometry("460x540")
        dialog.configure(bg=BG_CARD)
        dialog.grab_set()
        dialog.resizable(False, False)

        dh = tk.Frame(dialog, bg=BG_ACCENT, padx=24, pady=16)
        dh.pack(fill="x")
        tk.Label(dh, text="+  Register Apartment" if mode == "add" else "Edit Apartment",
                 bg=BG_ACCENT, fg=TEXT_WHITE, font=FONT_HEADING).pack(anchor="w")

        form = tk.Frame(dialog, bg=BG_CARD, padx=28, pady=20)
        form.pack(fill="both", expand=True)

        field_label(form, "CITY")
        cities = ApartmentDAO.get_cities()
        city_names = [c["name"] for c in cities]
        city_dd, city_var = make_dropdown(form, city_names,
            apartment["city_name"] if apartment else None)
        city_dd.pack(fill="x", pady=(4, 14))

        field_label(form, "APARTMENT NAME")
        name_e = make_entry(form)
        name_e.pack(fill="x", pady=(4, 14), ipady=6)
        if apartment:
            name_e.insert(0, apartment["apartment_name"])

        field_label(form, "TYPE")
        types = ["Studio", "1 Bedroom", "2 Bedroom", "3 Bedroom", "4 Bedroom"]
        type_dd, type_var = make_dropdown(form, types,
            apartment["type"] if apartment else None)
        type_dd.pack(fill="x", pady=(4, 14))

        field_label(form, "MONTHLY RENT (GBP)")
        rent_e = make_entry(form)
        rent_e.pack(fill="x", pady=(4, 14), ipady=6)
        if apartment:
            rent_e.insert(0, str(apartment["rent_amount"]))

        field_label(form, "NUMBER OF ROOMS")
        rooms_e = make_entry(form)
        rooms_e.pack(fill="x", pady=(4, 14), ipady=6)
        if apartment:
            rooms_e.insert(0, str(apartment["number_of_rooms"]))

        if mode == "edit":
            field_label(form, "STATUS")
            statuses = ["Vacant", "Occupied", "Under Maintenance"]
            stat_dd, stat_var = make_dropdown(form, statuses, apartment["status"])
            stat_dd.pack(fill="x", pady=(4, 14))

        err = tk.Label(form, text="", bg=BG_CARD, fg=RED, font=FONT_SMALL)
        err.pack(anchor="w")

        def save():
            city_name = city_var.get()
            city_id = None
            for c in cities:
                if c["name"] == city_name:
                    city_id = c["city_id"]
                    break

            name = name_e.get().strip()
            apt_type = type_var.get()
            try:
                rent = float(rent_e.get().strip())
                rooms = int(rooms_e.get().strip())
            except ValueError:
                err.config(text="Rent and rooms must be valid numbers.")
                return

            if not name or not city_id:
                err.config(text="Please fill in all fields.")
                return

            if mode == "add":
                ApartmentDAO.add_apartment(city_id, name, apt_type, rent, rooms)
                dialog.destroy()
                messagebox.showinfo("Success", "Apartment registered.")
                self.refresh_stats()
                self.refresh_table()
            else:
                kwargs = {"apartment_name": name, "type": apt_type,
                          "rent_amount": rent, "number_of_rooms": rooms,
                          "city_id": city_id, "status": stat_var.get()}
                ApartmentDAO.update_apartment(apartment["apartment_id"], **kwargs)
                dialog.destroy()
                messagebox.showinfo("Success", "Apartment updated.")
                self.refresh_stats()
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

    def deactivate(self, apartment_id):
        if messagebox.askyesno("Confirm", "Deactivate this apartment?\nIt will be hidden from normal views."):
            ApartmentDAO.deactivate_apartment(apartment_id)
            self.refresh_stats()
            self.refresh_table()

    def reactivate(self, apartment_id):
        ApartmentDAO.reactivate_apartment(apartment_id)
        self.refresh_stats()
        self.refresh_table()

    def show_history(self, apartment_id):
        apt = ApartmentDAO.get_apartment(apartment_id)
        history = ApartmentDAO.get_apartment_history(apartment_id)

        win = tk.Toplevel()
        win.title(f"History - {apt['apartment_name']}")
        win.geometry("500x400")
        win.configure(bg=BG_CARD)
        win.grab_set()

        dh = tk.Frame(win, bg=BG_ACCENT, padx=24, pady=16)
        dh.pack(fill="x")
        tk.Label(dh, text=f"{apt['apartment_name']} - {apt['city_name']}",
                 bg=BG_ACCENT, fg=TEXT_WHITE, font=FONT_HEADING).pack(anchor="w")

        body = tk.Frame(win, bg=BG_CARD, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        if not history:
            tk.Label(body, text="No lease history for this apartment.",
                     bg=BG_CARD, fg=TEXT_MUTED, font=FONT_BODY).pack(pady=40)
            return

        for i, h in enumerate(history):
            bg = BG_DARK if i % 2 == 0 else BG_CARD
            row = tk.Frame(body, bg=bg, padx=16, pady=10)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=h["tenant_name"], bg=bg, fg=TEXT_WHITE,
                     font=("Helvetica", 10, "bold")).pack(anchor="w")
            tk.Label(row, text=f"{h['start_date']} to {h['end_date']}  |  {h['status']}  |  £{h['monthly_rent']:,.2f}/mo",
                     bg=bg, fg=TEXT_MUTED, font=FONT_SMALL).pack(anchor="w")
