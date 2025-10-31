"""
Department widget for viewing staff and attendance records grouped by department
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QTabWidget, QGroupBox, QHeaderView,
    QComboBox, QFrame
)
from PySide6.QtCore import Qt
from database import DatabaseManager
import sqlite3


class DepartmentWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Departments Overview")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px; color: #0F172A;")
        layout.addWidget(title_label)
        
        # Department selection dropdown
        dept_selection_layout = QHBoxLayout()
        dept_selection_layout.addStretch()
        
        dept_label = QLabel("Select Department:")
        dept_label.setStyleSheet("color: #0F172A; font-weight: bold;")
        dept_selection_layout.addWidget(dept_label)
        
        self.department_combo = QComboBox()
        self.department_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #3B82F6;
                border-radius: 4px;
                color: #0F172A;
                background-color: white;
                min-width: 200px;
            }
            QComboBox:focus {
                border: 2px solid #1E3A8A;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 1px solid #3B82F6;
            }
        """)
        dept_selection_layout.addWidget(self.department_combo)
        
        dept_selection_layout.addStretch()
        
        layout.addLayout(dept_selection_layout)
        
        # Create tab widget for department-specific views
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #1E3A8A;
            }
            QTabBar::tab {
                background: #E0F2FE;
                padding: 8px;
                color: #0F172A;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #1E3A8A;
                color: white;
            }
        """)
        
        # Staff by Department tab
        staff_by_dept_tab = self.create_staff_by_department_tab()
        tab_widget.addTab(staff_by_dept_tab, "Staff by Department")
        
        # Attendance by Department tab
        attendance_by_dept_tab = self.create_attendance_by_department_tab()
        tab_widget.addTab(attendance_by_dept_tab, "Attendance by Department")
        
        layout.addWidget(tab_widget)
        
        # Add refresh button
        refresh_button = QPushButton("Refresh Departments")
        refresh_button.clicked.connect(self.refresh_departments)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;  /* Light blue */
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
                max-width: 200px;
            }
            QPushButton:hover {
                background-color: #2563EB;  /* Medium blue */
            }
            QPushButton:pressed {
                background-color: #1D4ED8;  /* Darker blue */
            }
        """)
        layout.addWidget(refresh_button, 0, Qt.AlignCenter)
        
        self.setLayout(layout)
        
        # Load departments and set up event listeners
        self.load_departments()
        self.department_combo.currentTextChanged.connect(self.on_department_changed)
        
        # Load initial data for the first department
        if self.department_combo.count() > 0:
            self.on_department_changed(self.department_combo.currentText())
    
    def load_departments(self):
        """Load all departments into the combo box"""
        self.department_combo.clear()
        
        departments = self.db.get_all_departments()
        for dept_id, dept_name, description in departments:
            self.department_combo.addItem(dept_name, dept_id)
        
        # Add "All Departments" option at the beginning
        self.department_combo.insertItem(0, "All Departments")
        self.department_combo.setCurrentIndex(0)
    
    def refresh_departments(self):
        """Refresh the department list in the combo box"""
        self.load_departments()
        # Trigger update for current data display
        if self.department_combo.count() > 0:
            self.on_department_changed(self.department_combo.currentText())
    
    def on_department_changed(self, department_name):
        """Handle department selection change"""
        if department_name == "All Departments":
            self.load_all_staff()
            self.load_all_attendance()
        else:
            dept_id = self.department_combo.currentData()
            self.load_staff_by_department(dept_id)
            self.load_attendance_by_department(dept_id)
    
    def create_staff_by_department_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Department staff table
        self.dept_staff_table = QTableWidget()
        self.dept_staff_table.setColumnCount(3)
        self.dept_staff_table.setHorizontalHeaderLabels(["Staff ID", "Name", "Department"])
        self.dept_staff_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #3B82F6;
                alternate-background-color: #F0F9FF;
                selection-background-color: #BAE6FD;
            }
            QHeaderView::section {
                background-color: #1E3A8A;
                color: white;
                padding: 4px;
                border: 1px solid #3B82F6;
            }
        """)
        
        # Set column widths (matching other tables in the application)
        header = self.dept_staff_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # Proportional resizing like other tables
        self.dept_staff_table.setColumnWidth(0, 100)  # Staff ID (smallest)
        self.dept_staff_table.setColumnWidth(1, 300)  # Name (2x Department size)
        self.dept_staff_table.setColumnWidth(2, 150)  # Department
        
        layout.addWidget(QLabel("Staff by Department"))
        layout.addWidget(self.dept_staff_table)
        
        tab.setLayout(layout)
        return tab
    
    def create_attendance_by_department_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Department attendance table
        self.dept_attendance_table = QTableWidget()
        self.dept_attendance_table.setColumnCount(6)
        self.dept_attendance_table.setHorizontalHeaderLabels(["Staff ID", "Name", "Department", "Date", "Time In", "Time Out"])
        self.dept_attendance_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #3B82F6;
                alternate-background-color: #F0F9FF;
                selection-background-color: #BAE6FD;
            }
            QHeaderView::section {
                background-color: #1E3A8A;
                color: white;
                padding: 4px;
                border: 1px solid #3B82F6;
            }
        """)
        
        # Set column widths (matching other attendance tables in the application)
        header = self.dept_attendance_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # Proportional resizing
        self.dept_attendance_table.setColumnWidth(0, 100)  # Staff ID (smallest)
        self.dept_attendance_table.setColumnWidth(1, 300)  # Name (2x Department size)
        self.dept_attendance_table.setColumnWidth(2, 150)  # Department
        self.dept_attendance_table.setColumnWidth(3, 120)  # Date (same as Time In/Out)
        self.dept_attendance_table.setColumnWidth(4, 120)  # Time In (same as Date/Time Out)
        self.dept_attendance_table.setColumnWidth(5, 120)  # Time Out (same as Date/Time In)
        
        layout.addWidget(QLabel("Attendance by Department"))
        layout.addWidget(self.dept_attendance_table)
        
        tab.setLayout(layout)
        return tab
    
    def load_all_staff(self):
        """Load all staff members from all departments"""
        try:
            staff_records = self.db.get_all_staff()
            
            self.dept_staff_table.setRowCount(0)
            for row_idx, (staff_id, name, department) in enumerate(staff_records):
                self.dept_staff_table.insertRow(row_idx)
                
                # Staff ID
                id_item = QTableWidgetItem(staff_id)
                id_item.setTextAlignment(Qt.AlignCenter)
                self.dept_staff_table.setItem(row_idx, 0, id_item)
                
                # Name
                name_item = QTableWidgetItem(name)
                name_item.setTextAlignment(Qt.AlignCenter)
                self.dept_staff_table.setItem(row_idx, 1, name_item)
                
                # Department
                dept_item = QTableWidgetItem(department)
                dept_item.setTextAlignment(Qt.AlignCenter)
                self.dept_staff_table.setItem(row_idx, 2, dept_item)
                
        except Exception as e:
            print(f"Error loading all staff: {e}")
    
    def load_staff_by_department(self, dept_id):
        """Load staff members for a specific department"""
        try:
            # Get department name from ID
            dept_info = self.db.get_department_by_id(dept_id)
            if not dept_info:
                return
            
            department_name = dept_info[1]  # name is the second element
            
            # Get staff members from the staff table
            conn = sqlite3.connect("attendance.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.staff_id, s.name, d.name as department_name
                FROM staff s
                JOIN departments d ON s.department_id = d.id
                WHERE s.department_id = ?
                ORDER BY s.name
            """, (dept_id,))
            
            staff_records = cursor.fetchall()
            conn.close()
            
            self.dept_staff_table.setRowCount(0)
            for row_idx, (staff_id, name, department) in enumerate(staff_records):
                self.dept_staff_table.insertRow(row_idx)
                
                # Staff ID
                id_item = QTableWidgetItem(staff_id)
                id_item.setTextAlignment(Qt.AlignCenter)
                self.dept_staff_table.setItem(row_idx, 0, id_item)
                
                # Name
                name_item = QTableWidgetItem(name)
                name_item.setTextAlignment(Qt.AlignCenter)
                self.dept_staff_table.setItem(row_idx, 1, name_item)
                
                # Department
                dept_item = QTableWidgetItem(department)
                dept_item.setTextAlignment(Qt.AlignCenter)
                self.dept_staff_table.setItem(row_idx, 2, dept_item)
                
        except Exception as e:
            print(f"Error loading staff for department {dept_id}: {e}")
    
    def load_all_attendance(self):
        """Load all attendance records"""
        try:
            # Get all attendance records
            attendance_records = self.db.get_all_attendance()
            
            self.dept_attendance_table.setRowCount(0)
            for row_idx, (staff_id, name, department, date, time_in, time_out) in enumerate(attendance_records):
                self.dept_attendance_table.insertRow(row_idx)
                
                # Staff ID
                id_item = QTableWidgetItem(staff_id)
                id_item.setTextAlignment(Qt.AlignCenter)
                self.dept_attendance_table.setItem(row_idx, 0, id_item)
                
                # Name
                name_item = QTableWidgetItem(name)
                name_item.setTextAlignment(Qt.AlignCenter)
                self.dept_attendance_table.setItem(row_idx, 1, name_item)
                
                # Department
                dept_item = QTableWidgetItem(department)
                dept_item.setTextAlignment(Qt.AlignCenter)
                self.dept_attendance_table.setItem(row_idx, 2, dept_item)
                
                # Date
                date_item = QTableWidgetItem(date)
                date_item.setTextAlignment(Qt.AlignCenter)
                self.dept_attendance_table.setItem(row_idx, 3, date_item)
                
                # Time In
                time_in_item = QTableWidgetItem(time_in if time_in else "")
                time_in_item.setTextAlignment(Qt.AlignCenter)
                self.dept_attendance_table.setItem(row_idx, 4, time_in_item)
                
                # Time Out
                time_out_item = QTableWidgetItem(time_out if time_out else "")
                time_out_item.setTextAlignment(Qt.AlignCenter)
                self.dept_attendance_table.setItem(row_idx, 5, time_out_item)
                
        except Exception as e:
            print(f"Error loading all attendance: {e}")
    
    def load_attendance_by_department(self, dept_id):
        """Load attendance records for a specific department"""
        try:
            # Get department name from ID
            dept_info = self.db.get_department_by_id(dept_id)
            if not dept_info:
                return
            
            department_name = dept_info[1]  # name is the second element
            
            # Get attendance records for this department
            conn = sqlite3.connect("attendance.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT a.staff_id, a.name, a.department, a.date, a.time_in, a.time_out
                FROM attendance a
                WHERE a.department = ?
                ORDER BY a.date DESC, a.time_in DESC
            """, (department_name,))
            
            attendance_records = cursor.fetchall()
            conn.close()
            
            self.dept_attendance_table.setRowCount(0)
            for row_idx, (staff_id, name, department, date, time_in, time_out) in enumerate(attendance_records):
                self.dept_attendance_table.insertRow(row_idx)
                
                # Staff ID
                id_item = QTableWidgetItem(staff_id)
                id_item.setTextAlignment(Qt.AlignCenter)
                self.dept_attendance_table.setItem(row_idx, 0, id_item)
                
                # Name
                name_item = QTableWidgetItem(name)
                name_item.setTextAlignment(Qt.AlignCenter)
                self.dept_attendance_table.setItem(row_idx, 1, name_item)
                
                # Department
                dept_item = QTableWidgetItem(department)
                dept_item.setTextAlignment(Qt.AlignCenter)
                self.dept_attendance_table.setItem(row_idx, 2, dept_item)
                
                # Date
                date_item = QTableWidgetItem(date)
                date_item.setTextAlignment(Qt.AlignCenter)
                self.dept_attendance_table.setItem(row_idx, 3, date_item)
                
                # Time In
                time_in_item = QTableWidgetItem(time_in if time_in else "")
                time_in_item.setTextAlignment(Qt.AlignCenter)
                self.dept_attendance_table.setItem(row_idx, 4, time_in_item)
                
                # Time Out
                time_out_item = QTableWidgetItem(time_out if time_out else "")
                time_out_item.setTextAlignment(Qt.AlignCenter)
                self.dept_attendance_table.setItem(row_idx, 5, time_out_item)
                
        except Exception as e:
            print(f"Error loading attendance for department {dept_id}: {e}")