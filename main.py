# Student ID: 24019989
# Student Name: Abdishakur Hasan
# Component: Component 2 - User Authentication, RBAC & Desktop UI Framework


import tkinter as tk
from database.db_setup import init_db, seed_data
from database.extend_schema import extend_schema
from ui.login_screen import LoginScreen
from ui.main_window import MainWindow

def main():
    init_db()
    seed_data()
    extend_schema()
    root = tk.Tk()
    root.title("PAMS - Paragon Apartment Management System")
    root.geometry("1200x700")
    root.configure(bg="#1a1a2e")

    def on_login_success():
        MainWindow(root)

    LoginScreen(root, on_login_success)
    root.mainloop()

if __name__ == "__main__":
    main()