"""
Admin widget for managing staff and viewing attendance
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QTableWidget, 
    QTableWidgetItem, QTabWidget, QFormLayout, QGroupBox, QHeaderView, QFileDialog, QDialog, QMessageBox, QDateEdit, QComboBox, QCheckBox
)
from PySide6.QtCore import Qt, QDate
from database import DatabaseManager
import csv
import sqlite3


class AdminWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Admin Panel")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px; color: #0F172A;")  # Dark blue-gray for better contrast
        layout.addWidget(title_label)
        
        # Create tab widget for different admin functions
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #1E3A8A;
            }
            QTabBar::tab {
                background: #E0F2FE;
                padding: 8px;
                color: #0F172A;  /* Dark blue-gray for better contrast */
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #1E3A8A;
                color: white;
            }
        """)
        
        # Staff management tab
        staff_tab = self.create_staff_tab()
        tab_widget.addTab(staff_tab, "Manage Staff")
        
        # Departments tab
        dept_tab = self.create_departments_tab()
        tab_widget.addTab(dept_tab, "Manage Departments")
        
        # Staff records tab
        staff_records_tab = self.create_staff_records_tab()
        tab_widget.addTab(staff_records_tab, "Staff Records")
        
        # Attendance records tab
        attendance_tab = self.create_attendance_tab()
        tab_widget.addTab(attendance_tab, "Attendance Records")
        
        # Lateness Report tab
        from ui.lateness_report_widget import LatenessReportWidget
        lateness_report_tab = LatenessReportWidget()
        tab_widget.addTab(lateness_report_tab, "Lateness Report")
        
        # Department View tab
        from ui.department_widget import DepartmentWidget
        department_tab = DepartmentWidget()
        tab_widget.addTab(department_tab, "Departments Overview")
        
        # Export tab
        export_tab = self.create_export_tab()
        tab_widget.addTab(export_tab, "Export Data")
        
        layout.addWidget(tab_widget)
        self.setLayout(layout)
    
    def create_staff_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Staff registration form
        form_group = QGroupBox("Register New Staff")
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #1E3A8A;  /* Dark blue */
                border-radius: 5px;
                margin: 10px 0px;
                padding-top: 15px;
                color: #0F172A;  /* Dark blue-gray for better contrast */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: #0F172A;  /* Dark blue-gray for better contrast */
                font-weight: bold;
            }
        """)
        form_layout = QFormLayout()
        
        self.staff_name_input = QLineEdit()
        self.staff_name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #3B82F6;  /* Light blue */
                border-radius: 4px;
                color: #0F172A;  /* Dark blue-gray for better contrast */
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #1E3A8A;  /* Dark blue */
            }
        """)
        self.staff_id_input = QLineEdit()
        self.staff_id_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #3B82F6;  /* Light blue */
                border-radius: 4px;
                color: #0F172A;  /* Dark blue-gray for better contrast */
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #1E3A8A;  /* Dark blue */
            }
        """)
        from PySide6.QtWidgets import QComboBox
        self.staff_department_combo = QComboBox()
        self.staff_department_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #3B82F6;  /* Light blue */
                border-radius: 4px;
                color: #0F172A;  /* Dark blue-gray for better contrast */
                background-color: white;
            }
            QComboBox:focus {
                border: 2px solid #1E3A8A;  /* Dark blue */
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 1px solid #3B82F6;
            }
            QComboBox::down-arrow {
                image: url(noimg);
                width: 10px;
                height: 10px;
            }
        """)
        self.update_department_combo()  # Load departments into the combobox
        
        form_layout.addRow("Full Name:", self.staff_name_input)
        form_layout.addRow("Staff ID:", self.staff_id_input)
        form_layout.addRow("Department:", self.staff_department_combo)
        
        register_button = QPushButton("Register Staff")
        register_button.clicked.connect(self.register_staff)
        register_button.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;  /* Light blue */
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;  /* Medium blue */
            }
            QPushButton:pressed {
                background-color: #1D4ED8;  /* Darker blue */
            }
        """)
        form_layout.addRow(register_button)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_staff_records_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Table to display staff records
        self.staff_table = QTableWidget()
        self.staff_table.setColumnCount(6)  # Increased to include action buttons
        self.staff_table.setHorizontalHeaderLabels(["Staff ID", "Name", "Department", "Edit", "Delete", "Actions"])
        self.staff_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #3B82F6;  /* Light blue */
                alternate-background-color: #F0F9FF;  /* Very light blue */
                selection-background-color: #BAE6FD;  /* Lighter blue for selected items */
            }
            QHeaderView::section {
                background-color: #1E3A8A;  /* Dark blue */
                color: white;
                padding: 4px;
                border: 1px solid #3B82F6;  /* Light blue */
            }
        """)
        # Staff Records - Match attendance records column sizing
        header = self.staff_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # Proportional resizing like attendance
        self.staff_table.setColumnWidth(0, 100)  # Staff ID (smallest)
        self.staff_table.setColumnWidth(1, 300)  # Name (2x Department size)
        self.staff_table.setColumnWidth(2, 150)  # Department
        self.staff_table.setColumnWidth(3, 80)   # Edit button (fixed width)
        self.staff_table.setColumnWidth(4, 80)   # Delete button (fixed width)
        self.staff_table.setColumnHidden(5, True)  # Hide the ID storage column
        
        layout.addWidget(QLabel("Registered Staff"))
        layout.addWidget(self.staff_table)
        
        # Pagination controls
        pagination_layout = QHBoxLayout()
        
        self.staff_page_label = QLabel("Page 1 of 1")
        self.staff_page_label.setStyleSheet("color: #0F172A; font-weight: bold; margin: 5px;")
        pagination_layout.addWidget(self.staff_page_label)
        
        pagination_layout.addStretch()
        
        self.staff_prev_button = QPushButton("Previous")
        self.staff_prev_button.clicked.connect(lambda: self.change_staff_page(-1))
        self.staff_prev_button.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;  /* Light blue */
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 5px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2563EB;  /* Medium blue */
            }
            QPushButton:pressed {
                background-color: #1D4ED8;  /* Darker blue */
            }
        """)
        self.staff_prev_button.setEnabled(False)  # Disabled initially
        pagination_layout.addWidget(self.staff_prev_button)
        
        self.staff_page_input = QLineEdit("1")
        self.staff_page_input.setMaximumWidth(50)
        self.staff_page_input.returnPressed.connect(self.goto_staff_page)
        self.staff_page_input.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #3B82F6;  /* Light blue */
                border-radius: 4px;
                color: #0F172A;  /* Dark blue-gray for better contrast */
                background-color: white;
                text-align: center;
            }
            QLineEdit:focus {
                border: 2px solid #1E3A8A;  /* Dark blue */
            }
        """)
        pagination_layout.addWidget(QLabel("Go to page:"))
        pagination_layout.addWidget(self.staff_page_input)
        
        self.staff_next_button = QPushButton("Next")
        self.staff_next_button.clicked.connect(lambda: self.change_staff_page(1))
        self.staff_next_button.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;  /* Light blue */
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 5px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2563EB;  /* Medium blue */
            }
            QPushButton:pressed {
                background-color: #1D4ED8;  /* Darker blue */
            }
        """)
        self.staff_next_button.setEnabled(False)  # Disabled initially
        pagination_layout.addWidget(self.staff_next_button)
        
        # Initialize pagination variables
        self.staff_current_page = 1
        self.staff_items_per_page = 20  # Show 20 staff members per page
        self.staff_total_items = 0
        self.staff_total_pages = 1
        
        layout.addLayout(pagination_layout)
        
        refresh_staff_button = QPushButton("Refresh Staff")
        refresh_staff_button.clicked.connect(self.refresh_staff)
        refresh_staff_button.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;  /* Light blue */
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;  /* Medium blue */
            }
            QPushButton:pressed {
                background-color: #1D4ED8;  /* Darker blue */
            }
        """)
        layout.addWidget(refresh_staff_button)
        
        tab.setLayout(layout)
        return tab
    
    def create_attendance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Table to display attendance records
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(6)
        self.attendance_table.setHorizontalHeaderLabels(["Staff ID", "Name", "Department", "Date", "Time In", "Time Out"])
        self.attendance_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #3B82F6;  /* Light blue */
                alternate-background-color: #F0F9FF;  /* Very light blue */
                selection-background-color: #BAE6FD;  /* Lighter blue for selected items */
            }
            QHeaderView::section {
                background-color: #1E3A8A;  /* Dark blue */
                color: white;
                padding: 4px;
                border: 1px solid #3B82F6;  /* Light blue */
            }
        """)
        
        # Attendance Records
        header = self.attendance_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # Proportional resizing
        self.attendance_table.setColumnWidth(0, 100)  # Staff ID (smallest)
        self.attendance_table.setColumnWidth(1, 300)  # Name (2x Department size)
        self.attendance_table.setColumnWidth(2, 150)  # Department
        self.attendance_table.setColumnWidth(3, 120)  # Date (same as Time In/Out)
        self.attendance_table.setColumnWidth(4, 120)  # Time In (same as Date/Time Out)
        self.attendance_table.setColumnWidth(5, 120)  # Time Out (same as Date/Time In)
        
        layout.addWidget(QLabel("Attendance Records"))
        layout.addWidget(self.attendance_table)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        # Date range filters
        date_from_label = QLabel("From Date:")
        date_from_label.setStyleSheet("color: #0F172A; font-weight: bold;")
        self.attendance_date_from = QDateEdit()
        from PySide6.QtCore import QDate
        self.attendance_date_from.setDate(QDate.currentDate().addMonths(-1))  # Default to last month
        self.attendance_date_from.setDisplayFormat("yyyy-MM-dd")
        self.attendance_date_from.setCalendarPopup(True)
        self.attendance_date_from.setStyleSheet("""
            QDateEdit {
                padding: 6px;
                border: 1px solid #3B82F6;
                border-radius: 4px;
                color: #0F172A;
                background-color: white;
            }
            QDateEdit:focus {
                border: 2px solid #1E3A8A;
            }
        """)
        
        date_to_label = QLabel("To Date:")
        date_to_label.setStyleSheet("color: #0F172A; font-weight: bold;")
        self.attendance_date_to = QDateEdit()
        self.attendance_date_to.setDate(QDate.currentDate())
        self.attendance_date_to.setDisplayFormat("yyyy-MM-dd")
        self.attendance_date_to.setCalendarPopup(True)
        self.attendance_date_to.setStyleSheet("""
            QDateEdit {
                padding: 6px;
                border: 1px solid #3B82F6;
                border-radius: 4px;
                color: #0F172A;
                background-color: white;
            }
            QDateEdit:focus {
                border: 2px solid #1E3A8A;
            }
        """)
        
        # Department filter
        dept_filter_label = QLabel("Department:")
        dept_filter_label.setStyleSheet("color: #0F172A; font-weight: bold;")
        self.attendance_dept_filter = QComboBox()
        self.update_department_filter_combo()  # Populate departments
        self.attendance_dept_filter.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #3B82F6;
                border-radius: 4px;
                color: #0F172A;
                background-color: white;
            }
            QComboBox:focus {
                border: 2px solid #1E3A8A;
            }
        """)
        
        # Staff ID filter
        staff_id_label = QLabel("Staff ID:")
        staff_id_label.setStyleSheet("color: #0F172A; font-weight: bold;")
        self.attendance_staff_id_filter = QLineEdit()
        self.attendance_staff_id_filter.setPlaceholderText("Filter by Staff ID...")
        self.attendance_staff_id_filter.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #3B82F6;
                border-radius: 4px;
                color: #0F172A;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #1E3A8A;
            }
        """)
        
        # Apply filter button
        apply_filter_button = QPushButton("Apply Filters")
        apply_filter_button.clicked.connect(self.apply_attendance_filters)
        apply_filter_button.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        
        # Clear filter button
        clear_filter_button = QPushButton("Clear Filters")
        clear_filter_button.clicked.connect(self.clear_attendance_filters)
        clear_filter_button.setStyleSheet("""
            QPushButton {
                background-color: #94A3B8;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #64748B;
            }
            QPushButton:pressed {
                background-color: #475569;
            }
        """)
        
        # Add filters to layout
        filter_layout.addWidget(date_from_label)
        filter_layout.addWidget(self.attendance_date_from)
        filter_layout.addWidget(date_to_label)
        filter_layout.addWidget(self.attendance_date_to)
        filter_layout.addWidget(dept_filter_label)
        filter_layout.addWidget(self.attendance_dept_filter)
        filter_layout.addWidget(staff_id_label)
        filter_layout.addWidget(self.attendance_staff_id_filter)
        filter_layout.addWidget(apply_filter_button)
        filter_layout.addWidget(clear_filter_button)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Pagination controls
        pagination_layout = QHBoxLayout()
        
        self.attendance_page_label = QLabel("Page 1 of 1")
        self.attendance_page_label.setStyleSheet("color: #0F172A; font-weight: bold; margin: 5px;")
        pagination_layout.addWidget(self.attendance_page_label)
        
        pagination_layout.addStretch()
        
        self.attendance_prev_button = QPushButton("Previous")
        self.attendance_prev_button.clicked.connect(lambda: self.change_attendance_page(-1))
        self.attendance_prev_button.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;  /* Light blue */
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 5px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2563EB;  /* Medium blue */
            }
            QPushButton:pressed {
                background-color: #1D4ED8;  /* Darker blue */
            }
        """)
        self.attendance_prev_button.setEnabled(False)  # Disabled initially
        pagination_layout.addWidget(self.attendance_prev_button)
        
        self.attendance_page_input = QLineEdit("1")
        self.attendance_page_input.setMaximumWidth(50)
        self.attendance_page_input.returnPressed.connect(self.goto_attendance_page)
        self.attendance_page_input.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #3B82F6;  /* Light blue */
                border-radius: 4px;
                color: #0F172A;  /* Dark blue-gray for better contrast */
                background-color: white;
                text-align: center;
            }
            QLineEdit:focus {
                border: 2px solid #1E3A8A;  /* Dark blue */
            }
        """)
        pagination_layout.addWidget(QLabel("Go to page:"))
        pagination_layout.addWidget(self.attendance_page_input)
        
        self.attendance_next_button = QPushButton("Next")
        self.attendance_next_button.clicked.connect(lambda: self.change_attendance_page(1))
        self.attendance_next_button.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;  /* Light blue */
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 5px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2563EB;  /* Medium blue */
            }
            QPushButton:pressed {
                background-color: #1D4ED8;  /* Darker blue */
            }
        """)
        self.attendance_next_button.setEnabled(False)  # Disabled initially
        pagination_layout.addWidget(self.attendance_next_button)
        
        # Initialize pagination variables
        self.attendance_current_page = 1
        self.attendance_items_per_page = 20  # Show 20 attendance records per page
        self.attendance_total_items = 0
        self.attendance_total_pages = 1
        
        # Store filter values
        self.attendance_filters = {
            'date_from': None,
            'date_to': None,
            'department': None,
            'staff_id': None
        }
        
        layout.addLayout(pagination_layout)
        
        refresh_button = QPushButton("Refresh Records")
        refresh_button.clicked.connect(self.refresh_attendance)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;  /* Light blue */
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;  /* Medium blue */
            }
            QPushButton:pressed {
                background-color: #1D4ED8;  /* Darker blue */
            }
        """)
        layout.addWidget(refresh_button)
        
        tab.setLayout(layout)
        return tab
    
    def create_export_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Export group
        export_group = QGroupBox("Export Attendance Data")
        export_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #1E3A8A;  /* Dark blue */
                border-radius: 5px;
                margin: 10px 0px;
                padding-top: 15px;
                color: #0F172A;  /* Dark blue-gray for better contrast */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: #0F172A;  /* Dark blue-gray for better contrast */
                font-weight: bold;
            }
        """)
        export_layout = QVBoxLayout()
        export_layout.setSpacing(15)
        
        # Filter controls for export
        filter_layout = QHBoxLayout()
        
        # Date range filters
        date_from_label = QLabel("From Date:")
        date_from_label.setStyleSheet("color: #0F172A; font-weight: bold;")
        self.export_date_from = QDateEdit()
        self.export_date_from.setDate(QDate.currentDate().addMonths(-1))  # Default to last month
        self.export_date_from.setDisplayFormat("yyyy-MM-dd")
        self.export_date_from.setCalendarPopup(True)
        self.export_date_from.setStyleSheet("""
            QDateEdit {
                padding: 6px;
                border: 1px solid #3B82F6;
                border-radius: 4px;
                color: #0F172A;
                background-color: white;
            }
            QDateEdit:focus {
                border: 2px solid #1E3A8A;
            }
        """)
        
        date_to_label = QLabel("To Date:")
        date_to_label.setStyleSheet("color: #0F172A; font-weight: bold;")
        self.export_date_to = QDateEdit()
        self.export_date_to.setDate(QDate.currentDate())
        self.export_date_to.setDisplayFormat("yyyy-MM-dd")
        self.export_date_to.setCalendarPopup(True)
        self.export_date_to.setStyleSheet("""
            QDateEdit {
                padding: 6px;
                border: 1px solid #3B82F6;
                border-radius: 4px;
                color: #0F172A;
                background-color: white;
            }
            QDateEdit:focus {
                border: 2px solid #1E3A8A;
            }
        """)
        
        # Department filter
        dept_filter_label = QLabel("Department:")
        dept_filter_label.setStyleSheet("color: #0F172A; font-weight: bold;")
        self.export_dept_filter = QComboBox()
        self.update_export_department_combo()  # Populate departments
        self.export_dept_filter.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #3B82F6;
                border-radius: 4px;
                color: #0F172A;
                background-color: white;
            }
            QComboBox:focus {
                border: 2px solid #1E3A8A;
            }
        """)
        
        # Staff ID filter
        staff_id_label = QLabel("Staff ID:")
        staff_id_label.setStyleSheet("color: #0F172A; font-weight: bold;")
        self.export_staff_id_filter = QLineEdit()
        self.export_staff_id_filter.setPlaceholderText("Filter by Staff ID...")
        self.export_staff_id_filter.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #3B82F6;
                border-radius: 4px;
                color: #0F172A;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #1E3A8A;
            }
        """)
        
        # Lateness filter checkbox
        self.lateness_filter_checkbox = QCheckBox("Filter by Lateness")
        self.lateness_filter_checkbox.setStyleSheet("""
            QCheckBox {
                color: #0F172A;
                font-weight: bold;
                margin-left: 10px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #3B82F6;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #3B82F6;
                background-color: #3B82F6;
            }
        """)
        
        # Minimum late count input
        late_count_label = QLabel("Min Late Count:")
        late_count_label.setStyleSheet("color: #0F172A; font-weight: bold;")
        self.export_min_late_count = QLineEdit("1")
        self.export_min_late_count.setPlaceholderText("e.g., 1")
        self.export_min_late_count.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #3B82F6;
                border-radius: 4px;
                color: #0F172A;
                background-color: #E2E8F0;  /* Light gray when disabled */
                min-width: 60px;
            }
            QLineEdit:enabled {
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #1E3A8A;
            }
        """)
        # Disable the late count input initially
        self.export_min_late_count.setEnabled(False)
        self.export_min_late_count.setReadOnly(True)  # Make it read-only initially
        # Connect checkbox to enable/disable the late count input using multiple signals for reliability
        self.lateness_filter_checkbox.stateChanged.connect(self.toggle_lateness_filter)
        self.lateness_filter_checkbox.clicked.connect(lambda: self.toggle_lateness_filter(self.lateness_filter_checkbox.checkState()))
        
        # Add filters to layout
        filter_layout.addWidget(date_from_label)
        filter_layout.addWidget(self.export_date_from)
        filter_layout.addWidget(date_to_label)
        filter_layout.addWidget(self.export_date_to)
        filter_layout.addWidget(dept_filter_label)
        filter_layout.addWidget(self.export_dept_filter)
        filter_layout.addWidget(staff_id_label)
        filter_layout.addWidget(self.export_staff_id_filter)
        filter_layout.addWidget(self.lateness_filter_checkbox)
        filter_layout.addWidget(late_count_label)
        filter_layout.addWidget(self.export_min_late_count)
        filter_layout.addStretch()
        
        export_layout.addLayout(filter_layout)
        
        # Export description
        export_desc = QLabel("Click the button below to export attendance records to a CSV file with selected filters.")
        export_desc.setAlignment(Qt.AlignCenter)
        export_desc.setWordWrap(True)
        export_desc.setStyleSheet("color: #0F172A; margin: 10px;")
        export_layout.addWidget(export_desc)
        
        # Export button
        export_button = QPushButton("Export to CSV")
        export_button.clicked.connect(self.export_to_csv)
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;  /* Light blue */
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #2563EB;  /* Medium blue */
            }
            QPushButton:pressed {
                background-color: #1D4ED8;  /* Darker blue */
            }
        """)
        export_layout.addWidget(export_button)
        export_layout.setAlignment(export_button, Qt.AlignCenter)
        
        # Additional info
        info_label = QLabel("The exported file will contain: Staff ID, Name, Department, Date, Time In, Time Out")
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #64748B; font-style: italic; margin: 10px;")
        export_layout.addWidget(info_label)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # Add stretch to center content vertically
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_departments_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Department management form
        form_group = QGroupBox("Add New Department")
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #1E3A8A;  /* Dark blue */
                border-radius: 5px;
                margin: 10px 0px;
                padding-top: 15px;
                color: #0F172A;  /* Dark blue-gray for better contrast */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: #0F172A;  /* Dark blue-gray for better contrast */
                font-weight: bold;
            }
        """)
        form_layout = QFormLayout()
        
        self.dept_name_input = QLineEdit()
        self.dept_name_input.setPlaceholderText("Department name")
        self.dept_name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #3B82F6;  /* Light blue */
                border-radius: 4px;
                color: #0F172A;  /* Dark blue-gray for better contrast */
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #1E3A8A;  /* Dark blue */
            }
        """)
        
        self.dept_description_input = QLineEdit()
        self.dept_description_input.setPlaceholderText("Description (optional)")
        self.dept_description_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #3B82F6;  /* Light blue */
                border-radius: 4px;
                color: #0F172A;  /* Dark blue-gray for better contrast */
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #1E3A8A;  /* Dark blue */
            }
        """)
        
        form_layout.addRow("Department Name:", self.dept_name_input)
        form_layout.addRow("Description:", self.dept_description_input)
        
        add_dept_button = QPushButton("Add Department")
        add_dept_button.clicked.connect(self.add_department)
        add_dept_button.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;  /* Light blue */
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;  /* Medium blue */
            }
            QPushButton:pressed {
                background-color: #1D4ED8;  /* Darker blue */
            }
        """)
        form_layout.addRow(add_dept_button)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Table to display departments
        self.dept_table = QTableWidget()
        self.dept_table.setColumnCount(4)  # ID, Name, Description, Actions
        self.dept_table.setHorizontalHeaderLabels(["ID", "Name", "Description", "Actions"])
        self.dept_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #3B82F6;  /* Light blue */
                alternate-background-color: #F0F9FF;  /* Very light blue */
                selection-background-color: #BAE6FD;  /* Lighter blue for selected items */
            }
            QHeaderView::section {
                background-color: #1E3A8A;  /* Dark blue */
                color: white;
                padding: 4px;
                border: 1px solid #3B82F6;  /* Light blue */
            }
        """)
        
        # Department table sizing
        header = self.dept_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID column - resize to fit
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Name column - stretch to fill
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Description column - stretch to fill
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Actions column - resize to fit
        
        layout.addWidget(QLabel("Departments"))
        layout.addWidget(self.dept_table)
        
        # Pagination controls
        pagination_layout = QHBoxLayout()
        
        self.dept_page_label = QLabel("Page 1 of 1")
        self.dept_page_label.setStyleSheet("color: #0F172A; font-weight: bold; margin: 5px;")
        pagination_layout.addWidget(self.dept_page_label)
        
        pagination_layout.addStretch()
        
        self.dept_prev_button = QPushButton("Previous")
        self.dept_prev_button.clicked.connect(lambda: self.change_dept_page(-1))
        self.dept_prev_button.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;  /* Light blue */
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 5px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2563EB;  /* Medium blue */
            }
            QPushButton:pressed {
                background-color: #1D4ED8;  /* Darker blue */
            }
        """)
        self.dept_prev_button.setEnabled(False)  # Disabled initially
        pagination_layout.addWidget(self.dept_prev_button)
        
        self.dept_page_input = QLineEdit("1")
        self.dept_page_input.setMaximumWidth(50)
        self.dept_page_input.returnPressed.connect(self.goto_dept_page)
        self.dept_page_input.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #3B82F6;  /* Light blue */
                border-radius: 4px;
                color: #0F172A;  /* Dark blue-gray for better contrast */
                background-color: white;
                text-align: center;
            }
            QLineEdit:focus {
                border: 2px solid #1E3A8A;  /* Dark blue */
            }
        """)
        pagination_layout.addWidget(QLabel("Go to page:"))
        pagination_layout.addWidget(self.dept_page_input)
        
        self.dept_next_button = QPushButton("Next")
        self.dept_next_button.clicked.connect(lambda: self.change_dept_page(1))
        self.dept_next_button.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;  /* Light blue */
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 5px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2563EB;  /* Medium blue */
            }
            QPushButton:pressed {
                background-color: #1D4ED8;  /* Darker blue */
            }
        """)
        self.dept_next_button.setEnabled(False)  # Disabled initially
        pagination_layout.addWidget(self.dept_next_button)
        
        # Initialize pagination variables
        self.dept_current_page = 1
        self.dept_items_per_page = 20  # Show 20 departments per page
        self.dept_total_items = 0
        self.dept_total_pages = 1
        
        layout.addLayout(pagination_layout)
        
        # Refresh button
        refresh_dept_button = QPushButton("Refresh Departments")
        refresh_dept_button.clicked.connect(self.refresh_departments)
        refresh_dept_button.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;  /* Light blue */
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;  /* Medium blue */
            }
            QPushButton:pressed {
                background-color: #1D4ED8;  /* Darker blue */
            }
        """)
        layout.addWidget(refresh_dept_button)
        
        # Load existing departments
        self.refresh_departments()
        
        tab.setLayout(layout)
        return tab
    
    def update_department_combo(self):
        """Update the department combobox with all available departments"""
        # Clear current items
        self.staff_department_combo.clear()
        
        # Get all departments from the database
        departments = self.db.get_all_departments()
        
        # Add departments to the combobox
        for dept_id, dept_name, description in departments:
            self.staff_department_combo.addItem(dept_name, dept_id)
        
        # Add an option to create a new department
        self.staff_department_combo.addItem("Add New Department...", -1)

    def register_staff(self):
        name = self.staff_name_input.text()
        staff_id = self.staff_id_input.text()
        
        # Get the selected department name from the combobox
        current_index = self.staff_department_combo.currentIndex()
        selected_data = self.staff_department_combo.itemData(current_index)
        
        # Check if "Add New Department..." was selected
        if selected_data == -1:
            # Open dialog to add a new department
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
            dialog = QDialog(self)
            dialog.setWindowTitle("Add New Department")
            dialog.setModal(True)
            dialog.resize(300, 150)

            layout = QVBoxLayout()

            label = QLabel("Enter department name:")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)

            dept_input = QLineEdit()
            dept_input.setPlaceholderText("Department name")
            layout.addWidget(dept_input)

            button_layout = QHBoxLayout()

            ok_button = QPushButton("Add Department")
            ok_button.clicked.connect(dialog.accept)

            cancel_button = QPushButton("Cancel")
            cancel_button.clicked.connect(dialog.reject)

            button_layout.addWidget(ok_button)
            button_layout.addWidget(cancel_button)

            layout.addLayout(button_layout)

            dialog.setLayout(layout)

            if dialog.exec() == QDialog.Accepted:
                new_department = dept_input.text().strip()
                if new_department:
                    # Add the new department
                    success = self.db.add_department(new_department)
                    if success:
                        # Update the combobox with the new department
                        self.update_department_combo()
                        
                        # Find and select the new department in the combobox
                        index = self.staff_department_combo.findText(new_department)
                        if index != -1:
                            self.staff_department_combo.setCurrentIndex(index)
                            department = new_department
                        else:
                            department = new_department
                    else:
                        QMessageBox.warning(self, "Error", f"Department '{new_department}' already exists!")
                        return
                else:
                    QMessageBox.warning(self, "Input Error", "Department name cannot be empty!")
                    return
            else:
                # User cancelled, return early
                return
        
        # Get the selected department name
        department = self.staff_department_combo.currentText()
        
        if department == "Add New Department...":
            return  # User cancelled adding a new department
        
        if name and staff_id and department:
            success = self.db.add_staff(staff_id, name, department)
            if success:
                self.staff_name_input.clear()
                # Update the combobox to reflect any new departments
                self.update_department_combo()
                
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Registration", f"Staff {name} registered successfully!")
            else:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Registration Error", f"Staff ID {staff_id} already exists!")
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Input Error", "Please fill in all fields")
    
    def refresh_attendance(self):
        # Convert QDate objects to strings for database query
        date_from = self.attendance_date_from.date().toString("yyyy-MM-dd") if self.attendance_date_from.date().year() > 1752 else None
        date_to = self.attendance_date_to.date().toString("yyyy-MM-dd") if self.attendance_date_to.date().year() > 1752 else None
        department = self.attendance_dept_filter.currentText() if self.attendance_dept_filter.currentText() != "All Departments" else None
        staff_id = self.attendance_staff_id_filter.text().strip() if self.attendance_staff_id_filter.text().strip() else None

        # Fetch attendance records from the database with pagination and filters
        offset = (self.attendance_current_page - 1) * self.attendance_items_per_page
        records = self.db.get_all_attendance(
            limit=self.attendance_items_per_page,
            offset=offset,
            date_from=date_from,
            date_to=date_to,
            department=department,
            staff_id=staff_id
        )
        
        # Update total attendance count with filters
        self.attendance_total_items = self.db.get_total_attendance_count(
            date_from=date_from,
            date_to=date_to,
            department=department,
            staff_id=staff_id
        )
        self.attendance_total_pages = max(1, (self.attendance_total_items + self.attendance_items_per_page - 1) // self.attendance_items_per_page)
        
        # Update the page label
        self.attendance_page_label.setText(f"Page {self.attendance_current_page} of {self.attendance_total_pages}")
        
        # Update pagination button states
        self.attendance_prev_button.setEnabled(self.attendance_current_page > 1)
        self.attendance_next_button.setEnabled(self.attendance_current_page < self.attendance_total_pages)
        
        # Clear existing data
        self.attendance_table.setRowCount(0)
        
        for row_idx, record in enumerate(records):
            self.attendance_table.insertRow(row_idx)
            # Insert the data into the appropriate columns
            for col_idx, data in enumerate(record):
                if data is None:
                    data = ""  # Display empty string instead of "None"
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignCenter)  # Center the text
                self.attendance_table.setItem(row_idx, col_idx, item)

    def change_attendance_page(self, direction):
        """Change the current page for attendance records"""
        new_page = self.attendance_current_page + direction
        
        if 1 <= new_page <= self.attendance_total_pages:
            self.attendance_current_page = new_page
            self.refresh_attendance()

    def goto_attendance_page(self):
        """Go to a specific page for attendance records"""
        try:
            page_num = int(self.attendance_page_input.text())
            if 1 <= page_num <= self.attendance_total_pages:
                self.attendance_current_page = page_num
                self.refresh_attendance()
            else:
                # Show error if page number is invalid
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Invalid Page", f"Please enter a page number between 1 and {self.attendance_total_pages}")
                self.attendance_page_input.setText(str(self.attendance_current_page))  # Reset to current page
        except ValueError:
            # Show error if input is not a valid number
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid page number")
            self.attendance_page_input.setText(str(self.attendance_current_page))  # Reset to current page

    def update_department_filter_combo(self):
        """Update the department filter combobox with all available departments"""
        # Clear current items
        self.attendance_dept_filter.clear()
        
        # Add "All Departments" option first
        self.attendance_dept_filter.addItem("All Departments")
        
        # Get all departments from the database
        departments = self.db.get_all_departments()
        
        # Add departments to the combobox
        for dept_id, dept_name, description in departments:
            self.attendance_dept_filter.addItem(dept_name)

    def apply_attendance_filters(self):
        """Apply the selected filters to attendance data"""
        # Reset to first page when applying filters
        self.attendance_current_page = 1
        self.refresh_attendance()

    def clear_attendance_filters(self):
        """Clear all filters and reset to default values"""
        # Reset to current date range (last month to today)
        from PySide6.QtCore import QDate
        self.attendance_date_from.setDate(QDate.currentDate().addMonths(-1))
        self.attendance_date_to.setDate(QDate.currentDate())
        
        # Reset department filter to "All Departments"
        self.attendance_dept_filter.setCurrentIndex(0)
        
        # Clear staff ID filter
        self.attendance_staff_id_filter.clear()
        
        # Reset to first page and refresh
        self.attendance_current_page = 1
        self.refresh_attendance()
    
    def refresh_staff(self):
        # Fetch staff records from the database with pagination
        offset = (self.staff_current_page - 1) * self.staff_items_per_page
        records = self.db.get_all_staff(limit=self.staff_items_per_page, offset=offset)
        
        # Update total staff count and calculate total pages
        self.staff_total_items = self.db.get_total_staff_count()
        self.staff_total_pages = max(1, (self.staff_total_items + self.staff_items_per_page - 1) // self.staff_items_per_page)
        
        # Update the page label
        self.staff_page_label.setText(f"Page {self.staff_current_page} of {self.staff_total_pages}")
        
        # Update pagination button states
        self.staff_prev_button.setEnabled(self.staff_current_page > 1)
        self.staff_next_button.setEnabled(self.staff_current_page < self.staff_total_pages)
        
        # Clear existing data
        self.staff_table.setRowCount(0)
        
        for row_idx, record in enumerate(records):
            self.staff_table.insertRow(row_idx)
            # Insert the basic data (Staff ID, Name, Department)
            for col_idx, data in enumerate(record):
                if col_idx < 3:  # Only for the visible columns (ID, Name, Department)
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.AlignCenter)  # Center the text
                    self.staff_table.setItem(row_idx, col_idx, item)
            
            # Add Edit button
            edit_button = QPushButton("Edit")
            edit_button.setStyleSheet("""
                QPushButton {
                    background-color: #10B981;  /* Green */
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #059669;  /* Darker Green */
                }
            """)
            edit_button.clicked.connect(lambda _, r=row_idx: self.edit_staff(r))
            self.staff_table.setCellWidget(row_idx, 3, edit_button)
            
            # Add Delete button
            delete_button = QPushButton("Delete")
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #EF4444;  /* Red */
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #DC2626;  /* Darker Red */
                }
            """)
            delete_button.clicked.connect(lambda _, r=row_idx: self.delete_staff(r))
            self.staff_table.setCellWidget(row_idx, 4, delete_button)
            
            # Add a hidden column to store the staff ID for reference
            self.staff_table.setItem(row_idx, 5, QTableWidgetItem(str(record[0])))  # Staff ID
            self.staff_table.setColumnHidden(5, True)  # Hide this column

    def change_staff_page(self, direction):
        """Change the current page for staff records"""
        new_page = self.staff_current_page + direction
        
        if 1 <= new_page <= self.staff_total_pages:
            self.staff_current_page = new_page
            self.refresh_staff()

    def goto_staff_page(self):
        """Go to a specific page for staff records"""
        try:
            page_num = int(self.staff_page_input.text())
            if 1 <= page_num <= self.staff_total_pages:
                self.staff_current_page = page_num
                self.refresh_staff()
            else:
                # Show error if page number is invalid
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Invalid Page", f"Please enter a page number between 1 and {self.staff_total_pages}")
                self.staff_page_input.setText(str(self.staff_current_page))  # Reset to current page
        except ValueError:
            # Show error if input is not a valid number
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid page number")
            self.staff_page_input.setText(str(self.staff_current_page))  # Reset to current page
    
    def edit_staff(self, row):
        # Get the staff ID from the hidden column
        staff_id = self.staff_table.item(row, 5).text()
        
        # Get current values
        current_name = self.staff_table.item(row, 1).text()
        current_department = self.staff_table.item(row, 2).text()
        
        # Create dialog for editing
        from PySide6.QtWidgets import QDialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Staff Member")
        dialog.setModal(True)
        dialog.resize(300, 150)
        
        from PySide6.QtWidgets import QFormLayout, QLineEdit, QComboBox, QHBoxLayout, QPushButton, QLabel, QVBoxLayout, QMessageBox
        layout = QFormLayout()
        
        name_input = QLineEdit(current_name)
        
        # Create department combobox for editing
        department_combo = QComboBox()
        
        # Get all departments from the database
        departments = self.db.get_all_departments()
        
        # Add departments to the combobox
        for dept_id, dept_name, description in departments:
            department_combo.addItem(dept_name, dept_id)
        
        # Add an option to create a new department
        department_combo.addItem("Add New Department...", -1)
        
        # Set the current department as selected
        current_index = department_combo.findText(current_department)
        if current_index != -1:
            department_combo.setCurrentIndex(current_index)
        else:
            # If department doesn't exist in the list, add it temporarily
            department_combo.insertItem(0, current_department)
            department_combo.setCurrentIndex(0)
        
        layout.addRow("Name:", name_input)
        layout.addRow("Department:", department_combo)
        
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(dialog.accept)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addRow(button_layout)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.Accepted:
            new_name = name_input.text()
            
            # Get the selected department name from the combobox
            current_index = department_combo.currentIndex()
            selected_data = department_combo.itemData(current_index)
            
            # Check if "Add New Department..." was selected
            if selected_data == -1:
                # Open dialog to add a new department
                dept_dialog = QDialog(self)
                dept_dialog.setWindowTitle("Add New Department")
                dept_dialog.setModal(True)
                dept_dialog.resize(300, 150)

                dept_layout = QVBoxLayout()

                dept_label = QLabel("Enter department name:")
                dept_label.setAlignment(Qt.AlignCenter)
                dept_layout.addWidget(dept_label)

                new_dept_input = QLineEdit()
                new_dept_input.setPlaceholderText("Department name")
                dept_layout.addWidget(new_dept_input)

                dept_button_layout = QHBoxLayout()

                dept_ok_button = QPushButton("Add Department")
                dept_ok_button.clicked.connect(dept_dialog.accept)

                dept_cancel_button = QPushButton("Cancel")
                dept_cancel_button.clicked.connect(dept_dialog.reject)

                dept_button_layout.addWidget(dept_ok_button)
                dept_button_layout.addWidget(dept_cancel_button)

                dept_layout.addLayout(dept_button_layout)

                dept_dialog.setLayout(dept_layout)

                if dept_dialog.exec() == QDialog.Accepted:
                    new_department = new_dept_input.text().strip()
                    if new_department:
                        # Add the new department
                        success = self.db.add_department(new_department)
                        if success:
                            new_dept = new_department
                        else:
                            QMessageBox.warning(self, "Error", f"Department '{new_department}' already exists!")
                            return
                    else:
                        QMessageBox.warning(self, "Input Error", "Department name cannot be empty!")
                        return
                else:
                    # User cancelled, return early
                    return
            else:
                new_dept = department_combo.currentText()
            
            if new_name and new_dept:
                # Update the staff member in the database
                success = self.db.update_staff(staff_id, new_name, new_dept)
                
                if success:
                    # Refresh the entire staff table to ensure consistency
                    self.refresh_staff()
                    QMessageBox.information(self, "Success", "Staff member updated successfully!")
                else:
                    QMessageBox.critical(self, "Error", "Failed to update staff member.")
            else:
                QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
    
    def add_department(self):
        """Add a new department"""
        name = self.dept_name_input.text().strip()
        description = self.dept_description_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Input Error", "Department name cannot be empty!")
            return
            
        # Check if department already exists
        existing_depts = self.db.get_all_departments()
        for dept_id, dept_name, dept_desc in existing_depts:
            if dept_name.lower() == name.lower():
                QMessageBox.warning(self, "Error", f"Department '{name}' already exists!")
                return
        
        success = self.db.add_department(name, description)
        if success:
            self.dept_name_input.clear()
            self.dept_description_input.clear()
            
            # Refresh the department list and combobox
            self.refresh_departments()
            self.update_department_combo()
            
            QMessageBox.information(self, "Success", f"Department '{name}' added successfully!")
        else:
            QMessageBox.warning(self, "Error", f"Department '{name}' already exists!")
    
    def refresh_departments(self):
        """Refresh the departments table with pagination"""
        # Calculate offset for pagination
        offset = (self.dept_current_page - 1) * self.dept_items_per_page
        
        # Get departments from the database with pagination
        departments = self.db.get_all_departments(limit=self.dept_items_per_page, offset=offset)
        
        # Update total departments count
        self.dept_total_items = self.db.get_total_departments_count()
        self.dept_total_pages = max(1, (self.dept_total_items + self.dept_items_per_page - 1) // self.dept_items_per_page)
        
        # Update the page label
        self.dept_page_label.setText(f"Page {self.dept_current_page} of {self.dept_total_pages}")
        
        # Update pagination button states
        self.dept_prev_button.setEnabled(self.dept_current_page > 1)
        self.dept_next_button.setEnabled(self.dept_current_page < self.dept_total_pages)
        
        # Clear existing data
        self.dept_table.setRowCount(0)
        
        for row_idx, (dept_id, dept_name, dept_description) in enumerate(departments):
            self.dept_table.insertRow(row_idx)
            
            # Add department ID
            id_item = QTableWidgetItem(str(dept_id))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.dept_table.setItem(row_idx, 0, id_item)
            
            # Add department name
            name_item = QTableWidgetItem(dept_name)
            name_item.setTextAlignment(Qt.AlignCenter)
            self.dept_table.setItem(row_idx, 1, name_item)
            
            # Add department description
            desc_item = QTableWidgetItem(dept_description if dept_description else "")
            desc_item.setTextAlignment(Qt.AlignCenter)
            self.dept_table.setItem(row_idx, 2, desc_item)
            
            # Add action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setAlignment(Qt.AlignCenter)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            # Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #10B981;  /* Green */
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #059669;  /* Darker Green */
                }
            """)
            edit_btn.clicked.connect(lambda _, id=dept_id: self.edit_department(id))
            actions_layout.addWidget(edit_btn)
            
            # Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #EF4444;  /* Red */
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #DC2626;  /* Darker Red */
                }
            """)
            delete_btn.clicked.connect(lambda _, id=dept_id: self.delete_department(id))
            actions_layout.addWidget(delete_btn)
            
            # Add the actions widget to the table
            self.dept_table.setCellWidget(row_idx, 3, actions_widget)

    def change_dept_page(self, direction):
        """Change the current page for department records"""
        new_page = self.dept_current_page + direction
        
        if 1 <= new_page <= self.dept_total_pages:
            self.dept_current_page = new_page
            self.refresh_departments()

    def goto_dept_page(self):
        """Go to a specific page for department records"""
        try:
            page_num = int(self.dept_page_input.text())
            if 1 <= page_num <= self.dept_total_pages:
                self.dept_current_page = page_num
                self.refresh_departments()
            else:
                # Show error if page number is invalid
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Invalid Page", f"Please enter a page number between 1 and {self.dept_total_pages}")
                self.dept_page_input.setText(str(self.dept_current_page))  # Reset to current page
        except ValueError:
            # Show error if input is not a valid number
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid page number")
            self.dept_page_input.setText(str(self.dept_current_page))  # Reset to current page
    
    def edit_department(self, dept_id):
        """Edit an existing department"""
        # Get current department info
        dept_info = self.db.get_department_by_id(dept_id)
        if not dept_info:
            QMessageBox.critical(self, "Error", "Department not found!")
            return
        
        dept_id, current_name, current_description = dept_info
        
        # Create dialog for editing
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Department")
        dialog.setModal(True)
        dialog.resize(300, 150)
        
        layout = QFormLayout()
        
        name_input = QLineEdit(current_name)
        description_input = QLineEdit(current_description if current_description else "")
        
        layout.addRow("Department Name:", name_input)
        layout.addRow("Description:", description_input)
        
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(dialog.accept)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addRow(button_layout)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.Accepted:
            new_name = name_input.text().strip()
            new_description = description_input.text().strip()
            
            if not new_name:
                QMessageBox.warning(self, "Input Error", "Department name cannot be empty!")
                return
            
            # Check if department name already exists (excluding this department)
            existing_depts = self.db.get_all_departments()
            for existing_id, existing_name, _ in existing_depts:
                if existing_name.lower() == new_name.lower() and existing_id != dept_id:
                    QMessageBox.warning(self, "Error", f"Department '{new_name}' already exists!")
                    return
            
            success = self.db.update_department(dept_id, new_name, new_description)
            if success:
                # Refresh the department list and combobox
                self.refresh_departments()
                self.update_department_combo()
                
                QMessageBox.information(self, "Success", "Department updated successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to update department.")
    
    def delete_department(self, dept_id):
        """Delete a department"""
        # Get department info to show in confirmation
        dept_info = self.db.get_department_by_id(dept_id)
        if not dept_info:
            QMessageBox.critical(self, "Error", "Department not found!")
            return
        
        dept_id, dept_name, dept_description = dept_info
        
        # Check if any staff are assigned to this department
        conn = sqlite3.connect("attendance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM staff WHERE department_id = ?", (dept_id,))
        staff_count = cursor.fetchone()[0]
        conn.close()
        
        if staff_count > 0:
            QMessageBox.critical(
                self, 
                "Cannot Delete", 
                f"Cannot delete department '{dept_name}' because {staff_count} staff member(s) are assigned to it.\n"
                f"Please reassign these staff members to other departments first."
            )
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete department '{dept_name}'?\n"
            f"This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.db.delete_department(dept_id)
            if success:
                # Refresh the department list and combobox
                self.refresh_departments()
                self.update_department_combo()
                
                QMessageBox.information(self, "Success", f"Department '{dept_name}' deleted successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to delete department.")

    def edit_staff_by_id(self, staff_id: str):
        """Edit staff by directly using ID instead of row index"""
        # Get current values from the database
        staff_info = self.db.get_staff(staff_id)
        if not staff_info:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", "Staff member not found!")
            return

        current_name = staff_info[1]
        current_department = staff_info[2]
        
        # Create dialog for editing
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Staff Member")
        dialog.setModal(True)
        dialog.resize(300, 150)
        
        layout = QFormLayout()
        
        name_input = QLineEdit(current_name)
        
        # Create department combobox for editing
        from PySide6.QtWidgets import QComboBox
        department_combo = QComboBox()

        # Get all departments from the database
        departments = self.db.get_all_departments()

        # Add departments to the combobox
        for dept_id, dept_name, description in departments:
            department_combo.addItem(dept_name, dept_id)

        # Add an option to create a new department
        department_combo.addItem("Add New Department...", -1)

        # Set the current department as selected
        current_index = department_combo.findText(current_department)
        if current_index != -1:
            department_combo.setCurrentIndex(current_index)
        else:
            # If department doesn't exist in the list, add it temporarily
            department_combo.insertItem(0, current_department)
            department_combo.setCurrentIndex(0)

        layout.addRow("Name:", name_input)
        layout.addRow("Department:", department_combo)

        button_layout = QHBoxLayout()

        save_button = QPushButton("Save")
        save_button.clicked.connect(dialog.accept)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        layout.addRow(button_layout)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.Accepted:
            new_name = name_input.text()

            # Get the selected department name from the combobox
            current_index = department_combo.currentIndex()
            selected_data = department_combo.itemData(current_index)

            # Check if "Add New Department..." was selected
            if selected_data == -1:
                # Open dialog to add a new department
                from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
                dept_dialog = QDialog(self)
                dept_dialog.setWindowTitle("Add New Department")
                dept_dialog.setModal(True)
                dept_dialog.resize(300, 150)

                dept_layout = QVBoxLayout()

                dept_label = QLabel("Enter department name:")
                dept_label.setAlignment(Qt.AlignCenter)
                dept_layout.addWidget(dept_label)

                new_dept_input = QLineEdit()
                new_dept_input.setPlaceholderText("Department name")
                dept_layout.addWidget(new_dept_input)

                dept_button_layout = QHBoxLayout()

                dept_ok_button = QPushButton("Add Department")
                dept_ok_button.clicked.connect(dept_dialog.accept)

                dept_cancel_button = QPushButton("Cancel")
                dept_cancel_button.clicked.connect(dept_dialog.reject)

                dept_button_layout.addWidget(dept_ok_button)
                dept_button_layout.addWidget(dept_cancel_button)

                dept_layout.addLayout(dept_button_layout)

                dept_dialog.setLayout(dept_layout)

                if dept_dialog.exec() == QDialog.Accepted:
                    new_department = new_dept_input.text().strip()
                    if new_department:
                        # Add the new department
                        success = self.db.add_department(new_department)
                        if success:
                            new_dept = new_department
                        else:
                            QMessageBox.warning(self, "Error", f"Department '{new_department}' already exists!")
                            return
                    else:
                        QMessageBox.warning(self, "Input Error", "Department name cannot be empty!")
                        return
                else:
                    # User cancelled, return early
                    return
            else:
                new_dept = department_combo.currentText()

            if new_name and new_dept:
                # Update the staff member in the database
                success = self.db.update_staff(staff_id, new_name, new_dept)

                if success:
                    # Refresh the staff table to show updated information
                    self.refresh_staff()
                    # Refresh the department combo in the main form too
                    self.update_department_combo()
                    QMessageBox.information(self, "Success", "Staff member updated successfully!")
                else:
                    QMessageBox.critical(self, "Error", "Failed to update staff member.")
            else:
                QMessageBox.warning(self, "Input Error", "Please fill in all fields.")

    def update_export_department_combo(self):
        """Update the export department filter combobox with all available departments"""
        # Clear current items
        self.export_dept_filter.clear()
        
        # Add "All Departments" option first
        self.export_dept_filter.addItem("All Departments")
        
        # Get all departments from the database
        departments = self.db.get_all_departments()
        
        # Add departments to the combobox
        for dept_id, dept_name, description in departments:
            self.export_dept_filter.addItem(dept_name)
    
    def toggle_lateness_filter(self, state):
        """Enable or disable the minimum late count input based on checkbox state"""
        if state == Qt.Checked:
            self.export_min_late_count.setEnabled(True)
            self.export_min_late_count.setReadOnly(False)  # Make sure it's not read-only
            self.export_min_late_count.setStyleSheet("""
                QLineEdit {
                    padding: 6px;
                    border: 1px solid #3B82F6;
                    border-radius: 4px;
                    color: #0F172A;
                    background-color: white;
                    min-width: 60px;
                }
                QLineEdit:focus {
                    border: 2px solid #1E3A8A;
                }
            """)
        else:
            self.export_min_late_count.setEnabled(False)
            self.export_min_late_count.setReadOnly(True)  # Make it read-only when disabled
            self.export_min_late_count.setStyleSheet("""
                QLineEdit {
                    padding: 6px;
                    border: 1px solid #3B82F6;
                    border-radius: 4px;
                    color: #0F172A;
                    background-color: #E2E8F0;  /* Light gray when disabled */
                    min-width: 60px;
                }
                QLineEdit:focus {
                    border: 2px solid #1E3A8A;
                }
            """)
        # Force a UI update
        self.export_min_late_count.update()

    def delete_staff_by_id(self, staff_id: str) -> bool:
        """Delete staff by directly using ID"""
        # Get staff info to show in confirmation
        staff_info = self.db.get_staff(staff_id)
        if not staff_info:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", "Staff member not found!")
            return False

        staff_name = staff_info[1]
        
        # Confirm deletion with message about data retention
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {staff_name} (ID: {staff_id})?\n\n"
            f"Their attendance records will be retained for audit purposes, "
            f"but they will no longer be able to log attendance.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete the staff member from the database
            success = self.db.delete_staff(staff_id)
            
            if success:
                # Refresh the staff table to show updated information
                self.refresh_staff()
                # Refresh the department combo in the main form too
                self.update_department_combo()
                QMessageBox.information(self, "Success", 
                    f"{staff_name} has been removed from staff list.\n"
                    f"Their attendance records will remain for audit purposes.")
                return True
            else:
                QMessageBox.critical(self, "Error", "Failed to delete staff member.")
                return False
        return False
    
    def delete_staff(self, row):
        # Import here to ensure availability
        from PySide6.QtWidgets import QMessageBox
        
        # Get the staff ID from the hidden column
        staff_id = self.staff_table.item(row, 5).text()
        staff_name = self.staff_table.item(row, 1).text()
        
        # Confirm deletion with message about data retention
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {staff_name} (ID: {staff_id})?\n\n"
            f"Their attendance records will be retained for audit purposes, "
            f"but they will no longer be able to log attendance.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete the staff member from the database
            success = self.db.delete_staff(staff_id)
            
            if success:
                # Refresh the entire staff table to ensure consistency
                self.refresh_staff()
                # Refresh the department combo in the main form too
                self.update_department_combo()
                QMessageBox.information(self, "Success", 
                    f"{staff_name} has been removed from staff list.\n"
                    f"Their attendance records will remain for audit purposes.")
            else:
                QMessageBox.critical(self, "Error", "Failed to delete staff member.")
    
    def export_to_csv(self):
        from PySide6.QtWidgets import QMessageBox, QFileDialog
        
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Attendance Records",
            "attendance_records.csv",
            "CSV Files (*.csv)",
            options=options
        )
        
        if filename:
            # Convert QDate objects to strings for database query
            date_from = self.export_date_from.date().toString("yyyy-MM-dd") if self.export_date_from.date().year() > 1752 else None
            date_to = self.export_date_to.date().toString("yyyy-MM-dd") if self.export_date_to.date().year() > 1752 else None
            department = self.export_dept_filter.currentText() if self.export_dept_filter.currentText() != "All Departments" else None
            staff_id = self.export_staff_id_filter.text().strip() if self.export_staff_id_filter.text().strip() else None
            
            # Check if lateness filter is enabled
            filter_by_lateness = self.lateness_filter_checkbox.isChecked()
            min_late_count = 1
            
            if filter_by_lateness:
                try:
                    min_late_count = int(self.export_min_late_count.text().strip())
                    if min_late_count < 1:
                        min_late_count = 1
                        self.export_min_late_count.setText("1")
                except ValueError:
                    min_late_count = 1
                    self.export_min_late_count.setText("1")
            
            # Get attendance records from database with filters
            records = self.db.get_all_attendance(
                date_from=date_from,
                date_to=date_to,
                department=department,
                staff_id=staff_id
            )
            
            # If lateness filter is enabled, filter the records to only include staff who meet the lateness criteria
            if filter_by_lateness and records:
                # For lateness filtering, we need to identify staff who were late at least the specified number of times
                # within the specified date range. Since the current database method works on a monthly basis,
                # we'll implement a manual check for the date range provided.
                
                # First, get unique staff IDs from the records
                all_staff_ids = list(set([record[0] for record in records]))  # Extract unique staff IDs
                late_staff_ids = []
                
                # Check each staff member to see if they meet the lateness criteria in the date range
                for staff_id in all_staff_ids:
                    # Count late arrivals for this staff member in the date range
                    late_count = 0
                    for record in records:
                        if record[0] == staff_id and record[4]:  # Check if staff_id matches and time_in exists
                            time_in = record[4]
                            date = record[3]
                            
                            # Check if the date is within the specified range (if specified)
                            date_ok = True
                            if date_from and date < date_from:
                                date_ok = False
                            if date_to and date > date_to:
                                date_ok = False
                            
                            if date_ok:
                                # Check if arrival time is after 8:30 AM (late arrival)
                                if time_in > "08:30:00":
                                    late_count += 1
                    
                    # If this staff member meets the minimum late count, add to the list
                    if late_count >= min_late_count:
                        late_staff_ids.append(staff_id)
                
                # Filter the records to include only those from staff members who met the lateness criteria
                filtered_records = [record for record in records if record[0] in late_staff_ids]
                records = filtered_records
                
                # Filter the records to include only those from late staff
                filtered_records = [record for record in records if record[0] in late_staff_ids]
                records = filtered_records
            
            # Write to CSV file
            try:
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Staff ID', 'Name', 'Department', 'Date', 'Time In', 'Time Out'])  # Header
                    writer.writerows(records)  # Data rows
                
                # Show information about the export
                info_message = f"Attendance records exported successfully to {filename}"
                if filter_by_lateness:
                    info_message += f"\n\nRecords filtered to show only staff who were late at least {min_late_count} time(s) in the period."
                
                QMessageBox.information(self, "Export", info_message)
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export records: {str(e)}")
        else:
            QMessageBox.information(self, "Export", "Export cancelled")