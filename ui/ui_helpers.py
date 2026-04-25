import tkinter as tk
from tkinter import ttk

BG_DARK = "#1a1a2e"
BG_CARD = "#16213e"
BG_ACCENT = "#0f3460"
GOLD = "#e2b96f"
GOLD_HOVER = "#c9a45a"
TEXT_WHITE = "white"
TEXT_MUTED = "#555e7a"
TEXT_DIM = "#3a4a6b"
GREEN = "#5cb85c"
RED = "#e05c5c"
BLUE = "#7a9cc4"
FONT_TITLE = ("Georgia", 22, "bold")
FONT_HEADING = ("Georgia", 14, "bold")
FONT_BODY = ("Helvetica", 10)
FONT_SMALL = ("Helvetica", 9)
FONT_LABEL = ("Helvetica", 8, "bold")


def clear_frame(frame):
    for w in frame.winfo_children():
        w.destroy()


def page_header(parent, title, subtitle=""):
    header = tk.Frame(parent, bg=BG_DARK)
    header.pack(fill="x", padx=36, pady=(32, 0))
    tk.Label(header, text=title, bg=BG_DARK, fg=TEXT_WHITE,
             font=FONT_TITLE).pack(side="left", anchor="w")
    if subtitle:
        tk.Label(parent, text=subtitle, bg=BG_DARK, fg=TEXT_MUTED,
                 font=FONT_BODY).pack(anchor="w", padx=36, pady=(4, 0))
    tk.Frame(parent, bg=BG_CARD, height=2).pack(fill="x", padx=36, pady=20)
    return header


def gold_button(parent, text, command, side="right"):
    btn = tk.Button(parent, text=text, bg=GOLD, fg=BG_DARK,
                    font=("Helvetica", 10, "bold"), relief="flat",
                    padx=16, pady=8, cursor="hand2",
                    activebackground=GOLD_HOVER, command=command)
    btn.pack(side=side)
    return btn


def secondary_button(parent, text, command, side="right"):
    btn = tk.Button(parent, text=text, bg=BG_ACCENT, fg=TEXT_WHITE,
                    font=FONT_BODY, relief="flat", padx=12, pady=6,
                    cursor="hand2", activebackground="#1a4a7a",
                    command=command)
    btn.pack(side=side, padx=(0, 8))
    return btn


def danger_button(parent, text, command, side="right"):
    btn = tk.Button(parent, text=text, bg="#2a1a1a", fg=RED,
                    font=FONT_BODY, relief="flat", padx=12, pady=6,
                    cursor="hand2", activebackground="#3a1a1a",
                    command=command)
    btn.pack(side=side, padx=(0, 8))
    return btn


def make_entry(parent, show=None):
    entry = tk.Entry(parent, bg=BG_DARK, fg=TEXT_WHITE,
                     insertbackground=GOLD, relief="flat",
                     font=("Helvetica", 11), bd=10, show=show,
                     highlightthickness=1, highlightcolor=GOLD,
                     highlightbackground=BG_ACCENT)
    return entry


def field_label(parent, text):
    tk.Label(parent, text=text, bg=BG_CARD, fg=TEXT_MUTED,
             font=FONT_LABEL).pack(anchor="w")


def make_dropdown(parent, values, default=None):
    var = tk.StringVar(value=default or values[0] if values else "")
    dd = ttk.Combobox(parent, textvariable=var, values=values,
                      state="readonly", font=FONT_BODY)
    return dd, var


def stat_card(parent, icon, label, value, color, col):
    card = tk.Frame(parent, bg=BG_CARD, padx=20, pady=20)
    card.grid(row=0, column=col, padx=(0, 12), sticky="ew")
    parent.grid_columnconfigure(col, weight=1)

    top = tk.Frame(card, bg=BG_CARD)
    top.pack(fill="x")
    tk.Label(top, text=icon, bg=BG_CARD, font=("Helvetica", 18)).pack(side="left")
    tk.Label(top, text="*", bg=BG_CARD, fg=color,
             font=("Helvetica", 8)).pack(side="right")

    tk.Label(card, text=str(value), bg=BG_CARD, fg=color,
             font=("Georgia", 26, "bold")).pack(anchor="w", pady=(8, 2))
    tk.Label(card, text=label, bg=BG_CARD, fg=TEXT_MUTED,
             font=FONT_SMALL).pack(anchor="w")


def table_header(parent, columns):
    header_row = tk.Frame(parent, bg=BG_ACCENT)
    header_row.pack(fill="x")
    for label, width in columns:
        tk.Label(header_row, text=label, bg=BG_ACCENT, fg=GOLD,
                 font=FONT_LABEL, width=width, anchor="w",
                 padx=12, pady=10).pack(side="left")
    return header_row


def table_row(parent, values, row_index, widths):
    bg = BG_CARD if row_index % 2 == 0 else BG_DARK
    row = tk.Frame(parent, bg=bg)
    row.pack(fill="x")
    for val, width in zip(values, widths):
        tk.Label(row, text=str(val), bg=bg, fg=TEXT_WHITE,
                 font=FONT_BODY, width=width, anchor="w",
                 padx=12, pady=10).pack(side="left")
    return row


def status_badge(parent, text, bg_frame):
    colors = {
        "Active": GREEN, "Inactive": TEXT_MUTED, "Overdue": RED,
        "Expired": TEXT_MUTED, "Terminated": RED,
        "Pending": GOLD, "Paid": GREEN, "Partial": BLUE,
        "Vacant": GREEN, "Occupied": BLUE, "Under Maintenance": GOLD,
        "In Progress": BLUE, "Resolved": GREEN, "Cancelled": TEXT_MUTED,
        "Low": TEXT_MUTED, "Medium": GOLD, "High": "#ff8c00", "Urgent": RED,
    }
    color = colors.get(text, TEXT_MUTED)
    lbl = tk.Label(parent, text=text, bg=bg_frame, fg=color,
                   font=("Helvetica", 9, "bold"))
    return lbl
