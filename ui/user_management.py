# Student ID: 24019989
# Student Name: Abdishakur Hasan
# Component: Component 2 - User Authentication, RBAC & Desktop UI Framework


import tkinter as tk
from tkinter import messagebox, ttk
import bcrypt
from auth.auth_manager import MOCK_USERS

ROLES  = ["Front-Desk Staff", "Finance Manager", "Maintenance Staff", "Administrator", "Manager"]
CITIES = ["Bristol", "Cardiff", "London", "Manchester", "All"]

class UserManagementScreen:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.selected_index = None
        self.build()

    def build(self):
        for w in self.parent_frame.winfo_children():
            w.destroy()

        # Page header
        header = tk.Frame(self.parent_frame, bg="#1a1a2e")
        header.pack(fill="x", padx=36, pady=(32, 0))

        tk.Label(
            header, text="User Management",
            bg="#1a1a2e", fg="white",
            font=("Georgia", 22, "bold")
        ).pack(side="left", anchor="w")

        tk.Button(
            header, text="＋  Add New User",
            bg="#e2b96f", fg="#1a1a2e",
            font=("Helvetica", 10, "bold"),
            relief="flat", padx=16, pady=8,
            cursor="hand2",
            activebackground="#c9a45a",
            command=self.open_add_dialog
        ).pack(side="right")

        tk.Label(
            self.parent_frame,
            text="Manage staff accounts, roles and location access",
            bg="#1a1a2e", fg="#555e7a",
            font=("Helvetica", 10)
        ).pack(anchor="w", padx=36, pady=(4, 0))

        tk.Frame(self.parent_frame, bg="#16213e", height=2).pack(
            fill="x", padx=36, pady=20
        )

        # Table
        table_wrap = tk.Frame(self.parent_frame, bg="#1a1a2e")
        table_wrap.pack(fill="both", expand=True, padx=36)

        # Header row
        col_defs = [("ID", 6), ("Username", 18), ("Role", 22), ("City", 14), ("Actions", 16)]
        header_row = tk.Frame(table_wrap, bg="#0f3460")
        header_row.pack(fill="x")

        for label, width in col_defs:
            tk.Label(
                header_row, text=label,
                bg="#0f3460", fg="#e2b96f",
                font=("Helvetica", 9, "bold"),
                width=width, anchor="w",
                padx=12, pady=10
            ).pack(side="left")

        self.rows_frame = tk.Frame(table_wrap, bg="#1a1a2e")
        self.rows_frame.pack(fill="both", expand=True)
        self.refresh_table()

    def refresh_table(self):
        for w in self.rows_frame.winfo_children():
            w.destroy()

        for i, user in enumerate(MOCK_USERS):
            bg = "#16213e" if i % 2 == 0 else "#1a1a2e"
            row = tk.Frame(self.rows_frame, bg=bg)
            row.pack(fill="x")

            for val, width in [
                (user["user_id"], 6),
                (user["username"], 18),
                (user["role"], 22),
                (user["city"], 14)
            ]:
                tk.Label(
                    row, text=str(val),
                    bg=bg, fg="white",
                    font=("Helvetica", 10),
                    width=width, anchor="w",
                    padx=12, pady=10
                ).pack(side="left")

            # Role badge color
            role_colors = {
                "Manager": "#e2b96f",
                "Administrator": "#7a9cc4",
                "Finance Manager": "#5cb85c",
                "Front-Desk Staff": "#aaaaaa",
                "Maintenance Staff": "#e05c5c"
            }

            actions = tk.Frame(row, bg=bg)
            actions.pack(side="left", padx=8)

            tk.Button(
                actions, text="Edit",
                bg="#0f3460", fg="white",
                relief="flat", padx=12, pady=4,
                cursor="hand2", font=("Helvetica", 9),
                activebackground="#1a4a7a",
                command=lambda idx=i: self.open_edit_dialog(idx)
            ).pack(side="left", padx=(0, 6))

            tk.Button(
                actions, text="Delete",
                bg="#2a1a1a", fg="#e05c5c",
                relief="flat", padx=12, pady=4,
                cursor="hand2", font=("Helvetica", 9),
                activebackground="#3a1a1a",
                command=lambda idx=i: self.delete_user(idx)
            ).pack(side="left")

    def open_add_dialog(self):
        self._open_dialog(mode="add")

    def open_edit_dialog(self, index):
        self.selected_index = index
        self._open_dialog(mode="edit", user=MOCK_USERS[index])

    def _open_dialog(self, mode="add", user=None):
        dialog = tk.Toplevel()
        dialog.title("Add User" if mode == "add" else "Edit User")
        dialog.geometry("440x520")
        dialog.configure(bg="#16213e")
        dialog.grab_set()
        dialog.resizable(False, False)

        # Header
        dheader = tk.Frame(dialog, bg="#0f3460", padx=24, pady=16)
        dheader.pack(fill="x")
        tk.Label(
            dheader,
            text="＋  Add New User" if mode == "add" else "✎  Edit User",
            bg="#0f3460", fg="white",
            font=("Georgia", 14, "bold")
        ).pack(anchor="w")

        form = tk.Frame(dialog, bg="#16213e", padx=28, pady=24)
        form.pack(fill="both", expand=True)

        def field(label_text, show=None):
            tk.Label(form, text=label_text, bg="#16213e",
                    fg="#555e7a", font=("Helvetica", 8, "bold")).pack(anchor="w")
            e = tk.Entry(form, bg="#1a1a2e", fg="white",
                        insertbackground="#e2b96f",
                        relief="flat", font=("Helvetica", 11),
                        bd=10, show=show,
                        highlightthickness=1,
                        highlightcolor="#e2b96f",
                        highlightbackground="#0f3460")
            e.pack(fill="x", pady=(4, 16), ipady=6)
            return e

        username_e = field("USERNAME")
        password_e = field("PASSWORD", show="●")

        if mode == "edit":
            tk.Label(form, text="Leave password blank to keep current",
                    bg="#16213e", fg="#3a4a6b",
                    font=("Helvetica", 8)).pack(anchor="w", pady=(0, 12))

        tk.Label(form, text="ROLE", bg="#16213e", fg="#555e7a",
                font=("Helvetica", 8, "bold")).pack(anchor="w")
        role_var = tk.StringVar(value=user["role"] if user else ROLES[0])
        role_dd = ttk.Combobox(form, textvariable=role_var,
                               values=ROLES, state="readonly",
                               font=("Helvetica", 10))
        role_dd.pack(fill="x", pady=(4, 16))

        tk.Label(form, text="CITY", bg="#16213e", fg="#555e7a",
                font=("Helvetica", 8, "bold")).pack(anchor="w")
        city_var = tk.StringVar(value=user["city"] if user else CITIES[0])
        city_dd = ttk.Combobox(form, textvariable=city_var,
                               values=CITIES, state="readonly",
                               font=("Helvetica", 10))
        city_dd.pack(fill="x", pady=(4, 16))

        if user:
            username_e.insert(0, user["username"])

        err = tk.Label(form, text="", bg="#16213e", fg="#e05c5c",
                      font=("Helvetica", 9))
        err.pack(anchor="w")

        def save():
            username = username_e.get().strip()
            password = password_e.get().strip()
            role = role_var.get()
            city = city_var.get()

            if not username:
                err.config(text="⚠  Username cannot be empty.")
                return

            if mode == "add":
                if not password:
                    err.config(text="⚠  Password cannot be empty.")
                    return
                if (len(password) < 8 or
                        not any(c.isupper() for c in password) or
                        not any(c.islower() for c in password) or
                        not any(c.isdigit() for c in password)):
                    err.config(text="⚠  8+ chars, uppercase, lowercase & number required.")
                    return
                new_id = max(u["user_id"] for u in MOCK_USERS) + 1
                MOCK_USERS.append({
                    "user_id": new_id,
                    "username": username,
                    "password": bcrypt.hashpw(password.encode(), bcrypt.gensalt()),
                    "role": role,
                    "city": city
                })
            else:
                MOCK_USERS[self.selected_index]["username"] = username
                MOCK_USERS[self.selected_index]["role"] = role
                MOCK_USERS[self.selected_index]["city"] = city
                if password:
                    MOCK_USERS[self.selected_index]["password"] = \
                        bcrypt.hashpw(password.encode(), bcrypt.gensalt())

            self.refresh_table()
            dialog.destroy()
            messagebox.showinfo("Success",
                f"User {'created' if mode == 'add' else 'updated'} successfully.")

        btn_row = tk.Frame(form, bg="#16213e")
        btn_row.pack(fill="x", pady=(8, 0))

        tk.Button(
            btn_row, text="Cancel",
            bg="#1a1a2e", fg="#aaaaaa",
            relief="flat", padx=16, pady=8,
            cursor="hand2", font=("Helvetica", 10),
            command=dialog.destroy
        ).pack(side="right", padx=(8, 0))

        tk.Button(
            btn_row, text="Save Changes" if mode == "edit" else "Create User",
            bg="#e2b96f", fg="#1a1a2e",
            relief="flat", padx=16, pady=8,
            cursor="hand2", font=("Helvetica", 10, "bold"),
            activebackground="#c9a45a",
            command=save
        ).pack(side="right")

    def delete_user(self, index):
        user = MOCK_USERS[index]
        if messagebox.askyesno("Confirm Delete",
                f"Delete user '{user['username']}'?\nThis cannot be undone."):
            MOCK_USERS.pop(index)
            self.refresh_table()
            messagebox.showinfo("Deleted", "User removed successfully.")