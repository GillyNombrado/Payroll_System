import os
import sys
import subprocess
import datetime
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from data import get_admin_data, RoundedBadge

class SteadypayEmployeePage(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Steadypay - Employee Management & HR Directory (Admin)")
        self.geometry("1240x780")
        self.minsize(1120, 680)
        self.configure(bg="#FFFFFF")

        # Color Palette Definition (Based on Steadypay visual design)
        self.colors = {
            "sidebar_bg": "#D6F4F0",        # Light mint pastel for left sidebar
            "sidebar_item": "#FFFFFF",      # White pill buttons in sidebar
            "primary_orange": "#FF9F1C",    # Vibrant CTA Orange
            "soft_orange": "#FFBF69",       # Peach / Light border orange
            "border_peach": "#FFDDB7",      # Delicate peach border for cards
            "pill_pending": "#FFE8D6",      # Pending status background
            "pill_pending_text": "#E67E22", # Pending status text
            "pill_approved": "#D1F4EE",     # Approved status background
            "pill_approved_text": "#16988B",# Approved status text
            "pill_offboard": "#FDE8E8",     # Offboarded / Terminated status bg
            "pill_offboard_text": "#E02424",# Offboarded text
            "white": "#FFFFFF",
            "card_bg": "#FFFFFF",
            "dark_teal": "#2EC4B6",         # Primary teal header/accents
            "deep_teal": "#147B72",         # Dark text teal
            "text_dark": "#2C3E50",         # Main dark text
            "gray_text": "#788896",         # Subtitle / placeholder gray
            "border_light": "#E8ECEB",      # Light divider border
            "border_color": "#FFBF69",      # Form field borders
            "row_alt": "#F7FCFC",           # Alternating row color
            "avatar_orange": "#FF9F1C",
            "avatar_mint": "#4ED8C8"
        }

        # Centralized Admin Data
        self.admin_data = get_admin_data()

        # Comprehensive Employee Master Database
        self.employees = [
            {
                "id": "EMP-001",
                "name": "Jane Doe",
                "role": "Software Engineer",
                "dept": "Engineering",
                "salary": 4500.00,
                "status": "Active",
                "email": "jane.doe@company.com",
                "phone": "+1 (555) 234-9081",
                "hire_date": "March 15, 2022",
                "emp_type": "Full-Time",
                "bank_account": "****4821",
                "tax_status": "Single (0)",
                "pto_balance": 14,
                "avatar_color": "#FF9F1C",
                "initials": "JD",
                "emergency_contact": "Mark Doe (Spouse) - +1 (555) 234-9082",
                "i9_verified": True,
                "w4_verified": True
            },
            {
                "id": "EMP-002",
                "name": "Alex Smith",
                "role": "Product Designer",
                "dept": "Design",
                "salary": 3800.00,
                "status": "Active",
                "email": "alex.smith@company.com",
                "phone": "+1 (555) 781-3490",
                "hire_date": "June 1, 2023",
                "emp_type": "Full-Time",
                "bank_account": "****9102",
                "tax_status": "Married (1)",
                "pto_balance": 12,
                "avatar_color": "#2EC4B6",
                "initials": "AS",
                "emergency_contact": "Sarah Smith (Sister) - +1 (555) 781-3499",
                "i9_verified": True,
                "w4_verified": True
            },
            {
                "id": "EMP-003",
                "name": "Maria Santos",
                "role": "HR Specialist",
                "dept": "Human Resources",
                "salary": 3200.00,
                "status": "Active",
                "email": "maria.santos@company.com",
                "phone": "+1 (555) 492-1102",
                "hire_date": "January 10, 2024",
                "emp_type": "Full-Time",
                "bank_account": "****3321",
                "tax_status": "Single (1)",
                "pto_balance": 10,
                "avatar_color": "#FFBF69",
                "initials": "MS",
                "emergency_contact": "Carlos Santos (Father) - +1 (555) 492-1100",
                "i9_verified": True,
                "w4_verified": True
            },
            {
                "id": "EMP-004",
                "name": "Liam Johnson",
                "role": "Accountant",
                "dept": "Finance",
                "salary": 3600.00,
                "status": "On Leave",
                "email": "liam.johnson@company.com",
                "phone": "+1 (555) 883-2940",
                "hire_date": "August 20, 2021",
                "emp_type": "Full-Time",
                "bank_account": "****8874",
                "tax_status": "Married (2)",
                "pto_balance": 6,
                "avatar_color": "#4ED8C8",
                "initials": "LJ",
                "emergency_contact": "Emma Johnson (Spouse) - +1 (555) 883-2941",
                "i9_verified": True,
                "w4_verified": True
            },
            {
                "id": "EMP-005",
                "name": "David Chen",
                "role": "QA Engineer",
                "dept": "Engineering",
                "salary": 3400.00,
                "status": "Active",
                "email": "david.chen@company.com",
                "phone": "+1 (555) 304-7621",
                "hire_date": "November 5, 2022",
                "emp_type": "Full-Time",
                "bank_account": "****7621",
                "tax_status": "Single (0)",
                "pto_balance": 11,
                "avatar_color": "#FFAE42",
                "initials": "DC",
                "emergency_contact": "Grace Chen (Mother) - +1 (555) 304-7629",
                "i9_verified": True,
                "w4_verified": True
            }
        ]

        # Search, Filter and Department State
        self._search_placeholder = "Search employee by name, ID, or role..."
        self.search_var = tk.StringVar(value="")
        self.dept_filter_var = tk.StringVar(value="All Departments")
        self.status_filter_var = tk.StringVar(value="All Statuses")

        self.setup_layout()

    # ==========================================
    # LAYOUT SETUP
    # ==========================================
    def setup_layout(self):
        # 1. Left Fixed Sidebar
        self.create_sidebar()

        # 2. Right Main Scrollable Area
        self.create_scrollable_main_content()

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
            w.bind("<Button-1>", lambda e: self.navigate_to_dashboard())
            w.configure(cursor="hand2")

        # Navigation Menu List
        menu_items = [
            ("🏠", "Dashboard", False),
            ("👥", "Employee\nmanagement", True),
            ("💳", "Process payroll", False),
            ("📄", "Payroll &\nPayslips", False),
            ("⚙️", "Settings", False)
        ]

        for icon, title, is_active in menu_items:
            btn_frame = tk.Frame(
                sidebar,
                bg=self.colors["sidebar_item"] if is_active else self.colors["sidebar_bg"],
                highlightbackground=self.colors["sidebar_item"] if is_active else self.colors["sidebar_bg"],
                highlightthickness=1,
                cursor="hand2"
            )
            btn_frame.pack(fill="x", padx=14, pady=4)

            icon_lbl = tk.Label(
                btn_frame,
                text=icon,
                font=("Segoe UI", 11),
                bg=btn_frame["bg"],
                fg=self.colors["dark_teal"] if is_active else self.colors["deep_teal"]
            )
            icon_lbl.pack(side="left", padx=(10, 6), pady=6)

            title_lbl = tk.Label(
                btn_frame,
                text=title,
                font=("Segoe UI", 9, "bold" if is_active else "normal"),
                fg=self.colors["dark_teal"] if is_active else "#355B57",
                bg=btn_frame["bg"],
                justify="left"
            )
            title_lbl.pack(side="left", pady=6)

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

    def on_menu_click(self, menu_name):
        if menu_name == "Dashboard":
            self.navigate_to_dashboard()
            return

        menu_map = {
            "Employee\nmanagement": "aEmployee.py",
            "Process payroll": "aProcessPay.py",
            "Payroll &\nPayslips": "aPayRecord&Slip.py",
            "Settings": "aSettings.py"
        }
        target = menu_map.get(menu_name)
        if target and target != "aEmployee.py":
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), target)
            if os.path.exists(script_path):
                self.destroy()
                subprocess.Popen([sys.executable, script_path])

    # ==========================================
    # SCROLLABLE MAIN CONTENT AREA
    # ==========================================
    def create_scrollable_main_content(self):
        right_container = tk.Frame(self, bg=self.colors["white"])
        right_container.pack(side="right", fill="both", expand=True)

        # Fixed top header outside the canvas
        self.create_top_header(right_container)

        self.main_canvas = tk.Canvas(right_container, bg=self.colors["white"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(right_container, orient="vertical", command=self.main_canvas.yview)

        self.content_frame = tk.Frame(self.main_canvas, bg=self.colors["white"], padx=26, pady=16)
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

        def _on_mousewheel(event):
            self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Populate Sections
        self.create_workforce_summary_cards(self.content_frame)
        self.create_employee_body(self.content_frame)

    # ==========================================
    # TOP HEADER (FIXED)
    # ==========================================
    def create_top_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.colors["white"], padx=26, pady=20)
        header_frame.pack(fill="x")

        # Subtle bottom divider line
        tk.Frame(parent, bg=self.colors["border_light"], height=1).pack(fill="x")

        left_box = tk.Frame(header_frame, bg=self.colors["white"])
        left_box.pack(side="left", anchor="w")

        tk.Label(
            left_box,
            text="WORKFORCE & HR DIRECTORY",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["primary_orange"],
            bg=self.colors["white"]
        ).pack(anchor="w")

        tk.Label(
            left_box,
            text=self.admin_data.get("company_name", "Steadypay Technologies Inc."),
            font=("Segoe UI", 20, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        ).pack(anchor="w", pady=(2, 2))

        tk.Label(
            left_box,
            text="Central employee master database, onboarding workflows, compensation & compliance vault.",
            font=("Segoe UI", 9),
            fg=self.colors["gray_text"],
            bg=self.colors["white"]
        ).pack(anchor="w")

        right_box = tk.Frame(header_frame, bg=self.colors["white"])
        right_box.pack(side="right", anchor="e")

        now_str = datetime.datetime.now().strftime("%B %d, %Y  |  %I:%M %p")
        tk.Label(
            right_box,
            text=now_str,
            font=("Segoe UI", 9, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        ).pack(side="left", padx=(0, 16))

        profile_btn = tk.Frame(
            right_box,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            cursor="hand2",
            padx=10,
            pady=4
        )
        profile_btn.pack(side="left")

        avatar_canvas = tk.Canvas(profile_btn, width=32, height=32, bg=self.colors["white"], highlightthickness=0)
        avatar_canvas.pack(side="left", padx=(0, 8))
        avatar_canvas.create_oval(2, 2, 30, 30, fill=self.colors["primary_orange"], outline="")
        avatar_canvas.create_text(16, 16, text="AM", fill="#FFFFFF", font=("Segoe UI", 9, "bold"))

        profile_info = tk.Frame(profile_btn, bg=self.colors["white"])
        profile_info.pack(side="left")

        tk.Label(
            profile_info,
            text=self.admin_data["name"],
            font=("Segoe UI", 9, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        ).pack(anchor="w")

        tk.Label(
            profile_info,
            text=self.admin_data["role"],
            font=("Segoe UI", 7),
            fg=self.colors["gray_text"],
            bg=self.colors["white"]
        ).pack(anchor="w")

    # ==========================================
    # WORKFORCE ANALYTICS & STAT CARDS
    # ==========================================
    def create_workforce_summary_cards(self, parent):
        self.stats_frame = tk.Frame(parent, bg=self.colors["white"])
        self.stats_frame.pack(fill="x", pady=(0, 14))

        self.stat_labels = {}
        specs = [
            ("total", "TOTAL WORKFORCE", "0 Staff", "Full-time & Contracted"),
            ("active", "ACTIVE ON ROLL", "0 Active", "In good operational standing"),
            ("leave", "ON LEAVE / AWAY", "0 On Leave", "Approved PTO & Medical"),
            ("depts", "TEAMS & DEPARTMENTS", "0 Teams", "Cross-functional staffing")
        ]

        for idx, (key, title, val, sub) in enumerate(specs):
            card = tk.Frame(
                self.stats_frame,
                bg=self.colors["white"],
                highlightbackground=self.colors["border_peach"],
                highlightthickness=1,
                padx=14,
                pady=10
            )
            card.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 10, 0))
            self.stats_frame.columnconfigure(idx, weight=1)

            t_lbl = tk.Label(card, text=title, font=("Segoe UI", 7, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"])
            t_lbl.pack(anchor="w")

            v_lbl = tk.Label(card, text=val, font=("Segoe UI", 14, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"])
            v_lbl.pack(anchor="w", pady=(1, 1))

            s_lbl = tk.Label(card, text=sub, font=("Segoe UI", 7), fg=self.colors["gray_text"], bg=self.colors["white"])
            s_lbl.pack(anchor="w")

            self.stat_labels[key] = (v_lbl, s_lbl)

        self.update_workforce_stats()

    def update_workforce_stats(self):
        """Updates summary numbers whenever employees are added, edited, or offboarded."""
        tot = len(self.employees)
        act = sum(1 for e in self.employees if e["status"] == "Active")
        on_leave = sum(1 for e in self.employees if e["status"] == "On Leave")
        depts = len(set(e["dept"] for e in self.employees))

        if "total" in self.stat_labels:
            self.stat_labels["total"][0].config(text=f"{tot} Team Members")
        if "active" in self.stat_labels:
            self.stat_labels["active"][0].config(text=f"{act} Active Staff")
        if "leave" in self.stat_labels:
            self.stat_labels["leave"][0].config(text=f"{on_leave} On Leave")
        if "depts" in self.stat_labels:
            self.stat_labels["depts"][0].config(text=f"{depts} Departments")

    # ==========================================
    # CENTRALIZED EMPLOYEE DIRECTORY & CONTROLS
    # ==========================================
    def create_employee_body(self, parent):
        body = tk.Frame(parent, bg=self.colors["white"])
        body.pack(fill="both", expand=True)

        # Main Table Card (matching dashboard card with peach border)
        self.table_card = tk.Frame(
            body,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=18,
            pady=14
        )
        self.table_card.pack(fill="both", expand=True)

        # Card Header: Title + Search & Filter Toolbar
        card_hdr = tk.Frame(self.table_card, bg=self.colors["white"])
        card_hdr.pack(fill="x", pady=(0, 12))

        left_hdr = tk.Frame(card_hdr, bg=self.colors["white"])
        left_hdr.pack(side="left")

        tk.Label(
            left_hdr,
            text="Employee Master Directory",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        ).pack(anchor="w")

        tk.Label(
            left_hdr,
            text="Click any employee row to open their full Comprehensive Master Record & Compliance Vault.",
            font=("Segoe UI", 7),
            fg=self.colors["gray_text"],
            bg=self.colors["white"]
        ).pack(anchor="w")

        # Right Controls: Department Filter + Status Filter + Search Entry
        right_ctrl = tk.Frame(card_hdr, bg=self.colors["white"])
        right_ctrl.pack(side="right")

        # Status Combobox
        tk.Label(right_ctrl, text="Status:", font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(side="left", padx=(0, 4))
        status_cb = ttk.Combobox(
            right_ctrl,
            textvariable=self.status_filter_var,
            values=["All Statuses", "Active", "On Leave", "Offboarded"],
            state="readonly",
            width=13,
            font=("Segoe UI", 8)
        )
        status_cb.pack(side="left", padx=(0, 8))
        status_cb.bind("<<ComboboxSelected>>", lambda e: self.render_table_rows())

        # Department Combobox
        tk.Label(right_ctrl, text="Dept:", font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(side="left", padx=(0, 4))
        departments = ["All Departments", "Engineering", "Design", "Human Resources", "Finance", "Operations", "Customer Support"]
        dept_cb = ttk.Combobox(
            right_ctrl,
            textvariable=self.dept_filter_var,
            values=departments,
            state="readonly",
            width=14,
            font=("Segoe UI", 8)
        )
        dept_cb.pack(side="left", padx=(0, 8))
        dept_cb.bind("<<ComboboxSelected>>", lambda e: self.render_table_rows())

        # Search Bar
        search_frame = tk.Frame(
            right_ctrl,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_color"],
            highlightthickness=1
        )
        search_frame.pack(side="left")

        tk.Label(search_frame, text="🔍", font=("Segoe UI", 8), bg=self.colors["white"], fg=self.colors["gray_text"]).pack(side="left", padx=(4, 2))

        self.search_entry = tk.Entry(
            search_frame,
            font=("Segoe UI", 8),
            bg=self.colors["white"],
            bd=0,
            relief="flat",
            width=22,
            fg=self.colors["gray_text"]
        )
        self.search_entry.insert(0, self._search_placeholder)
        self.search_entry.pack(side="left", ipady=4, padx=6)

        def _search_in(e):
            if self.search_entry.get() == self._search_placeholder:
                self.search_entry.delete(0, tk.END)
                self.search_entry.config(fg=self.colors["text_dark"])
                self.search_var.set("")

        def _search_out(e):
            if not self.search_entry.get().strip():
                self.search_entry.config(fg=self.colors["gray_text"])
                self.search_entry.delete(0, tk.END)
                self.search_entry.insert(0, self._search_placeholder)
                self.search_var.set("")
            else:
                self.search_var.set(self.search_entry.get().strip())
            self.render_table_rows()

        def _search_key(e):
            val = self.search_entry.get()
            if val != self._search_placeholder:
                self.search_var.set(val)
                self.render_table_rows()

        self.search_entry.bind("<FocusIn>", _search_in)
        self.search_entry.bind("<FocusOut>", _search_out)
        self.search_entry.bind("<KeyRelease>", _search_key)

        # Multi-Column Grid
        self.col_specs = [
            ("ID", 1, "center"),
            ("Employee", 3, "w"),
            ("Department", 2, "w"),
            ("Work Email & Phone", 3, "w"),
            ("Monthly Base", 2, "e"),
            ("Hire Date / Type", 2, "w"),
            ("Status", 2, "center"),
            ("Action", 2, "center")
        ]

        self.table_grid = tk.Frame(self.table_card, bg=self.colors["white"])
        self.table_grid.pack(fill="both", expand=True)

        for idx, (_, weight, _) in enumerate(self.col_specs):
            self.table_grid.columnconfigure(idx, weight=weight)

        self.render_table_rows()

        # Action Toolbar (Bottom Bar)
        actions_frame = tk.Frame(body, bg=self.colors["white"], pady=12)
        actions_frame.pack(fill="x")

        # Left: Onboard + Compliance Vault
        left_actions = tk.Frame(actions_frame, bg=self.colors["white"])
        left_actions.pack(side="left")

        tk.Button(
            left_actions,
            text="+ Onboard New Employee",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["primary_orange"],
            fg=self.colors["white"],
            activebackground=self.colors["soft_orange"],
            activeforeground=self.colors["white"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=7,
            command=self.show_onboard_employee_wizard
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            left_actions,
            text="📑 Document & Compliance Vault",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["white"],
            fg=self.colors["dark_teal"],
            highlightbackground=self.colors["dark_teal"],
            highlightthickness=1,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            command=self.show_compliance_vault_modal
        ).pack(side="left")

        # Right: Export CSV Directory
        right_actions = tk.Frame(actions_frame, bg=self.colors["white"])
        right_actions.pack(side="right")

        tk.Button(
            right_actions,
            text="📊 Export Workforce Directory (CSV)",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["sidebar_bg"],
            fg=self.colors["dark_teal"],
            activebackground=self.colors["border_peach"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=7,
            command=self.export_employee_directory_csv
        ).pack(side="left")

    # ==========================================
    # TABLE RENDERING & FILTERING
    # ==========================================
    def get_filtered_employees(self):
        query = self.search_var.get().lower().strip()
        dept = self.dept_filter_var.get()
        status = self.status_filter_var.get()

        visible = []
        for emp in self.employees:
            if query and query != self._search_placeholder.lower():
                matches = (query in emp["id"].lower() or
                           query in emp["name"].lower() or
                           query in emp["role"].lower() or
                           query in emp["dept"].lower() or
                           query in emp["email"].lower())
                if not matches:
                    continue

            if dept != "All Departments" and emp["dept"] != dept:
                continue

            if status != "All Statuses" and emp["status"] != status:
                continue

            visible.append(emp)
        return visible

    def render_table_rows(self):
        """Renders directory rows using the unified grid with visual badges and click modals."""
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
            lbl.grid(row=0, column=idx, sticky="ew", padx=6, pady=(0, 6))

        # Row 1: Divider line
        div = tk.Frame(self.table_grid, height=1, bg=self.colors["border_light"])
        div.grid(row=1, column=0, columnspan=len(self.col_specs), sticky="ew", pady=(0, 6))

        visible = self.get_filtered_employees()

        if not visible:
            no_data = tk.Label(
                self.table_grid,
                text="No employee records found matching your active filters.",
                font=("Segoe UI", 8, "italic"),
                fg=self.colors["gray_text"],
                bg=self.colors["white"],
                pady=24
            )
            no_data.grid(row=2, column=0, columnspan=len(self.col_specs), pady=24)
            return

        current_grid_row = 2
        for idx, emp in enumerate(visible):
            open_profile = lambda e=emp: self.show_master_record_drawer(e)

            # Col 0: ID
            id_lbl = tk.Label(
                self.table_grid,
                text=emp["id"],
                font=("Segoe UI", 8, "bold"),
                fg=self.colors["gray_text"],
                bg=self.colors["white"],
                cursor="hand2"
            )
            id_lbl.grid(row=current_grid_row, column=0, sticky="ew", padx=6, pady=4)
            id_lbl.bind("<Button-1>", lambda e, cmd=open_profile: cmd())

            # Col 1: Employee (Avatar + Name + Role)
            emp_box = tk.Frame(self.table_grid, bg=self.colors["white"], cursor="hand2")
            emp_box.grid(row=current_grid_row, column=1, sticky="w", padx=6, pady=4)
            emp_box.bind("<Button-1>", lambda e, cmd=open_profile: cmd())

            av_canvas = tk.Canvas(emp_box, width=28, height=28, bg=self.colors["white"], highlightthickness=0)
            av_canvas.pack(side="left", padx=(0, 6))
            av_canvas.create_oval(2, 2, 26, 26, fill=emp["avatar_color"], outline="")
            av_canvas.create_text(14, 14, text=emp["initials"], fill="#FFFFFF", font=("Segoe UI", 7, "bold"))
            av_canvas.bind("<Button-1>", lambda e, cmd=open_profile: cmd())

            name_role_box = tk.Frame(emp_box, bg=self.colors["white"])
            name_role_box.pack(side="left")

            name_lbl = tk.Label(
                name_role_box,
                text=emp["name"],
                font=("Segoe UI", 9, "bold"),
                fg=self.colors["dark_teal"],
                bg=self.colors["white"]
            )
            name_lbl.pack(anchor="w")
            name_lbl.bind("<Button-1>", lambda e, cmd=open_profile: cmd())

            role_lbl = tk.Label(
                name_role_box,
                text=emp["role"],
                font=("Segoe UI", 7),
                fg=self.colors["gray_text"],
                bg=self.colors["white"]
            )
            role_lbl.pack(anchor="w")
            role_lbl.bind("<Button-1>", lambda e, cmd=open_profile: cmd())

            # Col 2: Department
            tk.Label(
                self.table_grid,
                text=emp["dept"],
                font=("Segoe UI", 8),
                fg=self.colors["text_dark"],
                bg=self.colors["white"],
                anchor="w"
            ).grid(row=current_grid_row, column=2, sticky="ew", padx=6, pady=4)

            # Col 3: Work Contact
            contact_box = tk.Frame(self.table_grid, bg=self.colors["white"])
            contact_box.grid(row=current_grid_row, column=3, sticky="w", padx=6, pady=4)
            tk.Label(contact_box, text=emp["email"], font=("Segoe UI", 8), fg=self.colors["text_dark"], bg=self.colors["white"]).pack(anchor="w")
            tk.Label(contact_box, text=emp["phone"], font=("Segoe UI", 7), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(anchor="w")

            # Col 4: Monthly Base Salary
            tk.Label(
                self.table_grid,
                text=f"${emp['salary']:,.2f}",
                font=("Segoe UI", 9, "bold"),
                fg=self.colors["dark_teal"],
                bg=self.colors["white"],
                anchor="e"
            ).grid(row=current_grid_row, column=4, sticky="ew", padx=6, pady=4)

            # Col 5: Hire Date & Type
            hire_box = tk.Frame(self.table_grid, bg=self.colors["white"])
            hire_box.grid(row=current_grid_row, column=5, sticky="w", padx=6, pady=4)
            tk.Label(hire_box, text=emp["hire_date"], font=("Segoe UI", 8), fg=self.colors["text_dark"], bg=self.colors["white"]).pack(anchor="w")
            tk.Label(hire_box, text=emp["emp_type"], font=("Segoe UI", 7), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(anchor="w")

            # Col 6: Status Badge
            if emp["status"] == "Active":
                s_bg = self.colors["pill_approved"]
                s_fg = self.colors["pill_approved_text"]
            elif emp["status"] == "On Leave":
                s_bg = self.colors["pill_pending"]
                s_fg = self.colors["pill_pending_text"]
            else:
                s_bg = self.colors["pill_offboard"]
                s_fg = self.colors["pill_offboard_text"]

            status_pill = RoundedBadge(
                self.table_grid,
                text=emp["status"],
                bg_color=s_bg,
                fg_color=s_fg,
                radius=8,
                width=76,
                height=22,
                parent_bg=self.colors["white"]
            )
            status_pill.grid(row=current_grid_row, column=6, padx=6, pady=4)

            # Col 7: Actions (View Profile & Offboard Trigger)
            btn_box = tk.Frame(self.table_grid, bg=self.colors["white"])
            btn_box.grid(row=current_grid_row, column=7, padx=6, pady=4)

            view_btn = tk.Button(
                btn_box,
                text="View Profile",
                font=("Segoe UI", 7, "bold"),
                bg=self.colors["white"],
                fg=self.colors["primary_orange"],
                highlightbackground=self.colors["primary_orange"],
                highlightthickness=1,
                bd=0,
                relief="flat",
                cursor="hand2",
                padx=8,
                pady=2,
                command=open_profile
            )
            view_btn.pack(side="left", padx=(0, 4))

            if emp["status"] != "Offboarded":
                offboard_btn = tk.Button(
                    btn_box,
                    text="Offboard",
                    font=("Segoe UI", 7, "bold"),
                    bg=self.colors["white"],
                    fg="#E02424",
                    highlightbackground="#E02424",
                    highlightthickness=1,
                    bd=0,
                    relief="flat",
                    cursor="hand2",
                    padx=6,
                    pady=2,
                    command=lambda e=emp: self.show_offboarding_modal(e)
                )
                offboard_btn.pack(side="left")

            current_grid_row += 1

            if idx < len(visible) - 1:
                row_sep = tk.Frame(self.table_grid, height=1, bg="#F7F7F7")
                row_sep.grid(row=current_grid_row, column=0, columnspan=len(self.col_specs), sticky="ew", pady=2)
                current_grid_row += 1

    # =========================================================================
    # COMPREHENSIVE EMPLOYEE MASTER RECORD PROFILE MODAL
    # =========================================================================
    def show_master_record_drawer(self, emp):
        """Displays full comprehensive Master Record with personal, compensation, and compliance details."""
        modal = tk.Toplevel(self)
        modal.title(f"Employee Master Record: {emp['name']} ({emp['id']})")
        modal.geometry("560x700")
        modal.resizable(False, False)
        modal.configure(bg=self.colors["white"])
        modal.transient(self)
        modal.grab_set()

        # Center modal
        x = self.winfo_x() + (self.winfo_width() - 560) // 2
        y = self.winfo_y() + (self.winfo_height() - 700) // 2
        modal.geometry(f"+{max(x, 40)}+{max(y, 20)}")

        # Header Ribbon
        hdr = tk.Frame(modal, bg=self.colors["sidebar_bg"], padx=24, pady=18)
        hdr.pack(fill="x")

        # Top Badge row
        top_row = tk.Frame(hdr, bg=self.colors["sidebar_bg"])
        top_row.pack(fill="x")
        tk.Label(top_row, text=f"MASTER RECORD • {emp['id']}", font=("Segoe UI", 8, "bold"), fg=self.colors["primary_orange"], bg=self.colors["sidebar_bg"]).pack(side="left")
        status_lbl = tk.Label(top_row, text=emp["status"].upper(), font=("Segoe UI", 7, "bold"), bg=self.colors["pill_approved"] if emp["status"] == "Active" else self.colors["pill_pending"], fg=self.colors["deep_teal"], padx=6, pady=1)
        status_lbl.pack(side="right")

        # Avatar + Name Line
        profile_row = tk.Frame(hdr, bg=self.colors["sidebar_bg"])
        profile_row.pack(fill="x", pady=(10, 0))

        av = tk.Canvas(profile_row, width=42, height=42, bg=self.colors["sidebar_bg"], highlightthickness=0)
        av.pack(side="left", padx=(0, 10))
        av.create_oval(2, 2, 40, 40, fill=emp["avatar_color"], outline="")
        av.create_text(21, 21, text=emp["initials"], fill="#FFFFFF", font=("Segoe UI", 11, "bold"))

        name_box = tk.Frame(profile_row, bg=self.colors["sidebar_bg"])
        name_box.pack(side="left")
        tk.Label(name_box, text=emp["name"], font=("Segoe UI", 14, "bold"), fg=self.colors["dark_teal"], bg=self.colors["sidebar_bg"]).pack(anchor="w")
        tk.Label(name_box, text=f"{emp['role']} • {emp['dept']} Department", font=("Segoe UI", 8), fg=self.colors["deep_teal"], bg=self.colors["sidebar_bg"]).pack(anchor="w")

        # Scrollable Body Cards
        body = tk.Frame(modal, bg=self.colors["white"], padx=20, pady=14)
        body.pack(fill="both", expand=True)

        def make_section(title, pairs):
            sec = tk.Frame(body, bg="#F9FCFC", highlightbackground=self.colors["border_light"], highlightthickness=1, padx=12, pady=10)
            sec.pack(fill="x", pady=(0, 10))

            tk.Label(sec, text=title, font=("Segoe UI", 8, "bold"), fg=self.colors["primary_orange"], bg="#F9FCFC").pack(anchor="w", pady=(0, 6))
            for k, v in pairs:
                r = tk.Frame(sec, bg="#F9FCFC")
                r.pack(fill="x", pady=1)
                tk.Label(r, text=k, font=("Segoe UI", 7, "bold"), fg=self.colors["gray_text"], bg="#F9FCFC").pack(side="left")
                tk.Label(r, text=str(v), font=("Segoe UI", 7), fg=self.colors["text_dark"], bg="#F9FCFC").pack(side="right")

        # 1. Personal & Contact Info
        make_section("1. PERSONAL & CONTACT DETAILS", [
            ("Work Email Address:", emp["email"]),
            ("Primary Phone Number:", emp["phone"]),
            ("Emergency Contact:", emp["emergency_contact"]),
            ("Work Location / Office:", "New York Corporate HQ")
        ])

        # 2. Employment & Role
        make_section("2. EMPLOYMENT & ROLE CONFIGURATION", [
            ("Employee Identification:", emp["id"]),
            ("Designated Department:", emp["dept"]),
            ("Official Position Title:", emp["role"]),
            ("Hire Date:", emp["hire_date"]),
            ("Employment Classification:", emp["emp_type"])
        ])

        # 3. Compensation & Bank Disbursement
        ann_base = emp["salary"] * 12
        make_section("3. COMPENSATION & PAYMENT CONFIGURATION", [
            ("Monthly Base Salary:", f"${emp['salary']:,.2f}"),
            ("Annualized Base Rate:", f"${ann_base:,.2f}"),
            ("Disbursement Method:", "EFT Direct Deposit"),
            ("Bank Account Ending:", emp["bank_account"]),
            ("Tax Filing Classification:", f"IRS W-4: {emp['tax_status']}")
        ])

        # 4. Leave Balances & Compliance Vault
        make_section("4. LEAVE BALANCES & COMPLIANCE VAULT", [
            ("Available PTO Vacation:", f"{emp['pto_balance']} Days Remaining"),
            ("Paid Sick Leave Balance:", "8 Days Remaining"),
            ("Form W-4 Withholding Status:", "✓ Verified & On File"),
            ("Form I-9 Employment Eligibility:", "✓ Verified & Authorized")
        ])

        # Footer Actions
        footer = tk.Frame(modal, bg=self.colors["white"], padx=20, pady=12)
        footer.pack(fill="x", side="bottom")

        tk.Button(
            footer,
            text="Close",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["sidebar_bg"],
            fg=self.colors["dark_teal"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=6,
            command=modal.destroy
        ).pack(side="right")

        tk.Button(
            footer,
            text="Edit Master Profile ✏️",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["primary_orange"],
            fg=self.colors["white"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=6,
            command=lambda: self.edit_employee_profile_modal(emp, modal)
        ).pack(side="right", padx=(0, 8))

    def edit_employee_profile_modal(self, emp, parent_modal):
        """Allows administrator to update compensation, title, and department."""
        dialog = tk.Toplevel(parent_modal)
        dialog.title(f"Edit Profile: {emp['name']}")
        dialog.geometry("400x420")
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors["white"])
        dialog.transient(parent_modal)
        dialog.grab_set()

        tk.Label(dialog, text=f"Update Master Profile: {emp['name']}", font=("Segoe UI", 11, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(padx=20, pady=(16, 10), anchor="w")

        entries = {}
        fields = [
            ("Position / Role Title", "role", emp["role"]),
            ("Department", "dept", emp["dept"]),
            ("Monthly Base Salary ($)", "salary", str(emp["salary"])),
            ("Work Contact Phone", "phone", emp["phone"]),
            ("Tax Filing Status", "tax_status", emp["tax_status"])
        ]

        for label, key, val in fields:
            tk.Label(dialog, text=label, font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(padx=20, anchor="w", pady=(4, 1))
            ent = tk.Entry(dialog, font=("Segoe UI", 9))
            ent.insert(0, val)
            ent.pack(fill="x", padx=20, pady=(0, 4))
            entries[key] = ent

        def _save():
            try:
                emp["role"] = entries["role"].get().strip()
                emp["dept"] = entries["dept"].get().strip()
                emp["salary"] = float(entries["salary"].get().strip())
                emp["phone"] = entries["phone"].get().strip()
                emp["tax_status"] = entries["tax_status"].get().strip()

                dialog.destroy()
                parent_modal.destroy()
                self.update_workforce_stats()
                self.render_table_rows()
                messagebox.showinfo("Profile Updated", f"Master record for {emp['name']} updated successfully!", parent=self)
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid numeric salary.", parent=dialog)

        tk.Button(dialog, text="Save Changes", font=("Segoe UI", 8, "bold"), bg=self.colors["primary_orange"], fg=self.colors["white"], bd=0, relief="flat", cursor="hand2", padx=14, pady=6, command=_save).pack(padx=20, pady=(12, 0), anchor="e")

    # =========================================================================
    # EMPLOYEE ONBOARDING WORKFLOW (NEW HIRE WIZARD)
    # =========================================================================
    def show_onboard_employee_wizard(self):
        """Onboarding wizard modal to register new hires into the company directory."""
        wizard = tk.Toplevel(self)
        wizard.title("New Employee Onboarding Wizard")
        wizard.geometry("480x580")
        wizard.resizable(False, False)
        wizard.configure(bg=self.colors["white"])
        wizard.transient(self)
        wizard.grab_set()

        # Center
        x = self.winfo_x() + (self.winfo_width() - 480) // 2
        y = self.winfo_y() + (self.winfo_height() - 580) // 2
        wizard.geometry(f"+{max(x, 40)}+{max(y, 20)}")

        # Banner
        banner = tk.Frame(wizard, bg=self.colors["sidebar_bg"], padx=20, pady=16)
        banner.pack(fill="x")
        tk.Label(banner, text="ONBOARD NEW TEAM MEMBER", font=("Segoe UI", 8, "bold"), fg=self.colors["primary_orange"], bg=self.colors["sidebar_bg"]).pack(anchor="w")
        tk.Label(banner, text="Employee Master Registration & Compliance Setup", font=("Segoe UI", 12, "bold"), fg=self.colors["dark_teal"], bg=self.colors["sidebar_bg"]).pack(anchor="w", pady=(2, 0))

        # Form
        form = tk.Frame(wizard, bg=self.colors["white"], padx=20, pady=14)
        form.pack(fill="both", expand=True)

        new_id = f"EMP-{len(self.employees) + 1:03d}"
        entries = {}

        fields = [
            ("Full Legal Name", "name", ""),
            ("Job Title / Role", "role", ""),
            ("Department", "dept", "Engineering"),
            ("Monthly Base Salary ($)", "salary", "4000.00"),
            ("Corporate Work Email", "email", ""),
            ("Direct Deposit Bank Account", "bank", "****4589"),
            ("W-4 Tax Filing Status", "tax_status", "Single (0)")
        ]

        for label, key, default in fields:
            tk.Label(form, text=label, font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(anchor="w", pady=(4, 1))
            if key == "dept":
                cb = ttk.Combobox(form, values=["Engineering", "Design", "Human Resources", "Finance", "Operations", "Customer Support"], state="readonly")
                cb.set(default)
                cb.pack(fill="x", pady=(0, 4))
                entries[key] = cb
            else:
                ent = tk.Entry(form, font=("Segoe UI", 9))
                ent.insert(0, default)
                ent.pack(fill="x", pady=(0, 4))
                entries[key] = ent

        def _submit_onboarding():
            name = entries["name"].get().strip()
            role = entries["role"].get().strip()
            dept = entries["dept"].get().strip()
            salary_str = entries["salary"].get().strip()
            email = entries["email"].get().strip() or f"{name.lower().replace(' ', '.')}@company.com"
            bank = entries["bank"].get().strip()
            tax_stat = entries["tax_status"].get().strip()

            if not name or not role:
                messagebox.showwarning("Incomplete Form", "Please fill in all mandatory onboarding fields.", parent=wizard)
                return

            try:
                salary = float(salary_str)
            except ValueError:
                messagebox.showerror("Invalid Salary", "Please provide a valid numeric monthly base salary.", parent=wizard)
                return

            initials = "".join(part[0].upper() for part in name.split()[:2])
            avatar_colors = ["#FF9F1C", "#2EC4B6", "#FFBF69", "#4ED8C8", "#7C83FD"]
            color = avatar_colors[len(self.employees) % len(avatar_colors)]

            new_record = {
                "id": new_id,
                "name": name,
                "role": role,
                "dept": dept,
                "salary": salary,
                "status": "Active",
                "email": email,
                "phone": "+1 (555) 019-3829",
                "hire_date": datetime.datetime.now().strftime("%B %d, %Y"),
                "emp_type": "Full-Time",
                "bank_account": bank,
                "tax_status": tax_stat,
                "pto_balance": 15,
                "avatar_color": color,
                "initials": initials,
                "emergency_contact": "Emergency Contact On File",
                "i9_verified": True,
                "w4_verified": True
            }

            self.employees.append(new_record)
            self.update_workforce_stats()
            self.render_table_rows()
            wizard.destroy()
            messagebox.showinfo("Onboarding Complete", f"✓ {name} has been successfully onboarded as {new_id} in {dept}!", parent=self)

        footer = tk.Frame(wizard, bg=self.colors["white"], padx=20, pady=12)
        footer.pack(fill="x", side="bottom")

        tk.Button(footer, text="Cancel", font=("Segoe UI", 8, "bold"), bg=self.colors["sidebar_bg"], fg=self.colors["dark_teal"], bd=0, relief="flat", cursor="hand2", padx=12, pady=6, command=wizard.destroy).pack(side="right", padx=(8, 0))
        tk.Button(footer, text="Complete Onboarding ✓", font=("Segoe UI", 8, "bold"), bg=self.colors["primary_orange"], fg=self.colors["white"], bd=0, relief="flat", cursor="hand2", padx=14, pady=6, command=_submit_onboarding).pack(side="right")

    # =========================================================================
    # EMPLOYEE OFFBOARDING WORKFLOW (DEPARTURE CHECKLIST)
    # =========================================================================
    def show_offboarding_modal(self, emp):
        """Formal offboarding protocol modal to safely transition employee status."""
        modal = tk.Toplevel(self)
        modal.title(f"Offboard Employee: {emp['name']}")
        modal.geometry("450x420")
        modal.resizable(False, False)
        modal.configure(bg=self.colors["white"])
        modal.transient(self)
        modal.grab_set()

        hdr = tk.Frame(modal, bg="#FDE8E8", padx=20, pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text="EMPLOYEE OFFBOARDING PROTOCOL", font=("Segoe UI", 8, "bold"), fg="#E02424", bg="#FDE8E8").pack(anchor="w")
        tk.Label(hdr, text=f"Initiate Departure: {emp['name']} ({emp['id']})", font=("Segoe UI", 12, "bold"), fg=self.colors["text_dark"], bg="#FDE8E8").pack(anchor="w", pady=(2, 0))

        body = tk.Frame(modal, bg=self.colors["white"], padx=20, pady=14)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Mandatory Offboarding Audit Checklist:", font=("Segoe UI", 8, "bold"), fg=self.colors["text_dark"], bg=self.colors["white"]).pack(anchor="w", pady=(0, 8))

        checklist = [
            "Revoke corporate email, SSO, and administrative VPN access",
            "Calculate final pro-rated pay and unused PTO vacation cash-out",
            "Collect company equipment (laptop, security badges, tokens)",
            "Conduct exit interview & send COBRA health insurance notice"
        ]

        for item in checklist:
            r = tk.Frame(body, bg=self.colors["white"])
            r.pack(fill="x", pady=2)
            tk.Label(r, text="☑", font=("Segoe UI", 8, "bold"), fg=self.colors["primary_orange"], bg=self.colors["white"]).pack(side="left", padx=(0, 6))
            tk.Label(r, text=item, font=("Segoe UI", 7), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(side="left")

        tk.Label(body, text="Reason for Departure:", font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(anchor="w", pady=(12, 2))
        reason_cb = ttk.Combobox(body, values=["Voluntary Resignation", "Contract Completion", "Relocation / Retirement", "Mutual Agreement"], state="readonly")
        reason_cb.set("Voluntary Resignation")
        reason_cb.pack(fill="x")

        def _confirm_offboard():
            emp["status"] = "Offboarded"
            modal.destroy()
            self.update_workforce_stats()
            self.render_table_rows()
            messagebox.showinfo("Offboarding Executed", f"✓ {emp['name']} has been transitioned to Offboarded status.\nHistorical records remain preserved.", parent=self)

        footer = tk.Frame(modal, bg=self.colors["white"], padx=20, pady=12)
        footer.pack(fill="x", side="bottom")

        tk.Button(footer, text="Cancel", font=("Segoe UI", 8, "bold"), bg=self.colors["sidebar_bg"], fg=self.colors["dark_teal"], bd=0, relief="flat", cursor="hand2", padx=12, pady=6, command=modal.destroy).pack(side="right", padx=(8, 0))
        tk.Button(footer, text="Confirm Offboarding ⚠️", font=("Segoe UI", 8, "bold"), bg="#E02424", fg=self.colors["white"], bd=0, relief="flat", cursor="hand2", padx=14, pady=6, command=_confirm_offboard).pack(side="right")

    # =========================================================================
    # DOCUMENT & COMPLIANCE VAULT MODAL
    # =========================================================================
    def show_compliance_vault_modal(self):
        """Displays organization-wide statutory compliance audit and vault records."""
        modal = tk.Toplevel(self)
        modal.title("Organization Document & Compliance Vault")
        modal.geometry("520x480")
        modal.resizable(False, False)
        modal.configure(bg=self.colors["white"])
        modal.transient(self)
        modal.grab_set()

        hdr = tk.Frame(modal, bg=self.colors["sidebar_bg"], padx=20, pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text="STATUTORY & HR COMPLIANCE VAULT", font=("Segoe UI", 8, "bold"), fg=self.colors["primary_orange"], bg=self.colors["sidebar_bg"]).pack(anchor="w")
        tk.Label(hdr, text="Workforce Compliance Records & Verification Audit", font=("Segoe UI", 12, "bold"), fg=self.colors["dark_teal"], bg=self.colors["sidebar_bg"]).pack(anchor="w", pady=(2, 0))

        body = tk.Frame(modal, bg=self.colors["white"], padx=20, pady=14)
        body.pack(fill="both", expand=True)

        records = [
            ("IRS Form W-4 Withholding Certificates", "100% Verified", "All employee tax withholding forms validated for 2026 tax year."),
            ("USCIS Form I-9 Employment Eligibility", "100% Authorized", "Identity and legal employment authorizations on digital file."),
            ("Direct Deposit EFT Authorizations", "100% Active", "Bank routing and account confirmations on secure record."),
            ("Company Policy & Confidentiality NDA", "Completed", "Annual ethics, data privacy, and security training signed."),
            ("OSHA & Department of Labor Postings", "Current", "Required digital workplace rights and fair wage notices distributed.")
        ]

        for title, status, sub in records:
            box = tk.Frame(body, bg="#F9FCFC", highlightbackground=self.colors["border_light"], highlightthickness=1, padx=12, pady=8)
            box.pack(fill="x", pady=3)

            top_r = tk.Frame(box, bg="#F9FCFC")
            top_r.pack(fill="x")
            tk.Label(top_r, text=f"🔒 {title}", font=("Segoe UI", 8, "bold"), fg=self.colors["text_dark"], bg="#F9FCFC").pack(side="left")
            tk.Label(top_r, text=status, font=("Segoe UI", 7, "bold"), bg=self.colors["pill_approved"], fg=self.colors["pill_approved_text"], padx=5, pady=1).pack(side="right")

            tk.Label(box, text=sub, font=("Segoe UI", 7), fg=self.colors["gray_text"], bg="#F9FCFC").pack(anchor="w", pady=(2, 0))

        tk.Button(modal, text="Close Vault", font=("Segoe UI", 8, "bold"), bg=self.colors["sidebar_bg"], fg=self.colors["dark_teal"], bd=0, relief="flat", cursor="hand2", padx=14, pady=6, command=modal.destroy).pack(padx=20, pady=12, anchor="e")

    # =========================================================================
    # EXPORT DIRECTORY TO CSV
    # =========================================================================
    def export_employee_directory_csv(self):
        """Exports the active workforce master records into a standard CSV file."""
        default_file = f"Steadypay_Workforce_Directory_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
        filepath = filedialog.asksaveasfilename(
            parent=self,
            title="Export Workforce Directory",
            defaultextension=".csv",
            initialfile=default_file,
            filetypes=[("CSV Spreadsheet", "*.csv"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Steadypay Master Workforce Directory"])
                writer.writerow(["Exported Date", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                writer.writerow([])
                writer.writerow([
                    "Employee ID", "Full Name", "Position Title", "Department",
                    "Monthly Salary ($)", "Employment Status", "Work Email", "Phone",
                    "Hire Date", "Employment Type", "Bank Account", "W-4 Filing", "PTO Balance"
                ])

                for emp in self.employees:
                    writer.writerow([
                        emp["id"], emp["name"], emp["role"], emp["dept"],
                        f"{emp['salary']:.2f}", emp["status"], emp["email"], emp["phone"],
                        emp["hire_date"], emp["emp_type"], emp["bank_account"], emp["tax_status"], emp["pto_balance"]
                    ])

            messagebox.showinfo("Export Successful", f"Master employee directory exported to:\n{filepath}", parent=self)
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not export CSV file:\n{str(e)}", parent=self)

    # ==========================================
    # NAVIGATION & LOGOUT HANDLERS
    # ==========================================
    def navigate_to_dashboard(self):
        self.destroy()
        dashboard_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aDashboard.py")
        if os.path.exists(dashboard_script):
            subprocess.Popen([sys.executable, dashboard_script])

    def handle_logout(self):
        self.destroy()
        login_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "login.py")
        if os.path.exists(login_script):
            subprocess.Popen([sys.executable, login_script])

if __name__ == "__main__":
    app = SteadypayEmployeePage()
    app.mainloop()
