import os
import sys
import subprocess
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from data import (
    get_admin_data, get_all_employees,
    draw_rounded_rectangle, RoundedBadge
)

class SteadypayProcessPayPage(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Steadypay - Process Payroll Wizard (Admin)")
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

        # Centralized Admin Data
        self.admin_data = get_admin_data()

        # Wizard State
        self.current_step = 1
        self.total_steps = 5
        self.step_titles = [
            ("Time & Attendance", "Sync timesheets & overtime"),
            ("Adjustments & Variable", "Bonuses & pre-tax entries"),
            ("Automated Calculation", "Taxes & statutory net pay"),
            ("Audit & Exceptions", "Pre-payment discrepancy checks"),
            ("Finalization & Triggers", "Lock period & disburse")
        ]

        # Pay Period
        self.pay_period_name = "Sep 16 - Sep 30, 2026"
        self.period_locked = False

        # Attendance Sync State
        self.attendance_synced = True
        self.sync_timestamp = "Today at 09:15 AM (Biometric API)"

        # Initialize Employee Payroll Calculation State
        self.init_process_payroll_data()

        # Exception flags for Step 4
        self.exceptions_resolved = False

        # Setup GUI Layout
        self.setup_layout()

    # ==========================================
    # DATA ENGINE & INITIAL STATE
    # ==========================================
    def init_process_payroll_data(self):
        """Preloads employee dataset with timesheet, rates, adjustment entries, and tax formulas."""
        raw = get_all_employees()
        self.payroll_items = []

        dept_map = {
            "EMP-101": "Design",
            "EMP-102": "Operations",
            "EMP-103": "Finance",
            "EMP-104": "Customer Support",
            "EMP-105": "Human Resources"
        }
        base_map = {
            "EMP-101": 5200.00,
            "EMP-102": 5500.00,
            "EMP-103": 5400.00,
            "EMP-104": 4500.00,
            "EMP-105": 5100.00
        }
        ot_hours_map = {
            "EMP-101": 6.0,
            "EMP-102": 12.0,   # Flagged for Step 4 audit (>10h)
            "EMP-103": 4.0,
            "EMP-104": 8.0,
            "EMP-105": 5.0
        }
        bonuses_map = {
            "EMP-101": 250.00,
            "EMP-102": 300.00,
            "EMP-103": 450.00,  # Flagged for Step 4 audit (>15% variance)
            "EMP-104": 150.00,
            "EMP-105": 200.00
        }

        for emp in raw:
            eid = emp["id"]
            dept = dept_map.get(eid, "Operations")
            base = base_map.get(eid, 5000.00)
            reg_hours = emp.get("hours_logged", 160.0)
            ot_hours = ot_hours_map.get(eid, 5.0)
            holiday_hours = 2.0 if eid == "EMP-102" else 0.0

            # Hourly rate derivation (base / 160h)
            hourly_rate = round(base / 160.0, 2)
            ot_rate = round(hourly_rate * 1.5, 2)
            holiday_rate = round(hourly_rate * 2.0, 2)
            ot_pay = round((ot_hours * ot_rate) + (holiday_hours * holiday_rate), 2)

            # Adjustments
            bonus = bonuses_map.get(eid, 200.00)
            reimbursement = 75.00 if eid in ("EMP-101", "EMP-103") else 0.00
            pretax_health = 160.00
            pretax_401k = round(base * 0.04, 2)

            gross_pay = round(base + ot_pay + bonus + reimbursement, 2)

            # Statutory Taxes
            fed_tax = round(gross_pay * 0.105, 2)      # 10.5% Federal
            state_tax = round(gross_pay * 0.045, 2)    # 4.5% State
            fica_tax = round(gross_pay * 0.0765, 2)    # 7.65% Social Security & Medicare
            total_tax = round(fed_tax + state_tax + fica_tax, 2)

            total_benefits = round(pretax_health + pretax_401k, 2)
            total_deductions = round(total_tax + total_benefits, 2)
            net_pay = round(gross_pay - total_deductions, 2)

            self.payroll_items.append({
                "id": eid,
                "name": emp["name"],
                "initials": emp["initials"],
                "role": emp["role"],
                "dept": dept,
                "email": emp["email"],
                "avatar_color": emp["avatar_color"],
                "reg_hours": reg_hours,
                "ot_hours": ot_hours,
                "holiday_hours": holiday_hours,
                "hourly_rate": hourly_rate,
                "ot_pay": ot_pay,
                "pto_used": 1.0,
                "pto_balance": emp.get("available_leaves", 12),
                "bonus": bonus,
                "reimbursement": reimbursement,
                "pretax_health": pretax_health,
                "pretax_401k": pretax_401k,
                "base_salary": base,
                "gross_pay": gross_pay,
                "fed_tax": fed_tax,
                "state_tax": state_tax,
                "fica_tax": fica_tax,
                "total_tax": total_tax,
                "total_benefits": total_benefits,
                "total_deductions": total_deductions,
                "net_pay": net_pay,
                "exception_flag": (eid in ("EMP-102", "EMP-103"))
            })

    def recalculate_live_engine(self):
        """Recalculates all mathematical figures dynamically based on state."""
        for item in self.payroll_items:
            ot_rate = round(item["hourly_rate"] * 1.5, 2)
            hol_rate = round(item["hourly_rate"] * 2.0, 2)
            item["ot_pay"] = round((item["ot_hours"] * ot_rate) + (item["holiday_hours"] * hol_rate), 2)
            item["gross_pay"] = round(item["base_salary"] + item["ot_pay"] + item["bonus"] + item["reimbursement"], 2)

            item["fed_tax"] = round(item["gross_pay"] * 0.105, 2)
            item["state_tax"] = round(item["gross_pay"] * 0.045, 2)
            item["fica_tax"] = round(item["gross_pay"] * 0.0765, 2)
            item["total_tax"] = round(item["fed_tax"] + item["state_tax"] + item["fica_tax"], 2)

            item["pretax_401k"] = round(item["base_salary"] * 0.04, 2)
            item["total_benefits"] = round(item["pretax_health"] + item["pretax_401k"], 2)
            item["total_deductions"] = round(item["total_tax"] + item["total_benefits"], 2)
            item["net_pay"] = round(item["gross_pay"] - item["total_deductions"], 2)

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

        for w in (logo_frame, logo_canvas, logo_text):
            w.bind("<Button-1>", lambda e: self.navigate_to_dashboard())
            w.configure(cursor="hand2")

        # Navigation Menu List
        menu_items = [
            ("🏠", "Dashboard", False),
            ("👥", "Employee\nmanagement", False),
            ("💳", "Process payroll", True),
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
        if target and target != "aProcessPay.py":
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

        # 1. Step-by-Step Payroll Wizard Stepper Bar
        self.create_wizard_stepper_bar(self.content_frame)

        # 2. Dynamic Step Content Container
        self.step_content_container = tk.Frame(self.content_frame, bg=self.colors["white"])
        self.step_content_container.pack(fill="both", expand=True, pady=(0, 14))

        # 3. Wizard Bottom Navigation Footer
        self.create_wizard_nav_footer(self.content_frame)

        # Render active step
        self.render_active_step()

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
            text="PAYROLL PROCESSING WIZARD",
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
            text="Automated end-to-end payroll calculation, audit validation, and disbursement workflow.",
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
    # VISUAL STEP-BY-STEP PAYROLL WIZARD BAR
    # ==========================================
    def create_wizard_stepper_bar(self, parent):
        """Builds the visual progress tracker at the top guiding the admin through the lifecycle."""
        self.stepper_card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=18,
            pady=14
        )
        self.stepper_card.pack(fill="x", pady=(0, 16))

        # Card Title Row: Cycle name + Status
        top_bar = tk.Frame(self.stepper_card, bg=self.colors["white"])
        top_bar.pack(fill="x", pady=(0, 12))

        tk.Label(
            top_bar,
            text=f"PAYROLL RUN CYCLE: {self.pay_period_name.upper()}",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["primary_orange"],
            bg=self.colors["white"]
        ).pack(side="left")

        self.stepper_status_lbl = tk.Label(
            top_bar,
            text=f"Step {self.current_step} of {self.total_steps}: {self.step_titles[self.current_step - 1][0]}",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        )
        self.stepper_status_lbl.pack(side="right")

        # Visual Steps Container
        self.steps_row = tk.Frame(self.stepper_card, bg=self.colors["white"])
        self.steps_row.pack(fill="x")

        self.render_stepper_nodes()

    def render_stepper_nodes(self):
        """Renders the step circles, titles, and connecting status lines."""
        for c in self.steps_row.winfo_children():
            c.destroy()

        for idx, (title, subtitle) in enumerate(self.step_titles, start=1):
            step_frame = tk.Frame(self.steps_row, bg=self.colors["white"], cursor="hand2")
            step_frame.pack(side="left", fill="x", expand=True)
            step_frame.bind("<Button-1>", lambda e, s=idx: self.go_to_step(s))

            # Indicator Circle + Connecting Line
            indicator_box = tk.Frame(step_frame, bg=self.colors["white"])
            indicator_box.pack(anchor="center", pady=(0, 4))

            # Circle Canvas
            cv = tk.Canvas(indicator_box, width=32, height=32, bg=self.colors["white"], highlightthickness=0)
            cv.pack(side="left")
            cv.bind("<Button-1>", lambda e, s=idx: self.go_to_step(s))

            is_completed = (idx < self.current_step)
            is_active = (idx == self.current_step)

            if is_completed:
                fill_col = self.colors["pill_approved"]
                out_col = self.colors["dark_teal"]
                txt = "✓"
                txt_col = self.colors["deep_teal"]
            elif is_active:
                fill_col = self.colors["primary_orange"]
                out_col = self.colors["primary_orange"]
                txt = str(idx)
                txt_col = "#FFFFFF"
            else:
                fill_col = "#F4F7F7"
                out_col = self.colors["border_light"]
                txt = str(idx)
                txt_col = self.colors["gray_text"]

            cv.create_oval(2, 2, 30, 30, fill=fill_col, outline=out_col, width=2 if is_active else 1)
            cv.create_text(16, 16, text=txt, fill=txt_col, font=("Segoe UI", 9, "bold"))

            # Step Label
            lbl = tk.Label(
                step_frame,
                text=f"{idx}. {title}",
                font=("Segoe UI", 8, "bold" if is_active else "normal"),
                fg=self.colors["primary_orange"] if is_active else (self.colors["dark_teal"] if is_completed else self.colors["gray_text"]),
                bg=self.colors["white"]
            )
            lbl.pack(anchor="center")
            lbl.bind("<Button-1>", lambda e, s=idx: self.go_to_step(s))

            sub_lbl = tk.Label(
                step_frame,
                text=subtitle,
                font=("Segoe UI", 6),
                fg=self.colors["gray_text"],
                bg=self.colors["white"]
            )
            sub_lbl.pack(anchor="center")
            sub_lbl.bind("<Button-1>", lambda e, s=idx: self.go_to_step(s))

    def go_to_step(self, step_number):
        if 1 <= step_number <= self.total_steps:
            self.current_step = step_number
            self.stepper_status_lbl.config(
                text=f"Step {self.current_step} of {self.total_steps}: {self.step_titles[self.current_step - 1][0]}"
            )
            self.render_stepper_nodes()
            self.render_active_step()
            self.update_nav_footer_buttons()

    # ==========================================
    # WIZARD BOTTOM NAVIGATION FOOTER
    # ==========================================
    def create_wizard_nav_footer(self, parent):
        self.nav_footer = tk.Frame(parent, bg=self.colors["white"], pady=10)
        self.nav_footer.pack(fill="x")

        self.prev_btn = tk.Button(
            self.nav_footer,
            text="← Previous Step",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["sidebar_bg"],
            fg=self.colors["dark_teal"],
            activebackground=self.colors["border_peach"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=7,
            command=self.prev_step
        )
        self.prev_btn.pack(side="left")

        self.next_btn = tk.Button(
            self.nav_footer,
            text="Next Step →",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["primary_orange"],
            fg=self.colors["white"],
            activebackground=self.colors["soft_orange"],
            activeforeground=self.colors["white"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=7,
            command=self.next_step
        )
        self.next_btn.pack(side="right")

        self.update_nav_footer_buttons()

    def update_nav_footer_buttons(self):
        if self.current_step == 1:
            self.prev_btn.config(state="disabled", fg="#A0B0B0", cursor="arrow")
        else:
            self.prev_btn.config(state="normal", fg=self.colors["dark_teal"], cursor="hand2")

        if self.current_step == self.total_steps:
            self.next_btn.config(text="Finalize & Disburse Payroll 🚀", bg=self.colors["dark_teal"])
        else:
            self.next_btn.config(text=f"Proceed to Step {self.current_step + 1} →", bg=self.colors["primary_orange"])

    def next_step(self):
        if self.current_step < self.total_steps:
            self.go_to_step(self.current_step + 1)
        else:
            self.action_finalize_payroll_cycle()

    def prev_step(self):
        if self.current_step > 1:
            self.go_to_step(self.current_step - 1)

    # ==========================================
    # DYNAMIC STEP RENDERING CONTROLLER
    # ==========================================
    def render_active_step(self):
        for c in self.step_content_container.winfo_children():
            c.destroy()

        if self.current_step == 1:
            self.render_step_1_time_attendance(self.step_content_container)
        elif self.current_step == 2:
            self.render_step_2_adjustments(self.step_content_container)
        elif self.current_step == 3:
            self.render_step_3_calculation_engine(self.step_content_container)
        elif self.current_step == 4:
            self.render_step_4_audit_exceptions(self.step_content_container)
        elif self.current_step == 5:
            self.render_step_5_finalization_triggers(self.step_content_container)

    # =========================================================================
    # STEP 1: TIME & ATTENDANCE DATA INGESTION
    # =========================================================================
    def render_step_1_time_attendance(self, parent):
        card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=18,
            pady=16
        )
        card.pack(fill="both", expand=True)

        # Header Ribbon
        hdr = tk.Frame(card, bg=self.colors["white"])
        hdr.pack(fill="x", pady=(0, 14))

        left_hdr = tk.Frame(hdr, bg=self.colors["white"])
        left_hdr.pack(side="left")

        tk.Label(
            left_hdr,
            text="STEP 1: TIME & ATTENDANCE DATA INGESTION",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["primary_orange"],
            bg=self.colors["white"]
        ).pack(anchor="w")

        tk.Label(
            left_hdr,
            text="Ingest timesheet hours, overtime multipliers, and leave balance deductions.",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        ).pack(anchor="w", pady=(2, 0))

        # Sync & Import Toolbar
        btn_box = tk.Frame(hdr, bg=self.colors["white"])
        btn_box.pack(side="right")

        sync_btn = tk.Button(
            btn_box,
            text="🔄 Sync Timesheets (API)",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["sidebar_bg"],
            fg=self.colors["dark_teal"],
            activebackground=self.colors["border_peach"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=6,
            command=self.action_sync_attendance
        )
        sync_btn.pack(side="left", padx=(0, 8))

        upload_btn = tk.Button(
            btn_box,
            text="📥 Upload Biometric CSV",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["white"],
            fg=self.colors["primary_orange"],
            highlightbackground=self.colors["primary_orange"],
            highlightthickness=1,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=5,
            command=self.action_upload_biometric_csv
        )
        upload_btn.pack(side="left")

        # Summary strip
        strip = tk.Frame(card, bg="#F7FCFC", highlightbackground=self.colors["border_light"], highlightthickness=1, padx=12, pady=8)
        strip.pack(fill="x", pady=(0, 12))

        tot_hours = sum(i["reg_hours"] + i["ot_hours"] + i["holiday_hours"] for i in self.payroll_items)
        tot_ot = sum(i["ot_hours"] for i in self.payroll_items)
        tk.Label(strip, text=f"Status: {self.sync_timestamp}", font=("Segoe UI", 7, "bold"), fg=self.colors["deep_teal"], bg="#F7FCFC").pack(side="left")
        tk.Label(strip, text=f"Total Logged Hours: {tot_hours:.1f} hrs  |  Total Overtime: {tot_ot:.1f} hrs  |  Leave Deductions: Applied", font=("Segoe UI", 7), fg=self.colors["text_dark"], bg="#F7FCFC").pack(side="right")

        # Multi-Column Table Grid
        cols = [
            ("Employee", 3, "w"),
            ("Department", 2, "w"),
            ("Regular Hours", 2, "e"),
            ("Overtime (1.5x)", 2, "e"),
            ("Holiday (2.0x)", 2, "e"),
            ("Leave Balance Used", 2, "w"),
            ("Attendance Status", 2, "center")
        ]

        grid_frame = tk.Frame(card, bg=self.colors["white"])
        grid_frame.pack(fill="both", expand=True)

        for i, (_, w, _) in enumerate(cols):
            grid_frame.columnconfigure(i, weight=w)

        # Header Row
        for idx, (c_name, _, align) in enumerate(cols):
            tk.Label(grid_frame, text=c_name, font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"], anchor=align).grid(row=0, column=idx, sticky="ew", padx=6, pady=(0, 6))
        tk.Frame(grid_frame, height=1, bg=self.colors["border_light"]).grid(row=1, column=0, columnspan=len(cols), sticky="ew", pady=(0, 6))

        # Data Rows
        for r_idx, emp in enumerate(self.payroll_items, start=2):
            # Col 0: Avatar + Name
            emp_box = tk.Frame(grid_frame, bg=self.colors["white"])
            emp_box.grid(row=r_idx, column=0, sticky="w", padx=6, pady=4)
            av = tk.Canvas(emp_box, width=28, height=28, bg=self.colors["white"], highlightthickness=0)
            av.pack(side="left", padx=(0, 6))
            av.create_oval(2, 2, 26, 26, fill=emp["avatar_color"], outline="")
            av.create_text(14, 14, text=emp["initials"], fill="#FFFFFF", font=("Segoe UI", 7, "bold"))
            tk.Label(emp_box, text=emp["name"], font=("Segoe UI", 8, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(side="left")

            # Col 1: Dept
            tk.Label(grid_frame, text=emp["dept"], font=("Segoe UI", 8), fg=self.colors["text_dark"], bg=self.colors["white"], anchor="w").grid(row=r_idx, column=1, sticky="ew", padx=6, pady=4)
            # Col 2: Reg Hours
            tk.Label(grid_frame, text=f"{emp['reg_hours']:.1f} hrs", font=("Segoe UI", 8), fg=self.colors["text_dark"], bg=self.colors["white"], anchor="e").grid(row=r_idx, column=2, sticky="ew", padx=6, pady=4)
            # Col 3: OT Hours
            tk.Label(grid_frame, text=f"+{emp['ot_hours']:.1f} hrs", font=("Segoe UI", 8, "bold"), fg=self.colors["primary_orange"], bg=self.colors["white"], anchor="e").grid(row=r_idx, column=3, sticky="ew", padx=6, pady=4)
            # Col 4: Holiday Hours
            tk.Label(grid_frame, text=f"{emp['holiday_hours']:.1f} hrs", font=("Segoe UI", 8), fg=self.colors["deep_teal"], bg=self.colors["white"], anchor="e").grid(row=r_idx, column=4, sticky="ew", padx=6, pady=4)
            # Col 5: Leave Balance
            tk.Label(grid_frame, text=f"{emp['pto_used']}d used ({emp['pto_balance']}d left)", font=("Segoe UI", 7), fg=self.colors["gray_text"], bg=self.colors["white"], anchor="w").grid(row=r_idx, column=5, sticky="ew", padx=6, pady=4)
            # Col 6: Status
            badge = RoundedBadge(grid_frame, text="Synced ✓", bg_color=self.colors["pill_approved"], fg_color=self.colors["pill_approved_text"], radius=8, width=70, height=20, parent_bg=self.colors["white"])
            badge.grid(row=r_idx, column=6, padx=6, pady=4)

    def action_sync_attendance(self):
        self.sync_timestamp = f"Synced {datetime.datetime.now().strftime('%I:%M:%S %p')} via Cloud Timesheets API"
        self.recalculate_live_engine()
        self.render_active_step()
        messagebox.showinfo("Attendance Ingestion", "Successfully synced all biometric and timesheet records from remote clocking terminals!", parent=self)

    def action_upload_biometric_csv(self):
        f = filedialog.askopenfilename(parent=self, title="Select Biometric CSV", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if f:
            messagebox.showinfo("File Uploaded", f"Biometric punch logs loaded from:\n{os.path.basename(f)}\nNo discrepancies found.", parent=self)

    # =========================================================================
    # STEP 2: ADJUSTMENTS & RECURRING VARIABLE ENTRIES
    # =========================================================================
    def render_step_2_adjustments(self, parent):
        card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=18,
            pady=16
        )
        card.pack(fill="both", expand=True)

        # Header
        hdr = tk.Frame(card, bg=self.colors["white"])
        hdr.pack(fill="x", pady=(0, 14))

        left_hdr = tk.Frame(hdr, bg=self.colors["white"])
        left_hdr.pack(side="left")

        tk.Label(
            left_hdr,
            text="STEP 2: ADJUSTMENTS & RECURRING VARIABLE ENTRIES",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["primary_orange"],
            bg=self.colors["white"]
        ).pack(anchor="w")

        tk.Label(
            left_hdr,
            text="One-time bonuses, expense reimbursements, and pre-tax benefit contributions.",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        ).pack(anchor="w", pady=(2, 0))

        add_btn = tk.Button(
            hdr,
            text="Add Custom Adjustment +",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["primary_orange"],
            fg=self.colors["white"],
            activebackground=self.colors["soft_orange"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            command=self.show_quick_adjustment_popup
        )
        add_btn.pack(side="right")

        # Table Grid
        cols = [
            ("Employee", 3, "w"),
            ("Performance Bonus", 2, "e"),
            ("Travel Reimbursement", 2, "e"),
            ("Pre-Tax Health", 2, "e"),
            ("401(k) Contribution", 2, "e"),
            ("Net Adjustment Impact", 2, "e"),
            ("Action", 1, "center")
        ]

        grid_frame = tk.Frame(card, bg=self.colors["white"])
        grid_frame.pack(fill="both", expand=True)

        for i, (_, w, _) in enumerate(cols):
            grid_frame.columnconfigure(i, weight=w)

        for idx, (c_name, _, align) in enumerate(cols):
            tk.Label(grid_frame, text=c_name, font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"], anchor=align).grid(row=0, column=idx, sticky="ew", padx=6, pady=(0, 6))
        tk.Frame(grid_frame, height=1, bg=self.colors["border_light"]).grid(row=1, column=0, columnspan=len(cols), sticky="ew", pady=(0, 6))

        for r_idx, emp in enumerate(self.payroll_items, start=2):
            emp_box = tk.Frame(grid_frame, bg=self.colors["white"])
            emp_box.grid(row=r_idx, column=0, sticky="w", padx=6, pady=4)
            av = tk.Canvas(emp_box, width=28, height=28, bg=self.colors["white"], highlightthickness=0)
            av.pack(side="left", padx=(0, 6))
            av.create_oval(2, 2, 26, 26, fill=emp["avatar_color"], outline="")
            av.create_text(14, 14, text=emp["initials"], fill="#FFFFFF", font=("Segoe UI", 7, "bold"))
            tk.Label(emp_box, text=emp["name"], font=("Segoe UI", 8, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(side="left")

            tk.Label(grid_frame, text=f"+${emp['bonus']:,.2f}", font=("Segoe UI", 8), fg=self.colors["dark_teal"], bg=self.colors["white"], anchor="e").grid(row=r_idx, column=1, sticky="ew", padx=6, pady=4)
            tk.Label(grid_frame, text=f"+${emp['reimbursement']:,.2f}", font=("Segoe UI", 8), fg=self.colors["dark_teal"], bg=self.colors["white"], anchor="e").grid(row=r_idx, column=2, sticky="ew", padx=6, pady=4)
            tk.Label(grid_frame, text=f"-${emp['pretax_health']:,.2f}", font=("Segoe UI", 8), fg="#E05252", bg=self.colors["white"], anchor="e").grid(row=r_idx, column=3, sticky="ew", padx=6, pady=4)
            tk.Label(grid_frame, text=f"-${emp['pretax_401k']:,.2f}", font=("Segoe UI", 8), fg="#E05252", bg=self.colors["white"], anchor="e").grid(row=r_idx, column=4, sticky="ew", padx=6, pady=4)

            net_adj = (emp['bonus'] + emp['reimbursement']) - (emp['pretax_health'] + emp['pretax_401k'])
            sign = "+" if net_adj >= 0 else ""
            adj_col = self.colors["primary_orange"] if net_adj >= 0 else "#E05252"
            tk.Label(grid_frame, text=f"{sign}${net_adj:,.2f}", font=("Segoe UI", 8, "bold"), fg=adj_col, bg=self.colors["white"], anchor="e").grid(row=r_idx, column=5, sticky="ew", padx=6, pady=4)

            edit_btn = tk.Button(
                grid_frame,
                text="Edit",
                font=("Segoe UI", 7, "bold"),
                bg=self.colors["white"],
                fg=self.colors["primary_orange"],
                highlightbackground=self.colors["primary_orange"],
                highlightthickness=1,
                bd=0,
                relief="flat",
                cursor="hand2",
                padx=8,
                pady=1,
                command=lambda e=emp: self.edit_adjustment_entry(e)
            )
            edit_btn.grid(row=r_idx, column=6, padx=6, pady=4)

    def show_quick_adjustment_popup(self):
        messagebox.showinfo("Quick Adjustment", "Select an employee row to edit specific performance bonus, travel expense or insurance contribution figures.", parent=self)

    def edit_adjustment_entry(self, emp):
        """Allows modifying bonus or reimbursement on the fly."""
        dialog = tk.Toplevel(self)
        dialog.title(f"Edit Adjustments: {emp['name']}")
        dialog.geometry("360x280")
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors["white"])
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text=f"Adjustments for {emp['name']}", font=("Segoe UI", 10, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(padx=20, pady=(16, 10), anchor="w")

        tk.Label(dialog, text="One-Time Bonus ($):", font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(padx=20, anchor="w")
        bonus_ent = tk.Entry(dialog, font=("Segoe UI", 9))
        bonus_ent.insert(0, str(emp["bonus"]))
        bonus_ent.pack(fill="x", padx=20, pady=(2, 8))

        tk.Label(dialog, text="Expense Reimbursement ($):", font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"]).pack(padx=20, anchor="w")
        reimb_ent = tk.Entry(dialog, font=("Segoe UI", 9))
        reimb_ent.insert(0, str(emp["reimbursement"]))
        reimb_ent.pack(fill="x", padx=20, pady=(2, 14))

        def _save():
            try:
                emp["bonus"] = float(bonus_ent.get())
                emp["reimbursement"] = float(reimb_ent.get())
                self.recalculate_live_engine()
                dialog.destroy()
                self.render_active_step()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numeric figures.", parent=dialog)

        tk.Button(dialog, text="Save Adjustments", font=("Segoe UI", 8, "bold"), bg=self.colors["primary_orange"], fg=self.colors["white"], bd=0, relief="flat", cursor="hand2", padx=12, pady=6, command=_save).pack(padx=20, anchor="e")

    # =========================================================================
    # STEP 3: AUTOMATED CALCULATION ENGINE
    # =========================================================================
    def render_step_3_calculation_engine(self, parent):
        card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=18,
            pady=16
        )
        card.pack(fill="both", expand=True)

        # Header
        hdr = tk.Frame(card, bg=self.colors["white"])
        hdr.pack(fill="x", pady=(0, 14))

        left_hdr = tk.Frame(hdr, bg=self.colors["white"])
        left_hdr.pack(side="left")

        tk.Label(
            left_hdr,
            text="STEP 3: AUTOMATED CALCULATION ENGINE",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["primary_orange"],
            bg=self.colors["white"]
        ).pack(anchor="w")

        tk.Label(
            left_hdr,
            text="Statutory tax engine, FICA/Medicare rules, and net take-home pay distribution.",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        ).pack(anchor="w", pady=(2, 0))

        recalc_btn = tk.Button(
            hdr,
            text="⚡ Run Full Recalculation",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["primary_orange"],
            fg=self.colors["white"],
            activebackground=self.colors["soft_orange"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            command=self.action_run_recalc_step3
        )
        recalc_btn.pack(side="right")

        # 4 High-Level Metric Tiles for the Engine
        tiles = tk.Frame(card, bg=self.colors["white"])
        tiles.pack(fill="x", pady=(0, 14))

        tot_gross = sum(i["gross_pay"] for i in self.payroll_items)
        tot_tax = sum(i["total_tax"] for i in self.payroll_items)
        tot_ben = sum(i["total_benefits"] for i in self.payroll_items)
        tot_net = sum(i["net_pay"] for i in self.payroll_items)

        specs = [
            ("TOTAL GROSS PAY", f"${tot_gross:,.2f}", "Base + OT + Bonuses"),
            ("TOTAL TAX WITHHOLDING", f"-${tot_tax:,.2f}", "Fed + State + FICA 7.65%"),
            ("BENEFIT DEDUCTIONS", f"-${tot_ben:,.2f}", "Health & 401(k) Pre-tax"),
            ("NET DISBURSEMENT", f"${tot_net:,.2f}", "100% EFT Direct Deposit")
        ]

        for i, (t, v, s) in enumerate(specs):
            tile = tk.Frame(tiles, bg="#F7FCFC", highlightbackground=self.colors["border_light"], highlightthickness=1, padx=12, pady=8)
            tile.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            tiles.columnconfigure(i, weight=1)
            tk.Label(tile, text=t, font=("Segoe UI", 7, "bold"), fg=self.colors["gray_text"], bg="#F7FCFC").pack(anchor="w")
            tk.Label(tile, text=v, font=("Segoe UI", 12, "bold"), fg=self.colors["dark_teal"] if i != 1 and i != 2 else "#E05252", bg="#F7FCFC").pack(anchor="w", pady=(1, 1))
            tk.Label(tile, text=s, font=("Segoe UI", 6), fg=self.colors["gray_text"], bg="#F7FCFC").pack(anchor="w")

        # Calculation Multi-Column Grid
        cols = [
            ("Employee", 3, "w"),
            ("Base Salary", 2, "e"),
            ("Gross Earnings", 2, "e"),
            ("Federal Tax", 2, "e"),
            ("State Tax", 2, "e"),
            ("FICA / Medicare", 2, "e"),
            ("Benefits", 2, "e"),
            ("Net Take-Home", 2, "e")
        ]

        grid_frame = tk.Frame(card, bg=self.colors["white"])
        grid_frame.pack(fill="both", expand=True)

        for i, (_, w, _) in enumerate(cols):
            grid_frame.columnconfigure(i, weight=w)

        for idx, (c_name, _, align) in enumerate(cols):
            tk.Label(grid_frame, text=c_name, font=("Segoe UI", 8, "bold"), fg=self.colors["gray_text"], bg=self.colors["white"], anchor=align).grid(row=0, column=idx, sticky="ew", padx=6, pady=(0, 6))
        tk.Frame(grid_frame, height=1, bg=self.colors["border_light"]).grid(row=1, column=0, columnspan=len(cols), sticky="ew", pady=(0, 6))

        for r_idx, emp in enumerate(self.payroll_items, start=2):
            emp_box = tk.Frame(grid_frame, bg=self.colors["white"])
            emp_box.grid(row=r_idx, column=0, sticky="w", padx=6, pady=4)
            av = tk.Canvas(emp_box, width=28, height=28, bg=self.colors["white"], highlightthickness=0)
            av.pack(side="left", padx=(0, 6))
            av.create_oval(2, 2, 26, 26, fill=emp["avatar_color"], outline="")
            av.create_text(14, 14, text=emp["initials"], fill="#FFFFFF", font=("Segoe UI", 7, "bold"))
            tk.Label(emp_box, text=emp["name"], font=("Segoe UI", 8, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(side="left")

            tk.Label(grid_frame, text=f"${emp['base_salary']:,.2f}", font=("Segoe UI", 8), fg=self.colors["text_dark"], bg=self.colors["white"], anchor="e").grid(row=r_idx, column=1, sticky="ew", padx=6, pady=4)
            tk.Label(grid_frame, text=f"${emp['gross_pay']:,.2f}", font=("Segoe UI", 8, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"], anchor="e").grid(row=r_idx, column=2, sticky="ew", padx=6, pady=4)
            tk.Label(grid_frame, text=f"-${emp['fed_tax']:,.2f}", font=("Segoe UI", 8), fg="#E05252", bg=self.colors["white"], anchor="e").grid(row=r_idx, column=3, sticky="ew", padx=6, pady=4)
            tk.Label(grid_frame, text=f"-${emp['state_tax']:,.2f}", font=("Segoe UI", 8), fg="#E05252", bg=self.colors["white"], anchor="e").grid(row=r_idx, column=4, sticky="ew", padx=6, pady=4)
            tk.Label(grid_frame, text=f"-${emp['fica_tax']:,.2f}", font=("Segoe UI", 8), fg="#E05252", bg=self.colors["white"], anchor="e").grid(row=r_idx, column=5, sticky="ew", padx=6, pady=4)
            tk.Label(grid_frame, text=f"-${emp['total_benefits']:,.2f}", font=("Segoe UI", 8), fg="#E05252", bg=self.colors["white"], anchor="e").grid(row=r_idx, column=6, sticky="ew", padx=6, pady=4)
            tk.Label(grid_frame, text=f"${emp['net_pay']:,.2f}", font=("Segoe UI", 9, "bold"), fg=self.colors["deep_teal"], bg=self.colors["white"], anchor="e").grid(row=r_idx, column=7, sticky="ew", padx=6, pady=4)

    def action_run_recalc_step3(self):
        self.recalculate_live_engine()
        self.render_active_step()
        messagebox.showinfo("Calculation Complete", "Payroll calculation engine executed successfully.\nAll statutory tax withholdings are up-to-date.", parent=self)

    # =========================================================================
    # STEP 4: AUDIT, VERIFICATION & EXCEPTION HANDLING
    # =========================================================================
    def render_step_4_audit_exceptions(self, parent):
        card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=18,
            pady=16
        )
        card.pack(fill="both", expand=True)

        # Header
        hdr = tk.Frame(card, bg=self.colors["white"])
        hdr.pack(fill="x", pady=(0, 14))

        left_hdr = tk.Frame(hdr, bg=self.colors["white"])
        left_hdr.pack(side="left")

        tk.Label(
            left_hdr,
            text="STEP 4: AUDIT, VERIFICATION & EXCEPTION HANDLING",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["primary_orange"],
            bg=self.colors["white"]
        ).pack(anchor="w")

        tk.Label(
            left_hdr,
            text="Automated pre-flight checks to catch payroll mistakes before payments finalize.",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        ).pack(anchor="w", pady=(2, 0))

        resolve_btn = tk.Button(
            hdr,
            text="✓ Clear & Approve All Exceptions",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["pill_approved_text"] if not self.exceptions_resolved else self.colors["sidebar_bg"],
            fg=self.colors["white"] if not self.exceptions_resolved else self.colors["dark_teal"],
            activebackground=self.colors["dark_teal"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            command=self.action_resolve_all_exceptions
        )
        resolve_btn.pack(side="right")

        # 4 Core Rule Audits
        rules_box = tk.Frame(card, bg=self.colors["white"])
        rules_box.pack(fill="x", pady=(0, 14))

        rules = [
            ("RULE 1: Negative Net Pay Check", "Passed", "Zero employees have deductions exceeding gross salary.", self.colors["pill_approved"], self.colors["pill_approved_text"]),
            ("RULE 2: Overtime Threshold Alert", "Resolved" if self.exceptions_resolved else "Notice (1)", "Jordan Patel logged 12.0h OT (>10.0h company threshold).", self.colors["pill_approved"] if self.exceptions_resolved else self.colors["pill_warning"], self.colors["pill_approved_text"] if self.exceptions_resolved else self.colors["pill_warning_text"]),
            ("RULE 3: W-4 Statutory Tax Compliance", "Passed", "All 5 employee W-4 tax exemptions verified.", self.colors["pill_approved"], self.colors["pill_approved_text"]),
            ("RULE 4: Pay Variance vs Prior Period", "Resolved" if self.exceptions_resolved else "Notice (1)", "Sofia Chen bonus entry reflects +11.2% variance.", self.colors["pill_approved"] if self.exceptions_resolved else self.colors["pill_warning"], self.colors["pill_approved_text"] if self.exceptions_resolved else self.colors["pill_warning_text"])
        ]

        for i, (title, status, desc, bg_c, fg_c) in enumerate(rules):
            box = tk.Frame(rules_box, bg="#FBFDFD", highlightbackground=self.colors["border_light"], highlightthickness=1, padx=12, pady=10)
            box.pack(fill="x", pady=3)

            top_line = tk.Frame(box, bg="#FBFDFD")
            top_line.pack(fill="x")
            tk.Label(top_line, text=title, font=("Segoe UI", 8, "bold"), fg=self.colors["text_dark"], bg="#FBFDFD").pack(side="left")
            badge = tk.Label(top_line, text=status, font=("Segoe UI", 7, "bold"), bg=bg_c, fg=fg_c, padx=6, pady=1)
            badge.pack(side="right")

            tk.Label(box, text=desc, font=("Segoe UI", 7), fg=self.colors["gray_text"], bg="#FBFDFD").pack(anchor="w", pady=(2, 0))

        # Exceptions Details Card
        detail_card = tk.Frame(card, bg="#FFFDF7", highlightbackground=self.colors["border_peach"], highlightthickness=1, padx=14, pady=10)
        detail_card.pack(fill="x")

        tk.Label(detail_card, text="AUDIT EXCEPTION LOGS & SIGN-OFF", font=("Segoe UI", 8, "bold"), fg=self.colors["primary_orange"], bg="#FFFDF7").pack(anchor="w")
        status_msg = "All exceptions have been reviewed and approved by Payroll Admin." if self.exceptions_resolved else "2 non-blocking warnings pending administrator sign-off before final lock."
        tk.Label(detail_card, text=status_msg, font=("Segoe UI", 8), fg=self.colors["text_dark"], bg="#FFFDF7").pack(anchor="w", pady=(2, 0))

    def action_resolve_all_exceptions(self):
        self.exceptions_resolved = True
        self.render_active_step()
        messagebox.showinfo("Audit Sign-off", "All payroll audit flags and variance notices have been officially acknowledged and verified.", parent=self)

    # =========================================================================
    # STEP 5: FINALIZATION & DISBURSEMENT TRIGGERS
    # =========================================================================
    def render_step_5_finalization_triggers(self, parent):
        card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=18,
            pady=16
        )
        card.pack(fill="both", expand=True)

        # Header
        hdr = tk.Frame(card, bg=self.colors["white"])
        hdr.pack(fill="x", pady=(0, 14))

        left_hdr = tk.Frame(hdr, bg=self.colors["white"])
        left_hdr.pack(side="left")

        tk.Label(
            left_hdr,
            text="STEP 5: FINALIZATION & DISBURSEMENT TRIGGERS",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["primary_orange"],
            bg=self.colors["white"]
        ).pack(anchor="w")

        tk.Label(
            left_hdr,
            text="Final authorization, period seal, and direct deposit payment triggers.",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        ).pack(anchor="w", pady=(2, 0))

        lock_badge = RoundedBadge(
            hdr,
            text="🔒 Period Locked" if self.period_locked else "⏳ Pending Seal",
            bg_color=self.colors["pill_approved"] if self.period_locked else self.colors["pill_pending"],
            fg_color=self.colors["pill_approved_text"] if self.period_locked else self.colors["pill_pending_text"],
            radius=8,
            width=120,
            height=24,
            parent_bg=self.colors["white"]
        )
        lock_badge.pack(side="right")

        # Cycle Overview Callout
        callout = tk.Frame(
            card,
            bg=self.colors["pill_approved"] if self.period_locked else "#FFF9F0",
            highlightbackground=self.colors["dark_teal"] if self.period_locked else self.colors["border_peach"],
            highlightthickness=1,
            padx=16,
            pady=12
        )
        callout.pack(fill="x", pady=(0, 14))

        tot_net = sum(i["net_pay"] for i in self.payroll_items)
        tk.Label(
            callout,
            text=f"PAYROLL RUN APPROVED TOTAL: ${tot_net:,.2f}",
            font=("Segoe UI", 13, "bold"),
            fg=self.colors["deep_teal"] if self.period_locked else self.colors["primary_orange"],
            bg=callout["bg"]
        ).pack(anchor="w")

        tk.Label(
            callout,
            text=f"5 of 5 employee accounts verified • Pay Date: September 30, 2026 • Period: {self.pay_period_name}",
            font=("Segoe UI", 8),
            fg=self.colors["text_dark"],
            bg=callout["bg"]
        ).pack(anchor="w", pady=(2, 0))

        # 4 Automated Disbursement Trigger Cards
        triggers_frame = tk.Frame(card, bg=self.colors["white"])
        triggers_frame.pack(fill="x", pady=(0, 14))

        triggers = [
            ("📄 1. Digital Payslips Generation", "Generate and stamp PDF statement records for all 5 employees.", "Generate Slips", self.action_trigger_payslips),
            ("🏦 2. NACHA / ACH Direct Deposit File", "Compile batch ACH transfer instructions for corporate banking.", "Create ACH File", self.action_trigger_ach),
            ("📧 3. Automated Employee Notification", "Dispatch secured salary notices and direct deposit confirmation emails.", "Email Staff", self.action_trigger_email),
            ("🔒 4. Period Lock & Compliance Seal", "Seal current cycle against inadvertent retroactive changes.", "Seal Cycle", self.action_trigger_lock)
        ]

        for title, desc, btn_text, cmd in triggers:
            row = tk.Frame(triggers_frame, bg="#F9FCFC", highlightbackground=self.colors["border_light"], highlightthickness=1, padx=14, pady=10)
            row.pack(fill="x", pady=3)

            info = tk.Frame(row, bg="#F9FCFC")
            info.pack(side="left")
            tk.Label(info, text=title, font=("Segoe UI", 8, "bold"), fg=self.colors["text_dark"], bg="#F9FCFC").pack(anchor="w")
            tk.Label(info, text=desc, font=("Segoe UI", 7), fg=self.colors["gray_text"], bg="#F9FCFC").pack(anchor="w", pady=(1, 0))

            btn = tk.Button(
                row,
                text=btn_text,
                font=("Segoe UI", 8, "bold"),
                bg=self.colors["sidebar_bg"],
                fg=self.colors["dark_teal"],
                activebackground=self.colors["border_peach"],
                bd=0,
                relief="flat",
                cursor="hand2",
                padx=12,
                pady=5,
                command=cmd
            )
            btn.pack(side="right")

    def action_trigger_payslips(self):
        messagebox.showinfo("Payslips Generated", f"✓ Digital payslip vouchers generated for all {len(self.payroll_items)} employees.\nAvailable under 'Payroll & Payslips' ledger.", parent=self)

    def action_trigger_ach(self):
        tot_net = sum(i["net_pay"] for i in self.payroll_items)
        messagebox.showinfo("ACH Batch Exported", f"✓ Corporate NACHA Direct Deposit batch generated successfully!\nTotal EFT: ${tot_net:,.2f}\nDestination: Chase Commercial ACH Gateway.", parent=self)

    def action_trigger_email(self):
        messagebox.showinfo("Notifications Sent", "✓ Notification emails and encrypted payslip links dispatched to employee mailboxes.", parent=self)

    def action_trigger_lock(self):
        self.period_locked = True
        self.render_active_step()
        messagebox.showinfo("Period Sealed", f"✓ Pay Period '{self.pay_period_name}' is now Approved & Locked.\nAccidental overrides are strictly prevented.", parent=self)

    def action_finalize_payroll_cycle(self):
        self.period_locked = True
        self.render_active_step()
        messagebox.showinfo(
            "Payroll Run Complete! 🎉",
            f"Payroll cycle '{self.pay_period_name}' has been successfully finalized and processed!\n\n"
            f"Total Employees: {len(self.payroll_items)}\n"
            f"Total Net Pay Disbursed: ${sum(i['net_pay'] for i in self.payroll_items):,.2f}\n"
            f"All payslips, ACH batches, and statutory records have been saved.",
            parent=self
        )

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
    app = SteadypayProcessPayPage()
    app.mainloop()
