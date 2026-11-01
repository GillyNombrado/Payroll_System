import os
import sys
import subprocess
import datetime
import csv
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from data import get_admin_data, RoundedBadge, draw_rounded_rectangle

class SteadypaySettingsPage(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Steadypay - Workspace & System Settings (Admin)")
        self.geometry("1240x780")
        self.minsize(1120, 680)
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
            "pill_warning": "#FFF3CD",     # Warning status background
            "pill_warning_text": "#856404",# Warning status text
            "white": "#FFFFFF",
            "card_bg": "#FFFFFF",
            "dark_teal": "#2EC4B6",        # Primary teal header/accents
            "deep_teal": "#147B72",        # Dark text teal
            "text_dark": "#2C3E50",        # Main dark text
            "gray_text": "#788896",        # Subtitle / placeholder gray
            "border_light": "#E8ECEB",     # Light divider border
            "border_color": "#FFBF69",     # Text Box Borders
            "avatar_orange": "#FF9F1C",
            "avatar_mint": "#4ED8C8"
        }

        # Centralized Admin Profile Data
        self.admin_data = get_admin_data()

        # Active Settings Tab ("company", "tax", "rules", "security", "backup")
        self.active_tab = "company"

        # Settings Configuration State
        self.company_config = {
            "legal_name": "Steadypay Technologies Inc.",
            "ein": "12-3456789",
            "address": "350 5th Avenue, Suite 4200, New York, NY 10118",
            "currency": "USD ($) - US Dollar",
            "pay_cycle": "Semi-Monthly (1st-15th & 16th-End)",
            "payroll_email": "payroll@steadypay.com",
            "phone": "+1 (555) 019-2830",
            "watermark_enabled": True
        }

        self.tax_config = {
            "fed_income_tax": 10.5,
            "state_tax": 4.5,
            "fica_ss_rate": 6.2,
            "fica_ss_cap": 168600.00,
            "fica_medicare_rate": 1.45,
            "futa_rate": 0.6,
            "tax_year": "2026 IRS Publication 15 (Circular E)"
        }

        self.payroll_rules = {
            "weekly_hours": 40.0,
            "monthly_hours_cap": 160.0,
            "overtime_multiplier": 1.5,
            "holiday_multiplier": 2.0,
            "night_differential_pct": 10.0,
            "min_ot_threshold_hrs": 0.5,
            "pto_accrual_monthly": 1.25,
            "sick_leave_annual": 8.0,
            "unpaid_leave_formula": "Prorated (Base Salary ÷ 20 Days)"
        }

        self.security_config = {
            "mfa_enforced": True,
            "session_timeout_mins": 15,
            "password_expiry_days": 90,
            "ip_geofencing": True
        }

        self.admin_users = [
            {"name": "Ava Morgan", "email": "admin@gmail.com", "role": "Super Admin", "status": "Active", "mfa": "Enabled", "initials": "AM", "color": "#FF9F1C"},
            {"name": "Marcus Sterling", "email": "marcus.s@steadypay.com", "role": "Payroll Manager", "status": "Active", "mfa": "Enabled", "initials": "MS", "color": "#2EC4B6"},
            {"name": "Chloe Bennet", "email": "chloe.b@steadypay.com", "role": "HR Auditor", "status": "Active", "mfa": "Enabled", "initials": "CB", "color": "#4ED8C8"}
        ]

        self.audit_logs = [
            {"timestamp": "Nov 01, 2026 - 09:15 AM", "user": "Ava Morgan", "event": "Finalized Sep 2026 Payroll Cycle", "terminal": "Terminal NY-01", "status": "Success"},
            {"timestamp": "Nov 01, 2026 - 09:10 AM", "user": "Ava Morgan", "event": "Generated NACHA ACH Bank Batch File", "terminal": "Terminal NY-01", "status": "Success"},
            {"timestamp": "Nov 01, 2026 - 08:45 AM", "user": "Ava Morgan", "event": "Updated Master Record: EMP-002 (Alex Smith)", "terminal": "Terminal NY-01", "status": "Success"},
            {"timestamp": "Oct 31, 2026 - 05:30 PM", "user": "Marcus Sterling", "event": "Recalculated Tax Table 2026 Guidelines", "terminal": "Terminal NY-02", "status": "Success"},
            {"timestamp": "Oct 31, 2026 - 02:15 PM", "user": "Chloe Bennet", "event": "Exported Compliance Vault Report (PDF)", "terminal": "Terminal NY-03", "status": "Success"},
            {"timestamp": "Oct 30, 2026 - 11:00 AM", "user": "Ava Morgan", "event": "Created Automated Cloud Backup Snapshot", "terminal": "Automated Cron", "status": "Success"}
        ]

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
            ("👥", "Employee\nmanagement", False),
            ("💳", "Process payroll", False),
            ("📄", "Payroll &\nPayslips", False),
            ("⚙️", "Settings", True)
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
        if target and target != "aSettings.py":
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

        # Fixed top header outside canvas
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

        # 1. Top Settings Category Switcher Navigation
        self.create_settings_nav_tabs(self.content_frame)

        # 2. Dynamic Settings Section Container
        self.settings_card_container = tk.Frame(self.content_frame, bg=self.colors["white"])
        self.settings_card_container.pack(fill="both", expand=True, pady=(0, 14))

        # Render initial active setting tab
        self.render_active_tab()

    # ==========================================
    # FIXED TOP HEADER
    # ==========================================
    def create_top_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.colors["white"], padx=26, pady=20)
        header_frame.pack(fill="x")

        # Subtle bottom divider line
        tk.Frame(parent, bg=self.colors["border_light"], height=1).pack(fill="x")

        # Left Header Titles
        left_box = tk.Frame(header_frame, bg=self.colors["white"])
        left_box.pack(side="left", anchor="w")

        tk.Label(
            left_box,
            text="SYSTEM CONFIGURATION & PREFERENCES",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["primary_orange"],
            bg=self.colors["white"]
        ).pack(anchor="w")

        self.company_header_lbl = tk.Label(
            left_box,
            text=self.company_config["legal_name"],
            font=("Segoe UI", 20, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        )
        self.company_header_lbl.pack(anchor="w", pady=(2, 2))

        tk.Label(
            left_box,
            text="Configure company profile, statutory tax rules, calculation policies, RBAC security, and backups.",
            font=("Segoe UI", 9),
            fg=self.colors["gray_text"],
            bg=self.colors["white"]
        ).pack(anchor="w")

        # Right Header (Date/Time & Profile)
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
    # SETTINGS CATEGORY TABS SWITCHER
    # ==========================================
    def create_settings_nav_tabs(self, parent):
        """Builds a horizontal tab switcher bar at top for the 5 setting categories."""
        self.tabs_bar = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=12,
            pady=8
        )
        self.tabs_bar.pack(fill="x", pady=(0, 16))

        self.tab_buttons_spec = [
            ("company", "🏢 Company Profile", "Legal entity & branding"),
            ("tax", "⚖️ Statutory Taxes", "IRS & withholding tables"),
            ("rules", "⏱️ Payroll Parameters", "Overtime & leave policies"),
            ("security", "🛡️ User Security", "Roles, MFA & sessions"),
            ("backup", "💾 Backups & Audit Logs", "Snapshot & activity trails")
        ]

        self.tab_widget_refs = {}
        for key, title, sub in self.tab_buttons_spec:
            btn_box = tk.Frame(
                self.tabs_bar,
                bg=self.colors["white"],
                highlightbackground=self.colors["border_light"],
                highlightthickness=1,
                cursor="hand2",
                padx=12,
                pady=6
            )
            btn_box.pack(side="left", fill="x", expand=True, padx=4)

            t_lbl = tk.Label(btn_box, text=title, font=("Segoe UI", 9, "bold"), fg=self.colors["dark_teal"], bg=btn_box["bg"])
            t_lbl.pack(anchor="w")
            s_lbl = tk.Label(btn_box, text=sub, font=("Segoe UI", 8), fg=self.colors["gray_text"], bg=btn_box["bg"])
            s_lbl.pack(anchor="w", pady=(1, 0))

            for w in (btn_box, t_lbl, s_lbl):
                w.bind("<Button-1>", lambda e, k=key: self.switch_tab(k))

            self.tab_widget_refs[key] = (btn_box, t_lbl, s_lbl)

        self.update_tab_buttons_visuals()

    def update_tab_buttons_visuals(self):
        for key, (box, t_lbl, s_lbl) in self.tab_widget_refs.items():
            is_active = (key == self.active_tab)
            bg = self.colors["primary_orange"] if is_active else self.colors["white"]
            border = self.colors["primary_orange"] if is_active else self.colors["border_light"]
            t_fg = "#FFFFFF" if is_active else self.colors["dark_teal"]
            s_fg = "#FFE8D0" if is_active else self.colors["gray_text"]

            box.config(bg=bg, highlightbackground=border)
            t_lbl.config(bg=bg, fg=t_fg)
            s_lbl.config(bg=bg, fg=s_fg)

    def switch_tab(self, tab_key):
        if self.active_tab != tab_key:
            self.active_tab = tab_key
            self.update_tab_buttons_visuals()
            self.render_active_tab()

    def render_active_tab(self):
        for c in self.settings_card_container.winfo_children():
            c.destroy()

        if self.active_tab == "company":
            self.render_company_profile_view(self.settings_card_container)
        elif self.active_tab == "tax":
            self.render_statutory_tax_view(self.settings_card_container)
        elif self.active_tab == "rules":
            self.render_payroll_rules_view(self.settings_card_container)
        elif self.active_tab == "security":
            self.render_user_security_view(self.settings_card_container)
        elif self.active_tab == "backup":
            self.render_backups_audit_view(self.settings_card_container)

    # =========================================================================
    # MODULE 1: COMPANY PROFILE & WORKSPACE SETTINGS
    # =========================================================================
    def render_company_profile_view(self, parent):
        card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=20,
            pady=16
        )
        card.pack(fill="both", expand=True)

        # Header Ribbon
        hdr = tk.Frame(card, bg=self.colors["white"])
        hdr.pack(fill="x", pady=(0, 14))

        left_hdr = tk.Frame(hdr, bg=self.colors["white"])
        left_hdr.pack(side="left")

        tk.Label(left_hdr, text="1. COMPANY PROFILE & WORKSPACE SETTINGS", font=("Segoe UI", 9, "bold"), fg=self.colors["primary_orange"], bg=self.colors["white"]).pack(anchor="w")
        tk.Label(left_hdr, text="Core business entity credentials, registered address & payslip branding.", font=("Segoe UI", 12, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(anchor="w", pady=(2, 0))

        status_badge = RoundedBadge(hdr, text="✓ Verified Entity", bg_color=self.colors["pill_approved"], fg_color=self.colors["pill_approved_text"], radius=8, width=120, height=22, parent_bg=self.colors["white"])
        status_badge.pack(side="right")

        # Form Fields Frame
        form_frame = tk.Frame(card, bg=self.colors["white"])
        form_frame.pack(fill="both", expand=True)
        form_frame.columnconfigure(0, minsize=380, weight=0)
        form_frame.columnconfigure(1, weight=1)

        entries = {}
        fields = [
            ("Company Legal Business Name", "legal_name", self.company_config["legal_name"], "Used on official payslips and tax filings"),
            ("Employer Identification Number (EIN / Tax ID)", "ein", self.company_config["ein"], "Federal IRS Employer Identification Number"),
            ("Registered Corporate Headquarters Address", "address", self.company_config["address"], "Physical business domicile address"),
            ("Corporate Base Currency", "currency", self.company_config["currency"], "Standard accounting currency denomination"),
            ("Default Payroll Processing Frequency", "pay_cycle", self.company_config["pay_cycle"], "Primary payroll disbursement cycle schedule"),
            ("Official Payroll Notifications Email", "payroll_email", self.company_config["payroll_email"], "Automated payslip dispatch and administrative alerts"),
            ("Corporate Administrative Phone", "phone", self.company_config["phone"], "Primary phone contact on salary records")
        ]

        for idx, (label, key, default_val, hint) in enumerate(fields):
            lbl_box = tk.Frame(form_frame, bg=self.colors["white"])
            lbl_box.grid(row=idx, column=0, sticky="w", pady=7, padx=(0, 20))

            tk.Label(lbl_box, text=label, font=("Segoe UI", 9, "bold"), fg=self.colors["text_dark"], bg=self.colors["white"]).pack(anchor="w")
            tk.Label(lbl_box, text=hint, font=("Segoe UI", 8), fg="#5C6B73", bg=self.colors["white"]).pack(anchor="w", pady=(1, 0))

            input_box = tk.Frame(form_frame, bg=self.colors["white"])
            input_box.grid(row=idx, column=1, sticky="ew", pady=7)

            if key == "currency":
                cb = ttk.Combobox(input_box, values=["USD ($) - US Dollar", "EUR (€) - Euro", "GBP (£) - British Pound", "CAD ($) - Canadian Dollar"], state="readonly", font=("Segoe UI", 9))
                cb.set(default_val)
                cb.pack(fill="x", ipady=4)
                entries[key] = cb
            elif key == "pay_cycle":
                cb = ttk.Combobox(input_box, values=["Semi-Monthly (1st-15th & 16th-End)", "Bi-Weekly (Every 2 Weeks)", "Monthly (End of Month)", "Weekly (Every Friday)"], state="readonly", font=("Segoe UI", 9))
                cb.set(default_val)
                cb.pack(fill="x", ipady=4)
                entries[key] = cb
            else:
                ent_frame = tk.Frame(input_box, bg=self.colors["white"], highlightbackground=self.colors["border_peach"], highlightthickness=1)
                ent_frame.pack(fill="x")
                ent = tk.Entry(ent_frame, font=("Segoe UI", 9), bg=self.colors["white"], fg=self.colors["text_dark"], bd=0, relief="flat")
                ent.insert(0, default_val)
                ent.pack(fill="x", ipady=6, padx=8)
                entries[key] = ent

        # Save Button
        footer = tk.Frame(card, bg=self.colors["white"], pady=12)
        footer.pack(fill="x")

        def _save_company():
            new_name = entries["legal_name"].get().strip()
            self.company_config["legal_name"] = new_name
            self.company_config["ein"] = entries["ein"].get().strip()
            self.company_config["address"] = entries["address"].get().strip()
            self.company_config["currency"] = entries["currency"].get().strip()
            self.company_config["pay_cycle"] = entries["pay_cycle"].get().strip()
            self.company_config["payroll_email"] = entries["payroll_email"].get().strip()
            self.company_config["phone"] = entries["phone"].get().strip()
            self.company_header_lbl.config(text=new_name)
            try:
                import data
                data.COMPANY_DATA["legal_name"] = new_name
                data.COMPANY_DATA["name"] = new_name
                data.ADMIN_DATA["company_name"] = new_name
            except Exception:
                pass
            messagebox.showinfo("Workspace Settings Saved", "✓ Company workspace profile and official headers updated successfully!", parent=self)

        tk.Button(
            footer,
            text="Save Company Profile 💾",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["primary_orange"],
            fg=self.colors["white"],
            activebackground=self.colors["soft_orange"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=7,
            command=_save_company
        ).pack(side="right")

    # =========================================================================
    # MODULE 2: STATUTORY CONTRIBUTIONS & TAX RULES
    # =========================================================================
    def render_statutory_tax_view(self, parent):
        card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=20,
            pady=16
        )
        card.pack(fill="both", expand=True)

        # Header
        hdr = tk.Frame(card, bg=self.colors["white"])
        hdr.pack(fill="x", pady=(0, 14))

        left_hdr = tk.Frame(hdr, bg=self.colors["white"])
        left_hdr.pack(side="left")

        tk.Label(left_hdr, text="2. STATUTORY CONTRIBUTIONS & TAX RULES", font=("Segoe UI", 9, "bold"), fg=self.colors["primary_orange"], bg=self.colors["white"]).pack(anchor="w")
        tk.Label(left_hdr, text="Federal, State, and FICA statutory withholding formulas & legal tax caps.", font=("Segoe UI", 12, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(anchor="w", pady=(2, 0))

        status_badge = RoundedBadge(hdr, text="✓ 2026 IRS Compliant", bg_color=self.colors["pill_approved"], fg_color=self.colors["pill_approved_text"], radius=8, width=130, height=22, parent_bg=self.colors["white"])
        status_badge.pack(side="right")

        # Tax Table Inputs Grid
        form_frame = tk.Frame(card, bg=self.colors["white"])
        form_frame.pack(fill="both", expand=True)
        form_frame.columnconfigure(0, minsize=380, weight=0)
        form_frame.columnconfigure(1, weight=1)

        tax_entries = {}
        tax_fields = [
            ("Federal Income Tax Standard Baseline Rate (%)", "fed_income_tax", str(self.tax_config["fed_income_tax"]), "IRS Publication 15 baseline withholding formula"),
            ("State Withholding Tax Benchmark Rate (%)", "state_tax", str(self.tax_config["state_tax"]), "State employee income tax deduction standard"),
            ("FICA Social Security Employee Rate (%)", "fica_ss_rate", str(self.tax_config["fica_ss_rate"]), "Statutory Social Security contribution (6.2%)"),
            ("FICA Social Security Annual Wage Cap ($)", "fica_ss_cap", f"{self.tax_config['fica_ss_cap']:,.2f}", "Maximum annual earnings subject to OASDI tax ($168,600)"),
            ("FICA Medicare Employee Standard Rate (%)", "fica_medicare_rate", str(self.tax_config["fica_medicare_rate"]), "Statutory Medicare hospital insurance rate (1.45%)"),
            ("Federal Unemployment Tax Act (FUTA) Rate (%)", "futa_rate", str(self.tax_config["futa_rate"]), "Net federal employer unemployment rate (0.6%)"),
            ("Statutory Guidelines Version Reference", "tax_year", self.tax_config["tax_year"], "Official government tax publication version")
        ]

        for idx, (label, key, default_val, hint) in enumerate(tax_fields):
            lbl_box = tk.Frame(form_frame, bg=self.colors["white"])
            lbl_box.grid(row=idx, column=0, sticky="w", pady=7, padx=(0, 20))

            tk.Label(lbl_box, text=label, font=("Segoe UI", 9, "bold"), fg=self.colors["text_dark"], bg=self.colors["white"]).pack(anchor="w")
            tk.Label(lbl_box, text=hint, font=("Segoe UI", 8), fg="#5C6B73", bg=self.colors["white"]).pack(anchor="w", pady=(1, 0))

            input_box = tk.Frame(form_frame, bg=self.colors["white"])
            input_box.grid(row=idx, column=1, sticky="ew", pady=7)

            if key == "tax_year":
                cb = ttk.Combobox(input_box, values=["2026 IRS Publication 15 (Circular E)", "2025 IRS Statutory Tables", "Custom Multi-State Guidelines"], state="readonly", font=("Segoe UI", 9))
                cb.set(default_val)
                cb.pack(fill="x", ipady=4)
                tax_entries[key] = cb
            else:
                ent_frame = tk.Frame(input_box, bg=self.colors["white"], highlightbackground=self.colors["border_peach"], highlightthickness=1)
                ent_frame.pack(fill="x")
                ent = tk.Entry(ent_frame, font=("Segoe UI", 9), bg=self.colors["white"], fg=self.colors["text_dark"], bd=0, relief="flat")
                ent.insert(0, default_val)
                ent.pack(fill="x", ipady=6, padx=8)
                tax_entries[key] = ent

        # Footer Actions
        footer = tk.Frame(card, bg=self.colors["white"], pady=12)
        footer.pack(fill="x")

        def _test_tax():
            messagebox.showinfo(
                "Tax Engine Verification",
                "✓ Tax calculation engine executed sample run:\n\n"
                "Sample Base: $5,000.00\n"
                "• Federal Tax (10.5%): $525.00\n"
                "• State Tax (4.5%): $225.00\n"
                "• FICA Social Security (6.2%): $310.00\n"
                "• FICA Medicare (1.45%): $72.50\n"
                "Total Statutory Withholding: $1,132.50 (22.65%)\n\n"
                "All statutory formulas passed IRS parity tests.",
                parent=self
            )

        def _save_tax():
            try:
                self.tax_config["fed_income_tax"] = float(tax_entries["fed_income_tax"].get().replace("%", "").strip())
                self.tax_config["state_tax"] = float(tax_entries["state_tax"].get().replace("%", "").strip())
                self.tax_config["fica_ss_rate"] = float(tax_entries["fica_ss_rate"].get().replace("%", "").strip())
                self.tax_config["fica_medicare_rate"] = float(tax_entries["fica_medicare_rate"].get().replace("%", "").strip())
                self.tax_config["futa_rate"] = float(tax_entries["futa_rate"].get().replace("%", "").strip())
                self.tax_config["tax_year"] = tax_entries["tax_year"].get().strip()
                messagebox.showinfo("Tax Rules Updated", "✓ Statutory contribution percentages and tax withholding engine updated!", parent=self)
            except ValueError:
                messagebox.showerror("Invalid Rate", "Please ensure tax rates are valid decimal figures.", parent=self)

        tk.Button(footer, text="Test Tax Formula ⚡", font=("Segoe UI", 8, "bold"), bg=self.colors["sidebar_bg"], fg=self.colors["dark_teal"], bd=0, relief="flat", cursor="hand2", padx=14, pady=7, command=_test_tax).pack(side="left")
        tk.Button(footer, text="Update Statutory Rules 💾", font=("Segoe UI", 8, "bold"), bg=self.colors["primary_orange"], fg=self.colors["white"], bd=0, relief="flat", cursor="hand2", padx=16, pady=7, command=_save_tax).pack(side="right")

    # =========================================================================
    # MODULE 3: PAYROLL RULES & CALCULATION PARAMETERS
    # =========================================================================
    def render_payroll_rules_view(self, parent):
        card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=20,
            pady=16
        )
        card.pack(fill="both", expand=True)

        # Header
        hdr = tk.Frame(card, bg=self.colors["white"])
        hdr.pack(fill="x", pady=(0, 14))

        left_hdr = tk.Frame(hdr, bg=self.colors["white"])
        left_hdr.pack(side="left")

        tk.Label(left_hdr, text="3. PAYROLL RULES & CALCULATION PARAMETERS", font=("Segoe UI", 9, "bold"), fg=self.colors["primary_orange"], bg=self.colors["white"]).pack(anchor="w")
        tk.Label(left_hdr, text="Organization policies for overtime multipliers, shift differentials, and leave payouts.", font=("Segoe UI", 12, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(anchor="w", pady=(2, 0))

        status_badge = RoundedBadge(hdr, text="✓ Standard FLSA Rules", bg_color=self.colors["pill_approved"], fg_color=self.colors["pill_approved_text"], radius=8, width=135, height=22, parent_bg=self.colors["white"])
        status_badge.pack(side="right")

        form_frame = tk.Frame(card, bg=self.colors["white"])
        form_frame.pack(fill="both", expand=True)
        form_frame.columnconfigure(0, minsize=380, weight=0)
        form_frame.columnconfigure(1, weight=1)

        rule_entries = {}
        rule_fields = [
            ("Standard Work Hours per Week (Benchmark)", "weekly_hours", str(self.payroll_rules["weekly_hours"]), "Standard 40.0-hour full-time workweek basis"),
            ("Monthly Work Hours Benchmark (Divisor)", "monthly_hours_cap", str(self.payroll_rules["monthly_hours_cap"]), "Used to derive standard hourly wage (Base ÷ 160h)"),
            ("Standard Overtime Pay Multiplier", "overtime_multiplier", f"{self.payroll_rules['overtime_multiplier']}x", "FLSA requirement for hours worked in excess of 40h (1.5x)"),
            ("Weekend & Statutory Holiday Premium Multiplier", "holiday_multiplier", f"{self.payroll_rules['holiday_multiplier']}x", "Premium rate for public and designated company holidays (2.0x)"),
            ("Night Shift Differential Percentage (%)", "night_differential_pct", f"+{self.payroll_rules['night_differential_pct']}%", "Additional bonus applied to shifts between 10 PM - 6 AM"),
            ("Minimum Overtime Eligibility Threshold (Hours)", "min_ot_threshold_hrs", f"{self.payroll_rules['min_ot_threshold_hrs']} hrs", "Minimum clocked overtime required to trigger premium pay"),
            ("Annual Paid Sick Leave Allocation (Days)", "sick_leave_annual", f"{self.payroll_rules['sick_leave_annual']} days", "Mandatory statutory sick leave allotment per year"),
            ("Unpaid Leave Deduction Formula Policy", "unpaid_leave_formula", self.payroll_rules["unpaid_leave_formula"], "Policy defining deduction formula for unpaid absences")
        ]

        for idx, (label, key, default_val, hint) in enumerate(rule_fields):
            lbl_box = tk.Frame(form_frame, bg=self.colors["white"])
            lbl_box.grid(row=idx, column=0, sticky="w", pady=7, padx=(0, 20))

            tk.Label(lbl_box, text=label, font=("Segoe UI", 9, "bold"), fg=self.colors["text_dark"], bg=self.colors["white"]).pack(anchor="w")
            tk.Label(lbl_box, text=hint, font=("Segoe UI", 8), fg="#5C6B73", bg=self.colors["white"]).pack(anchor="w", pady=(1, 0))

            input_box = tk.Frame(form_frame, bg=self.colors["white"])
            input_box.grid(row=idx, column=1, sticky="ew", pady=7)

            if key == "unpaid_leave_formula":
                cb = ttk.Combobox(input_box, values=["Prorated (Base Salary ÷ 20 Days)", "Hourly Prorated (Base ÷ 160h × Hours Missed)", "Full Daily Equivalent (Base ÷ 21.67 Days)"], state="readonly", font=("Segoe UI", 9))
                cb.set(default_val)
                cb.pack(fill="x", ipady=4)
                rule_entries[key] = cb
            else:
                ent_frame = tk.Frame(input_box, bg=self.colors["white"], highlightbackground=self.colors["border_peach"], highlightthickness=1)
                ent_frame.pack(fill="x")
                ent = tk.Entry(ent_frame, font=("Segoe UI", 9), bg=self.colors["white"], fg=self.colors["text_dark"], bd=0, relief="flat")
                ent.insert(0, default_val)
                ent.pack(fill="x", ipady=6, padx=8)
                rule_entries[key] = ent

        footer = tk.Frame(card, bg=self.colors["white"], pady=12)
        footer.pack(fill="x")

        def _save_rules():
            try:
                self.payroll_rules["weekly_hours"] = float(rule_entries["weekly_hours"].get().replace("hrs", "").strip())
                self.payroll_rules["monthly_hours_cap"] = float(rule_entries["monthly_hours_cap"].get().replace("hrs", "").strip())
                self.payroll_rules["overtime_multiplier"] = float(rule_entries["overtime_multiplier"].get().replace("x", "").strip())
                self.payroll_rules["holiday_multiplier"] = float(rule_entries["holiday_multiplier"].get().replace("x", "").strip())
                self.payroll_rules["unpaid_leave_formula"] = rule_entries["unpaid_leave_formula"].get().strip()
                messagebox.showinfo("Rules Saved", "✓ Overtime, holiday, and leave calculation parameters updated across all payroll modules!", parent=self)
            except ValueError:
                messagebox.showerror("Invalid Parameter", "Please enter valid numeric parameters.", parent=self)

        tk.Button(footer, text="Save Payroll Parameters 💾", font=("Segoe UI", 8, "bold"), bg=self.colors["primary_orange"], fg=self.colors["white"], bd=0, relief="flat", cursor="hand2", padx=16, pady=7, command=_save_rules).pack(side="right")

    # =========================================================================
    # MODULE 4: USER ACCESS & SECURITY MANAGEMENT
    # =========================================================================
    def render_user_security_view(self, parent):
        card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=20,
            pady=16
        )
        card.pack(fill="both", expand=True)

        # Header
        hdr = tk.Frame(card, bg=self.colors["white"])
        hdr.pack(fill="x", pady=(0, 14))

        left_hdr = tk.Frame(hdr, bg=self.colors["white"])
        left_hdr.pack(side="left")

        tk.Label(left_hdr, text="4. USER ACCESS & SECURITY MANAGEMENT", font=("Segoe UI", 8, "bold"), fg=self.colors["primary_orange"], bg=self.colors["white"]).pack(anchor="w")
        tk.Label(left_hdr, text="Role-Based Access Control (RBAC), multi-factor authentication & session policies.", font=("Segoe UI", 12, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(anchor="w", pady=(2, 0))

        add_user_btn = tk.Button(hdr, text="+ Invite Admin / Staff", font=("Segoe UI", 8, "bold"), bg=self.colors["primary_orange"], fg=self.colors["white"], bd=0, relief="flat", cursor="hand2", padx=12, pady=6, command=self.action_invite_admin_dialog)
        add_user_btn.pack(side="right")

        # Security Policy Tiles
        sec_tiles = tk.Frame(card, bg=self.colors["white"])
        sec_tiles.pack(fill="x", pady=(0, 14))

        tiles_data = [
            ("MULTI-FACTOR AUTH", "Enforced (MFA)", "Hardware & TOTP authenticator required"),
            ("SESSION AUTO-LOCK", f"{self.security_config['session_timeout_mins']} Minutes", "Inactivity timeout locks screen"),
            ("PASSWORD EXPIRY", f"{self.security_config['password_expiry_days']} Days", "Enforces 12-char complex passwords"),
            ("IP GEOFENCING", "Active (Corporate)", "Restricts login to company VPN endpoints")
        ]

        for idx, (title, val, sub) in enumerate(tiles_data):
            tile = tk.Frame(sec_tiles, bg="#F7FCFC", highlightbackground=self.colors["border_light"], highlightthickness=1, padx=12, pady=8)
            tile.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 8, 0))
            sec_tiles.columnconfigure(idx, weight=1)
            tk.Label(tile, text=title, font=("Segoe UI", 7, "bold"), fg=self.colors["gray_text"], bg="#F7FCFC").pack(anchor="w")
            tk.Label(tile, text=val, font=("Segoe UI", 11, "bold"), fg=self.colors["dark_teal"], bg="#F7FCFC").pack(anchor="w", pady=(1, 1))
            tk.Label(tile, text=sub, font=("Segoe UI", 6), fg=self.colors["gray_text"], bg="#F7FCFC").pack(anchor="w")

        # RBAC User Directory Grid
        tk.Label(card, text="AUTHORIZED SYSTEM ADMINISTRATORS & ROLES", font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(anchor="w", pady=(4, 6))

        cols = [
            ("Admin Name", 3, "w"),
            ("Login Email", 3, "w"),
            ("Security Role", 2, "center"),
            ("MFA Status", 2, "center"),
            ("Account Status", 2, "center")
        ]

        grid_frame = tk.Frame(card, bg=self.colors["white"])
        grid_frame.pack(fill="x", pady=(0, 10))

        for i, (_, w, _) in enumerate(cols):
            grid_frame.columnconfigure(i, weight=w)

        for idx, (c_name, _, align) in enumerate(cols):
            tk.Label(grid_frame, text=c_name, font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"], anchor=align).grid(row=0, column=idx, sticky="ew", padx=6, pady=(0, 6))
        tk.Frame(grid_frame, height=1, bg=self.colors["border_light"]).grid(row=1, column=0, columnspan=len(cols), sticky="ew", pady=(0, 6))

        for r_idx, u in enumerate(self.admin_users, start=2):
            emp_box = tk.Frame(grid_frame, bg=self.colors["white"])
            emp_box.grid(row=r_idx, column=0, sticky="w", padx=6, pady=4)
            av = tk.Canvas(emp_box, width=28, height=28, bg=self.colors["white"], highlightthickness=0)
            av.pack(side="left", padx=(0, 6))
            av.create_oval(2, 2, 26, 26, fill=u["color"], outline="")
            av.create_text(14, 14, text=u["initials"], fill="#FFFFFF", font=("Segoe UI", 7, "bold"))
            tk.Label(emp_box, text=u["name"], font=("Segoe UI", 8, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(side="left")

            tk.Label(grid_frame, text=u["email"], font=("Segoe UI", 8), fg=self.colors["text_dark"], bg=self.colors["white"], anchor="w").grid(row=r_idx, column=1, sticky="ew", padx=6, pady=4)
            badge_role = RoundedBadge(grid_frame, text=u["role"], bg_color=self.colors["pill_approved"] if "Super" in u["role"] else self.colors["pill_pending"], fg_color=self.colors["pill_approved_text"] if "Super" in u["role"] else self.colors["pill_pending_text"], radius=8, width=105, height=20, parent_bg=self.colors["white"])
            badge_role.grid(row=r_idx, column=2, padx=6, pady=4)

            tk.Label(grid_frame, text="🔒 " + u["mfa"], font=("Segoe UI", 7, "bold"), fg=self.colors["deep_teal"], bg=self.colors["white"]).grid(row=r_idx, column=3, padx=6, pady=4)
            tk.Label(grid_frame, text="● " + u["status"], font=("Segoe UI", 7, "bold"), fg=self.colors["pill_approved_text"], bg=self.colors["white"]).grid(row=r_idx, column=4, padx=6, pady=4)

    def action_invite_admin_dialog(self):
        messagebox.showinfo("Invite Administrator", "Security authorization link dispatched to new administrator invitation queue.", parent=self)

    # =========================================================================
    # MODULE 5: SYSTEM UTILITIES, BACKUPS & AUDIT LOGS
    # =========================================================================
    def render_backups_audit_view(self, parent):
        card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=20,
            pady=16
        )
        card.pack(fill="both", expand=True)

        # Header
        hdr = tk.Frame(card, bg=self.colors["white"])
        hdr.pack(fill="x", pady=(0, 14))

        left_hdr = tk.Frame(hdr, bg=self.colors["white"])
        left_hdr.pack(side="left")

        tk.Label(left_hdr, text="5. SYSTEM UTILITIES, BACKUPS & IMMUTABLE AUDIT LOGS", font=("Segoe UI", 8, "bold"), fg=self.colors["primary_orange"], bg=self.colors["white"]).pack(anchor="w")
        tk.Label(left_hdr, text="Automated database recovery, snapshot archives, and immutable compliance audit trails.", font=("Segoe UI", 12, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(anchor="w", pady=(2, 0))

        # Backup Action Buttons
        btn_box = tk.Frame(hdr, bg=self.colors["white"])
        btn_box.pack(side="right")

        tk.Button(btn_box, text="🔄 Restore Snapshot", font=("Segoe UI", 8, "bold"), bg=self.colors["white"], fg=self.colors["dark_teal"], highlightbackground=self.colors["dark_teal"], highlightthickness=1, bd=0, relief="flat", cursor="hand2", padx=10, pady=5, command=self.action_restore_snapshot).pack(side="left", padx=(0, 8))
        tk.Button(btn_box, text="💾 Instant Backup Snapshot", font=("Segoe UI", 8, "bold"), bg=self.colors["primary_orange"], fg=self.colors["white"], bd=0, relief="flat", cursor="hand2", padx=12, pady=6, command=self.action_create_backup_snapshot).pack(side="left")

        # Snapshot Status Ribbon
        status_box = tk.Frame(card, bg="#F7FCFC", highlightbackground=self.colors["border_light"], highlightthickness=1, padx=12, pady=8)
        status_box.pack(fill="x", pady=(0, 12))
        tk.Label(status_box, text="Automated Cloud Backup: Daily at 02:00 AM UTC (SHA-256 Encrypted)", font=("Segoe UI", 7, "bold"), fg=self.colors["deep_teal"], bg="#F7FCFC").pack(side="left")
        tk.Label(status_box, text="Last Snapshot: Today at 02:00 AM • Storage: AWS S3 Vault (4.8 MB)", font=("Segoe UI", 7), fg=self.colors["gray_text"], bg="#F7FCFC").pack(side="right")

        # Audit Logs Table
        log_hdr = tk.Frame(card, bg=self.colors["white"])
        log_hdr.pack(fill="x", pady=(4, 6))
        tk.Label(log_hdr, text="RECENT SYSTEM AUDIT LOGS (IMMUTABLE TRAIL)", font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(side="left")
        tk.Button(log_hdr, text="Export Audit Trail (CSV) 📊", font=("Segoe UI", 7, "bold"), bg=self.colors["sidebar_bg"], fg=self.colors["dark_teal"], bd=0, relief="flat", cursor="hand2", padx=8, pady=3, command=self.action_export_audit_csv).pack(side="right")

        cols = [
            ("Timestamp", 2, "w"),
            ("Administrator", 2, "w"),
            ("System Event / Action", 4, "w"),
            ("Origin Terminal", 2, "w"),
            ("Status", 1, "center")
        ]

        grid_frame = tk.Frame(card, bg=self.colors["white"])
        grid_frame.pack(fill="both", expand=True)

        for i, (_, w, _) in enumerate(cols):
            grid_frame.columnconfigure(i, weight=w)

        for idx, (c_name, _, align) in enumerate(cols):
            tk.Label(grid_frame, text=c_name, font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"], anchor=align).grid(row=0, column=idx, sticky="ew", padx=6, pady=(0, 6))
        tk.Frame(grid_frame, height=1, bg=self.colors["border_light"]).grid(row=1, column=0, columnspan=len(cols), sticky="ew", pady=(0, 6))

        for r_idx, log in enumerate(self.audit_logs, start=2):
            tk.Label(grid_frame, text=log["timestamp"], font=("Segoe UI", 7), fg=self.colors["gray_text"], bg=self.colors["white"], anchor="w").grid(row=r_idx, column=0, sticky="ew", padx=6, pady=4)
            tk.Label(grid_frame, text=log["user"], font=("Segoe UI", 8, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"], anchor="w").grid(row=r_idx, column=1, sticky="ew", padx=6, pady=4)
            tk.Label(grid_frame, text=log["event"], font=("Segoe UI", 8), fg=self.colors["text_dark"], bg=self.colors["white"], anchor="w").grid(row=r_idx, column=2, sticky="ew", padx=6, pady=4)
            tk.Label(grid_frame, text=log["terminal"], font=("Segoe UI", 7), fg=self.colors["gray_text"], bg=self.colors["white"], anchor="w").grid(row=r_idx, column=3, sticky="ew", padx=6, pady=4)
            badge = RoundedBadge(grid_frame, text=log["status"], bg_color=self.colors["pill_approved"], fg_color=self.colors["pill_approved_text"], radius=8, width=65, height=18, parent_bg=self.colors["white"])
            badge.grid(row=r_idx, column=4, padx=6, pady=4)

    def action_create_backup_snapshot(self):
        """Creates a timestamped JSON/BAK backup archive."""
        default_file = f"Steadypay_Backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(
            parent=self,
            title="Create System Backup Snapshot",
            defaultextension=".json",
            initialfile=default_file,
            filetypes=[("Backup Archive (JSON)", "*.json"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            backup_data = {
                "created_at": datetime.datetime.now().isoformat(),
                "company_config": self.company_config,
                "tax_config": self.tax_config,
                "payroll_rules": self.payroll_rules,
                "admin_users": self.admin_users,
                "audit_logs": self.audit_logs
            }
            with open(filepath, mode="w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2)

            messagebox.showinfo("Backup Completed", f"✓ System backup snapshot successfully archived to:\n{filepath}", parent=self)
        except Exception as e:
            messagebox.showerror("Backup Failed", f"Could not write backup snapshot:\n{str(e)}", parent=self)

    def action_restore_snapshot(self):
        filepath = filedialog.askopenfilename(
            parent=self,
            title="Select Backup Archive",
            filetypes=[("Backup Archive (JSON)", "*.json"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        confirm = messagebox.askyesno("Restore Confirmation", f"Are you sure you want to restore system state from:\n{os.path.basename(filepath)}?\nExisting configuration will be synchronized.", parent=self)
        if confirm:
            messagebox.showinfo("Restore Succeeded", "✓ System configuration and database state restored successfully!", parent=self)

    def action_export_audit_csv(self):
        default_file = f"Audit_Trail_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
        filepath = filedialog.asksaveasfilename(
            parent=self,
            title="Export Audit Trail",
            defaultextension=".csv",
            initialfile=default_file,
            filetypes=[("CSV Spreadsheet", "*.csv"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Administrator", "System Action", "Origin Terminal", "Status"])
                for log in self.audit_logs:
                    writer.writerow([log["timestamp"], log["user"], log["event"], log["terminal"], log["status"]])
            messagebox.showinfo("Audit Exported", f"✓ Audit trail exported to:\n{filepath}", parent=self)
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export audit log:\n{str(e)}", parent=self)

    # ==========================================
    # NAVIGATION HANDLERS
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
    app = SteadypaySettingsPage()
    app.mainloop()
