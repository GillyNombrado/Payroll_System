import os
import sys
import subprocess
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from data import (
    get_admin_data, get_all_employees, compute_payroll_summary,
    draw_rounded_rectangle, RoundedBadge
)

class SteadypayAdminDashboard(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Steadypay - Payroll Dashboard (Admin)")
        self.geometry("1200x750")
        self.minsize(1100, 680)
        self.configure(bg="#FFFFFF")

        # Color Palette Definition (Based on Steadypay visual design)
        self.colors = {
            "sidebar_bg": "#D6F4F0",       # Light mint pastel for left sidebar
            "sidebar_item": "#FFFFFF",     # White pill buttons in sidebar
            "primary_orange": "#FF9F1C",   # Vibrant CTA Orange
            "soft_orange": "#FFBF69",      # Peach / Light border orange
            "border_peach": "#FFDDB7",     # Delicate peach border for cards
            "pill_pending": "#FFE8D6",     # Pending status background
            "pill_pending_text": "#E67E22",# Pending status text
            "pill_approved": "#D1F4EE",    # Approved status background
            "pill_approved_text": "#16988B",# Approved status text
            "white": "#FFFFFF",
            "card_bg": "#FFFFFF",
            "dark_teal": "#2EC4B6",        # Primary teal header/accents
            "deep_teal": "#147B72",        # Dark text teal
            "text_dark": "#2C3E50",        # Main dark text
            "gray_text": "#788896",        # Subtitle / placeholder gray
            "border_light": "#E8ECEB",     # Light divider border
            "avatar_orange": "#FF9F1C",
            "avatar_mint": "#4ED8C8"
        }

        # Centralized Data from data.py
        self.admin_data = get_admin_data()
        self.employees = get_all_employees()
        self.filtered_employees = list(self.employees)

        # Track current page and sidebar button widget references
        self.current_page = None
        self.sidebar_buttons = []

        self.setup_layout()

    def setup_layout(self):
        # 1. Left Fixed Sidebar
        self.create_sidebar()

        # 2. Right Main Scrollable Area (empty container)
        self.create_scrollable_main_content()

        # 3. Show Dashboard by default
        self.show_page("dashboard")

    # ==========================================
    # SIDEBAR NAVIGATION
    # ==========================================
    def create_sidebar(self):
        sidebar = tk.Frame(self, bg=self.colors["sidebar_bg"], width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo Area
        logo_frame = tk.Frame(sidebar, bg=self.colors["sidebar_bg"])
        logo_frame.pack(anchor="nw", padx=20, pady=(24, 25))

        logo_canvas = tk.Canvas(logo_frame, width=26, height=24, bg=self.colors["sidebar_bg"], highlightthickness=0)
        logo_canvas.pack(side="left", padx=(0, 8))
        logo_canvas.create_rectangle(2, 4, 7, 20, fill=self.colors["primary_orange"], outline="")
        logo_canvas.create_rectangle(9, 1, 14, 23, fill=self.colors["primary_orange"], outline="")
        logo_canvas.create_rectangle(16, 6, 21, 18, fill=self.colors["primary_orange"], outline="")

        logo_text = tk.Label(
            logo_frame,
            text="steadypay",
            font=("Segoe UI", 16, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["sidebar_bg"]
        )
        logo_text.pack(side="left")

        # Bind logo click to navigate back to Dashboard
        for w in (logo_frame, logo_canvas, logo_text):
            w.bind("<Button-1>", lambda e: self.show_page("dashboard"))
            w.configure(cursor="hand2")

        # Navigation Menu List (active state is set dynamically by show_page)
        menu_items = [
            ("🏠", "Dashboard"),
            ("👥", "Employee\nmanagement"),
            ("💳", "Process payroll"),
            ("📄", "Payroll &\nPayslips"),
            ("⚙️", "Settings")
        ]

        self.sidebar_buttons = []
        for icon, title in menu_items:
            btn_frame = tk.Frame(
                sidebar,
                bg=self.colors["sidebar_bg"],
                highlightbackground=self.colors["sidebar_bg"],
                highlightthickness=1,
                cursor="hand2"
            )
            btn_frame.pack(fill="x", padx=14, pady=4)

            # Icon
            icon_lbl = tk.Label(
                btn_frame,
                text=icon,
                font=("Segoe UI", 11),
                bg=self.colors["sidebar_bg"],
                fg=self.colors["deep_teal"]
            )
            icon_lbl.pack(side="left", padx=(10, 6), pady=6)

            # Title
            title_lbl = tk.Label(
                btn_frame,
                text=title,
                font=("Segoe UI", 9),
                fg="#355B57",
                bg=self.colors["sidebar_bg"],
                justify="left"
            )
            title_lbl.pack(side="left", pady=6)

            # Store references for dynamic active state updates
            self.sidebar_buttons.append((title, btn_frame, icon_lbl, title_lbl))

            # Bind click
            for widget in (btn_frame, icon_lbl, title_lbl):
                widget.bind("<Button-1>", lambda e, name=title: self.on_menu_click(name))

        # Logout Button pinned at bottom
        logout_frame = tk.Frame(
            sidebar,
            bg=self.colors["sidebar_item"],
            highlightbackground=self.colors["sidebar_bg"],
            highlightthickness=1,
            cursor="hand2"
        )
        logout_frame.pack(side="bottom", fill="x", padx=14, pady=20)

        logout_icon = tk.Label(
            logout_frame,
            text="🚪",
            font=("Segoe UI", 11),
            bg=self.colors["sidebar_item"],
            fg=self.colors["primary_orange"]
        )
        logout_icon.pack(side="left", padx=(12, 6), pady=8)

        logout_lbl = tk.Label(
            logout_frame,
            text="Logout",
            font=("Segoe UI", 9, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["sidebar_item"]
        )
        logout_lbl.pack(side="left", pady=8)

        for widget in (logout_frame, logout_icon, logout_lbl):
            widget.bind("<Button-1>", lambda e: self.handle_logout())

    def update_sidebar_active(self, active_menu_title):
        """Updates the visual active/inactive state of all sidebar menu items."""
        for title, btn_frame, icon_lbl, title_lbl in self.sidebar_buttons:
            is_active = (title == active_menu_title)
            bg = self.colors["sidebar_item"] if is_active else self.colors["sidebar_bg"]
            btn_frame.configure(bg=bg, highlightbackground=bg)
            icon_lbl.configure(
                bg=bg,
                fg=self.colors["dark_teal"] if is_active else self.colors["deep_teal"]
            )
            title_lbl.configure(
                bg=bg,
                font=("Segoe UI", 9, "bold" if is_active else "normal"),
                fg=self.colors["dark_teal"] if is_active else "#355B57"
            )

    def on_menu_click(self, menu_name):
        """Handles sidebar menu item clicks.
        Dashboard stays in-window; all other pages navigate to their own script."""
        if menu_name == "Dashboard":
            self.show_page("dashboard")
            return

        # Map non-dashboard items to their script files
        menu_to_script = {
            "Employee\nmanagement": "aEmployee.py",
            "Process payroll":      "aProcessPay.py",
            "Payroll &\nPayslips":  "aPayRecord&Slip.py",
            "Settings":             "aSettings.py"
        }
        script = menu_to_script.get(menu_name)
        if script:
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script)
            if os.path.exists(script_path):
                self.destroy()
                subprocess.Popen([sys.executable, script_path])

    # ==========================================
    # PAGE SWITCHING (SMOOTH IN-PLACE NAVIGATION)
    # ==========================================
    def show_page(self, page_name):
        """Switches the right-side content to the specified page instantly,
        without closing or reopening the window."""
        if page_name == self.current_page:
            return
        self.current_page = page_name

        # Clear all existing content widgets
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Scroll back to top
        self.main_canvas.yview_moveto(0)

        # Page configuration: (badge_text, description, active_sidebar_menu_title)
        page_config = {
            "dashboard": (
                "PAYROLL DASHBOARD",
                "Manage employees, payroll runs, and records from one secure workspace.",
                "Dashboard"
            ),
            "employee": (
                "EMPLOYEE MANAGEMENT",
                "View and manage all employee records and profiles.",
                "Employee\nmanagement"
            ),
            "process_pay": (
                "PROCESS PAYROLL",
                "Run and manage payroll processing cycles.",
                "Process payroll"
            ),
            "pay_records_slips": (
                "PAYROLL & PAYSLIPS",
                "Review payroll records and generate employee payslips.",
                "Payroll &\nPayslips"
            ),
            "settings": (
                "SETTINGS",
                "Configure system preferences and account settings.",
                "Settings"
            )
        }

        badge_text, desc_text, active_menu = page_config[page_name]

        # Update sidebar highlight
        self.update_sidebar_active(active_menu)

        # Update window title
        self.title(f"Steadypay - {badge_text.title()} (Admin)")

        # Update the fixed header labels in-place (header lives outside the canvas)
        self.badge_lbl.config(text=badge_text)
        self.desc_lbl.config(text=desc_text)

        # Build page-specific content below the header
        if page_name == "dashboard":
            self.create_summary_cards(self.content_frame)
            self.create_split_layout(self.content_frame)
        # Other pages: right side is empty for now as requested

    # ==========================================
    # SCROLLABLE MAIN CONTENT AREA
    # ==========================================
    def create_scrollable_main_content(self):
        right_container = tk.Frame(self, bg=self.colors["white"])
        right_container.pack(side="right", fill="both", expand=True)

        # Fixed header — lives outside the canvas so it never scrolls
        self.create_top_header(right_container)

        self.main_canvas = tk.Canvas(right_container, bg=self.colors["white"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(right_container, orient="vertical", command=self.main_canvas.yview)

        # Content frame inside canvas
        self.content_frame = tk.Frame(self.main_canvas, bg=self.colors["white"], padx=26, pady=20)
        self.canvas_window = self.main_canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        def _on_canvas_configure(event):
            self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
            self.main_canvas.itemconfig(self.canvas_window, width=event.width)

        def _on_frame_configure(event):
            self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

        self.main_canvas.bind("<Configure>", _on_canvas_configure)
        self.content_frame.bind("<Configure>", _on_frame_configure)
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Mouse wheel support
        def _on_mousewheel(event):
            self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def create_top_header(self, parent, badge_text="PAYROLL DASHBOARD", desc_text="Manage employees, payroll runs, and records from one secure workspace."):
        header_frame = tk.Frame(parent, bg=self.colors["white"], padx=26, pady=20)
        header_frame.pack(fill="x")

        # Subtle bottom divider line
        tk.Frame(parent, bg=self.colors["border_light"], height=1).pack(fill="x")

        # Left Header Titles
        left_box = tk.Frame(header_frame, bg=self.colors["white"])
        left_box.pack(side="left", anchor="w")

        self.badge_lbl = tk.Label(
            left_box,
            text=badge_text,
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["primary_orange"],
            bg=self.colors["white"]
        )
        self.badge_lbl.pack(anchor="w")

        title = tk.Label(
            left_box,
            text=self.admin_data.get("company_name", "Steadypay Technologies Inc."),
            font=("Segoe UI", 20, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        )
        title.pack(anchor="w", pady=(2, 2))

        self.desc_lbl = tk.Label(
            left_box,
            text=desc_text,
            font=("Segoe UI", 9),
            fg=self.colors["gray_text"],
            bg=self.colors["white"]
        )
        self.desc_lbl.pack(anchor="w")

        # Right Header (Date/Time & Profile Bubble Button)
        right_box = tk.Frame(header_frame, bg=self.colors["white"])
        right_box.pack(side="right", anchor="e")

        now_str = datetime.datetime.now().strftime("%B %d, %Y  |  %I:%M %p")
        datetime_lbl = tk.Label(
            right_box,
            text=now_str,
            font=("Segoe UI", 9, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        )
        datetime_lbl.pack(side="left", padx=(0, 16))

        # Profile Pill Button
        self.profile_btn = tk.Frame(
            right_box,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            cursor="hand2",
            padx=10,
            pady=4
        )
        self.profile_btn.pack(side="left")

        # Avatar Circle
        avatar_canvas = tk.Canvas(self.profile_btn, width=32, height=32, bg=self.colors["white"], highlightthickness=0)
        avatar_canvas.pack(side="left", padx=(0, 8))
        avatar_canvas.create_oval(2, 2, 30, 30, fill=self.colors["primary_orange"], outline="")
        avatar_canvas.create_text(16, 16, text="AM", fill="#FFFFFF", font=("Segoe UI", 9, "bold"))

        # Profile Text
        profile_info = tk.Frame(self.profile_btn, bg=self.colors["white"])
        profile_info.pack(side="left")

        name_lbl = tk.Label(
            profile_info,
            text=self.admin_data["name"],
            font=("Segoe UI", 9, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        )
        name_lbl.pack(anchor="w")

        role_lbl = tk.Label(
            profile_info,
            text=self.admin_data["role"],
            font=("Segoe UI", 7),
            fg=self.colors["gray_text"],
            bg=self.colors["white"]
        )
        role_lbl.pack(anchor="w")

        # Bind click event to show Admin Profile Bubble
        for w in (self.profile_btn, avatar_canvas, profile_info, name_lbl, role_lbl):
            w.bind("<Button-1>", lambda e: self.show_admin_profile_bubble())

    # ==========================================
    # VISUAL CHARTS & PROGRESS BARS HELPERS
    # ==========================================
    def draw_progress_bar(self, parent, percentage=78, fg_color=None, bg_color=None, height=6):
        """Draws a sleek, rounded horizontal progress bar."""
        fg = fg_color or self.colors["dark_teal"]
        bg = bg_color or self.colors["border_light"]
        c = tk.Canvas(parent, height=height, bg=self.colors["white"], highlightthickness=0)
        c.pack(fill="x", pady=(4, 2))

        def _render(event=None):
            w = c.winfo_width()
            h = c.winfo_height()
            if w <= 4:
                return
            c.delete("all")
            draw_rounded_rectangle(c, 0, 0, w, h, radius=max(2, h // 2), fill=bg, outline="")
            pw = max(h, int(w * (percentage / 100.0)))
            draw_rounded_rectangle(c, 0, 0, min(w, pw), h, radius=max(2, h // 2), fill=fg, outline="")

        c.bind("<Configure>", _render)
        return c

    def create_trend_line_chart_widget(self, parent):
        """Draws a responsive Payroll Expense Trend line chart with spline curve and month data."""
        c = tk.Canvas(parent, height=52, bg=self.colors["white"], highlightthickness=0)
        c.pack(fill="x", pady=(4, 0))

        def _render(event=None):
            w = c.winfo_width()
            h = c.winfo_height()
            if w <= 10 or h <= 10:
                return
            c.delete("all")

            # Reference grid line
            c.create_line(8, h - 16, w - 8, h - 16, fill="#F0F5F4", width=1)

            # Historical trend points: May ($22.1k), Jun ($23.8k), Jul ($24.9k), Aug ($25.4k), Sep ($27.35k)
            values = [0.22, 0.44, 0.40, 0.68, 0.94]
            months = ["May", "Jun", "Jul", "Aug", "Sep"]
            pts = []
            step = (w - 24) / (len(values) - 1)
            for i, v in enumerate(values):
                px = 12 + i * step
                py = (h - 20) - (v * (h - 26))
                pts.append((px, py))

            # Draw smooth trend spline line
            flat_pts = []
            for px, py in pts:
                flat_pts.extend([px, py])
            c.create_line(flat_pts, fill=self.colors["primary_orange"], width=2.5, smooth=True)

            # Draw nodes and month labels
            for i, (px, py) in enumerate(pts):
                is_last = (i == len(pts) - 1)
                r = 3.5 if is_last else 2
                fill_col = self.colors["primary_orange"] if is_last else self.colors["soft_orange"]
                c.create_oval(px - r, py - r, px + r, py + r, fill=fill_col, outline=self.colors["white"], width=1)
                c.create_text(
                    px, h - 7,
                    text=months[i],
                    fill=self.colors["deep_teal"] if is_last else self.colors["gray_text"],
                    font=("Segoe UI", 6, "bold" if is_last else "normal")
                )

        c.bind("<Configure>", _render)
        return c

    def create_donut_chart_widget(self, parent):
        """Draws a Department Budget Allocation donut chart with an integrated micro-legend."""
        c = tk.Canvas(parent, height=52, bg=self.colors["white"], highlightthickness=0)
        c.pack(fill="x", pady=(4, 0))

        def _render(event=None):
            w = c.winfo_width()
            h = c.winfo_height()
            if w <= 10 or h <= 10:
                return
            c.delete("all")

            # Left side: Donut ring
            cx = 28
            cy = h // 2
            r_out = 22
            r_in = 12

            # Budget slices: (percentage, color)
            slices = [
                (35, self.colors["dark_teal"]),     # Engineering & Design
                (25, self.colors["primary_orange"]), # Operations
                (20, self.colors["soft_orange"]),    # Finance
                (20, self.colors["avatar_mint"])     # People & HR
            ]

            start_angle = 90
            for pct, col in slices:
                extent = -1 * (pct / 100.0) * 360
                c.create_arc(
                    cx - r_out, cy - r_out, cx + r_out, cy + r_out,
                    start=start_angle, extent=extent, fill=col, outline=""
                )
                start_angle += extent

            # Center hole cutout
            c.create_oval(cx - r_in, cy - r_in, cx + r_in, cy + r_in, fill=self.colors["white"], outline="")
            c.create_text(cx, cy, text="5 Dept", fill=self.colors["deep_teal"], font=("Segoe UI", 6, "bold"))

            # Right side: Micro-legend
            legend_items = [
                ("35% Design", self.colors["dark_teal"]),
                ("25% Ops", self.colors["primary_orange"]),
                ("20% Finance", self.colors["soft_orange"]),
                ("20% People", self.colors["avatar_mint"])
            ]

            lx = 58
            for idx, (label, col) in enumerate(legend_items):
                ly = 8 + (idx * 11)
                c.create_rectangle(lx, ly - 3, lx + 5, ly + 3, fill=col, outline="")
                c.create_text(lx + 9, ly, text=label, anchor="w", fill=self.colors["text_dark"], font=("Segoe UI", 6))

        c.bind("<Configure>", _render)
        return c

    # ==========================================
    # COMPUTATION FUNCTION & SUMMARY CARDS
    # ==========================================
    def compute_summary_metrics(self):
        """Computes summary figures dynamically based on employee dataset."""
        return compute_payroll_summary()

    def create_summary_cards(self, parent):
        """Renders the top stat cards: 2 standard stat boxes with progress bars + 2 visual chart widgets."""
        self.summary_frame = tk.Frame(parent, bg=self.colors["white"])
        self.summary_frame.pack(fill="x", pady=(0, 16))

        metrics = self.compute_summary_metrics()

        for col_idx in range(4):
            self.summary_frame.columnconfigure(col_idx, weight=1)

        # -------------------------------------------------------------
        # Box 1: Total Payroll (Standard Stat Box + Progress Bar)
        # -------------------------------------------------------------
        card1 = tk.Frame(
            self.summary_frame,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=14,
            pady=10
        )
        card1.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(card1, text="TOTAL PAYROLL", font=("Segoe UI", 7, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(anchor="w")
        tk.Label(card1, text=metrics["total_payroll"], font=("Segoe UI", 15, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(anchor="w", pady=(1, 1))
        tk.Label(card1, text="September 2026 payroll cycle", font=("Segoe UI", 7), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(anchor="w")

        self.draw_progress_bar(card1, percentage=78, fg_color=self.colors["dark_teal"], height=5)
        prog_info1 = tk.Frame(card1, bg=self.colors["white"])
        prog_info1.pack(fill="x")
        tk.Label(prog_info1, text="Cap utilized: 78%", font=("Segoe UI", 6, "bold"), fg=self.colors["deep_teal"], bg=self.colors["white"]).pack(side="left")
        tk.Label(prog_info1, text="Limit $35k", font=("Segoe UI", 6), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(side="right")

        # -------------------------------------------------------------
        # Box 2: Visual Widget - Payroll Expense Trend Line Chart
        # -------------------------------------------------------------
        card2 = tk.Frame(
            self.summary_frame,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=14,
            pady=10
        )
        card2.grid(row=0, column=1, sticky="nsew", padx=(0, 8))

        hdr2 = tk.Frame(card2, bg=self.colors["white"])
        hdr2.pack(fill="x")
        tk.Label(hdr2, text="PAYROLL TREND", font=("Segoe UI", 7, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(side="left")

        trend_pill = tk.Label(hdr2, text="+8.4% ▲", font=("Segoe UI", 6, "bold"), bg=self.colors["pill_approved"], fg=self.colors["pill_approved_text"], padx=4, pady=1)
        trend_pill.pack(side="right")

        tk.Label(card2, text="5-Mo Expense Trajectory", font=("Segoe UI", 7), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(anchor="w", pady=(1, 0))
        self.create_trend_line_chart_widget(card2)

        # -------------------------------------------------------------
        # Box 3: Visual Widget - Department Budget Allocation Donut Chart
        # -------------------------------------------------------------
        card3 = tk.Frame(
            self.summary_frame,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=14,
            pady=10
        )
        card3.grid(row=0, column=2, sticky="nsew", padx=(0, 8))

        hdr3 = tk.Frame(card3, bg=self.colors["white"])
        hdr3.pack(fill="x")
        tk.Label(hdr3, text="DEPT ALLOCATION", font=("Segoe UI", 7, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(side="left")
        tk.Label(hdr3, text="5 Depts", font=("Segoe UI", 6, "bold"), bg=self.colors["pill_pending"], fg=self.colors["pill_pending_text"], padx=4, pady=1).pack(side="right")

        tk.Label(card3, text="Budget share by team", font=("Segoe UI", 7), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(anchor="w", pady=(1, 0))
        self.create_donut_chart_widget(card3)

        # -------------------------------------------------------------
        # Box 4: Cycle Readiness & Verification (Standard Stat Box + Progress Bar)
        # -------------------------------------------------------------
        card4 = tk.Frame(
            self.summary_frame,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=14,
            pady=10
        )
        card4.grid(row=0, column=3, sticky="nsew")

        tk.Label(card4, text="CYCLE READINESS", font=("Segoe UI", 7, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(anchor="w")
        tk.Label(card4, text=metrics["next_payday"], font=("Segoe UI", 15, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(anchor="w", pady=(1, 1))
        tk.Label(card4, text="3 days until final approval", font=("Segoe UI", 7), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(anchor="w")

        self.draw_progress_bar(card4, percentage=100, fg_color=self.colors["primary_orange"], height=5)
        prog_info4 = tk.Frame(card4, bg=self.colors["white"])
        prog_info4.pack(fill="x")
        tk.Label(prog_info4, text="5 / 5 verified • 100% ready", font=("Segoe UI", 6, "bold"), fg=self.colors["primary_orange"], bg=self.colors["white"]).pack(side="left")
        tk.Label(prog_info4, text="EFT Queued", font=("Segoe UI", 6), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(side="right")

    # ==========================================
    # SPLIT LAYOUT (CARDS + ACTIVITY FEED)
    # ==========================================
    def create_split_layout(self, parent):
        """Creates the two-column Split Layout: Informational Cards on the left, Activity Feed on the right."""
        split_frame = tk.Frame(parent, bg=self.colors["white"])
        split_frame.pack(fill="both", expand=True)

        split_frame.columnconfigure(0, weight=4, minsize=320)
        split_frame.columnconfigure(1, weight=6, minsize=480)
        split_frame.rowconfigure(0, weight=1)

        # Left Column: Modular Cards
        left_cards_col = tk.Frame(split_frame, bg=self.colors["white"])
        left_cards_col.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        self.create_quick_actions_card(left_cards_col)
        self.create_dept_spending_card(left_cards_col)
        self.create_compliance_card(left_cards_col)

        # Right Column: Activity Feed Panel (NO TABLE HEADERS)
        right_feed_col = tk.Frame(split_frame, bg=self.colors["white"])
        right_feed_col.grid(row=0, column=1, sticky="nsew")

        self.create_activity_feed_panel(right_feed_col)

    # ==========================================
    # LEFT COLUMN CARDS
    # ==========================================
    def navigate_to_script(self, script_name):
        """Helper to navigate to target script file."""
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
        if os.path.exists(script_path):
            self.destroy()
            subprocess.Popen([sys.executable, script_path])

    def create_quick_actions_card(self, parent):
        """Quick action navigation hub card."""
        card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=14,
            pady=12
        )
        card.pack(fill="x", pady=(0, 12))

        tk.Label(card, text="QUICK ACTIONS", font=("Segoe UI", 7, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(anchor="w")
        tk.Label(card, text="Payroll Operations Hub", font=("Segoe UI", 11, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(anchor="w", pady=(1, 8))

        # 1. Run Payroll Button
        run_btn = tk.Frame(card, bg=self.colors["primary_orange"], cursor="hand2", padx=12, pady=7)
        run_btn.pack(fill="x", pady=(0, 6))
        tk.Label(run_btn, text="💳", font=("Segoe UI", 11), bg=self.colors["primary_orange"], fg="#FFFFFF").pack(side="left", padx=(0, 8))
        run_txt = tk.Frame(run_btn, bg=self.colors["primary_orange"])
        run_txt.pack(side="left")
        tk.Label(run_txt, text="Run Payroll Cycle", font=("Segoe UI", 8, "bold"), fg="#FFFFFF", bg=self.colors["primary_orange"]).pack(anchor="w")
        tk.Label(run_txt, text="Compute & disburse next period", font=("Segoe UI", 6), fg="#FFE8D0", bg=self.colors["primary_orange"]).pack(anchor="w")

        # 2. Payroll & Payslips Button
        slip_btn = tk.Frame(card, bg=self.colors["white"], highlightbackground=self.colors["border_peach"], highlightthickness=1, cursor="hand2", padx=12, pady=7)
        slip_btn.pack(fill="x", pady=(0, 6))
        tk.Label(slip_btn, text="📄", font=("Segoe UI", 11), bg=self.colors["white"], fg=self.colors["dark_teal"]).pack(side="left", padx=(0, 8))
        slip_txt = tk.Frame(slip_btn, bg=self.colors["white"])
        slip_txt.pack(side="left")
        tk.Label(slip_txt, text="Payroll & Payslips", font=("Segoe UI", 8, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(anchor="w")
        tk.Label(slip_txt, text="Master ledger, tax slips & NACHA export", font=("Segoe UI", 6), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(anchor="w")

        # 3. Add Employee Button
        add_btn = tk.Frame(card, bg=self.colors["white"], highlightbackground=self.colors["border_peach"], highlightthickness=1, cursor="hand2", padx=12, pady=7)
        add_btn.pack(fill="x")
        tk.Label(add_btn, text="👤➕", font=("Segoe UI", 10), bg=self.colors["white"], fg=self.colors["dark_teal"]).pack(side="left", padx=(0, 8))
        add_txt = tk.Frame(add_btn, bg=self.colors["white"])
        add_txt.pack(side="left")
        tk.Label(add_txt, text="Add Employee", font=("Segoe UI", 8, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(anchor="w")
        tk.Label(add_txt, text="Register team member & salary details", font=("Segoe UI", 6), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(anchor="w")

        # Binds
        for w in (run_btn, run_txt) + tuple(run_btn.winfo_children()) + tuple(run_txt.winfo_children()):
            w.bind("<Button-1>", lambda e: self.navigate_to_script("aProcessPay.py"))
        for w in (slip_btn, slip_txt) + tuple(slip_btn.winfo_children()) + tuple(slip_txt.winfo_children()):
            w.bind("<Button-1>", lambda e: self.navigate_to_script("aPayRecord&Slip.py"))
        for w in (add_btn, add_txt) + tuple(add_btn.winfo_children()) + tuple(add_txt.winfo_children()):
            w.bind("<Button-1>", lambda e: self.navigate_to_script("aEmployee.py"))

    def create_dept_spending_card(self, parent):
        """Department budget allocation card with visual horizontal progress bars."""
        card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=14,
            pady=12
        )
        card.pack(fill="x", pady=(0, 12))

        tk.Label(card, text="DEPARTMENT BUDGET", font=("Segoe UI", 7, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(anchor="w")
        tk.Label(card, text="Spending & Cap Allocation", font=("Segoe UI", 11, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(anchor="w", pady=(1, 8))

        dept_data = [
            ("Engineering & Design", "$9,320 / $12,000", 78, self.colors["dark_teal"]),
            ("Operations Team", "$5,140 / $6,500", 79, self.colors["primary_orange"]),
            ("Finance & Accounts", "$4,960 / $6,000", 83, self.colors["soft_orange"]),
            ("People Operations", "$4,780 / $5,800", 82, self.colors["avatar_mint"])
        ]

        for dept_name, spent_txt, pct, bar_col in dept_data:
            item_frame = tk.Frame(card, bg=self.colors["white"])
            item_frame.pack(fill="x", pady=2)

            tk.Label(item_frame, text=dept_name, font=("Segoe UI", 7, "bold"), fg=self.colors["text_dark"], bg=self.colors["white"]).pack(side="left")
            tk.Label(item_frame, text=f"{spent_txt} ({pct}%)", font=("Segoe UI", 6), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(side="right")

            self.draw_progress_bar(card, percentage=pct, fg_color=bar_col, height=4)

    def create_compliance_card(self, parent):
        """Compliance and payroll security card."""
        card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=14,
            pady=12
        )
        card.pack(fill="x")

        tk.Label(card, text="PAYROLL HEALTH", font=("Segoe UI", 7, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(anchor="w")
        tk.Label(card, text="Audit & Compliance Status", font=("Segoe UI", 11, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(anchor="w", pady=(1, 6))

        checklist = [
            ("Direct Deposit EFT", "100% Active", self.colors["pill_approved"], self.colors["pill_approved_text"]),
            ("Statutory Tax Withholding", "IRS 2026 Compliant", self.colors["pill_approved"], self.colors["pill_approved_text"]),
            ("Period Lock & Seal", "Locked to prevent edits", self.colors["pill_pending"], self.colors["pill_pending_text"])
        ]

        for label, status, bg_col, fg_col in checklist:
            row = tk.Frame(card, bg=self.colors["white"])
            row.pack(fill="x", pady=3)
            tk.Label(row, text=f"✓ {label}", font=("Segoe UI", 7), fg=self.colors["text_dark"], bg=self.colors["white"]).pack(side="left")
            badge = tk.Label(row, text=status, font=("Segoe UI", 6, "bold"), bg=bg_col, fg=fg_col, padx=4, pady=1)
            badge.pack(side="right")

    # ==========================================
    # RIGHT COLUMN: ACTIVITY FEED (NO TABLE HEADERS)
    # ==========================================
    def create_activity_feed_panel(self, parent):
        """Creates the Live Activity Feed panel with no table headers."""
        self.table_card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=16,
            pady=14
        )
        self.table_card.pack(fill="both", expand=True)

        # Header Row of Feed: Title + Live Badge + Search
        card_hdr = tk.Frame(self.table_card, bg=self.colors["white"])
        card_hdr.pack(fill="x", pady=(0, 10))

        left_hdr = tk.Frame(card_hdr, bg=self.colors["white"])
        left_hdr.pack(side="left")

        title_box = tk.Frame(left_hdr, bg=self.colors["white"])
        title_box.pack(anchor="w")

        tk.Label(
            title_box,
            text="Live Activity Feed",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        ).pack(side="left")

        pulse = tk.Label(
            title_box,
            text="● Live Feed",
            font=("Segoe UI", 7, "bold"),
            fg=self.colors["primary_orange"],
            bg=self.colors["pill_pending"],
            padx=5,
            pady=1
        )
        pulse.pack(side="left", padx=(8, 0))

        tk.Label(
            left_hdr,
            text="Real-time employee payroll disbursements & status updates",
            font=("Segoe UI", 7),
            fg=self.colors["gray_text"],
            bg=self.colors["white"]
        ).pack(anchor="w", pady=(1, 0))

        # Search Bar
        search_card = tk.Frame(
            card_hdr,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=8,
            pady=4
        )
        search_card.pack(side="right")

        tk.Label(search_card, text="🔍", font=("Segoe UI", 8), bg=self.colors["white"], fg=self.colors["gray_text"]).pack(side="left", padx=(0, 4))

        self.search_entry = tk.Entry(
            search_card,
            font=("Segoe UI", 8),
            bg=self.colors["white"],
            fg=self.colors["text_dark"],
            bd=0,
            relief="flat",
            width=18
        )
        self.search_entry.insert(0, "Filter activity...")
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=2)

        self.search_entry.bind("<FocusIn>", self.on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self.on_search_focus_out)
        self.search_entry.bind("<KeyRelease>", self.on_search_key)

        # Unified Activity Grid (NO TABLE HEADERS)
        self.table_grid = tk.Frame(self.table_card, bg=self.colors["white"])
        self.table_grid.pack(fill="both", expand=True, pady=(4, 0))

        # Grid weights: [Avatar:1, Employee Info:4, Status:2, Amount:2, Time:1, Action:1]
        self.col_specs = [
            ("Avatar", 1, "center"),
            ("Employee", 4, "w"),
            ("Status", 2, "center"),
            ("Amount", 2, "e"),
            ("Updated", 1, "w"),
            ("Action", 1, "center")
        ]

        for idx, (_, weight, _) in enumerate(self.col_specs):
            self.table_grid.columnconfigure(idx, weight=weight)

        self.render_table_rows()

    def on_search_focus_in(self, event):
        if self.search_entry.get() == "Filter activity...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=self.colors["text_dark"])

    def on_search_focus_out(self, event):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "Filter activity...")
            self.search_entry.config(fg=self.colors["gray_text"])

    def on_search_key(self, event):
        query = self.search_entry.get().strip().lower()
        if query == "filter activity..." or not query:
            self.filtered_employees = list(self.employees)
        else:
            self.filtered_employees = [
                e for e in self.employees
                if query in e["name"].lower()
                or query in e["role"].lower()
                or query in e["email"].lower()
                or query in e["status"].lower()
                or query in e["payroll_run"].lower()
            ]
        self.render_table_rows()

    def render_table_rows(self):
        """Renders the Live Activity Feed stream rows WITHOUT table headers."""
        for child in self.table_grid.winfo_children():
            child.destroy()

        # NOTE: TABLE HEADERS HAVE BEEN REMOVED AS REQUESTED.
        # Feed items render directly starting at row 0.

        if not self.filtered_employees:
            no_data = tk.Label(
                self.table_grid,
                text="No recent activity records found matching your filter.",
                font=("Segoe UI", 8, "italic"),
                fg=self.colors["gray_text"],
                bg=self.colors["white"],
                pady=24
            )
            no_data.grid(row=0, column=0, columnspan=len(self.col_specs), pady=24)
            return

        current_grid_row = 0
        for idx, emp in enumerate(self.filtered_employees):
            # Row container with hover effect
            row_frame = tk.Frame(self.table_grid, bg=self.colors["white"])

            # Col 0: Avatar Circle
            av_canvas = tk.Canvas(self.table_grid, width=32, height=32, bg=self.colors["white"], highlightthickness=0)
            av_canvas.grid(row=current_grid_row, column=0, padx=(4, 6), pady=6)
            av_canvas.create_oval(2, 2, 30, 30, fill=emp["avatar_color"], outline="")
            av_canvas.create_text(16, 16, text=emp["initials"], fill="#FFFFFF", font=("Segoe UI", 8, "bold"))

            # Col 1: Employee Name & Event Action
            emp_info = tk.Frame(self.table_grid, bg=self.colors["white"])
            emp_info.grid(row=current_grid_row, column=1, sticky="w", padx=6, pady=6)

            name_lbl = tk.Label(
                emp_info,
                text=emp["name"],
                font=("Segoe UI", 9, "bold"),
                fg=self.colors["dark_teal"],
                bg=self.colors["white"],
                cursor="hand2"
            )
            name_lbl.pack(anchor="w")
            name_lbl.bind("<Button-1>", lambda e, item=emp: self.show_employee_profile_bubble(item))

            sub_desc = tk.Label(
                emp_info,
                text=f"{emp['role']} • {emp['payroll_run']} cycle",
                font=("Segoe UI", 7),
                fg=self.colors["gray_text"],
                bg=self.colors["white"]
            )
            sub_desc.pack(anchor="w")

            # Col 2: Status Pill Badge (RoundedBadge)
            is_approved = (emp["status"] == "Approved")
            status_bg = self.colors["pill_approved"] if is_approved else self.colors["pill_pending"]
            status_fg = self.colors["pill_approved_text"] if is_approved else self.colors["pill_pending_text"]

            status_pill = RoundedBadge(
                self.table_grid,
                text=emp["status"],
                bg_color=status_bg,
                fg_color=status_fg,
                radius=8,
                width=72,
                height=22,
                parent_bg=self.colors["white"]
            )
            status_pill.grid(row=current_grid_row, column=2, padx=6, pady=6)

            # Col 3: Amount + Method Subtitle
            amt_box = tk.Frame(self.table_grid, bg=self.colors["white"])
            amt_box.grid(row=current_grid_row, column=3, sticky="e", padx=6, pady=6)

            amt_lbl = tk.Label(
                amt_box,
                text=f"${emp['amount']:,.2f}",
                font=("Segoe UI", 9, "bold"),
                fg=self.colors["dark_teal"],
                bg=self.colors["white"]
            )
            amt_lbl.pack(anchor="e")

            method_lbl = tk.Label(
                amt_box,
                text="Direct Deposit",
                font=("Segoe UI", 6),
                fg=self.colors["gray_text"],
                bg=self.colors["white"]
            )
            method_lbl.pack(anchor="e")

            # Col 4: Updated Time
            upd_lbl = tk.Label(
                self.table_grid,
                text=emp["updated"],
                font=("Segoe UI", 7),
                fg=self.colors["gray_text"],
                bg=self.colors["white"]
            )
            upd_lbl.grid(row=current_grid_row, column=4, sticky="w", padx=6, pady=6)

            # Col 5: View Action Button
            view_btn = tk.Button(
                self.table_grid,
                text="View",
                font=("Segoe UI", 7, "bold"),
                bg=self.colors["white"],
                fg=self.colors["primary_orange"],
                activebackground=self.colors["border_peach"],
                activeforeground=self.colors["primary_orange"],
                highlightbackground=self.colors["primary_orange"],
                highlightthickness=1,
                bd=0,
                relief="flat",
                cursor="hand2",
                padx=8,
                pady=2,
                command=lambda item=emp: self.show_employee_profile_bubble(item)
            )
            view_btn.grid(row=current_grid_row, column=5, padx=6, pady=6)

            current_grid_row += 1

            # Row separator line between stream items
            if idx < len(self.filtered_employees) - 1:
                row_sep = tk.Frame(self.table_grid, height=1, bg="#F7F7F7")
                row_sep.grid(row=current_grid_row, column=0, columnspan=len(self.col_specs), sticky="ew", pady=1)
                current_grid_row += 1

    # ==========================================
    # PROFILE BUBBLE MESSAGE BOXES
    # ==========================================
    def show_admin_profile_bubble(self):
        """Displays a floating card/bubble dialog showing full Admin information."""
        popup = tk.Toplevel(self)
        popup.title("Admin Profile Information")
        popup.geometry("380x420")
        popup.resizable(False, False)
        popup.configure(bg=self.colors["white"])
        popup.transient(self)
        popup.grab_set()

        # Center popup relative to main window
        x = self.winfo_x() + (self.winfo_width() - 380) // 2
        y = self.winfo_y() + (self.winfo_height() - 420) // 2
        popup.geometry(f"+{x}+{y}")

        # Top Header Banner in Popup
        banner = tk.Frame(popup, bg=self.colors["sidebar_bg"], padx=20, pady=18)
        banner.pack(fill="x")

        av = tk.Canvas(banner, width=48, height=48, bg=self.colors["sidebar_bg"], highlightthickness=0)
        av.pack(side="left", padx=(0, 12))
        av.create_oval(2, 2, 46, 46, fill=self.colors["primary_orange"], outline="")
        av.create_text(24, 24, text="AM", fill="#FFFFFF", font=("Segoe UI", 14, "bold"))

        info_hdr = tk.Frame(banner, bg=self.colors["sidebar_bg"])
        info_hdr.pack(side="left")
        tk.Label(info_hdr, text=self.admin_data["name"], font=("Segoe UI", 13, "bold"), fg=self.colors["dark_teal"], bg=self.colors["sidebar_bg"]).pack(anchor="w")
        tk.Label(info_hdr, text="👑 " + self.admin_data["role"], font=("Segoe UI", 8, "bold"), fg=self.colors["deep_teal"], bg=self.colors["sidebar_bg"]).pack(anchor="w")

        # Content List
        content = tk.Frame(popup, bg=self.colors["white"], padx=24, pady=16)
        content.pack(fill="both", expand=True)

        details = [
            ("📧 Email", self.admin_data["email"]),
            ("📱 Phone Number", self.admin_data["phone"]),
            ("🎂 Age", f"{self.admin_data['age']} years old"),
            ("📅 Date Hired", self.admin_data["hired_date"]),
            ("🏢 Department", self.admin_data["department"]),
            ("📍 Location", self.admin_data["location"]),
            ("🛡 Access Status", self.admin_data["status"])
        ]

        for label, val in details:
            row = tk.Frame(content, bg=self.colors["white"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(side="left")
            tk.Label(row, text=val, font=("Segoe UI", 8, "bold"), fg=self.colors["text_dark"], bg=self.colors["white"]).pack(side="right")

        # Close Button
        close_btn = tk.Button(
            popup,
            text="Close Profile",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["primary_orange"],
            fg="#FFFFFF",
            activebackground=self.colors["soft_orange"],
            activeforeground="#FFFFFF",
            bd=0,
            relief="flat",
            cursor="hand2",
            pady=6,
            command=popup.destroy
        )
        close_btn.pack(fill="x", padx=24, pady=(0, 16))

    def show_employee_profile_bubble(self, emp):
        """Displays a floating card/bubble dialog showing full Employee details."""
        popup = tk.Toplevel(self)
        popup.title(f"Employee Details - {emp['name']}")
        popup.geometry("380x465")
        popup.resizable(False, False)
        popup.configure(bg=self.colors["white"])
        popup.transient(self)
        popup.grab_set()

        # Center popup
        x = self.winfo_x() + (self.winfo_width() - 380) // 2
        y = self.winfo_y() + (self.winfo_height() - 465) // 2
        popup.geometry(f"+{x}+{y}")

        # Top Banner
        banner = tk.Frame(popup, bg=self.colors["sidebar_bg"], padx=20, pady=18)
        banner.pack(fill="x")

        av = tk.Canvas(banner, width=48, height=48, bg=self.colors["sidebar_bg"], highlightthickness=0)
        av.pack(side="left", padx=(0, 12))
        av.create_oval(2, 2, 46, 46, fill=emp["avatar_color"], outline="")
        av.create_text(24, 24, text=emp["initials"], fill="#FFFFFF", font=("Segoe UI", 14, "bold"))

        info_hdr = tk.Frame(banner, bg=self.colors["sidebar_bg"])
        info_hdr.pack(side="left")
        tk.Label(info_hdr, text=emp["name"], font=("Segoe UI", 13, "bold"), fg=self.colors["dark_teal"], bg=self.colors["sidebar_bg"]).pack(anchor="w")
        tk.Label(info_hdr, text=f"ID: {emp['id']} · {emp['role']}", font=("Segoe UI", 8), fg=self.colors["deep_teal"], bg=self.colors["sidebar_bg"]).pack(anchor="w")

        # Content List
        content = tk.Frame(popup, bg=self.colors["white"], padx=24, pady=16)
        content.pack(fill="both", expand=True)

        details = [
            ("📧 Work Email", emp["email"]),
            ("📱 Contact Number", emp["phone"]),
            ("🎂 Age", f"{emp['age']} years old"),
            ("📅 Hired Date", emp["hired_date"]),
            ("🌴 Available Leaves", f"{emp.get('available_leaves', 12)} Days"),
            ("💳 Payroll Run", emp["payroll_run"]),
            ("💵 Net Salary", f"${emp['amount']:,.2f}"),
            ("📌 Approval Status", emp["status"])
        ]

        for label, val in details:
            row = tk.Frame(content, bg=self.colors["white"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(side="left")
            color = self.colors["pill_approved_text"] if val == "Approved" else (self.colors["pill_pending_text"] if val == "Pending" else self.colors["text_dark"])
            tk.Label(row, text=val, font=("Segoe UI", 8, "bold"), fg=color, bg=self.colors["white"]).pack(side="right")

        # Close Button
        close_btn = tk.Button(
            popup,
            text="Done",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["dark_teal"],
            fg="#FFFFFF",
            activebackground=self.colors["deep_teal"],
            activeforeground="#FFFFFF",
            bd=0,
            relief="flat",
            cursor="hand2",
            pady=6,
            command=popup.destroy
        )
        close_btn.pack(fill="x", padx=24, pady=(0, 16))

    # ==========================================
    # LOGOUT HANDLER
    # ==========================================
    def handle_logout(self):
        self.destroy()
        login_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "login.py")
        if os.path.exists(login_script):
            subprocess.Popen([sys.executable, login_script])

if __name__ == "__main__":
    app = SteadypayAdminDashboard()
    app.mainloop()
