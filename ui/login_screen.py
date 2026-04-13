# Student ID: 24019989
# Student Name: Abdishakur Hasan
# Component: Component 2 - User Authentication, RBAC & Desktop UI Framework

import tkinter as tk
from auth.auth_manager import attempt_login, load_remember_me, save_remember_me, clear_remember_me

class LoginScreen:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.build()

    def build(self):
        # Outer container - split layout
        self.frame = tk.Frame(self.root, bg="#1a1a2e")
        self.frame.pack(fill="both", expand=True)

        # Left panel - branding
        left = tk.Frame(self.frame, bg="#0f3460", width=480)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        # Center content in left panel
        left_inner = tk.Frame(left, bg="#0f3460")
        left_inner.place(relx=0.5, rely=0.5, anchor="center")

        # Logo circle
        canvas = tk.Canvas(left_inner, width=80, height=80,
                           bg="#0f3460", highlightthickness=0)
        canvas.pack(pady=(0, 24))
        canvas.create_oval(4, 4, 76, 76, fill="#e2b96f", outline="")
        canvas.create_text(40, 40, text="P", fill="#1a1a2e",
                          font=("Georgia", 32, "bold"))

        tk.Label(
            left_inner, text="PARAGON",
            bg="#0f3460", fg="#e2b96f",
            font=("Georgia", 28, "bold")
        ).pack()

        tk.Label(
            left_inner, text="APARTMENT MANAGEMENT",
            bg="#0f3460", fg="#7a9cc4",
            font=("Helvetica", 9)
        ).pack(pady=(4, 0))

        # Divider
        div = tk.Frame(left_inner, bg="#e2b96f", height=2, width=60)
        div.pack(pady=24)

        tk.Label(
            left_inner,
            text="Streamlined operations\nacross all locations.",
            bg="#0f3460", fg="#aaaaaa",
            font=("Helvetica", 11),
            justify="center"
        ).pack()

        # Version tag at bottom
        tk.Label(
            left, text="v1.0  ·  2025-26",
            bg="#0f3460", fg="#444f6b",
            font=("Helvetica", 8)
        ).pack(side="bottom", pady=20)

        # Right panel - login form
        right = tk.Frame(self.frame, bg="#1a1a2e")
        right.pack(side="right", fill="both", expand=True)

        form_outer = tk.Frame(right, bg="#1a1a2e")
        form_outer.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            form_outer, text="Welcome back",
            bg="#1a1a2e", fg="white",
            font=("Georgia", 22, "bold")
        ).pack(anchor="w")

        tk.Label(
            form_outer, text="Sign in to your account to continue",
            bg="#1a1a2e", fg="#555e7a",
            font=("Helvetica", 10)
        ).pack(anchor="w", pady=(4, 32))

        # Username field
        self._field_label(form_outer, "USERNAME")
        self.username_entry = self._field_entry(form_outer)
        self.username_entry.pack(fill="x", pady=(6, 20), ipady=10)

        # Password field
        self._field_label(form_outer, "PASSWORD")
        self.password_entry = self._field_entry(form_outer, show="●")
        self.password_entry.pack(fill="x", pady=(6, 16), ipady=10)

        # Remember me
        self.remember_var = tk.BooleanVar()
        remember_row = tk.Frame(form_outer, bg="#1a1a2e")
        remember_row.pack(fill="x", pady=(0, 24))

        tk.Checkbutton(
            remember_row, text="Remember me",
            variable=self.remember_var,
            bg="#1a1a2e", fg="#7a9cc4",
            selectcolor="#16213e",
            activebackground="#1a1a2e",
            activeforeground="#e2b96f",
            font=("Helvetica", 9),
            cursor="hand2",
            relief="flat", bd=0
        ).pack(side="left")

        # Login button
        tk.Button(
            form_outer, text="SIGN IN  →",
            bg="#e2b96f", fg="#1a1a2e",
            font=("Helvetica", 11, "bold"),
            relief="flat", pady=12,
            cursor="hand2",
            activebackground="#c9a45a",
            activeforeground="#1a1a2e",
            command=self.attempt_login
        ).pack(fill="x")

        # Error label
        self.error_label = tk.Label(
            form_outer, text="",
            bg="#1a1a2e", fg="#e05c5c",
            font=("Helvetica", 9)
        )
        self.error_label.pack(pady=(12, 0), anchor="w")

        # Pre-fill
        saved = load_remember_me()
        if saved:
            self.username_entry.insert(0, saved)
            self.remember_var.set(True)
            self.password_entry.focus()
        else:
            self.username_entry.focus()

        self.root.bind("<Return>", lambda e: self.attempt_login())

    def _field_label(self, parent, text):
        tk.Label(
            parent, text=text,
            bg="#1a1a2e", fg="#555e7a",
            font=("Helvetica", 8, "bold")
        ).pack(anchor="w")

    def _field_entry(self, parent, show=None):
        entry = tk.Entry(
            parent,
            bg="#16213e", fg="white",
            insertbackground="#e2b96f",
            relief="flat", font=("Helvetica", 11),
            bd=12, show=show,
            highlightthickness=1,
            highlightcolor="#e2b96f",
            highlightbackground="#0f3460"
        )
        return entry

    def attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.error_label.config(text="⚠  Please enter your username and password.")
            return

        success, message = attempt_login(username, password)

        if success:
            if self.remember_var.get():
                save_remember_me(username)
            else:
                clear_remember_me()
            self.frame.destroy()
            self.on_login_success()
        else:
            self.error_label.config(text=f"⚠  {message}")
            if "locked" in message:
                self.username_entry.config(state="disabled")
                self.password_entry.config(state="disabled")