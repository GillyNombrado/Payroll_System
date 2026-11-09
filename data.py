"""
data.py - Centralized Data Store for Steadypay Payroll System
Contains all Admin, Employee, Account credentials, Payslips, Role Permissions, and computation helpers.
Supports JSON-based persistence so that runtime changes (e.g. status updates) survive across sessions.
"""

from enum import Enum
import json
import os
import re

# Path to the persistent JSON data file (stored alongside data.py)
_DATA_DIR = os.path.dirname(os.path.abspath(__file__))
_PERSIST_FILE = os.path.join(_DATA_DIR, "steadypay_data.json")

# ==============================================================================
# ROLE & PERMISSION DEFINITIONS (OOP Architecture)
# ==============================================================================
class Role(Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    STANDARD_ADMIN = "STANDARD_ADMIN"

class UserSession:
    """
    Manages the authenticated user's profile, role, and permission checks.
    Enforces strict segregation between Standard Admin and Super Admin capabilities.
    """
    def __init__(self, data=None):
        self._data = data if data is not None else get_admin_data()
        self.name = self._data.get("name", "Ava Morgan")
        self.role_title = self._data.get("role", "Payroll Admin")
        self.email = self._data.get("email", "admin@gmail.com")
        self.company_name = self._data.get("company_name", "Steadypay Technologies Inc.")
        status = self._data.get("status", "")

        # Explicit role classification: Default Ava Morgan session is Standard Admin
        if "Super Admin" in status and "Standard" not in status:
            self.role = Role.SUPER_ADMIN
        else:
            self.role = Role.STANDARD_ADMIN

    def has_role(self, required_role: Role) -> bool:
        """Explicit permission verification."""
        if self.role == Role.SUPER_ADMIN:
            return True
        return self.role == required_role

    def is_super_admin(self) -> bool:
        return self.role == Role.SUPER_ADMIN

    def is_standard_admin(self) -> bool:
        return self.role == Role.STANDARD_ADMIN

    def can_manage_employees(self) -> bool:
        """Super Admin only: creating/onboarding/offboarding employees."""
        return self.has_role(Role.SUPER_ADMIN)

    def can_edit_sensitive_financials(self) -> bool:
        """Super Admin only: modifying base salaries, bank details, tax status."""
        return self.has_role(Role.SUPER_ADMIN)

    def can_override_audit_exceptions(self) -> bool:
        """Super Admin only: clearing and overriding critical audit check exceptions."""
        return self.has_role(Role.SUPER_ADMIN)

    def can_execute_final_disbursement(self) -> bool:
        """Super Admin only: generating banking NACHA files and sealing/disbursing payroll periods."""
        return self.has_role(Role.SUPER_ADMIN)

_CURRENT_USER_SESSION = None

def get_current_user() -> UserSession:
    """Returns the singleton authenticated UserSession instance."""
    global _CURRENT_USER_SESSION
    if _CURRENT_USER_SESSION is None:
        _CURRENT_USER_SESSION = UserSession()
    return _CURRENT_USER_SESSION

def set_current_user_role(role: Role):
    """Allows toggling role for testing or session switching."""
    user = get_current_user()
    user.role = role

# ==============================================================================
# 1. ADMIN USER & COMPANY DATA
# ==============================================================================
COMPANY_DATA = {
    "name": "Steadypay Technologies Inc.",
    "legal_name": "Steadypay Technologies Inc.",
    "ein": "009-876-543-000",
    "address": "350 5th Avenue, Suite 4200, New York, NY 10118",
    "currency": "USD ($) - US Dollar",
    "pay_cycle": "Semi-Monthly (1st-15th & 16th-End)",
    "payroll_email": "payroll@steadypay.com",
    "phone": "+1 (555) 019-2830"
}

ADMIN_DATA = {
    "name": "Ava Morgan",
    "role": "Payroll Admin",
    "company_name": "Steadypay Technologies Inc.",
    "email": "admin@gmail.com",
    "phone": "+1 (555) 234-5678",
    "age": 34,
    "hired_date": "March 12, 2021",
    "department": "Finance & Human Resources",
    "location": "New York HQ",
    "status": "Active (Standard Admin)",
    "avatar_initials": "AM",
    "avatar_color": "#FF9F1C"
}

# ==============================================================================
# 2. EMPLOYEE DATASETS (5 Detailed Profiles & Payroll Records)
# ==============================================================================
EMPLOYEES_DATA = [
    {
        "id": "EMP-101",
        "name": "Maya Lewis",
        "initials": "ML",
        "role": "Senior designer",
        "email": "maya.lewis@company.com",
        "phone": "+1 (555) 438-9102",
        "age": 29,
        "hired_date": "May 14, 2023",
        "payroll_run": "Sep 2026",
        "status": "Approved",
        "amount": 4820.00,
        "updated": "Today",
        "avatar_color": "#FF9F1C",
        "hours_logged": 160.0,
        "available_leaves": 12,
        "payslips": [
            ("Sep 16 - Sep 30, 2026", "$5,500.00", "$680.00", "$4,820.00", "✓ Paid (Direct Deposit)"),
            ("Sep 01 - Sep 15, 2026", "$5,500.00", "$680.00", "$4,820.00", "✓ Paid (Direct Deposit)"),
            ("Aug 16 - Aug 31, 2026", "$5,500.00", "$680.00", "$4,820.00", "✓ Paid (Direct Deposit)"),
            ("Aug 01 - Aug 15, 2026", "$5,450.00", "$670.00", "$4,780.00", "✓ Paid (Direct Deposit)")
        ]
    },
    {
        "id": "EMP-102",
        "name": "Jordan Patel",
        "initials": "JP",
        "role": "Operations lead",
        "email": "jordan.patel@company.com",
        "phone": "+1 (555) 892-3341",
        "age": 35,
        "hired_date": "August 20, 2021",
        "payroll_run": "Sep 2026",
        "status": "Approved",
        "amount": 5140.00,
        "updated": "Today",
        "avatar_color": "#FFAE42",
        "hours_logged": 168.0,
        "available_leaves": 15,
        "payslips": [
            ("Sep 16 - Sep 30, 2026", "$5,900.00", "$760.00", "$5,140.00", "✓ Paid (Direct Deposit)"),
            ("Sep 01 - Sep 15, 2026", "$5,900.00", "$760.00", "$5,140.00", "✓ Paid (Direct Deposit)"),
            ("Aug 16 - Aug 31, 2026", "$5,900.00", "$760.00", "$5,140.00", "✓ Paid (Direct Deposit)")
        ]
    },
    {
        "id": "EMP-103",
        "name": "Sofia Chen",
        "initials": "SC",
        "role": "Finance analyst",
        "email": "sofia.chen@company.com",
        "phone": "+1 (555) 773-1290",
        "age": 27,
        "hired_date": "January 10, 2024",
        "payroll_run": "Sep 2026",
        "status": "Pending",
        "amount": 4960.00,
        "updated": "Yesterday",
        "avatar_color": "#FF9F1C",
        "hours_logged": 160.0,
        "available_leaves": 10,
        "payslips": [
            ("Sep 16 - Sep 30, 2026", "$5,700.00", "$740.00", "$4,960.00", "⏳ Pending Approval"),
            ("Sep 01 - Sep 15, 2026", "$5,700.00", "$740.00", "$4,960.00", "✓ Paid (Direct Deposit)"),
            ("Aug 16 - Aug 31, 2026", "$5,700.00", "$740.00", "$4,960.00", "✓ Paid (Direct Deposit)")
        ]
    },
    {
        "id": "EMP-104",
        "name": "Noah Kim",
        "initials": "NK",
        "role": "Customer support",
        "email": "noah.kim@company.com",
        "phone": "+1 (555) 612-8874",
        "age": 31,
        "hired_date": "November 05, 2022",
        "payroll_run": "Sep 2026",
        "status": "Pending",
        "amount": 4120.00,
        "updated": "Yesterday",
        "avatar_color": "#4ED8C8",
        "hours_logged": 160.0,
        "available_leaves": 8,
        "payslips": [
            ("Sep 16 - Sep 30, 2026", "$4,800.00", "$680.00", "$4,120.00", "⏳ Pending Approval"),
            ("Sep 01 - Sep 15, 2026", "$4,800.00", "$680.00", "$4,120.00", "✓ Paid (Direct Deposit)")
        ]
    },
    {
        "id": "EMP-105",
        "name": "Elena Ruiz",
        "initials": "ER",
        "role": "People operations",
        "email": "elena.ruiz@company.com",
        "phone": "+1 (555) 304-7621",
        "age": 33,
        "hired_date": "June 18, 2022",
        "payroll_run": "Sep 2026",
        "status": "Approved",
        "amount": 4780.00,
        "updated": "Sep 18",
        "avatar_color": "#FF9F1C",
        "hours_logged": 160.0,
        "available_leaves": 14,
        "payslips": [
            ("Sep 16 - Sep 30, 2026", "$5,450.00", "$670.00", "$4,780.00", "✓ Paid (Direct Deposit)"),
            ("Sep 01 - Sep 15, 2026", "$5,450.00", "$670.00", "$4,780.00", "✓ Paid (Direct Deposit)"),
            ("Aug 16 - Aug 31, 2026", "$5,450.00", "$670.00", "$4,780.00", "✓ Paid (Direct Deposit)")
        ]
    }
]

# Standard default employee account record (for employee@gmail.com login)
DEFAULT_EMPLOYEE_ACCOUNT = {
    "id": "EMP-100",
    "name": "John Doe",
    "initials": "JD",
    "role": "Software Engineer",
    "email": "employee@gmail.com",
    "phone": "+1 (555) 019-3829",
    "age": 28,
    "hired_date": "February 1, 2023",
    "payroll_run": "Sep 2026",
    "status": "Approved",
    "amount": 3450.00,
    "updated": "Sep 30",
    "avatar_color": "#FF9F1C",
    "hours_logged": 160.0,
    "available_leaves": 12,
    "payslips": [
        ("Sep 16 - Sep 30, 2026", "$4,100.00", "$650.00", "$3,450.00", "✓ Paid (Direct Deposit)"),
        ("Sep 01 - Sep 15, 2026", "$4,100.00", "$650.00", "$3,450.00", "✓ Paid (Direct Deposit)"),
        ("Aug 16 - Aug 31, 2026", "$4,100.00", "$650.00", "$3,450.00", "✓ Paid (Direct Deposit)"),
        ("Aug 01 - Aug 15, 2026", "$4,050.00", "$640.00", "$3,410.00", "✓ Paid (Direct Deposit)")
    ]
}

# ==============================================================================
# 3. AUTHENTICATION ACCOUNTS
# ==============================================================================
LOGIN_ACCOUNTS = {
    "admin@gmail.com": {
        "password": "123456789",
        "role": "Admin",
        "target_script": "aDashboard.py"
    }
}

# ==============================================================================
# 4. HELPER FUNCTIONS FOR RETRIEVAL & COMPUTATION
# ==============================================================================
def authenticate_user(email: str, password: str):
    """
    Verifies user credentials.
    Returns (True, target_script, role) on success, or (False, None, None) on failure.
    """
    cleaned_email = email.strip()
    account = LOGIN_ACCOUNTS.get(cleaned_email)
    if account and account["password"] == password:
        return True, account["target_script"], account["role"]
    return False, None, None

def get_admin_data():
    """Returns the central admin profile dictionary."""
    return dict(ADMIN_DATA)

def get_company_data():
    """Returns company profile data."""
    return dict(COMPANY_DATA)

def get_all_employees():
    """Returns a list of all employee records."""
    return list(EMPLOYEES_DATA)

def get_employee_by_email(email: str):
    """Finds an employee by email, defaulting to the standard employee account if not found."""
    cleaned = email.strip().lower()
    for emp in EMPLOYEES_DATA:
        if emp["email"].lower() == cleaned:
            return dict(emp)
    if cleaned == "employee@gmail.com":
        return dict(DEFAULT_EMPLOYEE_ACCOUNT)
    return dict(DEFAULT_EMPLOYEE_ACCOUNT)

def compute_payroll_summary():
    """
    Dynamically computes overall payroll summary metrics from EMPLOYEES_DATA.
    """
    total_amount = sum(emp["amount"] for emp in EMPLOYEES_DATA)
    active_count = len(EMPLOYEES_DATA)
    pending_count = sum(1 for emp in EMPLOYEES_DATA if emp["status"] == "Pending")

    return {
        "total_payroll": f"${total_amount:,.2f}",
        "active_employees": f"{active_count} people",
        "pending_payslips": f"{pending_count} slips",
        "next_payday": "Sep 30, 2026"
    }

def update_employee_status(emp_id: str, new_status: str):
    """
    Updates an employee's status in EMPLOYEES_DATA and persists the change.
    emp_id: e.g. 'EMP-103'
    new_status: e.g. 'Approved' or 'Pending'
    """
    for emp in EMPLOYEES_DATA:
        if emp["id"] == emp_id:
            emp["status"] = new_status
            break
    save_data()

def update_all_employee_statuses(new_status: str):
    """
    Updates the status of ALL employees in EMPLOYEES_DATA and persists the change.
    """
    for emp in EMPLOYEES_DATA:
        emp["status"] = new_status
    save_data()

def save_data():
    """
    Persists the current state of EMPLOYEES_DATA, COMPANY_DATA, and ADMIN_DATA
    both to the JSON persistence file and directly into data.py so changes
    persist permanently across sessions and appear directly in data.py.
    """
    payload = {
        "employees": EMPLOYEES_DATA,
        "company": COMPANY_DATA,
        "admin": ADMIN_DATA
    }
    # 1. Save to JSON persistence file
    try:
        with open(_PERSIST_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

    # 2. Update data.py source file directly on disk so viewing data.py reflects changes
    try:
        py_file = os.path.join(_DATA_DIR, "data.py")
        if os.path.exists(py_file):
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            for emp in EMPLOYEES_DATA:
                eid = emp["id"]
                estat = emp["status"]
                pattern = r'("id":\s*"' + re.escape(eid) + r'"[\s\S]*?)("status":\s*)"[^"]+"'
                content = re.sub(pattern, r'\g<1>\g<2>"' + estat + '"', content)

            with open(py_file, "w", encoding="utf-8") as f:
                f.write(content)
    except Exception:
        pass

def load_data():
    """
    Loads persisted data from the JSON file and merges it into the module-level
    dictionaries. Called once at import time. If the file does not exist, the
    hard-coded defaults above are used as-is.
    """
    global EMPLOYEES_DATA, COMPANY_DATA, ADMIN_DATA
    if not os.path.exists(_PERSIST_FILE):
        return
    try:
        with open(_PERSIST_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
        if "employees" in payload and isinstance(payload["employees"], list):
            EMPLOYEES_DATA.clear()
            EMPLOYEES_DATA.extend(payload["employees"])
        if "company" in payload and isinstance(payload["company"], dict):
            COMPANY_DATA.clear()
            COMPANY_DATA.update(payload["company"])
        if "admin" in payload and isinstance(payload["admin"], dict):
            ADMIN_DATA.clear()
            ADMIN_DATA.update(payload["admin"])
    except Exception:
        pass  # Fall back to hard-coded defaults on any read error

# Load persisted data on module import (merges saved state over defaults)
load_data()

# ==============================================================================
# 5. UI ROUNDED CORNER DRAWING HELPERS & COMPONENTS
# ==============================================================================
import tkinter as tk

def draw_rounded_rectangle(canvas, x1, y1, x2, y2, radius=12, **kwargs):
    """Draws a smooth rounded rectangle on any Tkinter Canvas."""
    points = (
        x1 + radius, y1,
        x1 + radius, y1,
        x2 - radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1 + radius,
        x1, y1
    )
    return canvas.create_polygon(points, **kwargs, smooth=True)

class RoundedFrame(tk.Canvas):
    """
    Canvas container that draws a sleek rounded background with soft edges and optional border.
    Contains an inner Frame for child widgets.
    """
    def __init__(self, parent, radius=12, bg_color="#FFFFFF", border_color="", border_width=1, parent_bg="#FFFFFF", **kwargs):
        super().__init__(parent, bg=parent_bg, highlightthickness=0, **kwargs)
        self.radius = radius
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width
        self.parent_bg = parent_bg

        self.inner = tk.Frame(self, bg=bg_color)
        self.window_id = self.create_window(0, 0, window=self.inner, anchor="nw")
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event=None):
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 1 or h <= 1:
            return
        self.delete("rounded_bg")
        pad = self.border_width
        if w > 2 * pad and h > 2 * pad:
            draw_rounded_rectangle(
                self,
                pad, pad, w - pad, h - pad,
                radius=self.radius,
                fill=self.bg_color,
                outline=self.border_color if self.border_color else "",
                width=self.border_width,
                tags="rounded_bg"
            )
            self.tag_lower("rounded_bg")
            inner_pad = max(pad + 2, 6)
            self.coords(self.window_id, inner_pad, inner_pad)
            self.itemconfigure(self.window_id, width=max(1, w - 2 * inner_pad), height=max(1, h - 2 * inner_pad))

class RoundedButton(tk.Canvas):
    """
    A stylish rounded CTA button widget with smooth corner radius and hover animation.
    """
    def __init__(self, parent, text="", command=None, radius=10, bg_color="#FF9F1C", fg_color="#FFFFFF",
                 hover_bg="#FFAE42", font=("Segoe UI", 9, "bold"), width=120, height=36, parent_bg="#FFFFFF", **kwargs):
        super().__init__(parent, width=width, height=height, bg=parent_bg, highlightthickness=0, cursor="hand2", **kwargs)
        self.text = text
        self.command = command
        self.radius = radius
        self.bg_color = bg_color
        self.current_bg = bg_color
        self.hover_bg = hover_bg
        self.fg_color = fg_color
        self.font = font
        self.bind("<Configure>", self._render)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", lambda e: self.command() if self.command else None)

    def _render(self, event=None):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w > 2 and h > 2:
            draw_rounded_rectangle(self, 1, 1, w - 1, h - 1, radius=self.radius, fill=self.current_bg, outline="")
            self.create_text(w // 2, h // 2, text=self.text, fill=self.fg_color, font=self.font)

    def _on_enter(self, event):
        self.current_bg = self.hover_bg
        self._render()

    def _on_leave(self, event):
        self.current_bg = self.bg_color
        self._render()

class RoundedBadge(tk.Canvas):
    """
    A compact rounded pill badge (e.g. Approved, Pending status tags).
    """
    def __init__(self, parent, text="", bg_color="#D1F4EE", fg_color="#16988B", radius=8,
                 font=("Segoe UI", 7, "bold"), width=75, height=22, parent_bg="#FFFFFF", **kwargs):
        super().__init__(parent, width=width, height=height, bg=parent_bg, highlightthickness=0, **kwargs)
        self.text = text
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.radius = radius
        self.font = font
        self.bind("<Configure>", self._render)

    def _render(self, event=None):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w > 2 and h > 2:
            draw_rounded_rectangle(self, 1, 1, w - 1, h - 1, radius=self.radius, fill=self.bg_color, outline="")
            self.create_text(w // 2, h // 2, text=self.text, fill=self.fg_color, font=self.font)

