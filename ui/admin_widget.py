"""
Admin widget for managing staff and viewing attendance
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QTableWidget, 
    QTableWidgetItem, QTabWidget, QFormLayout, QGroupBox
)
from PySide6.QtCore import Qt
from database import DatabaseManager
import csv


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
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px; color: #1E3A8A;")  # Dark blue
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
                color: #1E3A8A;
            }
            QTabBar::tab:selected {
                background: #1E3A8A;
                color: white;
            }
        """)
        
        # Staff management tab
        staff_tab = self.create_staff_tab()
        tab_widget.addTab(staff_tab, "Manage Staff")
        
        # Staff records tab
        staff_records_tab = self.create_staff_records_tab()
        tab_widget.addTab(staff_records_tab, "Staff Records")
        
        # Attendance records tab
        attendance_tab = self.create_attendance_tab()
        tab_widget.addTab(attendance_tab, "Attendance Records")
        
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
                color: #1E3A8A;  /* Dark blue */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: #1E3A8A;  /* Dark blue */
            }
        """)
        form_layout = QFormLayout()
        
        self.staff_name_input = QLineEdit()
        self.staff_name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #3B82F6;  /* Light blue */
                border-radius: 4px;
                color: #1E3A8A;  /* Dark blue */
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
                color: #1E3A8A;  /* Dark blue */
            }
            QLineEdit:focus {
                border: 2px solid #1E3A8A;  /* Dark blue */
            }
        """)
        self.staff_position_input = QLineEdit()
        self.staff_position_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #3B82F6;  /* Light blue */
                border-radius: 4px;
                color: #1E3A8A;  /* Dark blue */
            }
            QLineEdit:focus {
                border: 2px solid #1E3A8A;  /* Dark blue */
            }
        """)
        
        form_layout.addRow("Full Name:", self.staff_name_input)
        form_layout.addRow("Staff ID:", self.staff_id_input)
        form_layout.addRow("Position:", self.staff_position_input)
        
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
        self.staff_table.setColumnCount(3)
        self.staff_table.setHorizontalHeaderLabels(["Staff ID", "Name", "Position"])
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
        
        layout.addWidget(QLabel("Registered Staff"))
        layout.addWidget(self.staff_table)
        
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
        self.attendance_table.setColumnCount(4)
        self.attendance_table.setHorizontalHeaderLabels(["Staff ID", "Name", "Date", "Time"])
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
        
        layout.addWidget(QLabel("Attendance Records"))
        layout.addWidget(self.attendance_table)
        
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
        
        export_group = QGroupBox("Export Attendance Data")
        export_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #1E3A8A;  /* Dark blue */
                border-radius: 5px;
                margin: 10px 0px;
                padding-top: 15px;
                color: #1E3A8A;  /* Dark blue */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: #1E3A8A;  /* Dark blue */
            }
        """)
        export_layout = QVBoxLayout()
        
        export_label = QLabel("Export attendance records to CSV file")
        export_label.setStyleSheet("color: #1E3A8A;")  # Dark blue
        export_layout.addWidget(export_label)
        
        export_button = QPushButton("Export to CSV")
        export_button.clicked.connect(self.export_to_csv)
        export_button.setStyleSheet("""
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
        export_layout.addWidget(export_button)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        tab.setLayout(layout)
        return tab
    
    def register_staff(self):
        name = self.staff_name_input.text()
        staff_id = self.staff_id_input.text()
        position = self.staff_position_input.text()
        
        if name and staff_id and position:
            success = self.db.add_staff(staff_id, name, position)
            if success:
                self.staff_name_input.clear()
                self.staff_id_input.clear()
                self.staff_position_input.clear()
                
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Registration", f"Staff {name} registered successfully!")
            else:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Registration Error", f"Staff ID {staff_id} already exists!")
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Input Error", "Please fill in all fields")
    
    def refresh_attendance(self):
        # Fetch attendance records from the database
        self.attendance_table.setRowCount(0)  # Clear existing data
        
        records = self.db.get_all_attendance()
        
        for row_idx, record in enumerate(records):
            self.attendance_table.insertRow(row_idx)
            for col_idx, data in enumerate(record):
                self.attendance_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))
    
    def refresh_staff(self):
        # Fetch staff records from the database
        self.staff_table.setRowCount(0)  # Clear existing data
        
        records = self.db.get_all_staff()
        
        for row_idx, record in enumerate(records):
            self.staff_table.insertRow(row_idx)
            for col_idx, data in enumerate(record):
                self.staff_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))
    
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
            # Get attendance records from database
            records = self.db.get_all_attendance()
            
            # Write to CSV file
            try:
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Staff ID', 'Name', 'Date', 'Time'])  # Header
                    writer.writerows(records)  # Data rows
                
                QMessageBox.information(self, "Export", f"Attendance records exported successfully to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export records: {str(e)}")
        else:
            QMessageBox.information(self, "Export", "Export cancelled")