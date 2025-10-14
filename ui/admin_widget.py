"""
Admin widget for managing staff and viewing attendance
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QTableWidget, 
    QTableWidgetItem, QTabWidget, QFormLayout, QGroupBox, QHeaderView, QFileDialog, QDialog, QMessageBox
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
        self.staff_department_input = QLineEdit()
        self.staff_department_input.setStyleSheet("""
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
        
        form_layout.addRow("Full Name:", self.staff_name_input)
        form_layout.addRow("Staff ID:", self.staff_id_input)
        form_layout.addRow("Department:", self.staff_department_input)
        
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
        
        # Main title
       # title_label = QLabel("Export Attendance Data")
       # title_label.setAlignment(Qt.AlignCenter)
       # title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #0F172A; margin: 10px;")
       # layout.addWidget(title_label)
        
        # Description
       # desc_label = QLabel("Export attendance records to CSV file for external use.")
       # desc_label.setAlignment(Qt.AlignCenter)
       # desc_label.setStyleSheet("color: #0F172A; font-size: 12px; margin: 5px;")
       # layout.addWidget(desc_label)
        
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
        
        # Export description
        export_desc = QLabel("Click the button below to export all attendance records to a CSV file.")
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
    
    def register_staff(self):
        name = self.staff_name_input.text()
        staff_id = self.staff_id_input.text()
        department = self.staff_department_input.text()
        
        if name and staff_id and department:
            success = self.db.add_staff(staff_id, name, department)
            if success:
                self.staff_name_input.clear()
                self.staff_id_input.clear()
                self.staff_department_input.clear()
                
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
            # Insert the data into the appropriate columns
            for col_idx, data in enumerate(record):
                if data is None:
                    data = ""  # Display empty string instead of "None"
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignCenter)  # Center the text
                self.attendance_table.setItem(row_idx, col_idx, item)
    
    def refresh_staff(self):
        # Fetch staff records from the database
        self.staff_table.setRowCount(0)  # Clear existing data
        
        records = self.db.get_all_staff()
        
        for row_idx, record in enumerate(records):
            self.staff_table.insertRow(row_idx)
            # Insert the basic data (Staff ID, Name, Department)
            for col_idx, data in enumerate(record):
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
    
    def edit_staff(self, row):
        # Get the staff ID from the hidden column
        staff_id = self.staff_table.item(row, 5).text()
        
        # Get current values
        current_name = self.staff_table.item(row, 1).text()
        current_department = self.staff_table.item(row, 2).text()
        
        # Create dialog for editing
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Staff Member")
        dialog.setModal(True)
        dialog.resize(300, 150)
        
        layout = QFormLayout()
        
        name_input = QLineEdit(current_name)
        department_input = QLineEdit(current_department)
        
        layout.addRow("Name:", name_input)
        layout.addRow("Department:", department_input)
        
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
            new_department = department_input.text()
            
            if new_name and new_department:
                # Update the staff member in the database
                success = self.db.update_staff(staff_id, new_name, new_department)
                
                if success:
                    # Update the table display
                    self.staff_table.item(row, 1).setText(new_name)
                    self.staff_table.item(row, 2).setText(new_department)
                    QMessageBox.information(self, "Success", "Staff member updated successfully!")
                else:
                    QMessageBox.critical(self, "Error", "Failed to update staff member.")
            else:
                QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
    
    def delete_staff(self, row):
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
                # Remove the row from the table
                self.staff_table.removeRow(row)
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
            # Get attendance records from database
            records = self.db.get_all_attendance()
            
            # Write to CSV file
            try:
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Staff ID', 'Name', 'Department', 'Date', 'Time In', 'Time Out'])  # Header
                    writer.writerows(records)  # Data rows
                
                QMessageBox.information(self, "Export", f"Attendance records exported successfully to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export records: {str(e)}")
        else:
            QMessageBox.information(self, "Export", "Export cancelled")