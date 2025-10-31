"""
Attendance Records widget for viewing attendance data
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QTableWidget, 
    QTableWidgetItem, QTabWidget, QFormLayout, QGroupBox, QHeaderView, QFileDialog, QDialog, QMessageBox, QDateEdit, QComboBox
)
from PySide6.QtCore import Qt, QDate
from database import DatabaseManager


class AttendanceRecordsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
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
        
        self.setLayout(layout)
        
        # Load initial attendance data
        self.refresh_attendance()
    
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