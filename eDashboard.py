import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from data import (
    get_employee_by_email,
    draw_rounded_rectangle,
    RoundedBadge
)

class SteadypayEmployeeDashboard(tk.Tk):
    def __init__(self, email="employee@gmail.com"):
        super().__init__()

        self.title("Steadypay - Employee Dashboard")
        self.geometry("1000x650")
        self.minsize(900, 600)
        self.configure(bg="#F8FAF9")

        # Fetch employee profile from centralized data
        self.employee = get_employee_by_email(email)

        # Color Palette Definition (Consistent with Steadypay design system)
        self.colors = {
            "primary_orange": "#FF9F1C",
            "soft_orange": "#FFBF69",
            "white": "#FFFFFF",
            "bg_light": "#F8FAF9",
            "light_mint": "#CBF3F0",
            "dark_teal": "#2EC4B6",
            "deep_teal": "#1B9A8F",
            "gray_text": "#707070",
            "dark_text": "#2C3E50",
            "card_bg": "#FFFFFF",
            "border_color": "#E5E9E8",
            "success_green": "#2ECC71"
        }

        self.create_header()
        self.create_scrollable_main_content()

    def create_header(self):
        # Top Navbar Header (Fixed at top)
        header_frame = tk.Frame(self, bg=self.colors["white"], height=65, highlightbackground=self.colors["border_color"], highlightthickness=1)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        # Left: Logo and Portal Badge
        left_box = tk.Frame(header_frame, bg=self.colors["white"])
        left_box.pack(side="left", padx=25, pady=12)

        logo_icon = tk.Canvas(left_box, width=22, height=22, bg=self.colors["white"], highlightthickness=0)
        logo_icon.pack(side="left", padx=(0, 8))
        logo_icon.create_rectangle(2, 4, 6, 18, fill=self.colors["primary_orange"], outline="")
        logo_icon.create_rectangle(8, 2, 12, 20, fill=self.colors["primary_orange"], outline="")
        logo_icon.create_rectangle(14, 6, 18, 16, fill=self.colors["primary_orange"], outline="")

        logo_label = tk.Label(
            left_box,
            text="steadypay",
            font=("Segoe UI", 15, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        )
        logo_label.pack(side="left")

        badge = RoundedBadge(
            left_box,
            text="EMPLOYEE PORTAL",
            bg_color=self.colors["light_mint"],
            fg_color=self.colors["deep_teal"],
            radius=8,
            width=115,
            height=22,
            parent_bg=self.colors["white"]
        )
        badge.pack(side="left", padx=12)

        # Right: User Profile & Logout Button
        right_box = tk.Frame(header_frame, bg=self.colors["white"])
        right_box.pack(side="right", padx=25, pady=12)

        user_label = tk.Label(
            right_box,
            text=f"👤 {self.employee['email']}",
            font=("Segoe UI", 9),
            fg=self.colors["gray_text"],
            bg=self.colors["white"]
        )
        user_label.pack(side="left", padx=(0, 12))

        logout_btn = tk.Button(
            right_box,
            text="Logout",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["light_mint"],
            fg=self.colors["deep_teal"],
            activebackground=self.colors["soft_orange"],
            activeforeground=self.colors["white"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=3,
            command=self.handle_logout
        )
        logout_btn.pack(side="left")

    def create_scrollable_main_content(self):
        main_container = tk.Frame(self, bg=self.colors["bg_light"])
        main_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(main_container, bg=self.colors["bg_light"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)

        self.content_frame = tk.Frame(self.canvas, bg=self.colors["bg_light"], padx=30, pady=20)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        def _on_canvas_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.canvas.itemconfig(self.canvas_window, width=event.width)

        def _on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.canvas.bind("<Configure>", _on_canvas_configure)
        self.content_frame.bind("<Configure>", _on_frame_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Welcome Section
        welcome_frame = tk.Frame(self.content_frame, bg=self.colors["bg_light"])
        welcome_frame.pack(fill="x", pady=(0, 16))

        welcome_title = tk.Label(
            welcome_frame,
            text=f"Welcome back, {self.employee['name']}!",
            font=("Segoe UI", 18, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["bg_light"]
        )
        welcome_title.pack(anchor="w")

        welcome_sub = tk.Label(
            welcome_frame,
            text=f"{self.employee['role']} · {self.employee['id']} | Here is your personal payroll summary.",
            font=("Segoe UI", 9),
            fg=self.colors["gray_text"],
            bg=self.colors["bg_light"]
        )
        welcome_sub.pack(anchor="w", pady=(2, 0))

        # Metrics Cards Row (4 cards with clean compact padding)
        metrics_frame = tk.Frame(self.content_frame, bg=self.colors["bg_light"])
        metrics_frame.pack(fill="x", pady=(0, 16))

        cards_data = [
            ("💵 Net Pay (Last Period)", f"${self.employee['amount']:,.2f}", f"Payroll Run: {self.employee['payroll_run']}", self.colors["dark_teal"]),
            ("⏱ Hours Logged", f"{self.employee.get('hours_logged', 160.0):.1f} hrs", "Regular: 160h | OT: 0h", self.colors["primary_orange"]),
            ("🌴 Available Leaves", f"{self.employee.get('available_leaves', 12)} Days", "Paid Time Off Balance", self.colors["dark_teal"]),
            ("📅 Next Pay Date", "Sep 30, 2026", "Status: " + self.employee['status'], self.colors["primary_orange"])
        ]

        for i, (title, value, subtext, color) in enumerate(cards_data):
            card = tk.Frame(
                metrics_frame,
                bg=self.colors["card_bg"],
                highlightbackground=self.colors["border_color"],
                highlightthickness=1,
                padx=16,
                pady=12
            )
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 10, 0))
            metrics_frame.columnconfigure(i, weight=1)

            t_lbl = tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg=self.colors["card_bg"])
            t_lbl.pack(anchor="w")

            v_lbl = tk.Label(card, text=value, font=("Segoe UI", 15, "bold"), fg=color, bg=self.colors["card_bg"])
            v_lbl.pack(anchor="w", pady=(2, 2))

            s_lbl = tk.Label(card, text=subtext, font=("Segoe UI", 7), fg=self.colors["gray_text"], bg=self.colors["card_bg"])
            s_lbl.pack(anchor="w")

        # Payslip History Card
        history_card = tk.Frame(
            self.content_frame,
            bg=self.colors["card_bg"],
            highlightbackground=self.colors["border_color"],
            highlightthickness=1,
            padx=18,
            pady=14
        )
        history_card.pack(fill="both", expand=True)

        history_header = tk.Frame(history_card, bg=self.colors["card_bg"])
        history_header.pack(fill="x", pady=(0, 10))

        history_title = tk.Label(
            history_header,
            text="Recent Payslip History",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["dark_text"],
            bg=self.colors["card_bg"]
        )
        history_title.pack(side="left")

        # Table Header
        columns = ("Pay Period", "Gross Earnings", "Deductions", "Net Pay", "Payment Status")
        table_header = tk.Frame(history_card, bg=self.colors["light_mint"])
        table_header.pack(fill="x", ipady=4)

        col_weights = [3, 2, 2, 2, 2]
        for col_idx, (col_name, weight) in enumerate(zip(columns, col_weights)):
            table_header.columnconfigure(col_idx, weight=weight)
            lbl = tk.Label(
                table_header,
                text=col_name,
                font=("Segoe UI", 8, "bold"),
                fg=self.colors["deep_teal"],
                bg=self.colors["light_mint"],
                anchor="w",
                padx=8
            )
            lbl.grid(row=0, column=col_idx, sticky="ew")

        # Pay Records from centralized data
        records = self.employee.get("payslips", [])

        for row_idx, (period, gross, ded, net, status) in enumerate(records):
            bg_row = self.colors["card_bg"] if row_idx % 2 == 0 else "#FAFAFA"
            row_frame = tk.Frame(history_card, bg=bg_row)
            row_frame.pack(fill="x", ipady=6)

            for col_idx, (val, weight) in enumerate(zip((period, gross, ded, net, status), col_weights)):
                row_frame.columnconfigure(col_idx, weight=weight)
                color = self.colors["dark_teal"] if col_idx == 3 else (self.colors["success_green"] if "Paid" in val else self.colors["primary_orange"] if "Pending" in val else self.colors["dark_text"])
                font_weight = "bold" if col_idx in [0, 3] else "normal"
                lbl = tk.Label(
                    row_frame,
                    text=val,
                    font=("Segoe UI", 8, font_weight),
                    fg=color,
                    bg=bg_row,
                    anchor="w",
                    padx=8
                )
                lbl.grid(row=0, column=col_idx, sticky="ew")

    def handle_logout(self):
        self.destroy()
        login_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "login.py")
        if os.path.exists(login_script):
            subprocess.Popen([sys.executable, login_script])

if __name__ == "__main__":
    app = SteadypayEmployeeDashboard()
    app.mainloop()
