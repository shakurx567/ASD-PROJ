# Student ID: 24019989
# Student Name: Abdishakur Hasan
# Component: Component 2 - User Authentication, RBAC & Desktop UI Framework


import tkinter as tk
from tkinter import messagebox
from auth.auth_manager import CITIES

class AddCityScreen:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.build()

    def build(self):
        for w in self.parent_frame.winfo_children():
            w.destroy()

        # Header
        header = tk.Frame(self.parent_frame, bg="#1a1a2e")
        header.pack(fill="x", padx=36, pady=(32, 0))

        tk.Label(
            header, text="Add New City",
            bg="#1a1a2e", fg="white",
            font=("Georgia", 22, "bold")
        ).pack(anchor="w")

        tk.Label(
            self.parent_frame,
            text="Expand Paragon operations to a new location",
            bg="#1a1a2e", fg="#555e7a",
            font=("Helvetica", 10)
        ).pack(anchor="w", padx=36, pady=(4, 0))

        tk.Frame(self.parent_frame, bg="#16213e", height=2).pack(
            fill="x", padx=36, pady=20
        )

        # Two column layout
        body = tk.Frame(self.parent_frame, bg="#1a1a2e")
        body.pack(fill="both", expand=True, padx=36)

        # Left - current cities
        left = tk.Frame(body, bg="#16213e", padx=24, pady=24, width=280)
        left.pack(side="left", fill="y", padx=(0, 16))
        left.pack_propagate(False)

        tk.Label(
            left, text="CURRENT LOCATIONS",
            bg="#16213e", fg="#3a4a6b",
            font=("Helvetica", 8, "bold")
        ).pack(anchor="w", pady=(0, 12))

        self.cities_frame = tk.Frame(left, bg="#16213e")
        self.cities_frame.pack(fill="x", anchor="w")
        self.render_cities()

        # Right - add form
        right = tk.Frame(body, bg="#16213e", padx=28, pady=24)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(
            right, text="NEW CITY",
            bg="#16213e", fg="#3a4a6b",
            font=("Helvetica", 8, "bold")
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(
            right, text="CITY NAME",
            bg="#16213e", fg="#555e7a",
            font=("Helvetica", 8, "bold")
        ).pack(anchor="w")

        self.city_entry = tk.Entry(
            right, bg="#1a1a2e", fg="white",
            insertbackground="#e2b96f",
            relief="flat", font=("Helvetica", 11),
            bd=10,
            highlightthickness=1,
            highlightcolor="#e2b96f",
            highlightbackground="#0f3460"
        )
        self.city_entry.pack(fill="x", pady=(4, 20), ipady=8)

        self.error_label = tk.Label(
            right, text="",
            bg="#16213e", fg="#e05c5c",
            font=("Helvetica", 9)
        )
        self.error_label.pack(anchor="w", pady=(0, 12))

        tk.Button(
            right, text="＋  Add City",
            bg="#e2b96f", fg="#1a1a2e",
            font=("Helvetica", 10, "bold"),
            relief="flat", padx=20, pady=10,
            cursor="hand2",
            activebackground="#c9a45a",
            command=self.add_city
        ).pack(anchor="w")

    def render_cities(self):
        for w in self.cities_frame.winfo_children():
            w.destroy()

        display = [c for c in CITIES if c != "All"]
        for city in display:
            row = tk.Frame(self.cities_frame, bg="#1a2a4a")
            row.pack(fill="x", pady=3)
            tk.Label(
                row, text=f"📍  {city}",
                bg="#1a2a4a", fg="white",
                font=("Helvetica", 10),
                padx=12, pady=8, anchor="w"
            ).pack(fill="x")

    def add_city(self):
        name = self.city_entry.get().strip()

        if not name:
            self.error_label.config(text="⚠  City name cannot be empty.")
            return
        if len(name) < 2:
            self.error_label.config(text="⚠  City name must be at least 2 characters.")
            return
        if name in CITIES:
            self.error_label.config(text=f"⚠  '{name}' already exists.")
            return

        CITIES.insert(-1, name)
        self.city_entry.delete(0, tk.END)
        self.error_label.config(text="")
        self.render_cities()
        messagebox.showinfo("City Added", f"'{name}' has been added to Paragon locations.")