import os
import sys
import subprocess
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from data import (
    get_admin_data, get_all_employees,
    draw_rounded_rectangle, RoundedBadge,
    Role, get_current_user
)

class ToolTip:
    """Lightweight tooltip widget for displaying helpful role and status context."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        try:
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
            self.tip_window = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            label = tk.Label(
                tw,
                text=self.text,
                justify="left",
                background="#2C3E50",
                foreground="#FFFFFF",
                relief="flat",
                font=("Segoe UI", 8),
                padx=8,
                pady=4
            )
            label.pack()
        except Exception:
            pass

    def hide_tip(self, event=None):
        if self.tip_window:
            try:
                self.tip_window.destroy()
            except Exception:
                pass
            self.tip_window = None

class SteadypayProcessPayPage(tk.Frame):
    def __init__(self, parent=None, controller=None):
        if parent is None:
            self.root = tk.Tk()
            self.root.title("Steadypay - Process Payroll")
            self.root.geometry("1240x780")
            self.root.minsize(1120, 680)
            self.root.configure(bg="#FFFFFF")
            super().__init__(self.root, bg="#FFFFFF")
            self.pack(fill="both", expand=True)
            self.controller = controller
        else:
            self.root = parent.winfo_toplevel()
            super().__init__(parent, bg="#FFFFFF")
            self.controller = controller

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

        # Centralized Admin Data & User Session
        self.admin_data = get_admin_data()
        self.user = get_current_user()

        # Wizard State
        self.current_step = 1
        self.total_steps = 5
        self.visited_steps = {1}
        self.step_titles = [
            ("Time & Attendance", "Sync timesheets & overtime"),
            ("Adjustments & Variable", "Bonuses, allowances & statutory entries"),
            ("Automated Calculation", "BIR taxes & statutory net pay"),
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

            # Adjustments & Mandatory Benefits
            bonus = bonuses_map.get(eid, 200.00)
            reimbursement = 75.00 if eid in ("EMP-101", "EMP-103") else 0.00
            pretax_health = 160.00  # PhilHealth Employee Share
            pretax_401k = round(base * 0.04, 2)  # Pag-IBIG Mandatory Contribution

            gross_pay = round(base + ot_pay + bonus + reimbursement, 2)

            # Philippine Statutory Deductions & Tax Withholdings (TRAIN Law RA 10963)
            bir_tax = round(gross_pay * 0.105, 2)      # 10.5% BIR Withholding (TRAIN Law)
            sss_tax = round(gross_pay * 0.045, 2)      # 4.5% SSS Employee Share (RA 11199)
            philhealth_tax = round(gross_pay * 0.0765, 2) # PhilHealth & Pag-IBIG statutory share
            total_tax = round(bir_tax + sss_tax + philhealth_tax, 2)

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
                "bir_tax": bir_tax,
                "sss_tax": sss_tax,
                "philhealth_tax": philhealth_tax,
                "fed_tax": bir_tax,
                "state_tax": sss_tax,
                "fica_tax": philhealth_tax,
                "total_tax": total_tax,
                "total_benefits": total_benefits,
                "total_deductions": total_deductions,
                "net_pay": net_pay,
                "exception_flag": (eid in ("EMP-102", "EMP-103"))
            })

    def recalculate_live_engine(self):
        """Recalculates all mathematical figures dynamically based on Philippine statutory rates."""
        for item in self.payroll_items:
            ot_rate = round(item["hourly_rate"] * 1.5, 2)
            hol_rate = round(item["hourly_rate"] * 2.0, 2)
            item["ot_pay"] = round((item["ot_hours"] * ot_rate) + (item["holiday_hours"] * hol_rate), 2)
            item["gross_pay"] = round(item["base_salary"] + item["ot_pay"] + item["bonus"] + item["reimbursement"], 2)

            item["bir_tax"] = round(item["gross_pay"] * 0.105, 2)
            item["sss_tax"] = round(item["gross_pay"] * 0.045, 2)
            item["philhealth_tax"] = round(item["gross_pay"] * 0.0765, 2)
            item["fed_tax"] = item["bir_tax"]
            item["state_tax"] = item["sss_tax"]
            item["fica_tax"] = item["philhealth_tax"]
            item["total_tax"] = round(item["bir_tax"] + item["sss_tax"] + item["philhealth_tax"], 2)

            item["pretax_401k"] = round(item["base_salary"] * 0.04, 2)
            item["total_benefits"] = round(item["pretax_health"] + item["pretax_401k"], 2)
            item["total_deductions"] = round(item["total_tax"] + item["total_benefits"], 2)
            item["net_pay"] = round(item["gross_pay"] - item["total_deductions"], 2)

        self.update_live_summary_bar()

    # ==========================================
    # LAYOUT SETUP
    # ==========================================
    def setup_layout(self):
        if self.controller is None:
            self.create_sidebar()
            self.create_scrollable_main_content()
        else:
            self.create_scrollable_main_content(parent=self)

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
            ("👥", "Workforce\nDirectory", False),
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
        menu_to_page = {
            "Dashboard": "dashboard",
            "Workforce\nDirectory": "employee",
            "Process payroll": "process_pay",
            "Payroll &\nPayslips": "pay_records_slips",
            "Settings": "settings"
        }
        if self.controller:
            page = menu_to_page.get(menu_name, "dashboard")
            self.controller.show_page(page)
            return

        if menu_name == "Dashboard":
            self.navigate_to_dashboard()
            return

        menu_map = {
            "Workforce\nDirectory": "aEmployee.py",
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
    def create_scrollable_main_content(self, parent=None):
        if parent is None:
            right_container = tk.Frame(self, bg=self.colors["white"])
            right_container.pack(side="right", fill="both", expand=True)
        else:
            right_container = parent

        # 1. Fixed Top Header outside canvas
        self.create_top_header(right_container)

        # 2. Persistent Live Summary & Exception Drawer (Always Visible)
        self.create_persistent_summary_bar(right_container)

        # 3. Sticky Bottom Navigation Bar (Fixed at Viewport Bottom)
        self.create_wizard_nav_footer(right_container)

        # 4. Middle Scrollable Container
        middle_frame = tk.Frame(right_container, bg=self.colors["white"])
        middle_frame.pack(side="left", fill="both", expand=True)

        self.main_canvas = tk.Canvas(middle_frame, bg=self.colors["white"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(middle_frame, orient="vertical", command=self.main_canvas.yview)

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

        self.main_canvas.bind("<MouseWheel>", self._on_mousewheel)

        # Step-by-Step Payroll Wizard Stepper Bar (Clickable Tabs)
        self.create_wizard_stepper_bar(self.content_frame)

        # Dynamic Step Content Container
        self.step_content_container = tk.Frame(self.content_frame, bg=self.colors["white"])
        self.step_content_container.pack(fill="both", expand=True, pady=(0, 14))

        # Render active step
        self.render_active_step()

    def _on_mousewheel(self, event):
        if hasattr(self, "main_canvas") and self.main_canvas.winfo_exists():
            self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_show(self):
        """Called whenever this tab is brought into view."""
        if hasattr(self, "main_canvas"):
            self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

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
            text="Interactive Payroll Workbench • Direct Stepper Navigation & Real-Time Calculation Engine",
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
            text=f"{self.user.role_title}",
            font=("Segoe UI", 7),
            fg=self.colors["gray_text"],
            bg=self.colors["white"]
        ).pack(anchor="w")

    # ==========================================
    # PERSISTENT LIVE SUMMARY & EXCEPTION DRAWER
    # ==========================================
    def create_persistent_summary_bar(self, parent):
        """Builds the persistent live payout summary panel and exception drawer."""
        self.summary_bar = tk.Frame(
            parent,
            bg="#F7FCFC",
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            padx=22,
            pady=10
        )
        self.summary_bar.pack(side="top", fill="x")

        inner = tk.Frame(self.summary_bar, bg="#F7FCFC")
        inner.pack(fill="x")

        # Left: 4 Financial KPI Blocks
        left_kpis = tk.Frame(inner, bg="#F7FCFC")
        left_kpis.pack(side="left")

        # 1. Total Gross Pay
        b1 = tk.Frame(left_kpis, bg="#F7FCFC")
        b1.pack(side="left", padx=(0, 22))
        tk.Label(b1, text="TOTAL GROSS PAY", font=("Segoe UI", 7, "bold"), fg=self.colors["gray_text"], bg="#F7FCFC").pack(anchor="w")
        self.live_lbl_gross = tk.Label(b1, text="$0.00", font=("Segoe UI", 11, "bold"), fg=self.colors["dark_teal"], bg="#F7FCFC")
        self.live_lbl_gross.pack(anchor="w")

        # 2. Tax Withholding
        b2 = tk.Frame(left_kpis, bg="#F7FCFC")
        b2.pack(side="left", padx=(0, 22))
        tk.Label(b2, text="TAX WITHHOLDING", font=("Segoe UI", 7, "bold"), fg=self.colors["gray_text"], bg="#F7FCFC").pack(anchor="w")
        self.live_lbl_tax = tk.Label(b2, text="-$0.00", font=("Segoe UI", 11, "bold"), fg="#E05252", bg="#F7FCFC")
        self.live_lbl_tax.pack(anchor="w")

        # 3. Benefit Deductions
        b3 = tk.Frame(left_kpis, bg="#F7FCFC")
        b3.pack(side="left", padx=(0, 22))
        tk.Label(b3, text="BENEFIT DEDUCTIONS", font=("Segoe UI", 7, "bold"), fg=self.colors["gray_text"], bg="#F7FCFC").pack(anchor="w")
        self.live_lbl_ben = tk.Label(b3, text="-$0.00", font=("Segoe UI", 11, "bold"), fg="#E05252", bg="#F7FCFC")
        self.live_lbl_ben.pack(anchor="w")

        # 4. Net Take-Home Disbursement
        b4 = tk.Frame(left_kpis, bg="#F7FCFC")
        b4.pack(side="left", padx=(0, 22))
        tk.Label(b4, text="NET DISBURSEMENT", font=("Segoe UI", 7, "bold"), fg=self.colors["gray_text"], bg="#F7FCFC").pack(anchor="w")
        self.live_lbl_net = tk.Label(b4, text="$0.00", font=("Segoe UI", 12, "bold"), fg=self.colors["deep_teal"], bg="#F7FCFC")
        self.live_lbl_net.pack(anchor="w")

        # Right: Exception Drawer & Status Badges
        right_drawer = tk.Frame(inner, bg="#F7FCFC")
        right_drawer.pack(side="right")

        # Cycle Pill
        cycle_box = tk.Frame(right_drawer, bg="#F7FCFC")
        cycle_box.pack(side="left", padx=(0, 10))
        tk.Label(cycle_box, text="PAY PERIOD", font=("Segoe UI", 6, "bold"), fg=self.colors["gray_text"], bg="#F7FCFC").pack(anchor="e")
        tk.Label(cycle_box, text=self.pay_period_name, font=("Segoe UI", 8, "bold"), fg=self.colors["text_dark"], bg="#F7FCFC").pack(anchor="e")

        # Clickable Exception Drawer Pill
        self.live_exception_pill = tk.Label(
            right_drawer,
            text="⚠️ 2 Warnings (Click to Audit)",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["pill_warning"],
            fg=self.colors["pill_warning_text"],
            padx=10,
            pady=4,
            cursor="hand2"
        )
        self.live_exception_pill.pack(side="left", padx=(0, 8))
        self.live_exception_pill.bind("<Button-1>", lambda e: self.go_to_step(4))
        ToolTip(self.live_exception_pill, "Click to jump immediately to Step 4: Audit & Exceptions")

        # Lock / Draft Status Badge
        self.live_seal_badge = tk.Label(
            right_drawer,
            text="⏳ Draft Mode",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["pill_pending"],
            fg=self.colors["pill_pending_text"],
            padx=10,
            pady=4
        )
        self.live_seal_badge.pack(side="left")

        # Compute initial figures
        self.update_live_summary_bar()

    def update_live_summary_bar(self):
        if not hasattr(self, "live_lbl_gross"):
            return
        tot_gross = sum(i["gross_pay"] for i in self.payroll_items)
        tot_tax = sum(i["total_tax"] for i in self.payroll_items)
        tot_ben = sum(i["total_benefits"] for i in self.payroll_items)
        tot_net = sum(i["net_pay"] for i in self.payroll_items)

        self.live_lbl_gross.config(text=f"${tot_gross:,.2f}")
        self.live_lbl_tax.config(text=f"-${tot_tax:,.2f}")
        self.live_lbl_ben.config(text=f"-${tot_ben:,.2f}")
        self.live_lbl_net.config(text=f"${tot_net:,.2f}")

        if self.exceptions_resolved:
            self.live_exception_pill.config(
                text="✓ All Checks Passed",
                bg=self.colors["pill_approved"],
                fg=self.colors["pill_approved_text"]
            )
        else:
            self.live_exception_pill.config(
                text="⚠️ 2 Warnings (Click to Audit)",
                bg=self.colors["pill_warning"],
                fg=self.colors["pill_warning_text"]
            )

        if self.period_locked:
            self.live_seal_badge.config(
                text="🔒 Sealed",
                bg=self.colors["pill_approved"],
                fg=self.colors["pill_approved_text"]
            )
        else:
            self.live_seal_badge.config(
                text="⏳ Draft Mode",
                bg=self.colors["pill_pending"],
                fg=self.colors["pill_pending_text"]
            )

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
        """Renders the step circles, titles, and connecting status lines with clickable tabs."""
        for c in self.steps_row.winfo_children():
            c.destroy()

        for idx, (title, subtitle) in enumerate(self.step_titles, start=1):
            is_active = (idx == self.current_step)
            is_completed = (idx < self.current_step or idx in self.visited_steps) and not is_active

            step_frame = tk.Frame(
                self.steps_row,
                bg="#FFF9F2" if is_active else self.colors["white"],
                highlightbackground=self.colors["primary_orange"] if is_active else self.colors["border_light"],
                highlightthickness=1 if is_active else 0,
                cursor="hand2",
                padx=8,
                pady=6
            )
            step_frame.pack(side="left", fill="x", expand=True, padx=4)
            step_frame.bind("<Button-1>", lambda e, s=idx: self.go_to_step(s))

            # Indicator Circle Box
            indicator_box = tk.Frame(step_frame, bg=step_frame["bg"])
            indicator_box.pack(anchor="center", pady=(0, 4))
            indicator_box.bind("<Button-1>", lambda e, s=idx: self.go_to_step(s))

            cv = tk.Canvas(indicator_box, width=30, height=30, bg=step_frame["bg"], highlightthickness=0)
            cv.pack(side="left")
            cv.bind("<Button-1>", lambda e, s=idx: self.go_to_step(s))

            if is_active:
                fill_col = self.colors["primary_orange"]
                out_col = self.colors["primary_orange"]
                txt = str(idx)
                txt_col = "#FFFFFF"
            elif is_completed:
                fill_col = self.colors["pill_approved"]
                out_col = self.colors["dark_teal"]
                txt = "✓"
                txt_col = self.colors["deep_teal"]
            else:
                fill_col = "#F4F7F7"
                out_col = self.colors["border_light"]
                txt = str(idx)
                txt_col = self.colors["gray_text"]

            cv.create_oval(2, 2, 28, 28, fill=fill_col, outline=out_col, width=2 if is_active else 1)
            cv.create_text(15, 15, text=txt, fill=txt_col, font=("Segoe UI", 9, "bold"))

            # Step Title Label
            title_col = self.colors["primary_orange"] if is_active else (self.colors["dark_teal"] if is_completed else self.colors["gray_text"])
            lbl = tk.Label(
                step_frame,
                text=f"{idx}. {title}",
                font=("Segoe UI", 8, "bold" if is_active else "normal"),
                fg=title_col,
                bg=step_frame["bg"]
            )
            lbl.pack(anchor="center")
            lbl.bind("<Button-1>", lambda e, s=idx: self.go_to_step(s))

            sub_lbl = tk.Label(
                step_frame,
                text=subtitle,
                font=("Segoe UI", 6),
                fg=self.colors["gray_text"],
                bg=step_frame["bg"]
            )
            sub_lbl.pack(anchor="center")
            sub_lbl.bind("<Button-1>", lambda e, s=idx: self.go_to_step(s))

    def go_to_step(self, step_number):
        if 1 <= step_number <= self.total_steps:
            self.current_step = step_number
            self.visited_steps.add(step_number)
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
        self.nav_footer = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_light"],
            highlightthickness=1,
            padx=24,
            pady=12
        )
        self.nav_footer.pack(side="bottom", fill="x")

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

        self.save_draft_btn = tk.Button(
            self.nav_footer,
            text="💾 Save Draft",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["white"],
            fg=self.colors["text_dark"],
            highlightbackground=self.colors["border_peach"],
            highlightthickness=1,
            activebackground=self.colors["sidebar_bg"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=6,
            command=self.action_save_draft
        )
        self.save_draft_btn.pack(side="left", padx=12)

        self.next_btn = tk.Button(
            self.nav_footer,
            text="Proceed to Next Step →",
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

    def action_save_draft(self):
        tot_net = sum(i["net_pay"] for i in self.payroll_items)
        messagebox.showinfo(
            "Draft Saved 💾",
            f"Payroll Workbench draft for cycle '{self.pay_period_name}' saved successfully!\n\n"
            f"• Headcount: {len(self.payroll_items)} employees\n"
            f"• Current Net Disbursement: ${tot_net:,.2f}\n"
            f"• All attendance logs, adjustments, and variable entries have been cached.",
            parent=self
        )

    def update_nav_footer_buttons(self):
        if self.current_step == 1:
            self.prev_btn.config(state="disabled", fg="#A0B0B0", cursor="arrow")
        else:
            self.prev_btn.config(state="normal", fg=self.colors["dark_teal"], cursor="hand2")

        if self.current_step == self.total_steps:
            if self.user.has_role(Role.SUPER_ADMIN):
                self.next_btn.config(text="Finalize & Disburse Payroll 🚀", bg=self.colors["dark_teal"])
            else:
                self.next_btn.config(text="Submit for Super Admin Approval 📋", bg=self.colors["primary_orange"])
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
    # STEP 2: ADJUSTMENTS & RECURRING VARIABLE ENTRIES (INLINE WORKBENCH)
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
            text="Interactive Spreadsheet: Edit bonuses & reimbursements directly below. (Auto-calculates & saves live)",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        ).pack(anchor="w", pady=(2, 0))

        # Right Live Indicator Badge
        RoundedBadge(
            hdr,
            text="⚡ Live Grid Active",
            bg_color=self.colors["pill_approved"],
            fg_color=self.colors["pill_approved_text"],
            radius=8,
            width=130,
            height=24,
            parent_bg=self.colors["white"]
        ).pack(side="right")

        # Table Grid
        cols = [
            ("Employee", 3, "w"),
            ("Performance Bonus ($)", 2, "e"),
            ("Travel Reimbursement ($)", 2, "e"),
            ("PhilHealth Share 🔒", 2, "e"),
            ("Pag-IBIG Fund 🔒", 2, "e"),
            ("Net Adjustment Impact", 2, "e"),
            ("Status", 1, "center")
        ]

        grid_frame = tk.Frame(card, bg=self.colors["white"])
        grid_frame.pack(fill="both", expand=True)

        for i, (_, w, _) in enumerate(cols):
            grid_frame.columnconfigure(i, weight=w)

        for idx, (c_name, _, align) in enumerate(cols):
            tk.Label(
                grid_frame,
                text=c_name,
                font=("Segoe UI", 8, "bold"),
                fg=self.colors["gray_text"],
                bg=self.colors["white"],
                anchor=align
            ).grid(row=0, column=idx, sticky="ew", padx=6, pady=(0, 6))
        tk.Frame(grid_frame, height=1, bg=self.colors["border_light"]).grid(row=1, column=0, columnspan=len(cols), sticky="ew", pady=(0, 6))

        for r_idx, emp in enumerate(self.payroll_items, start=2):
            # Col 0: Avatar + Name
            emp_box = tk.Frame(grid_frame, bg=self.colors["white"])
            emp_box.grid(row=r_idx, column=0, sticky="w", padx=6, pady=4)
            av = tk.Canvas(emp_box, width=28, height=28, bg=self.colors["white"], highlightthickness=0)
            av.pack(side="left", padx=(0, 6))
            av.create_oval(2, 2, 26, 26, fill=emp["avatar_color"], outline="")
            av.create_text(14, 14, text=emp["initials"], fill="#FFFFFF", font=("Segoe UI", 7, "bold"))
            tk.Label(emp_box, text=emp["name"], font=("Segoe UI", 8, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(side="left")

            # Col 1: Bonus inline Entry
            b_var = tk.StringVar(value=f"{emp['bonus']:.2f}")
            b_frame = tk.Frame(grid_frame, bg=self.colors["white"])
            b_frame.grid(row=r_idx, column=1, sticky="e", padx=6, pady=3)
            tk.Label(b_frame, text="$", font=("Segoe UI", 8, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(side="left")
            b_entry = tk.Entry(
                b_frame,
                textvariable=b_var,
                font=("Segoe UI", 8, "bold"),
                fg=self.colors["dark_teal"],
                bg=self.colors["white"],
                highlightbackground=self.colors["border_peach"],
                highlightcolor=self.colors["primary_orange"],
                highlightthickness=1,
                bd=0,
                width=8,
                justify="right"
            )
            b_entry.pack(side="left", ipady=2)

            # Col 2: Reimbursement inline Entry
            r_var = tk.StringVar(value=f"{emp['reimbursement']:.2f}")
            r_frame = tk.Frame(grid_frame, bg=self.colors["white"])
            r_frame.grid(row=r_idx, column=2, sticky="e", padx=6, pady=3)
            tk.Label(r_frame, text="$", font=("Segoe UI", 8, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(side="left")
            r_entry = tk.Entry(
                r_frame,
                textvariable=r_var,
                font=("Segoe UI", 8, "bold"),
                fg=self.colors["dark_teal"],
                bg=self.colors["white"],
                highlightbackground=self.colors["border_peach"],
                highlightcolor=self.colors["primary_orange"],
                highlightthickness=1,
                bd=0,
                width=8,
                justify="right"
            )
            r_entry.pack(side="left", ipady=2)

            # Col 3: PhilHealth Share (Locked by Super Admin)
            health_lbl = tk.Label(
                grid_frame,
                text=f"🔒 -${emp['pretax_health']:,.2f}",
                font=("Segoe UI", 8),
                fg="#E05252",
                bg=self.colors["white"],
                anchor="e",
                cursor="question_arrow"
            )
            health_lbl.grid(row=r_idx, column=3, sticky="ew", padx=6, pady=4)
            ToolTip(health_lbl, "PhilHealth Statutory Premium (RA 11223): Managed by Super Admin")

            # Col 4: Pag-IBIG Fund (Locked by Super Admin)
            k401_lbl = tk.Label(
                grid_frame,
                text=f"🔒 -${emp['pretax_401k']:,.2f}",
                font=("Segoe UI", 8),
                fg="#E05252",
                bg=self.colors["white"],
                anchor="e",
                cursor="question_arrow"
            )
            k401_lbl.grid(row=r_idx, column=4, sticky="ew", padx=6, pady=4)
            ToolTip(k401_lbl, "Pag-IBIG / HDMF Statutory Contribution (RA 9679): Managed by Super Admin")

            # Col 5: Net Adjustment Impact
            net_adj = (emp['bonus'] + emp['reimbursement']) - (emp['pretax_health'] + emp['pretax_401k'])
            sign = "+" if net_adj >= 0 else ""
            adj_col = self.colors["primary_orange"] if net_adj >= 0 else "#E05252"
            net_lbl = tk.Label(
                grid_frame,
                text=f"{sign}${net_adj:,.2f}",
                font=("Segoe UI", 8, "bold"),
                fg=adj_col,
                bg=self.colors["white"],
                anchor="e"
            )
            net_lbl.grid(row=r_idx, column=5, sticky="ew", padx=6, pady=4)

            # Col 6: Status feedback
            status_lbl = tk.Label(
                grid_frame,
                text="Auto-saved ✓",
                font=("Segoe UI", 7, "bold"),
                fg=self.colors["deep_teal"],
                bg=self.colors["white"],
                anchor="center"
            )
            status_lbl.grid(row=r_idx, column=6, sticky="ew", padx=6, pady=4)

            # Real-time event handler for keystrokes, focus changes, Enter, and Tab
            def _bind_row(e_ref, b_ent, r_ent, nl, sl):
                def _on_change(*args):
                    try:
                        b_val = float(b_ent.get().replace("$", "").replace(",", "").strip() or 0)
                        r_val = float(r_ent.get().replace("$", "").replace(",", "").strip() or 0)
                        e_ref["bonus"] = b_val
                        e_ref["reimbursement"] = r_val
                        self.recalculate_live_engine()

                        n_adj = (b_val + r_val) - (e_ref["pretax_health"] + e_ref["pretax_401k"])
                        s = "+" if n_adj >= 0 else ""
                        c = self.colors["primary_orange"] if n_adj >= 0 else "#E05252"
                        nl.config(text=f"{s}${n_adj:,.2f}", fg=c)
                        sl.config(text="Auto-saved ✓", fg=self.colors["deep_teal"])
                        self.update_live_summary_bar()
                    except ValueError:
                        sl.config(text="Invalid #", fg="#E05252")
                return _on_change

            handler = _bind_row(emp, b_entry, r_entry, net_lbl, status_lbl)
            b_entry.b_var = b_var
            r_entry.r_var = r_var
            b_var.trace_add("write", handler)
            r_var.trace_add("write", handler)
            for w in (b_entry, r_entry):
                w.bind("<KeyRelease>", handler)
                w.bind("<FocusOut>", handler)
                w.bind("<Return>", handler)
                w.bind("<Tab>", handler)

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
            text="Interactive Engine: Edit Base Salary below to test live statutory recalculation and net take-home pay.",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        ).pack(anchor="w", pady=(2, 0))

        if self.user.has_role(Role.SUPER_ADMIN):
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
        else:
            badge = RoundedBadge(
                hdr,
                text="🔒 Statutory Formulas Verified (Super Admin)",
                bg_color=self.colors["sidebar_bg"],
                fg_color=self.colors["dark_teal"],
                radius=8,
                width=265,
                height=26,
                parent_bg=self.colors["white"]
            )
            badge.pack(side="right")

        # 4 High-Level Metric Tiles for the Engine
        tiles = tk.Frame(card, bg=self.colors["white"])
        tiles.pack(fill="x", pady=(0, 14))

        tot_gross = sum(i["gross_pay"] for i in self.payroll_items)
        tot_tax = sum(i["total_tax"] for i in self.payroll_items)
        tot_ben = sum(i["total_benefits"] for i in self.payroll_items)
        tot_net = sum(i["net_pay"] for i in self.payroll_items)

        specs = [
            ("TOTAL GROSS PAY", f"${tot_gross:,.2f}", "Base + OT + Bonuses"),
            ("TOTAL TAX WITHHOLDING", f"-${tot_tax:,.2f}", "BIR Withholding (TRAIN Law)"),
            ("STATUTORY CONTRIBUTIONS", f"-${tot_ben:,.2f}", "SSS + PhilHealth + Pag-IBIG"),
            ("NET DISBURSEMENT", f"${tot_net:,.2f}", "100% EFT Direct Deposit")
        ]

        metric_lbls = {}
        for i, (t, v, s) in enumerate(specs):
            tile = tk.Frame(tiles, bg="#F7FCFC", highlightbackground=self.colors["border_light"], highlightthickness=1, padx=12, pady=8)
            tile.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            tiles.columnconfigure(i, weight=1)
            tk.Label(tile, text=t, font=("Segoe UI", 7, "bold"), fg=self.colors["gray_text"], bg="#F7FCFC").pack(anchor="w")
            v_lbl = tk.Label(tile, text=v, font=("Segoe UI", 12, "bold"), fg=self.colors["dark_teal"] if i != 1 and i != 2 else "#E05252", bg="#F7FCFC")
            v_lbl.pack(anchor="w", pady=(1, 1))
            metric_lbls[t] = v_lbl
            tk.Label(tile, text=s, font=("Segoe UI", 6), fg=self.colors["gray_text"], bg="#F7FCFC").pack(anchor="w")

        # Calculation Multi-Column Grid
        cols = [
            ("Employee", 3, "w"),
            ("Base Salary ($)", 2, "e"),
            ("Gross Earnings", 2, "e"),
            ("BIR Tax (TRAIN)", 2, "e"),
            ("SSS Contrib.", 2, "e"),
            ("PhilHealth/HDMF", 2, "e"),
            ("Statutory Deductions", 2, "e"),
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

            # Col 1: Base Salary inline Entry (Changable like Step 2 adjustments)
            sal_var = tk.StringVar(value=f"{emp['base_salary']:.2f}")
            sal_frame = tk.Frame(grid_frame, bg=self.colors["white"])
            sal_frame.grid(row=r_idx, column=1, sticky="e", padx=6, pady=3)
            tk.Label(sal_frame, text="$", font=("Segoe UI", 8, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"]).pack(side="left")
            sal_entry = tk.Entry(
                sal_frame,
                textvariable=sal_var,
                font=("Segoe UI", 8, "bold"),
                fg=self.colors["dark_teal"],
                bg=self.colors["white"],
                highlightbackground=self.colors["border_peach"],
                highlightcolor=self.colors["primary_orange"],
                highlightthickness=1,
                bd=0,
                width=8,
                justify="right"
            )
            sal_entry.pack(side="left", ipady=2)

            # Col 2-7: Auto-computed figures with live labels
            gross_lbl = tk.Label(grid_frame, text=f"${emp['gross_pay']:,.2f}", font=("Segoe UI", 8, "bold"), fg=self.colors["dark_teal"], bg=self.colors["white"], anchor="e")
            gross_lbl.grid(row=r_idx, column=2, sticky="ew", padx=6, pady=4)

            fed_lbl = tk.Label(grid_frame, text=f"-${emp['fed_tax']:,.2f}", font=("Segoe UI", 8), fg="#E05252", bg=self.colors["white"], anchor="e")
            fed_lbl.grid(row=r_idx, column=3, sticky="ew", padx=6, pady=4)

            state_lbl = tk.Label(grid_frame, text=f"-${emp['state_tax']:,.2f}", font=("Segoe UI", 8), fg="#E05252", bg=self.colors["white"], anchor="e")
            state_lbl.grid(row=r_idx, column=4, sticky="ew", padx=6, pady=4)

            fica_lbl = tk.Label(grid_frame, text=f"-${emp['fica_tax']:,.2f}", font=("Segoe UI", 8), fg="#E05252", bg=self.colors["white"], anchor="e")
            fica_lbl.grid(row=r_idx, column=5, sticky="ew", padx=6, pady=4)

            ben_lbl = tk.Label(grid_frame, text=f"-${emp['total_benefits']:,.2f}", font=("Segoe UI", 8), fg="#E05252", bg=self.colors["white"], anchor="e")
            ben_lbl.grid(row=r_idx, column=6, sticky="ew", padx=6, pady=4)

            net_lbl = tk.Label(grid_frame, text=f"${emp['net_pay']:,.2f}", font=("Segoe UI", 9, "bold"), fg=self.colors["deep_teal"], bg=self.colors["white"], anchor="e")
            net_lbl.grid(row=r_idx, column=7, sticky="ew", padx=6, pady=4)

            # Live calculation bind handler for real-time recalculation
            def _bind_step3_row(e_ref, ent, gl, fl, sl, fcl, bl, nl):
                def _on_change(*args):
                    try:
                        raw = ent.get().replace("$", "").replace(",", "").strip()
                        s_val = float(raw or 0)
                        e_ref["base_salary"] = s_val
                        if s_val > 0:
                            e_ref["hourly_rate"] = round(s_val / 160.0, 2)
                        self.recalculate_live_engine()

                        # Update row labels
                        gl.config(text=f"${e_ref['gross_pay']:,.2f}")
                        fl.config(text=f"-${e_ref['fed_tax']:,.2f}")
                        sl.config(text=f"-${e_ref['state_tax']:,.2f}")
                        fcl.config(text=f"-${e_ref['fica_tax']:,.2f}")
                        bl.config(text=f"-${e_ref['total_benefits']:,.2f}")
                        nl.config(text=f"${e_ref['net_pay']:,.2f}")

                        # Update Step 3 Metric Tiles
                        tot_g = sum(i["gross_pay"] for i in self.payroll_items)
                        tot_t = sum(i["total_tax"] for i in self.payroll_items)
                        tot_b = sum(i["total_benefits"] for i in self.payroll_items)
                        tot_n = sum(i["net_pay"] for i in self.payroll_items)

                        if "TOTAL GROSS PAY" in metric_lbls:
                            metric_lbls["TOTAL GROSS PAY"].config(text=f"${tot_g:,.2f}")
                        if "TOTAL TAX WITHHOLDING" in metric_lbls:
                            metric_lbls["TOTAL TAX WITHHOLDING"].config(text=f"-${tot_t:,.2f}")
                        if "STATUTORY CONTRIBUTIONS" in metric_lbls:
                            metric_lbls["STATUTORY CONTRIBUTIONS"].config(text=f"-${tot_b:,.2f}")
                        if "NET DISBURSEMENT" in metric_lbls:
                            metric_lbls["NET DISBURSEMENT"].config(text=f"${tot_n:,.2f}")

                        self.update_live_summary_bar()
                    except ValueError:
                        pass
                return _on_change

            handler = _bind_step3_row(emp, sal_entry, gross_lbl, fed_lbl, state_lbl, fica_lbl, ben_lbl, net_lbl)
            sal_entry.sal_var = sal_var
            sal_var.trace_add("write", handler)
            for w in (sal_entry,):
                w.bind("<KeyRelease>", handler)
                w.bind("<FocusOut>", handler)
                w.bind("<Return>", handler)
                w.bind("<Tab>", handler)

    def action_run_recalc_step3(self):
        if not self.user.has_role(Role.SUPER_ADMIN):
            messagebox.showwarning(
                "Restricted Action",
                "Standard Admins cannot execute manual tax engine overrides or statutory formula recalculations.\nSuper Admin access required.",
                parent=self
            )
            return
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

        if self.user.has_role(Role.SUPER_ADMIN):
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
        else:
            badge = RoundedBadge(
                hdr,
                text="🔒 Super Admin Sign-Off Required for Exceptions",
                bg_color=self.colors["pill_pending"],
                fg_color=self.colors["pill_pending_text"],
                radius=8,
                width=285,
                height=26,
                parent_bg=self.colors["white"]
            )
            badge.pack(side="right")

        # 4 Core Rule Audits
        rules_box = tk.Frame(card, bg=self.colors["white"])
        rules_box.pack(fill="x", pady=(0, 14))

        rules = [
            ("RULE 1: Negative Net Pay Check", "Passed", "Zero employees have deductions exceeding gross salary.", self.colors["pill_approved"], self.colors["pill_approved_text"]),
            ("RULE 2: Overtime Threshold Alert", "Resolved" if self.exceptions_resolved else "Notice (1)", "Jordan Patel logged 12.0h OT (>10.0h company threshold).", self.colors["pill_approved"] if self.exceptions_resolved else self.colors["pill_warning"], self.colors["pill_approved_text"] if self.exceptions_resolved else self.colors["pill_warning_text"]),
            ("RULE 3: BIR Statutory Tax Compliance", "Passed", "All 5 employee BIR Form 2316 exemptions & TRAIN brackets verified.", self.colors["pill_approved"], self.colors["pill_approved_text"]),
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
        if self.exceptions_resolved:
            status_msg = "All exceptions have been reviewed and approved by Super Admin."
        elif not self.user.has_role(Role.SUPER_ADMIN):
            status_msg = "2 non-blocking warnings logged. Super Admin sign-off is required before final disbursement authorization."
        else:
            status_msg = "2 non-blocking warnings pending administrator sign-off before final lock."
        tk.Label(detail_card, text=status_msg, font=("Segoe UI", 8), fg=self.colors["text_dark"], bg="#FFFDF7").pack(anchor="w", pady=(2, 0))

    def action_resolve_all_exceptions(self):
        if not self.user.has_role(Role.SUPER_ADMIN):
            messagebox.showwarning(
                "Permission Denied",
                "Audit exception sign-offs and compliance overrides require Super Admin authorization.\nStandard Admins cannot override critical audit checks.",
                parent=self
            )
            return
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

        is_super = self.user.has_role(Role.SUPER_ADMIN)
        triggers = [
            ("📄 1. Digital Payslips Generation", "Generate and stamp PDF statement records for all 5 employees.", "Generate Slips", self.action_trigger_payslips, True),
            ("🏦 2. NACHA / ACH Direct Deposit File", "Compile batch ACH transfer instructions for corporate banking. (Super Admin Only)", "Create ACH File" if is_super else "Locked 🔒", self.action_trigger_ach, is_super),
            ("📧 3. Automated Employee Notification", "Dispatch secured salary notices and direct deposit confirmation emails.", "Email Staff", self.action_trigger_email, True),
            ("🔒 4. Period Lock & Compliance Seal", "Seal current cycle against inadvertent retroactive changes. (Super Admin Only)", "Seal Cycle" if is_super else "Locked 🔒", self.action_trigger_lock, is_super)
        ]

        for title, desc, btn_text, cmd, enabled in triggers:
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
                bg=self.colors["sidebar_bg"] if enabled else "#F4F7F7",
                fg=self.colors["dark_teal"] if enabled else self.colors["gray_text"],
                activebackground=self.colors["border_peach"],
                bd=0,
                relief="flat",
                cursor="hand2" if enabled else "arrow",
                state="normal" if enabled else "disabled",
                padx=12,
                pady=5,
                command=cmd
            )
            btn.pack(side="right")

    def action_trigger_payslips(self):
        messagebox.showinfo("Payslips Generated", f"✓ Digital payslip vouchers generated for all {len(self.payroll_items)} employees.\nAvailable under 'Payroll & Payslips' ledger.", parent=self)

    def action_trigger_ach(self):
        if not self.user.has_role(Role.SUPER_ADMIN):
            messagebox.showwarning(
                "Access Restricted",
                "Generation of corporate NACHA / ACH Direct Deposit banking batches is restricted to Super Admins only.",
                parent=self
            )
            return
        tot_net = sum(i["net_pay"] for i in self.payroll_items)
        messagebox.showinfo("ACH Batch Exported", f"✓ Corporate NACHA Direct Deposit batch generated successfully!\nTotal EFT: ${tot_net:,.2f}\nDestination: Chase Commercial ACH Gateway.", parent=self)

    def action_trigger_email(self):
        messagebox.showinfo("Notifications Sent", "✓ Notification emails and encrypted payslip links dispatched to employee mailboxes.", parent=self)

    def action_trigger_lock(self):
        if not self.user.has_role(Role.SUPER_ADMIN):
            messagebox.showwarning(
                "Access Restricted",
                "Period Lock & Compliance Seals can only be executed by Super Admins.",
                parent=self
            )
            return
        self.period_locked = True
        self.render_active_step()
        messagebox.showinfo("Period Sealed", f"✓ Pay Period '{self.pay_period_name}' is now Approved & Locked.\nAccidental overrides are strictly prevented.", parent=self)

    def action_submit_for_super_admin_approval(self):
        tot_net = sum(i["net_pay"] for i in self.payroll_items)
        messagebox.showinfo(
            "Submitted for Super Admin Approval 📋",
            f"Payroll cycle '{self.pay_period_name}' draft has been compiled and submitted for Super Admin review!\n\n"
            f"• Action: Submitted by {self.admin_data['name']} (Standard Admin)\n"
            f"• Headcount: {len(self.payroll_items)} employees\n"
            f"• Calculated Net Disbursement: ${tot_net:,.2f}\n"
            f"• Status: Awaiting Super Admin final audit clearance, NACHA batch release & compliance seal.",
            parent=self
        )

    def action_finalize_payroll_cycle(self):
        if not self.user.has_role(Role.SUPER_ADMIN):
            self.action_submit_for_super_admin_approval()
            return
        self.period_locked = True
        self.render_active_step()
        messagebox.showinfo(
            "Payroll Run Complete! 🎉",
            f"Payroll cycle '{self.pay_period_name}' has been successfully finalized and processed!\n\n"
            f"Total Employees: {len(self.payroll_items)}\n"
            f"Total Net Pay Disbursed: ${sum(i['net_pay'] for i in self.payroll_items):,.2f}\n"
            f"All payslips, bank disbursement batches, and BIR statutory records have been saved.",
            parent=self
        )

    # ==========================================
    # NAVIGATION HANDLERS
    # ==========================================
    def navigate_to_dashboard(self):
        if self.controller:
            self.controller.show_page("dashboard")
            return
        self.destroy()
        dashboard_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aDashboard.py")
        if os.path.exists(dashboard_script):
            subprocess.Popen([sys.executable, dashboard_script])

    def handle_logout(self):
        if self.controller:
            self.controller.handle_logout()
            return
        self.destroy()
        login_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "login.py")
        if os.path.exists(login_script):
            subprocess.Popen([sys.executable, login_script])

if __name__ == "__main__":
    from aDashboard import SteadypayAdminDashboard
    app = SteadypayAdminDashboard(initial_page="process_pay")
    app.mainloop()
