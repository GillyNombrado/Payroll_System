import os
import sys
import subprocess
import datetime
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from data import (
    get_admin_data, get_all_employees,
    draw_rounded_rectangle, RoundedBadge
)

class SteadypayPayrollPayslipsPage(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Steadypay - Payroll & Payslips (Admin)")
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
            "pill_draft": "#ECEFF1",       # Draft status background
            "pill_draft_text": "#607D8B",  # Draft status text
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

        # Centralized Admin Data
        self.admin_data = get_admin_data()

        # Pay Period State
        self.pay_periods = [
            "Sep 16 - Sep 30, 2026 (Current)",
            "Sep 01 - Sep 15, 2026",
            "Aug 16 - Aug 31, 2026",
            "Aug 01 - Aug 15, 2026"
        ]
        self.current_period_var = tk.StringVar(value=self.pay_periods[0])
        self.period_status_map = {
            "Sep 16 - Sep 30, 2026 (Current)": "Approved & Locked",
            "Sep 01 - Sep 15, 2026": "Approved & Locked",
            "Aug 16 - Aug 31, 2026": "Approved & Locked",
            "Aug 01 - Aug 15, 2026": "Approved & Locked"
        }

        # Initial Master Employee Payroll Records
        self.init_payroll_master_data()

        # Search, Filter and Sort variables
        self._search_placeholder = "Search employee, ID, or role..."
        self.search_var = tk.StringVar(value="")
        self.dept_filter_var = tk.StringVar(value="All Departments")
        self.sort_var = tk.StringVar(value="Employee ID")

        # Layout Setup
        self.setup_layout()

    # ==========================================
    # DATA INITIALIZATION & CALCULATION ENGINE
    # ==========================================
    def init_payroll_master_data(self):
        """Initializes full ledger records with base, overtime, tax withholdings, and benefits."""
        raw_employees = get_all_employees()
        self.payroll_records = []

        dept_lookup = {
            "EMP-101": "Design",
            "EMP-102": "Operations",
            "EMP-103": "Finance",
            "EMP-104": "Customer Support",
            "EMP-105": "Human Resources"
        }

        base_lookup = {
            "EMP-101": 5200.00,
            "EMP-102": 5500.00,
            "EMP-103": 5400.00,
            "EMP-104": 4500.00,
            "EMP-105": 5100.00
        }

        ot_lookup = {
            "EMP-101": 300.00,
            "EMP-102": 400.00,
            "EMP-103": 300.00,
            "EMP-104": 300.00,
            "EMP-105": 350.00
        }

        for emp in raw_employees:
            eid = emp["id"]
            dept = dept_lookup.get(eid, "Operations")
            base = base_lookup.get(eid, 5000.00)
            ot = ot_lookup.get(eid, 250.00)
            rec = self.calculate_individual_payroll(emp, dept, base, ot)
            self.payroll_records.append(rec)

    def calculate_individual_payroll(self, emp, dept, base, overtime):
        """Computes gross pay, taxes, benefit deductions, and net pay."""
        gross_pay = base + overtime

        # Taxes: Federal/State Income Tax (approx 10.5%), FICA Social Security & Medicare (7.65%)
        tax_withholding = round(gross_pay * 0.1815, 2)
        # Benefits: Health Insurance contribution + 401(k) retirement (approx 4.5%)
        benefits = round(gross_pay * 0.045, 2)
        total_deductions = round(tax_withholding + benefits, 2)
        net_pay = round(gross_pay - total_deductions, 2)

        return {
            "id": emp["id"],
            "name": emp["name"],
            "initials": emp["initials"],
            "role": emp["role"],
            "email": emp["email"],
            "phone": emp["phone"],
            "dept": dept,
            "avatar_color": emp["avatar_color"],
            "hours_logged": emp.get("hours_logged", 160.0),
            "base_salary": base,
            "overtime": overtime,
            "gross_pay": gross_pay,
            "tax_withholding": tax_withholding,
            "benefit_deductions": benefits,
            "total_deductions": total_deductions,
            "net_pay": net_pay,
            "status": "Paid" if emp["status"] == "Approved" else "Pending"
        }

    def recalculate_all_payroll(self):
        """Action handler to re-compute payroll across all employees for the selected period."""
        current_period = self.current_period_var.get()
        is_locked = self.period_status_map.get(current_period, "Draft") == "Approved & Locked"

        if is_locked:
            confirm = messagebox.askyesno(
                "Period Locked",
                f"The pay period '{current_period}' is currently Approved & Locked.\n\n"
                "Do you want to temporarily unlock it to recalculate gross pay, overtime, and tax withholdings?",
                parent=self
            )
            if not confirm:
                return
            self.period_status_map[current_period] = "Pending Approval"
            self.update_period_status_ui()

        # Perform recalculated variance based on chosen period
        factor = 1.0
        if "Sep 01" in current_period:
            factor = 0.98
        elif "Aug 16" in current_period:
            factor = 1.02
        elif "Aug 01" in current_period:
            factor = 0.95

        for rec in self.payroll_records:
            base = round(rec["base_salary"] * factor, 2)
            ot = round(rec["overtime"] * (1.1 if factor > 1 else 0.9), 2)
            gross = base + ot
            tax = round(gross * 0.1815, 2)
            benefits = round(gross * 0.045, 2)
            deductions = round(tax + benefits, 2)
            net = round(gross - deductions, 2)

            rec["base_salary"] = base
            rec["overtime"] = ot
            rec["gross_pay"] = gross
            rec["tax_withholding"] = tax
            rec["benefit_deductions"] = benefits
            rec["total_deductions"] = deductions
            rec["net_pay"] = net

        self.update_financial_summary_cards()
        self.render_table_rows()
        messagebox.showinfo(
            "Recalculation Complete",
            f"Payroll successfully recalculated for {current_period}!\n\n"
            f"Total Active Employees: {len(self.payroll_records)}\n"
            f"Tax withholdings & benefit contributions updated.",
            parent=self
        )

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
            ("📄", "Payroll &\nPayslips", True),
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
        if target and target != "aPayRecord&Slip.py":
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

        # Populate Sections
        self.create_period_control_bar(self.content_frame)
        self.create_financial_summary_cards(self.content_frame)
        self.create_export_actions_bar(self.content_frame)
        self.create_master_ledger_table(self.content_frame)

    # ==========================================
    # TOP HEADER (FIXED)
    # ==========================================
    def create_top_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.colors["white"], padx=26, pady=20)
        header_frame.pack(fill="x")

        # Bottom divider line
        tk.Frame(parent, bg=self.colors["border_light"], height=1).pack(fill="x")

        # Left Header Titles
        left_box = tk.Frame(header_frame, bg=self.colors["white"])
        left_box.pack(side="left", anchor="w")

        tk.Label(
            left_box,
            text="PAYROLL & PAYSLIPS",
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
            text="Master payroll ledger, automated tax withholdings, and employee payslip preview.",
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
    # SECTION 1: PAY PERIOD CONTROL & LOCK BADGE
    # ==========================================
    def create_period_control_bar(self, parent):
        period_card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=16,
            pady=12
        )
        period_card.pack(fill="x", pady=(0, 14))

        # Left Group: Pay Period Label + Combobox
        left_ctrl = tk.Frame(period_card, bg=self.colors["white"])
        left_ctrl.pack(side="left", fill="y")

        tk.Label(
            left_ctrl,
            text="PAY PERIOD:",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["gray_text"],
            bg=self.colors["white"]
        ).pack(side="left", padx=(0, 8))

        self.period_dropdown = ttk.Combobox(
            left_ctrl,
            textvariable=self.current_period_var,
            values=self.pay_periods,
            state="readonly",
            width=28,
            font=("Segoe UI", 9)
        )
        self.period_dropdown.pack(side="left", padx=(0, 14))
        self.period_dropdown.bind("<<ComboboxSelected>>", self.on_period_changed)

        # Recalculate CTA button
        recalc_btn = tk.Button(
            left_ctrl,
            text="Run & Recalculate Payroll  ⚡",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["primary_orange"],
            fg=self.colors["white"],
            activebackground=self.colors["soft_orange"],
            activeforeground=self.colors["white"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=6,
            command=self.recalculate_all_payroll
        )
        recalc_btn.pack(side="left")

        # Right Group: Status Badge + Period Lock/Unlock Toggle
        self.right_ctrl = tk.Frame(period_card, bg=self.colors["white"])
        self.right_ctrl.pack(side="right")

        tk.Label(
            self.right_ctrl,
            text="Period Status:",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["gray_text"],
            bg=self.colors["white"]
        ).pack(side="left", padx=(0, 8))

        self.period_badge_container = tk.Frame(self.right_ctrl, bg=self.colors["white"])
        self.period_badge_container.pack(side="left", padx=(0, 10))

        self.lock_toggle_btn = tk.Button(
            self.right_ctrl,
            text="Unlock Period",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["sidebar_bg"],
            fg=self.colors["dark_teal"],
            activebackground=self.colors["border_peach"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=5,
            command=self.toggle_period_lock
        )
        self.lock_toggle_btn.pack(side="left")

        self.update_period_status_ui()

    def update_period_status_ui(self):
        """Refreshes the period lock badge and toggle button text."""
        for c in self.period_badge_container.winfo_children():
            c.destroy()

        current_period = self.current_period_var.get()
        status = self.period_status_map.get(current_period, "Approved & Locked")

        if status == "Approved & Locked":
            badge = RoundedBadge(
                self.period_badge_container,
                text="🔒 Approved & Locked",
                bg_color=self.colors["pill_approved"],
                fg_color=self.colors["pill_approved_text"],
                radius=8,
                width=135,
                height=24,
                parent_bg=self.colors["white"]
            )
            self.lock_toggle_btn.config(text="Unlock to Edit 🔓", bg=self.colors["sidebar_bg"], fg=self.colors["dark_teal"])
        elif status == "Pending Approval":
            badge = RoundedBadge(
                self.period_badge_container,
                text="⏳ Pending Approval",
                bg_color=self.colors["pill_pending"],
                fg_color=self.colors["pill_pending_text"],
                radius=8,
                width=135,
                height=24,
                parent_bg=self.colors["white"]
            )
            self.lock_toggle_btn.config(text="Approve & Lock 🔒", bg=self.colors["primary_orange"], fg=self.colors["white"])
        else:
            badge = RoundedBadge(
                self.period_badge_container,
                text="📝 Draft",
                bg_color=self.colors["pill_draft"],
                fg_color=self.colors["pill_draft_text"],
                radius=8,
                width=100,
                height=24,
                parent_bg=self.colors["white"]
            )
            self.lock_toggle_btn.config(text="Submit for Approval", bg=self.colors["primary_orange"], fg=self.colors["white"])

        badge.pack(side="left")

    def toggle_period_lock(self):
        """Toggles between locked and editable period status."""
        current_period = self.current_period_var.get()
        current_status = self.period_status_map.get(current_period, "Approved & Locked")

        if current_status == "Approved & Locked":
            self.period_status_map[current_period] = "Pending Approval"
            messagebox.showinfo("Period Unlocked", f"Period '{current_period}' unlocked.\nEdits and payroll adjustments are now permitted.", parent=self)
        else:
            self.period_status_map[current_period] = "Approved & Locked"
            messagebox.showinfo("Period Approved & Locked", f"Period '{current_period}' has been Approved & Locked.\nAccidental changes are now prevented.", parent=self)

        self.update_period_status_ui()

    def on_period_changed(self, event=None):
        self.update_period_status_ui()
        self.update_financial_summary_cards()
        self.render_table_rows()

    # ==========================================
    # SECTION 2: FINANCIAL SUMMARY CARDS
    # ==========================================
    def create_financial_summary_cards(self, parent):
        self.summary_cards_frame = tk.Frame(parent, bg=self.colors["white"])
        self.summary_cards_frame.pack(fill="x", pady=(0, 14))

        self.card_widgets = {}
        specs = [
            ("total_gross", "TOTAL GROSS PAY", "$0.00", "Base + Overtime & Bonuses"),
            ("total_deductions", "TOTAL DEDUCTIONS", "$0.00", "Tax withholdings & Benefits"),
            ("net_pay", "NET DISBURSEMENT", "$0.00", "Ready for Direct Deposit"),
            ("coverage", "EMPLOYEE COVERAGE", "0 / 0", "100% Calculated & Verified")
        ]

        for idx, (key, title, val, sub) in enumerate(specs):
            card = tk.Frame(
                self.summary_cards_frame,
                bg=self.colors["white"],
                highlightbackground=self.colors["border_peach"],
                highlightthickness=1,
                padx=16,
                pady=10
            )
            card.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 10, 0))
            self.summary_cards_frame.columnconfigure(idx, weight=1)

            t_lbl = tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"])
            t_lbl.pack(anchor="w")

            v_lbl = tk.Label(card, text=val, font=("Segoe UI", 15, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"])
            v_lbl.pack(anchor="w", pady=(2, 2))

            s_lbl = tk.Label(card, text=sub, font=("Segoe UI", 7), fg=self.colors["gray_text"], bg=self.colors["white"])
            s_lbl.pack(anchor="w")

            self.card_widgets[key] = (v_lbl, s_lbl)

        self.update_financial_summary_cards()

    def update_financial_summary_cards(self):
        """Recalculates card metrics from current payroll records."""
        tot_gross = sum(r["gross_pay"] for r in self.payroll_records)
        tot_ded = sum(r["total_deductions"] for r in self.payroll_records)
        tot_tax = sum(r["tax_withholding"] for r in self.payroll_records)
        tot_ben = sum(r["benefit_deductions"] for r in self.payroll_records)
        tot_net = sum(r["net_pay"] for r in self.payroll_records)
        count = len(self.payroll_records)

        if "total_gross" in self.card_widgets:
            self.card_widgets["total_gross"][0].config(text=f"${tot_gross:,.2f}")
            self.card_widgets["total_gross"][1].config(text=f"Base: ${sum(r['base_salary'] for r in self.payroll_records):,.2f} | OT: ${sum(r['overtime'] for r in self.payroll_records):,.2f}")

        if "total_deductions" in self.card_widgets:
            self.card_widgets["total_deductions"][0].config(text=f"${tot_ded:,.2f}")
            self.card_widgets["total_deductions"][1].config(text=f"Taxes: ${tot_tax:,.2f} | Benefits: ${tot_ben:,.2f}")

        if "net_pay" in self.card_widgets:
            self.card_widgets["net_pay"][0].config(text=f"${tot_net:,.2f}")
            self.card_widgets["net_pay"][1].config(text="100% EFT Direct Deposit")

        if "coverage" in self.card_widgets:
            self.card_widgets["coverage"][0].config(text=f"{count} / {count} Active")
            self.card_widgets["coverage"][1].config(text="All Profiles Accounted")

    # ==========================================
    # SECTION 3: DOCUMENT & EXPORT ACTIONS BAR
    # ==========================================
    def create_export_actions_bar(self, parent):
        export_card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=16,
            pady=10
        )
        export_card.pack(fill="x", pady=(0, 14))

        tk.Label(
            export_card,
            text="DOCUMENT & EXPORT UTILITIES:",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["gray_text"],
            bg=self.colors["white"]
        ).pack(side="left", padx=(0, 12))

        # 1. Single Payslip Generator
        tk.Button(
            export_card,
            text="📄 Single Payslip PDF",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["sidebar_bg"],
            fg=self.colors["dark_teal"],
            activebackground=self.colors["border_peach"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=5,
            command=self.action_single_payslip_dialog
        ).pack(side="left", padx=(0, 8))

        # 2. Bulk Email Payslips
        tk.Button(
            export_card,
            text="📧 Bulk Email Payslips",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["sidebar_bg"],
            fg=self.colors["dark_teal"],
            activebackground=self.colors["border_peach"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=5,
            command=self.action_bulk_email_payslips
        ).pack(side="left", padx=(0, 8))

        # 3. Payroll Register Export (CSV)
        tk.Button(
            export_card,
            text="📊 Export Register (CSV)",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["sidebar_bg"],
            fg=self.colors["dark_teal"],
            activebackground=self.colors["border_peach"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=5,
            command=self.action_export_csv_register
        ).pack(side="left", padx=(0, 8))

        # 4. Bank Transfer File Exporter (ACH/NACHA)
        tk.Button(
            export_card,
            text="🏦 Bank Transfer (ACH / NACHA)",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["primary_orange"],
            fg=self.colors["white"],
            activebackground=self.colors["soft_orange"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=5,
            command=self.action_export_ach_nacha
        ).pack(side="right")

    # ==========================================
    # SECTION 4: MASTER PAYROLL LEDGER (TABLE)
    # ==========================================
    def create_master_ledger_table(self, parent):
        self.table_card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=18,
            pady=14
        )
        self.table_card.pack(fill="both", expand=True)

        # Header of Card: Title + Search & Filters
        card_hdr = tk.Frame(self.table_card, bg=self.colors["white"])
        card_hdr.pack(fill="x", pady=(0, 12))

        left_hdr = tk.Frame(card_hdr, bg=self.colors["white"])
        left_hdr.pack(side="left")

        tk.Label(
            left_hdr,
            text="Payroll Master Ledger",
            font=("Segoe UI", 13, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        ).pack(anchor="w")

        tk.Label(
            left_hdr,
            text="Click any employee row to open their Interactive Payslip Drawer preview.",
            font=("Segoe UI", 8),
            fg=self.colors["gray_text"],
            bg=self.colors["white"]
        ).pack(anchor="w")

        # Right Side: Search Box + Dept Filter + Sort
        right_hdr = tk.Frame(card_hdr, bg=self.colors["white"])
        right_hdr.pack(side="right")

        # Sort Dropdown
        tk.Label(right_hdr, text="Sort by:", font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(side="left", padx=(0, 4))
        sort_cb = ttk.Combobox(
            right_hdr,
            textvariable=self.sort_var,
            values=["Employee ID", "Name (A-Z)", "Net Pay (High-Low)", "Base Salary (High-Low)"],
            state="readonly",
            width=16,
            font=("Segoe UI", 8)
        )
        sort_cb.pack(side="left", padx=(0, 8))
        sort_cb.bind("<<ComboboxSelected>>", lambda e: self.render_table_rows())

        # Dept Dropdown
        tk.Label(right_hdr, text="Dept:", font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(side="left", padx=(0, 4))
        departments = ["All Departments", "Design", "Operations", "Finance", "Customer Support", "Human Resources"]
        dept_cb = ttk.Combobox(
            right_hdr,
            textvariable=self.dept_filter_var,
            values=departments,
            state="readonly",
            width=15,
            font=("Segoe UI", 8)
        )
        dept_cb.pack(side="left", padx=(0, 8))
        dept_cb.bind("<<ComboboxSelected>>", lambda e: self.render_table_rows())

        # Search Entry
        search_frame = tk.Frame(
            right_hdr,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_color"],
            highlightthickness=1
        )
        search_frame.pack(side="left")

        self.search_entry = tk.Entry(
            search_frame,
            font=("Segoe UI", 9),
            bg=self.colors["white"],
            bd=0,
            relief="flat",
            width=22,
            fg=self.colors["gray_text"]
        )
        self.search_entry.insert(0, self._search_placeholder)
        self.search_entry.pack(side="left", ipady=4, padx=8)

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

        # Multi-Column Specs: (Name, weight, anchor)
        self.col_specs = [
            ("ID", 1, "center"),
            ("Employee", 3, "w"),
            ("Department", 2, "w"),
            ("Base Salary", 2, "e"),
            ("Overtime/Bonuses", 2, "e"),
            ("Total Deductions", 2, "e"),
            ("Net Pay", 2, "e"),
            ("Status", 2, "w"),
            ("Action", 1, "center")
        ]

        self.table_grid = tk.Frame(self.table_card, bg=self.colors["white"])
        self.table_grid.pack(fill="both", expand=True)

        for idx, (_, weight, _) in enumerate(self.col_specs):
            self.table_grid.columnconfigure(idx, weight=weight)

        self.render_table_rows()

    def get_filtered_and_sorted_records(self):
        """Applies Search, Department Filter, and Sorting criteria."""
        query = self.search_var.get().lower().strip()
        dept = self.dept_filter_var.get()
        sort_by = self.sort_var.get()

        res = []
        for r in self.payroll_records:
            # Query match
            if query and query != self._search_placeholder.lower():
                matches = (query in r["id"].lower() or
                           query in r["name"].lower() or
                           query in r["role"].lower() or
                           query in r["dept"].lower())
                if not matches:
                    continue

            # Dept match
            if dept != "All Departments" and r["dept"] != dept:
                continue

            res.append(r)

        # Sorting
        if sort_by == "Name (A-Z)":
            res.sort(key=lambda x: x["name"])
        elif sort_by == "Net Pay (High-Low)":
            res.sort(key=lambda x: x["net_pay"], reverse=True)
        elif sort_by == "Base Salary (High-Low)":
            res.sort(key=lambda x: x["base_salary"], reverse=True)
        else: # Employee ID
            res.sort(key=lambda x: x["id"])

        return res

    def render_table_rows(self):
        """Builds each row using tk.grid matching dashboard and employee styling."""
        for c in self.table_grid.winfo_children():
            c.destroy()

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

        # Row 1: Divider
        div = tk.Frame(self.table_grid, height=1, bg=self.colors["border_light"])
        div.grid(row=1, column=0, columnspan=len(self.col_specs), sticky="ew", pady=(0, 6))

        visible_records = self.get_filtered_and_sorted_records()

        if not visible_records:
            no_data = tk.Label(
                self.table_grid,
                text="No payroll records found matching your filters.",
                font=("Segoe UI", 9, "italic"),
                fg=self.colors["gray_text"],
                bg=self.colors["white"],
                pady=20
            )
            no_data.grid(row=2, column=0, columnspan=len(self.col_specs), pady=20)
            return

        current_grid_row = 2
        for idx, r in enumerate(visible_records):
            # Click row handler to open payslip drawer
            open_cmd = lambda item=r: self.open_payslip_preview_drawer(item)

            # Col 0: ID
            id_lbl = tk.Label(
                self.table_grid,
                text=r["id"],
                font=("Segoe UI", 8, "bold"),
                fg=self.colors["gray_text"],
                bg=self.colors["white"],
                cursor="hand2"
            )
            id_lbl.grid(row=current_grid_row, column=0, sticky="ew", padx=6, pady=4)
            id_lbl.bind("<Button-1>", lambda e, cmd=open_cmd: cmd())

            # Col 1: Employee (Avatar + Name + Role)
            emp_box = tk.Frame(self.table_grid, bg=self.colors["white"], cursor="hand2")
            emp_box.grid(row=current_grid_row, column=1, sticky="w", padx=6, pady=4)
            emp_box.bind("<Button-1>", lambda e, cmd=open_cmd: cmd())

            av_canvas = tk.Canvas(emp_box, width=30, height=30, bg=self.colors["white"], highlightthickness=0)
            av_canvas.pack(side="left", padx=(0, 8))
            av_canvas.create_oval(2, 2, 28, 28, fill=r["avatar_color"], outline="")
            av_canvas.create_text(15, 15, text=r["initials"], fill="#FFFFFF", font=("Segoe UI", 8, "bold"))
            av_canvas.bind("<Button-1>", lambda e, cmd=open_cmd: cmd())

            name_role_box = tk.Frame(emp_box, bg=self.colors["white"])
            name_role_box.pack(side="left")

            name_lbl = tk.Label(
                name_role_box,
                text=r["name"],
                font=("Segoe UI", 9, "bold"),
                fg=self.colors["dark_teal"],
                bg=self.colors["white"]
            )
            name_lbl.pack(anchor="w")
            name_lbl.bind("<Button-1>", lambda e, cmd=open_cmd: cmd())

            role_lbl = tk.Label(
                name_role_box,
                text=r["role"],
                font=("Segoe UI", 7),
                fg=self.colors["gray_text"],
                bg=self.colors["white"]
            )
            role_lbl.pack(anchor="w")
            role_lbl.bind("<Button-1>", lambda e, cmd=open_cmd: cmd())

            # Col 2: Department
            dept_lbl = tk.Label(
                self.table_grid,
                text=r["dept"],
                font=("Segoe UI", 8),
                fg=self.colors["text_dark"],
                bg=self.colors["white"],
                anchor="w",
                cursor="hand2"
            )
            dept_lbl.grid(row=current_grid_row, column=2, sticky="ew", padx=6, pady=4)
            dept_lbl.bind("<Button-1>", lambda e, cmd=open_cmd: cmd())

            # Col 3: Base Salary
            tk.Label(
                self.table_grid,
                text=f"${r['base_salary']:,.2f}",
                font=("Segoe UI", 8),
                fg=self.colors["text_dark"],
                bg=self.colors["white"],
                anchor="e"
            ).grid(row=current_grid_row, column=3, sticky="ew", padx=6, pady=4)

            # Col 4: Overtime / Bonuses
            tk.Label(
                self.table_grid,
                text=f"+${r['overtime']:,.2f}",
                font=("Segoe UI", 8),
                fg=self.colors["primary_orange"],
                bg=self.colors["white"],
                anchor="e"
            ).grid(row=current_grid_row, column=4, sticky="ew", padx=6, pady=4)

            # Col 5: Total Deductions
            tk.Label(
                self.table_grid,
                text=f"-${r['total_deductions']:,.2f}",
                font=("Segoe UI", 8),
                fg="#E05252",
                bg=self.colors["white"],
                anchor="e"
            ).grid(row=current_grid_row, column=5, sticky="ew", padx=6, pady=4)

            # Col 6: Net Pay
            tk.Label(
                self.table_grid,
                text=f"${r['net_pay']:,.2f}",
                font=("Segoe UI", 9, "bold"),
                fg=self.colors["dark_teal"],
                bg=self.colors["white"],
                anchor="e"
            ).grid(row=current_grid_row, column=6, sticky="ew", padx=6, pady=4)

            # Col 7: Payment Status (RoundedBadge)
            is_paid = (r["status"] == "Paid")
            s_bg = self.colors["pill_approved"] if is_paid else self.colors["pill_pending"]
            s_fg = self.colors["pill_approved_text"] if is_paid else self.colors["pill_pending_text"]

            badge = RoundedBadge(
                self.table_grid,
                text=r["status"],
                bg_color=s_bg,
                fg_color=s_fg,
                radius=8,
                width=76,
                height=22,
                parent_bg=self.colors["white"]
            )
            badge.grid(row=current_grid_row, column=7, sticky="w", padx=6, pady=4)
            badge.bind("<Button-1>", lambda e, cmd=open_cmd: cmd())

            # Col 8: View Slip Action Button
            view_btn = tk.Button(
                self.table_grid,
                text="View Slip",
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
                padx=8,
                pady=2,
                command=open_cmd
            )
            view_btn.grid(row=current_grid_row, column=8, sticky="w", padx=6, pady=4)

            current_grid_row += 1

            # Separator Line
            if idx < len(visible_records) - 1:
                row_sep = tk.Frame(self.table_grid, height=1, bg="#F7F7F7")
                row_sep.grid(row=current_grid_row, column=0, columnspan=len(self.col_specs), sticky="ew", pady=2)
                current_grid_row += 1

    # ==========================================
    # INTERACTIVE PAYSLIP PREVIEW DRAWER / MODAL
    # ==========================================
    def open_payslip_preview_drawer(self, record):
        """Displays an interactive detailed payslip preview modal."""
        modal = tk.Toplevel(self)
        modal.title(f"Payslip Preview - {record['name']} ({record['id']})")
        modal.geometry("540x680")
        modal.resizable(False, False)
        modal.configure(bg=self.colors["white"])
        modal.transient(self)
        modal.grab_set()

        # Center modal over main window
        x = self.winfo_x() + (self.winfo_width() - 540) // 2
        y = self.winfo_y() + (self.winfo_height() - 680) // 2
        modal.geometry(f"540x680+{max(x, 50)}+{max(y, 30)}")

        # Header Ribbon
        hdr = tk.Frame(modal, bg=self.colors["sidebar_bg"], padx=24, pady=18)
        hdr.pack(fill="x")

        tk.Label(
            hdr,
            text="STEADYPAY OFFICIAL EARNINGS STATEMENT",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["primary_orange"],
            bg=self.colors["sidebar_bg"]
        ).pack(anchor="w")

        tk.Label(
            hdr,
            text=f"Payslip: {self.current_period_var.get()}",
            font=("Segoe UI", 13, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["sidebar_bg"]
        ).pack(anchor="w", pady=(2, 0))

        # Main Scrollable Form Body
        body = tk.Frame(modal, bg=self.colors["white"], padx=24, pady=16)
        body.pack(fill="both", expand=True)

        # Employee Info Card
        emp_card = tk.Frame(body, bg="#F8FCFB", highlightbackground=self.colors["border_light"], highlightthickness=1, padx=14, pady=10)
        emp_card.pack(fill="x", pady=(0, 14))

        info_grid = [
            ("Employee Name:", record["name"], "Employee ID:", record["id"]),
            ("Department:", record["dept"], "Position:", record["role"]),
            ("Pay Date:", "Sep 30, 2026", "Disbursement:", "Direct Deposit (ACH)")
        ]

        for r_idx, (k1, v1, k2, v2) in enumerate(info_grid):
            tk.Label(emp_card, text=k1, font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg="#F8FCFB").grid(row=r_idx, column=0, sticky="w", pady=2)
            tk.Label(emp_card, text=v1, font=("Segoe UI", 8, "bold"), fg=self.colors["text_dark"], bg="#F8FCFB").grid(row=r_idx, column=1, sticky="w", padx=(4, 16), pady=2)
            tk.Label(emp_card, text=k2, font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg="#F8FCFB").grid(row=r_idx, column=2, sticky="w", pady=2)
            tk.Label(emp_card, text=v2, font=("Segoe UI", 8), fg=self.colors["text_dark"], bg="#F8FCFB").grid(row=r_idx, column=3, sticky="w", padx=(4, 0), pady=2)

        # Earnings & Deductions Breakdown Tables
        breakdown_box = tk.Frame(body, bg=self.colors["white"])
        breakdown_box.pack(fill="x", pady=(0, 14))

        # Earnings Column (Left)
        earn_col = tk.Frame(breakdown_box, bg=self.colors["white"])
        earn_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(earn_col, text="EARNINGS", font=("Segoe UI", 9, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(anchor="w")
        tk.Frame(earn_col, bg=self.colors["border_light"], height=1).pack(fill="x", pady=(3, 8))

        earnings_lines = [
            ("Regular Base Salary", f"${record['base_salary']:,.2f}"),
            ("Overtime / Bonus", f"${record['overtime']:,.2f}"),
            ("Gross Pay", f"${record['gross_pay']:,.2f}")
        ]
        for item, val in earnings_lines:
            row = tk.Frame(earn_col, bg=self.colors["white"])
            row.pack(fill="x", pady=2)
            is_bold = (item == "Gross Pay")
            tk.Label(row, text=item, font=("Segoe UI", 8, "bold" if is_bold else "normal"), fg=self.colors["text_dark"], bg=self.colors["white"]).pack(side="left")
            tk.Label(row, text=val, font=("Segoe UI", 8, "bold" if is_bold else "normal"), fg=self.colors["dark_teal"] if is_bold else self.colors["text_dark"], bg=self.colors["white"]).pack(side="right")

        # Deductions Column (Right)
        ded_col = tk.Frame(breakdown_box, bg=self.colors["white"])
        ded_col.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Label(ded_col, text="DEDUCTIONS", font=("Segoe UI", 9, "bold"), fg="#E05252", bg=self.colors["white"]).pack(anchor="w")
        tk.Frame(ded_col, bg=self.colors["border_light"], height=1).pack(fill="x", pady=(3, 8))

        deduction_lines = [
            ("Federal/State Withholding", f"${record['tax_withholding']:,.2f}"),
            ("Benefits & 401(k)", f"${record['benefit_deductions']:,.2f}"),
            ("Total Deductions", f"-${record['total_deductions']:,.2f}")
        ]
        for item, val in deduction_lines:
            row = tk.Frame(ded_col, bg=self.colors["white"])
            row.pack(fill="x", pady=2)
            is_bold = (item == "Total Deductions")
            tk.Label(row, text=item, font=("Segoe UI", 8, "bold" if is_bold else "normal"), fg=self.colors["text_dark"], bg=self.colors["white"]).pack(side="left")
            tk.Label(row, text=val, font=("Segoe UI", 8, "bold" if is_bold else "normal"), fg="#E05252" if is_bold else self.colors["text_dark"], bg=self.colors["white"]).pack(side="right")

        # Net Pay Disbursement Callout Box
        net_card = tk.Frame(
            body,
            bg=self.colors["pill_approved"],
            highlightbackground=self.colors["dark_teal"],
            highlightthickness=1,
            padx=16,
            pady=12
        )
        net_card.pack(fill="x", pady=(0, 16))

        tk.Label(
            net_card,
            text="TAKE HOME NET DISBURSEMENT",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["deep_teal"],
            bg=self.colors["pill_approved"]
        ).pack(anchor="w")

        tk.Label(
            net_card,
            text=f"${record['net_pay']:,.2f}",
            font=("Segoe UI", 20, "bold"),
            fg=self.colors["deep_teal"],
            bg=self.colors["pill_approved"]
        ).pack(anchor="w", pady=(2, 2))

        tk.Label(
            net_card,
            text="Disbursement via Direct Deposit EFT to employee account ending in ****3829.",
            font=("Segoe UI", 7),
            fg=self.colors["deep_teal"],
            bg=self.colors["pill_approved"]
        ).pack(anchor="w")

        # Bottom Utilities Bar
        footer = tk.Frame(modal, bg=self.colors["white"], padx=24, pady=14)
        footer.pack(fill="x", side="bottom")

        tk.Button(
            footer,
            text="Close",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["sidebar_bg"],
            fg=self.colors["dark_teal"],
            activebackground=self.colors["border_peach"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=6,
            command=modal.destroy
        ).pack(side="right", padx=(8, 0))

        tk.Button(
            footer,
            text="Download / Export PDF",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["primary_orange"],
            fg=self.colors["white"],
            activebackground=self.colors["soft_orange"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=6,
            command=lambda: self.save_payslip_to_file(record, modal)
        ).pack(side="right", padx=(8, 0))

        tk.Button(
            footer,
            text="Email to Employee ✉️",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["sidebar_bg"],
            fg=self.colors["dark_teal"],
            activebackground=self.colors["soft_orange"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            command=lambda: messagebox.showinfo("Email Dispatched", f"Official payslip for {record['name']} has been emailed to:\n{record['email']}", parent=modal)
        ).pack(side="right")

    # ==========================================
    # DOCUMENT & EXPORT ACTIONS IMPLEMENTATION
    # ==========================================
    def action_single_payslip_dialog(self):
        """Allows selecting any employee to generate their payslip file."""
        names = [f"{r['id']} - {r['name']}" for r in self.payroll_records]

        dialog = tk.Toplevel(self)
        dialog.title("Select Employee Payslip")
        dialog.geometry("380x200")
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors["white"])
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="Generate Individual Payslip", font=("Segoe UI", 11, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(padx=20, pady=(16, 6), anchor="w")
        tk.Label(dialog, text="Choose an employee to open preview or export:", font=("Segoe UI", 8), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(padx=20, pady=(0, 10), anchor="w")

        selected_emp = tk.StringVar(value=names[0] if names else "")
        cb = ttk.Combobox(dialog, textvariable=selected_emp, values=names, state="readonly", width=36)
        cb.pack(padx=20, pady=8)

        def _proceed():
            sel_id = selected_emp.get().split(" - ")[0]
            rec = next((r for r in self.payroll_records if r["id"] == sel_id), None)
            dialog.destroy()
            if rec:
                self.open_payslip_preview_drawer(rec)

        tk.Button(
            dialog,
            text="Open Payslip Preview",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["primary_orange"],
            fg=self.colors["white"],
            activebackground=self.colors["soft_orange"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            command=_proceed
        ).pack(padx=20, pady=12, anchor="e")

    def action_bulk_email_payslips(self):
        """Simulates sending digital payslips to all employees in the current period."""
        count = len(self.payroll_records)
        period = self.current_period_var.get()

        confirm = messagebox.askyesno(
            "Bulk Email Confirmation",
            f"Are you sure you want to email digital payslips to all {count} active employees for pay period:\n{period}?",
            parent=self
        )
        if not confirm:
            return

        messagebox.showinfo(
            "Bulk Email Sent Successfully",
            f"✓ {count} employee payslips have been successfully delivered to their registered email addresses!\n\n"
            f"Period: {period}\nStatus: Direct Deposit verification attached.",
            parent=self
        )

    def action_export_csv_register(self):
        """Exports the entire payroll ledger to a CSV file."""
        period = self.current_period_var.get()
        default_filename = f"Payroll_Register_{period.split()[0]}_{datetime.datetime.now().strftime('%Y%m%d')}.csv"

        filepath = filedialog.asksaveasfilename(
            parent=self,
            title="Export Payroll Register (CSV)",
            defaultextension=".csv",
            initialfile=default_filename,
            filetypes=[("CSV Spreadsheet", "*.csv"), ("All Files", "*.*")]
        )

        if not filepath:
            return

        try:
            with open(filepath, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Pay Period", period])
                writer.writerow(["Exported On", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                writer.writerow([])
                writer.writerow([
                    "Employee ID", "Employee Name", "Department", "Role",
                    "Base Salary ($)", "Overtime / Bonus ($)", "Gross Pay ($)",
                    "Tax Withholdings ($)", "Benefit Deductions ($)", "Total Deductions ($)",
                    "Net Pay ($)", "Payment Status"
                ])

                for r in self.payroll_records:
                    writer.writerow([
                        r["id"], r["name"], r["dept"], r["role"],
                        f"{r['base_salary']:.2f}", f"{r['overtime']:.2f}", f"{r['gross_pay']:.2f}",
                        f"{r['tax_withholding']:.2f}", f"{r['benefit_deductions']:.2f}", f"{r['total_deductions']:.2f}",
                        f"{r['net_pay']:.2f}", r["status"]
                    ])

            messagebox.showinfo("Export Complete", f"Payroll register successfully exported to:\n{filepath}", parent=self)
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not write CSV file:\n{str(e)}", parent=self)

    def action_export_ach_nacha(self):
        """Generates an automated clearing house (ACH / NACHA) direct deposit batch file."""
        period = self.current_period_var.get()
        default_filename = f"NACHA_ACH_DirectDeposit_{datetime.datetime.now().strftime('%Y%m%d')}.ach"

        filepath = filedialog.asksaveasfilename(
            parent=self,
            title="Export NACHA Direct Deposit File",
            defaultextension=".ach",
            initialfile=default_filename,
            filetypes=[("ACH NACHA File", "*.ach"), ("Text File", "*.txt"), ("All Files", "*.*")]
        )

        if not filepath:
            return

        try:
            tot_net = sum(r["net_pay"] for r in self.payroll_records)
            today_nacha = datetime.datetime.now().strftime("%y%m%d")

            with open(filepath, mode="w", encoding="utf-8") as f:
                # Standard File Header Record (Type 1)
                f.write(f"101 121000358 111223344 {today_nacha} 1000 A 094 101 STEADYPAY CORP        CHASE BANK          \n")
                # Company Batch Header Record (Type 5)
                f.write(f"5200 STEADYPAY PAYROLL          111223344 PPD PAYROLL   {today_nacha} {today_nacha}   1 12100035 0000001\n")

                # Entry Detail Records (Type 6)
                for idx, r in enumerate(self.payroll_records, start=1):
                    cents = int(round(r["net_pay"] * 100))
                    name_padded = r["name"][:15].ljust(15)
                    id_padded = r["id"][:15].ljust(15)
                    f.write(f"622 12100035 8 9876543210      {cents:010d} {id_padded} {name_padded}  0 12100035{idx:07d}\n")

                # Batch Control Record (Type 8)
                f.write(f"8200 {len(self.payroll_records):06d} 0012100035 0000000000 {int(round(tot_net*100)):012d} 111223344                         12100035 0000001\n")
                # File Control Record (Type 9)
                f.write(f"9000001 000001 {len(self.payroll_records):08d} 0012100035 0000000000 {int(round(tot_net*100)):012d}                                       \n")

            messagebox.showinfo(
                "ACH Export Generated",
                f"NACHA formatted bank file generated successfully!\n\n"
                f"File: {filepath}\n"
                f"Total Direct Deposit Batched: ${tot_net:,.2f}\n"
                f"Record Count: {len(self.payroll_records)} Entries",
                parent=self
            )
        except Exception as e:
            messagebox.showerror("ACH Export Error", f"Could not create ACH file:\n{str(e)}", parent=self)

    def save_payslip_to_file(self, record, parent_window):
        """Saves a human-readable text/PDF payslip document."""
        period = self.current_period_var.get()
        default_filename = f"Payslip_{record['id']}_{record['name'].replace(' ', '_')}.txt"

        filepath = filedialog.asksaveasfilename(
            parent=parent_window,
            title="Save Payslip Statement",
            defaultextension=".txt",
            initialfile=default_filename,
            filetypes=[("Text Document / PDF Source", "*.txt"), ("All Files", "*.*")]
        )

        if not filepath:
            return

        try:
            with open(filepath, mode="w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                f.write("                  STEADYPAY PAYROLL SYSTEM               \n")
                f.write("                 OFFICIAL EARNINGS STATEMENT             \n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Pay Period:        {period}\n")
                f.write(f"Payment Date:      September 30, 2026\n")
                f.write(f"Employee ID:       {record['id']}\n")
                f.write(f"Employee Name:     {record['name']}\n")
                f.write(f"Department:        {record['dept']}\n")
                f.write(f"Job Title:         {record['role']}\n")
                f.write(f"Disbursement:      Direct Deposit (Checking ****3829)\n\n")
                f.write("-" * 60 + "\n")
                f.write("EARNINGS BREAKDOWN\n")
                f.write("-" * 60 + "\n")
                f.write(f"  Regular Base Salary:                     ${record['base_salary']:>12,.2f}\n")
                f.write(f"  Overtime & Bonuses:                      ${record['overtime']:>12,.2f}\n")
                f.write(f"  TOTAL GROSS EARNINGS:                    ${record['gross_pay']:>12,.2f}\n\n")
                f.write("-" * 60 + "\n")
                f.write("WITHHOLDINGS & DEDUCTIONS\n")
                f.write("-" * 60 + "\n")
                f.write(f"  Federal / State Income Tax Withholding:  ${record['tax_withholding']:>12,.2f}\n")
                f.write(f"  Health Insurance & Benefit 401(k):       ${record['benefit_deductions']:>12,.2f}\n")
                f.write(f"  TOTAL DEDUCTIONS:                       -${record['total_deductions']:>12,.2f}\n\n")
                f.write("=" * 60 + "\n")
                f.write(f"  NET TAKE-HOME PAY:                       ${record['net_pay']:>12,.2f}\n")
                f.write("=" * 60 + "\n\n")
                f.write("Notice: All statutory deductions are calculated under federal and state\n")
                f.write("payroll guidelines. Please retain this statement for your financial records.\n")

            messagebox.showinfo("Payslip Saved", f"Payslip statement saved successfully to:\n{filepath}", parent=parent_window)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save payslip statement:\n{str(e)}", parent=parent_window)

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
    app = SteadypayPayrollPayslipsPage()
    app.mainloop()
