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
            ("📄", "Payroll records"),
            ("📑", "Generate payslips"),
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
        """Handles sidebar menu item clicks by switching to the corresponding page."""
        menu_to_page = {
            "Dashboard": "dashboard",
            "Employee\nmanagement": "employee",
            "Process payroll": "process_pay",
            "Payroll records": "pay_records",
            "Generate payslips": "payslips",
            "Settings": "settings"
        }
        page = menu_to_page.get(menu_name)
        if page:
            self.show_page(page)

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
            "pay_records": (
                "PAYROLL RECORDS",
                "Review past payroll runs and historical records.",
                "Payroll records"
            ),
            "payslips": (
                "GENERATE PAYSLIPS",
                "Generate and export employee payslip documents.",
                "Generate payslips"
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
            self.create_quick_actions(self.content_frame)
            self.create_summary_cards(self.content_frame)
            self.create_activity_table(self.content_frame)
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
            text="Name of Company",
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
    # QUICK ACTION BUTTONS & SEARCH ROW
    # ==========================================
    def create_quick_actions(self, parent):
        actions_row = tk.Frame(parent, bg=self.colors["white"])
        actions_row.pack(fill="x", pady=(0, 16))

        # 1. Run Payroll (Orange CTA Card)
        run_card = tk.Frame(
            actions_row,
            bg=self.colors["primary_orange"],
            cursor="hand2",
            padx=14,
            pady=8
        )
        run_card.pack(side="left", padx=(0, 10))

        run_icon = tk.Label(run_card, text="💳", font=("Segoe UI", 12), bg=self.colors["primary_orange"], fg="#FFFFFF")
        run_icon.pack(side="left", padx=(0, 8))

        run_txt = tk.Frame(run_card, bg=self.colors["primary_orange"])
        run_txt.pack(side="left")
        tk.Label(run_txt, text="Run payroll", font=("Segoe UI", 9, "bold"), fg="#FFFFFF", bg=self.colors["primary_orange"]).pack(anchor="w")
        tk.Label(run_txt, text="Process the next cycle", font=("Segoe UI", 7), fg="#FFE8D0", bg=self.colors["primary_orange"]).pack(anchor="w")

        # 2. Export Data (White bordered card)
        export_card = tk.Frame(
            actions_row,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            cursor="hand2",
            padx=14,
            pady=8
        )
        export_card.pack(side="left", padx=(0, 10))

        exp_icon = tk.Label(export_card, text="📥", font=("Segoe UI", 11), bg=self.colors["white"], fg=self.colors["dark_teal"])
        exp_icon.pack(side="left", padx=(0, 8))

        exp_txt = tk.Frame(export_card, bg=self.colors["white"])
        exp_txt.pack(side="left")
        tk.Label(exp_txt, text="Export data", font=("Segoe UI", 9, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(anchor="w")
        tk.Label(exp_txt, text="CSV, PDF, or payroll files", font=("Segoe UI", 7), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(anchor="w")

        # 3. Add Employee (White bordered card)
        add_card = tk.Frame(
            actions_row,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            cursor="hand2",
            padx=14,
            pady=8
        )
        add_card.pack(side="left", padx=(0, 10))

        add_icon = tk.Label(add_card, text="👤➕", font=("Segoe UI", 10), bg=self.colors["white"], fg=self.colors["dark_teal"])
        add_icon.pack(side="left", padx=(0, 8))

        add_txt = tk.Frame(add_card, bg=self.colors["white"])
        add_txt.pack(side="left")
        tk.Label(add_txt, text="Add employee", font=("Segoe UI", 9, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(anchor="w")
        tk.Label(add_txt, text="Invite a new team member", font=("Segoe UI", 7), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(anchor="w")

        # 4. Search Bar
        search_card = tk.Frame(
            actions_row,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=10,
            pady=6
        )
        search_card.pack(side="right", fill="x", expand=True)

        s_icon = tk.Label(search_card, text="🔍", font=("Segoe UI", 10), bg=self.colors["white"], fg=self.colors["gray_text"])
        s_icon.pack(side="left", padx=(0, 6))

        self.search_entry = tk.Entry(
            search_card,
            font=("Segoe UI", 9),
            bg=self.colors["white"],
            fg=self.colors["text_dark"],
            bd=0,
            relief="flat"
        )
        self.search_entry.insert(0, "Search employees, payslips, or payroll runs")
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=3)

        self.search_entry.bind("<FocusIn>", self.on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self.on_search_focus_out)
        self.search_entry.bind("<KeyRelease>", self.on_search_key)

    def on_search_focus_in(self, event):
        if self.search_entry.get() == "Search employees, payslips, or payroll runs":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=self.colors["text_dark"])

    def on_search_focus_out(self, event):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "Search employees, payslips, or payroll runs")
            self.search_entry.config(fg=self.colors["gray_text"])

    def on_search_key(self, event):
        query = self.search_entry.get().strip().lower()
        if query == "search employees, payslips, or payroll runs" or not query:
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

    # ==========================================
    # COMPUTATION FUNCTION & SUMMARY CARDS
    # ==========================================
    def compute_summary_metrics(self):
        """Computes summary figures dynamically based on employee dataset."""
        return compute_payroll_summary()

    def create_summary_cards(self, parent):
        self.summary_frame = tk.Frame(parent, bg=self.colors["white"])
        self.summary_frame.pack(fill="x", pady=(0, 16))

        metrics = self.compute_summary_metrics()

        cards_spec = [
            ("Total payroll", metrics["total_payroll"], "September 2026 payroll cycle"),
            ("Active employees", metrics["active_employees"], "3 new hires this month"),
            ("Pending payslips", metrics["pending_payslips"], "Ready for review and export"),
            ("Next payday", metrics["next_payday"], "3 days until final approval")
        ]

        for i, (title, value, subtitle) in enumerate(cards_spec):
            card = tk.Frame(
                self.summary_frame,
                bg=self.colors["white"],
                highlightbackground=self.colors["border_peach"],
                highlightthickness=1,
                padx=16,
                pady=10
            )
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 10, 0))
            self.summary_frame.columnconfigure(i, weight=1)

            t_lbl = tk.Label(card, text=title, font=("Segoe UI", 8), fg=self.colors["gray_text"], bg=self.colors["white"])
            t_lbl.pack(anchor="w")

            v_lbl = tk.Label(card, text=value, font=("Segoe UI", 15, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"])
            v_lbl.pack(anchor="w", pady=(2, 2))

            s_lbl = tk.Label(card, text=subtitle, font=("Segoe UI", 7), fg=self.colors["gray_text"], bg=self.colors["white"])
            s_lbl.pack(anchor="w")

    # ==========================================
    # RECENT ACTIVITY TABLE
    # ==========================================
    def create_activity_table(self, parent):
        self.table_card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=18,
            pady=14
        )
        self.table_card.pack(fill="both", expand=True)

        # Header Row of Card
        card_hdr = tk.Frame(self.table_card, bg=self.colors["white"])
        card_hdr.pack(fill="x", pady=(0, 10))

        tbl_title = tk.Label(
            card_hdr,
            text="Recent activity",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        )
        tbl_title.pack(side="left")

        updated_lbl = tk.Label(
            card_hdr,
            text="Updated 2 minutes ago",
            font=("Segoe UI", 8),
            fg=self.colors["primary_orange"],
            bg=self.colors["white"]
        )
        updated_lbl.pack(side="right")

        # Table Column Specs: (Column Name, weight, alignment)
        self.col_specs = [
            ("Employee", 3, "w"),
            ("Email", 3, "w"),
            ("Payroll run", 2, "w"),
            ("Status", 2, "w"),
            ("Amount", 2, "e"),
            ("Updated", 2, "w"),
            ("Action", 1, "w")
        ]

        # Unified table grid frame to guarantee 100% column alignment
        self.table_grid = tk.Frame(self.table_card, bg=self.colors["white"])
        self.table_grid.pack(fill="both", expand=True)

        for idx, (_, weight, _) in enumerate(self.col_specs):
            self.table_grid.columnconfigure(idx, weight=weight)

        self.render_table_rows()

    def render_table_rows(self):
        # Clear existing widgets from grid
        for child in self.table_grid.winfo_children():
            child.destroy()

        # Row 0: Column Headers
        for idx, (col_name, _, align) in enumerate(self.col_specs):
            lbl = tk.Label(
                self.table_grid,
                text=col_name,
                font=("Segoe UI", 8, "bold"),
                fg=self.colors["gray_text"],
                bg=self.colors["white"],
                anchor=align
            )
            lbl.grid(row=0, column=idx, sticky="ew", padx=8, pady=(0, 6))

        # Row 1: Divider line spanning all columns
        div = tk.Frame(self.table_grid, height=1, bg=self.colors["border_light"])
        div.grid(row=1, column=0, columnspan=len(self.col_specs), sticky="ew", pady=(0, 6))

        if not self.filtered_employees:
            no_data = tk.Label(
                self.table_grid,
                text="No employee records found matching your search.",
                font=("Segoe UI", 9, "italic"),
                fg=self.colors["gray_text"],
                bg=self.colors["white"],
                pady=20
            )
            no_data.grid(row=2, column=0, columnspan=len(self.col_specs), pady=20)
            return

        current_grid_row = 2
        for idx, emp in enumerate(self.filtered_employees):
            # Col 0: Employee (Avatar Circle + Name + Role)
            emp_box = tk.Frame(self.table_grid, bg=self.colors["white"])
            emp_box.grid(row=current_grid_row, column=0, sticky="w", padx=8, pady=4)

            av_canvas = tk.Canvas(emp_box, width=30, height=30, bg=self.colors["white"], highlightthickness=0)
            av_canvas.pack(side="left", padx=(0, 8))
            av_canvas.create_oval(2, 2, 28, 28, fill=emp["avatar_color"], outline="")
            av_canvas.create_text(15, 15, text=emp["initials"], fill="#FFFFFF", font=("Segoe UI", 8, "bold"))

            name_role_box = tk.Frame(emp_box, bg=self.colors["white"])
            name_role_box.pack(side="left")

            name_lbl = tk.Label(
                name_role_box,
                text=emp["name"],
                font=("Segoe UI", 9, "bold"),
                fg=self.colors["dark_teal"],
                bg=self.colors["white"],
                cursor="hand2"
            )
            name_lbl.pack(anchor="w")
            name_lbl.bind("<Button-1>", lambda e, item=emp: self.show_employee_profile_bubble(item))

            role_lbl = tk.Label(
                name_role_box,
                text=emp["role"],
                font=("Segoe UI", 7),
                fg=self.colors["gray_text"],
                bg=self.colors["white"]
            )
            role_lbl.pack(anchor="w")

            # Col 1: Email (Separate Column)
            email_lbl = tk.Label(
                self.table_grid,
                text=emp["email"],
                font=("Segoe UI", 8),
                fg=self.colors["text_dark"],
                bg=self.colors["white"],
                anchor="w"
            )
            email_lbl.grid(row=current_grid_row, column=1, sticky="ew", padx=8, pady=4)

            # Col 2: Payroll Run
            run_lbl = tk.Label(
                self.table_grid,
                text=emp["payroll_run"],
                font=("Segoe UI", 8),
                fg=self.colors["gray_text"],
                bg=self.colors["white"],
                anchor="w"
            )
            run_lbl.grid(row=current_grid_row, column=2, sticky="ew", padx=8, pady=4)

            # Col 3: Status Badge
            is_approved = emp["status"] == "Approved"
            status_bg = self.colors["pill_approved"] if is_approved else self.colors["pill_pending"]
            status_fg = self.colors["pill_approved_text"] if is_approved else self.colors["pill_pending_text"]

            status_pill = RoundedBadge(
                self.table_grid,
                text=emp["status"],
                bg_color=status_bg,
                fg_color=status_fg,
                radius=8,
                width=76,
                height=22,
                parent_bg=self.colors["white"]
            )
            status_pill.grid(row=current_grid_row, column=3, sticky="w", padx=8, pady=4)

            # Col 4: Amount
            amt_lbl = tk.Label(
                self.table_grid,
                text=f"${emp['amount']:,.2f}",
                font=("Segoe UI", 9, "bold"),
                fg=self.colors["dark_teal"],
                bg=self.colors["white"],
                anchor="e"
            )
            amt_lbl.grid(row=current_grid_row, column=4, sticky="ew", padx=8, pady=4)

            # Col 5: Updated
            upd_lbl = tk.Label(
                self.table_grid,
                text=emp["updated"],
                font=("Segoe UI", 8),
                fg=self.colors["gray_text"],
                bg=self.colors["white"],
                anchor="w"
            )
            upd_lbl.grid(row=current_grid_row, column=5, sticky="ew", padx=8, pady=4)

            # Col 6: View Action Button
            view_btn = tk.Button(
                self.table_grid,
                text="View",
                font=("Segoe UI", 8, "bold"),
                bg=self.colors["white"],
                fg=self.colors["primary_orange"],
                activebackground=self.colors["border_peach"],
                activeforeground=self.colors["primary_orange"],
                highlightbackground=self.colors["primary_orange"],
                highlightthickness=1,
                bd=0,
                relief="flat",
                cursor="hand2",
                padx=10,
                pady=2,
                command=lambda item=emp: self.show_employee_profile_bubble(item)
            )
            view_btn.grid(row=current_grid_row, column=6, sticky="w", padx=8, pady=4)

            current_grid_row += 1

            # Subtle row separator line
            if idx < len(self.filtered_employees) - 1:
                row_sep = tk.Frame(self.table_grid, height=1, bg="#F7F7F7")
                row_sep.grid(row=current_grid_row, column=0, columnspan=len(self.col_specs), sticky="ew", pady=2)
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
