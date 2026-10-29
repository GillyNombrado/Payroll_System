import os
import sys
import subprocess
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from data import get_admin_data

class SteadypayEmployeePage(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Steadypay - Employee Management (Admin)")
        self.geometry("1200x750")
        self.minsize(1100, 680)
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

        # Centralized Data from data.py
        self.admin_data = get_admin_data()

        # Employee dataset
        self.employees = [
            ("EMP-001", "Jane Doe", "Software Engineer", "Engineering", "$4,500.00", "Active"),
            ("EMP-002", "Alex Smith", "Product Designer", "Design", "$3,800.00", "Active"),
            ("EMP-003", "Maria Santos", "HR Specialist", "Human Resources", "$3,200.00", "Active"),
            ("EMP-004", "Liam Johnson", "Accountant", "Finance", "$3,600.00", "On Leave"),
            ("EMP-005", "David Chen", "QA Engineer", "Engineering", "$3,400.00", "Active"),
        ]

        # Search state
        self._search_placeholder = "Search employee..."
        self.search_var = None   # initialised in create_employee_body

        self.setup_layout()

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
            ("📄", "Payroll records", False),
            ("📑", "Generate payslips", False),
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
        # Handle Dashboard tab directly
        if menu_name == "Dashboard":
            self.navigate_to_dashboard()
            return
        # Map menu names to their corresponding script files
        menu_map = {
            "Employee\nmanagement": "aEmployee.py",
            "Process payroll": "aProcessPay.py",
            "Payroll records": "aPayRecords.py",
            "Generate payslips": "aPayslips.py",
            "Settings": "aSettings.py"
        }
        target = menu_map.get(menu_name)
        if target:
            if target == "aEmployee.py":
                return
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

        # Fixed header — lives outside the canvas so it never scrolls
        self.create_top_header(right_container)

        self.main_canvas = tk.Canvas(right_container, bg=self.colors["white"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(right_container, orient="vertical", command=self.main_canvas.yview)

        # Content frame inside canvas
        self.content_frame = tk.Frame(self.main_canvas, bg=self.colors["white"])
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

        # Build scrollable page content (header is fixed above)
        self.create_employee_body(self.content_frame)

    # ==========================================
    # TOP HEADER (badge + title + profile)
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
            text="EMPLOYEE MANAGEMENT",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["primary_orange"],
            bg=self.colors["white"]
        ).pack(anchor="w")

        tk.Label(
            left_box,
            text="Name of Company",
            font=("Segoe UI", 20, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        ).pack(anchor="w", pady=(2, 2))

        tk.Label(
            left_box,
            text="View and manage all employee records and profiles.",
            font=("Segoe UI", 9),
            fg=self.colors["gray_text"],
            bg=self.colors["white"]
        ).pack(anchor="w")

        # Right: date/time + profile pill
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

        avatar_canvas = tk.Canvas(self.profile_btn, width=32, height=32, bg=self.colors["white"], highlightthickness=0)
        avatar_canvas.pack(side="left", padx=(0, 8))
        avatar_canvas.create_oval(2, 2, 30, 30, fill=self.colors["primary_orange"], outline="")
        avatar_canvas.create_text(16, 16, text="AM", fill="#FFFFFF", font=("Segoe UI", 9, "bold"))

        profile_info = tk.Frame(self.profile_btn, bg=self.colors["white"])
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
    # EMPLOYEE BODY: Full-width Table
    # ==========================================
    def create_employee_body(self, parent):
        body = tk.Frame(parent, bg=self.colors["white"], padx=26, pady=10)
        body.pack(fill="both", expand=True)

        # ---- Table header row: title + search ----
        tbl_header = tk.Frame(body, bg=self.colors["white"])
        tbl_header.pack(fill="x", pady=(0, 12))

        tk.Label(
            tbl_header,
            text="Employee Directory",
            font=("Segoe UI", 15, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        ).pack(side="left")

        search_frame = tk.Frame(
            tbl_header,
            bg=self.colors["white"],
            highlightbackground=self.colors["border_color"],
            highlightthickness=1
        )
        search_frame.pack(side="right")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)

        search_entry = tk.Entry(
            search_frame,
            font=("Segoe UI", 9),
            bg=self.colors["white"],
            bd=0,
            relief="flat",
            width=24,
            fg=self.colors["gray_text"]
        )
        search_entry.insert(0, self._search_placeholder)
        search_entry.pack(side="left", ipady=5, padx=10)

        def _search_focus_in(e):
            if search_entry.get() == self._search_placeholder:
                search_entry.delete(0, tk.END)
                search_entry.config(fg=self.colors["text_dark"])
                self.search_var.set("")

        def _search_focus_out(e):
            if not search_entry.get().strip():
                search_entry.config(fg=self.colors["gray_text"])
                search_entry.delete(0, tk.END)
                search_entry.insert(0, self._search_placeholder)
                self.search_var.set("")
            else:
                self.search_var.set(search_entry.get())

        def _search_key(e):
            val = search_entry.get()
            if val != self._search_placeholder:
                self.search_var.set(val)

        search_entry.bind("<FocusIn>",  _search_focus_in)
        search_entry.bind("<FocusOut>", _search_focus_out)
        search_entry.bind("<KeyRelease>", _search_key)

        # ---- Treeview style ----
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Employee.Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            background=self.colors["sidebar_bg"],
            foreground=self.colors["dark_teal"],
            relief="flat"
        )
        style.map("Employee.Treeview.Heading",
                  background=[("active", self.colors["soft_orange"])])
        style.configure(
            "Employee.Treeview",
            font=("Segoe UI", 9),
            rowheight=34,
            fieldbackground=self.colors["white"],
            borderwidth=0
        )
        style.map(
            "Employee.Treeview",
            background=[("selected", self.colors["sidebar_bg"])],
            foreground=[("selected", self.colors["dark_teal"])]
        )

        columns = ("id", "name", "role", "dept", "salary", "status")
        self.tree = ttk.Treeview(
            body,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Employee.Treeview"
        )

        self.tree.heading("id",     text="ID")
        self.tree.heading("name",   text="Name")
        self.tree.heading("role",   text="Position")
        self.tree.heading("dept",   text="Department")
        self.tree.heading("salary", text="Monthly Salary")
        self.tree.heading("status", text="Status")

        self.tree.column("id",     width=90,  anchor="center")
        self.tree.column("name",   width=180, anchor="w")
        self.tree.column("role",   width=160, anchor="w")
        self.tree.column("dept",   width=140, anchor="w")
        self.tree.column("salary", width=120, anchor="e")
        self.tree.column("status", width=100, anchor="center")

        self.load_table_data()
        self.tree.pack(fill="both", expand=True, pady=(0, 14))

        # ---- Action buttons row (bottom bar) ----
        actions_frame = tk.Frame(body, bg=self.colors["white"])
        actions_frame.pack(fill="x")

        # Left side: Remove + Add buttons
        left_actions = tk.Frame(actions_frame, bg=self.colors["white"])
        left_actions.pack(side="left")

        tk.Button(
            left_actions,
            text="Remove Selected",
            font=("Segoe UI", 8, "bold"),
            bg="#FF6B6B",
            fg=self.colors["white"],
            activebackground="#E05252",
            activeforeground=self.colors["white"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            command=self.delete_employee
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            left_actions,
            text="Add Employee  +",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["primary_orange"],
            fg=self.colors["white"],
            activebackground=self.colors["soft_orange"],
            activeforeground=self.colors["white"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            command=self.show_add_employee_popup
        ).pack(side="left")

        # Right side: active count badge + Export CSV
        right_actions = tk.Frame(actions_frame, bg=self.colors["white"])
        right_actions.pack(side="right")

        self.active_count_lbl = tk.Label(
            right_actions,
            text=f"👥 {sum(1 for e in self.employees if e[5] == 'Active')} Active Employees",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["white"]
        )
        self.active_count_lbl.pack(side="left", padx=(0, 14))

        tk.Button(
            right_actions,
            text="Export CSV",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["sidebar_bg"],
            fg=self.colors["dark_teal"],
            activebackground=self.colors["soft_orange"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6
        ).pack(side="left")

    # ==========================================
    # ADD EMPLOYEE POPUP
    # ==========================================
    def show_add_employee_popup(self):
        """Opens a centered modal popup with the Add New Employee form."""
        popup = tk.Toplevel(self)
        popup.title("Add New Employee")
        popup.resizable(False, False)
        popup.configure(bg=self.colors["white"])
        popup.transient(self)
        popup.grab_set()

        popup_w, popup_h = 400, 440
        x = self.winfo_x() + (self.winfo_width()  - popup_w) // 2
        y = self.winfo_y() + (self.winfo_height() - popup_h) // 2
        popup.geometry(f"{popup_w}x{popup_h}+{x}+{y}")

        # ---- Header banner ----
        banner = tk.Frame(popup, bg=self.colors["sidebar_bg"], padx=24, pady=18)
        banner.pack(fill="x")

        tk.Label(
            banner,
            text="Add New Employee",
            font=("Segoe UI", 13, "bold"),
            fg=self.colors["dark_teal"],
            bg=self.colors["sidebar_bg"]
        ).pack(anchor="w")

        tk.Label(
            banner,
            text="Fill in the details below to register a new team member.",
            font=("Segoe UI", 8),
            fg=self.colors["deep_teal"],
            bg=self.colors["sidebar_bg"]
        ).pack(anchor="w", pady=(2, 0))

        # ---- Form body ----
        form = tk.Frame(popup, bg=self.colors["white"], padx=24, pady=20)
        form.pack(fill="both", expand=True)

        popup_entries = {}
        fields = [
            ("Full Name",          "name"),
            ("Role / Position",    "role"),
            ("Department",         "dept"),
            ("Monthly Salary ($)", "salary"),
        ]

        for label_text, key in fields:
            tk.Label(
                form,
                text=label_text,
                font=("Segoe UI", 8, "bold"),
                fg=self.colors["dark_teal"],
                bg=self.colors["white"]
            ).pack(anchor="w", pady=(8, 2))

            ef = tk.Frame(
                form,
                bg=self.colors["white"],
                highlightbackground=self.colors["border_color"],
                highlightthickness=1
            )
            ef.pack(fill="x")

            ent = tk.Entry(ef, font=("Segoe UI", 9), bg=self.colors["white"], bd=0, relief="flat")
            ent.pack(fill="x", ipady=6, padx=10)
            popup_entries[key] = ent

        # ---- Footer buttons ----
        footer = tk.Frame(popup, bg=self.colors["white"], padx=24, pady=14)
        footer.pack(fill="x")

        def _submit():
            name   = popup_entries["name"].get().strip()
            role   = popup_entries["role"].get().strip()
            dept   = popup_entries["dept"].get().strip()
            salary = popup_entries["salary"].get().strip()

            if not name or not role or not dept or not salary:
                messagebox.showwarning("Incomplete Form",
                                       "Please fill in all fields.", parent=popup)
                return

            new_id = f"EMP-{len(self.employees) + 1:03d}"
            try:
                formatted_salary = f"${float(salary):,.2f}"
            except ValueError:
                formatted_salary = salary

            self.employees.append((new_id, name, role, dept, formatted_salary, "Active"))
            self.load_table_data(filter_text=self.search_var.get())
            self.active_count_lbl.config(
                text=f"👥 {sum(1 for e in self.employees if e[5] == 'Active')} Active Employees"
            )
            popup.destroy()

        tk.Button(
            footer,
            text="Cancel",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["sidebar_bg"],
            fg=self.colors["dark_teal"],
            activebackground=self.colors["border_peach"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=6,
            command=popup.destroy
        ).pack(side="right", padx=(8, 0))

        tk.Button(
            footer,
            text="Add Employee  +",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["primary_orange"],
            fg=self.colors["white"],
            activebackground=self.colors["soft_orange"],
            activeforeground=self.colors["white"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=6,
            command=_submit
        ).pack(side="right")

    # ==========================================
    # TABLE DATA MANAGEMENT
    # ==========================================
    def load_table_data(self, filter_text=""):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.tree.tag_configure("even", background=self.colors["white"])
        self.tree.tag_configure("odd", background=self.colors["row_alt"])

        ft = filter_text.lower().strip()
        visible = [
            emp for emp in self.employees
            if not ft or any(ft in str(v).lower() for v in emp)
        ]

        for i, emp in enumerate(visible):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", values=emp, tags=(tag,))

    def _on_search_change(self, *args):
        if self.search_var is None:
            return
        query = self.search_var.get()
        placeholder = getattr(self, "_search_placeholder", "")
        if query == placeholder:
            query = ""
        self.load_table_data(filter_text=query)

    def delete_employee(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Record",
                                "Please select an employee from the table to remove.")
            return

        item_values = self.tree.item(selected[0], "values")
        self.employees = [emp for emp in self.employees if emp[0] != item_values[0]]
        self.load_table_data(filter_text=self.search_var.get())
        self.active_count_lbl.config(
            text=f"👥 {sum(1 for e in self.employees if e[5] == 'Active')} Active Employees"
        )

    # ==========================================
    # NAVIGATION HANDLER
    # ==========================================
    def navigate_to_dashboard(self):
        self.destroy()
        dashboard_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aDashboard.py")
        if os.path.exists(dashboard_script):
            subprocess.Popen([sys.executable, dashboard_script])

    # ==========================================
    # LOGOUT HANDLER
    # ==========================================
    def handle_logout(self):
        self.destroy()
        login_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "login.py")
        if os.path.exists(login_script):
            subprocess.Popen([sys.executable, login_script])

if __name__ == "__main__":
    app = SteadypayEmployeePage()
    app.mainloop()
