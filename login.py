import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
from data import authenticate_user, RoundedBadge, RoundedButton

class SteadypayLoginPage(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Steadypay")
        self.geometry("1000x650")
        self.resizable(False, False)

        # Color Palette Definition
        self.colors = {
            "primary_orange": "#FF9F1C",  # Main CTA Buttons, Accent Labels
            "soft_orange": "#FFBF69",     # Circle Background, Borders
            "white": "#FFFFFF",           # Right Panel & Card Fill
            "light_mint": "#CBF3F0",       # Left Panel Background
            "dark_teal": "#2EC4B6",        # Text Headlines & Primary Mint Accents
            "gray_text": "#707070",        # Subtitles and Footer text
            "border_color": "#FFBF69"     # Entry box borders
        }

        # Configure root window background
        self.configure(bg=self.colors["white"])

        # Grid configuration for 50/50 split
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.create_left_panel()
        self.create_right_panel()

    def create_left_panel(self):
        # Left container frame
        left_frame = tk.Frame(self, bg=self.colors["light_mint"])
        left_frame.grid(row=0, column=0, sticky="nsew")

        # Top Logo Area
        logo_frame = tk.Frame(left_frame, bg=self.colors["light_mint"])
        logo_frame.pack(anchor="nw", padx=40, pady=30)

        # Logo icon representation
        logo_icon = tk.Canvas(logo_frame, width=24, height=24, bg=self.colors["light_mint"], highlightthickness=0)
        logo_icon.pack(side="left", padx=(0, 8))
        logo_icon.create_rectangle(2, 4, 6, 20, fill=self.colors["primary_orange"], outline="")
        logo_icon.create_rectangle(9, 2, 13, 22, fill=self.colors["primary_orange"], outline="")
        logo_icon.create_rectangle(16, 6, 20, 18, fill=self.colors["primary_orange"], outline="")

        logo_label = tk.Label(
            logo_frame,
            text="steadypay",
            font=("Segoe UI", 16, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["light_mint"]
        )
        logo_label.pack(side="left")

        # Main Headline Section
        content_frame = tk.Frame(left_frame, bg=self.colors["light_mint"])
        content_frame.pack(fill="x", padx=40, pady=(10, 0))

        sub_header = tk.Label(
            content_frame,
            text="PAYROLL, IN GOOD HANDS",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["primary_orange"],
            bg=self.colors["light_mint"]
        )
        sub_header.pack(anchor="w")

        main_title = tk.Label(
            content_frame,
            text="A little less admin.\nA lot more peace of mind.",
            font=("Segoe UI", 22, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["light_mint"],
            justify="left"
        )
        main_title.pack(anchor="w", pady=(8, 12))

        description = tk.Label(
            content_frame,
            text="One secure place for your people, your payroll, and every\npayday in between.",
            font=("Segoe UI", 9),
            fg=self.colors["gray_text"],
            bg=self.colors["light_mint"],
            justify="left"
        )
        description.pack(anchor="w")

        # Graphic Section with Circle Accent and Card Overlay
        graphic_canvas = tk.Canvas(left_frame, width=380, height=260, bg=self.colors["light_mint"], highlightthickness=0)
        graphic_canvas.pack(pady=20)

        # Orange Decorative Circle Behind Card
        graphic_canvas.create_oval(60, 20, 300, 260, fill=self.colors["soft_orange"], outline="")

        # Payroll Card Widget Container (compact & softened)
        card = tk.Frame(
            graphic_canvas,
            bg=self.colors["white"],
            highlightbackground="#E0E0E0",
            highlightthickness=1,
            padx=14,
            pady=12
        )
        graphic_canvas.create_window(180, 140, window=card, width=310, height=190)

        # Card Content: Header & Status Tag
        card_header = tk.Frame(card, bg=self.colors["white"])
        card_header.pack(fill="x", pady=(0, 4))

        card_title = tk.Label(card_header, text="Monthly payroll", font=("Segoe UI", 10, "bold"), bg=self.colors["white"], fg="#333333")
        card_title.pack(side="left")

        status_tag = RoundedBadge(
            card_header,
            text="✓ Approved",
            bg_color=self.colors["light_mint"],
            fg_color=self.colors["dark_teal"],
            radius=8,
            width=80,
            height=22,
            parent_bg=self.colors["white"]
        )
        status_tag.pack(side="right")

        # Card Content: Main Value
        amount_label = tk.Label(card, text="$84,250.00", font=("Segoe UI", 20, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"])
        amount_label.pack(anchor="w", pady=(4, 0))

        sub_amount = tk.Label(card, text="Total payroll · September 2026", font=("Segoe UI", 8), fg=self.colors["gray_text"], bg=self.colors["white"])
        sub_amount.pack(anchor="w")

        # Divider
        divider = tk.Frame(card, height=1, bg="#EAEAEA")
        divider.pack(fill="x", pady=8)

        # Details Rows
        emp_row = tk.Frame(card, bg=self.colors["white"])
        emp_row.pack(fill="x", pady=2)
        tk.Label(emp_row, text="👥  Employees", font=("Segoe UI", 8), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(side="left")
        tk.Label(emp_row, text="28 people", font=("Segoe UI", 8, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(side="right")

        pay_row = tk.Frame(card, bg=self.colors["white"])
        pay_row.pack(fill="x", pady=2)
        tk.Label(pay_row, text="📅  Payday", font=("Segoe UI", 8), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(side="left")
        tk.Label(pay_row, text="September 30, 2026", font=("Segoe UI", 8, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(side="right")

        # Footer Badge
        left_footer = tk.Label(
            left_frame,
            text="🛡  Built for the work that matters. Protected at every step.",
            font=("Segoe UI", 8),
            fg=self.colors["dark_teal"],
            bg=self.colors["light_mint"]
        )
        left_footer.pack(side="bottom", anchor="w", padx=40, pady=20)

    def create_right_panel(self):
        # Right container frame
        right_frame = tk.Frame(self, bg=self.colors["white"])
        right_frame.grid(row=0, column=1, sticky="nsew")

        # Top Navigation Link
        top_link = tk.Label(
            right_frame,
            text="Need a hand? Contact support ↗",
            font=("Segoe UI", 8),
            fg=self.colors["primary_orange"],
            bg=self.colors["white"],
            cursor="hand2"
        )
        top_link.pack(anchor="ne", padx=40, pady=20)

        # Form Container Frame
        form_frame = tk.Frame(right_frame, bg=self.colors["white"])
        form_frame.pack(expand=True, padx=60)

        # Form Headers
        welcome_title = tk.Label(
            form_frame,
            text="Welcome back",
            font=("Segoe UI", 22, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        )
        welcome_title.pack(anchor="w")

        welcome_sub = tk.Label(
            form_frame,
            text="Log in to your Steadypay workspace.",
            font=("Segoe UI", 9),
            fg=self.colors["gray_text"],
            bg=self.colors["white"]
        )
        welcome_sub.pack(anchor="w", pady=(4, 25))

        # Email Input Field
        email_label = tk.Label(form_frame, text="Work email", font=("Segoe UI", 8, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"])
        email_label.pack(anchor="w", pady=(0, 4))

        # Compact bordered container for email
        email_entry_frame = tk.Frame(
            form_frame,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_color"],
            highlightcolor=self.colors["primary_orange"],
            highlightthickness=1
        )
        email_entry_frame.pack(fill="x", pady=(0, 15))

        self.email_entry = tk.Entry(
            email_entry_frame,
            font=("Segoe UI", 10),
            bg=self.colors["white"],
            fg="#333333",
            bd=0,
            relief="flat"
        )
        self.email_entry.insert(0, " you@company.com")
        self.email_entry.pack(fill="x", ipady=6, padx=10)

        # Password Input Field
        password_label = tk.Label(form_frame, text="Password", font=("Segoe UI", 8, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"])
        password_label.pack(anchor="w", pady=(0, 4))

        # Compact bordered container for password
        pwd_entry_frame = tk.Frame(
            form_frame,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_color"],
            highlightcolor=self.colors["primary_orange"],
            highlightthickness=1
        )
        pwd_entry_frame.pack(fill="x", pady=(0, 10))

        self.password_entry = tk.Entry(
            pwd_entry_frame,
            font=("Segoe UI", 10),
            bg=self.colors["white"],
            fg="#333333",
            bd=0,
            relief="flat",
            show="•"
        )
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(10, 0))

        # Visibility Toggle (Eye Icon)
        self.password_visible = False
        self.eye_btn = tk.Label(
            pwd_entry_frame,
            text="👁",
            font=("Segoe UI", 10),
            bg=self.colors["white"],
            fg=self.colors["gray_text"],
            cursor="hand2"
        )
        self.eye_btn.pack(side="right", padx=10)
        self.eye_btn.bind("<Button-1>", self.toggle_password_visibility)

        # Options Row (Remember Me / Forgot Password)
        opts_frame = tk.Frame(form_frame, bg=self.colors["white"])
        opts_frame.pack(fill="x", pady=(0, 20))

        remember_check = tk.Checkbutton(
            opts_frame,
            text=" Remember me",
            font=("Segoe UI", 8),
            fg=self.colors["gray_text"],
            bg=self.colors["white"],
            activebackground=self.colors["white"],
            bd=0,
            highlightthickness=0
        )
        remember_check.pack(side="left")

        forgot_link = tk.Label(
            opts_frame,
            text="Forgot password?",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["primary_orange"],
            bg=self.colors["white"],
            cursor="hand2"
        )
        forgot_link.pack(side="right")

        self.email_entry.bind("<Return>", self.handle_login)
        self.password_entry.bind("<Return>", self.handle_login)

        # Action Button (Log in)
        login_btn = tk.Button(
            form_frame,
            text="Log in  →",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["primary_orange"],
            fg=self.colors["white"],
            activebackground=self.colors["soft_orange"],
            activeforeground=self.colors["white"],
            bd=0,
            relief="flat",
            cursor="hand2",
            pady=8,
            command=self.handle_login
        )
        login_btn.pack(fill="x", pady=(0, 15))

        # Security Note
        sec_note = tk.Label(
            form_frame,
            text="🔒 Your connection is secure and encrypted.",
            font=("Segoe UI", 8),
            fg=self.colors["gray_text"],
            bg=self.colors["white"]
        )
        sec_note.pack()

        # Separator Line
        sep = tk.Frame(form_frame, height=1, bg="#EAEAEA")
        sep.pack(fill="x", pady=20)

        # Invitation Link
        invite_label = tk.Label(
            form_frame,
            text="First time here? Check your invitation email",
            font=("Segoe UI", 8),
            fg=self.colors["primary_orange"],
            bg=self.colors["white"],
            cursor="hand2"
        )
        invite_label.pack()

        # Footer Area
        right_footer = tk.Frame(right_frame, bg=self.colors["white"])
        right_footer.pack(side="bottom", fill="x", padx=40, pady=20)

        copy_text = tk.Label(right_footer, text="© 2026 Steadypay", font=("Segoe UI", 8), fg=self.colors["gray_text"], bg=self.colors["white"])
        copy_text.pack(side="left")

        terms_text = tk.Label(right_footer, text="Privacy   Terms", font=("Segoe UI", 8), fg=self.colors["gray_text"], bg=self.colors["white"])
        terms_text.pack(side="right")

    def toggle_password_visibility(self, event=None):
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.password_entry.config(show="")
            self.eye_btn.config(fg=self.colors["primary_orange"])
        else:
            self.password_entry.config(show="•")
            self.eye_btn.config(fg=self.colors["gray_text"])

    def handle_login(self, event=None):
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        is_valid, target_script_name, _ = authenticate_user(email, password)

        if is_valid and target_script_name:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            target_script = os.path.join(current_dir, target_script_name)
            self.redirect_to(target_script)
        else:
            messagebox.showerror("Login Failed", "Invalid email or password. Please try again.")

    def redirect_to(self, script_path):
        self.destroy()
        if os.path.exists(script_path):
            subprocess.Popen([sys.executable, script_path])
        else:
            messagebox.showerror("Error", f"Dashboard file not found: {os.path.basename(script_path)}")

if __name__ == "__main__":
    app = SteadypayLoginPage()
    app.mainloop()