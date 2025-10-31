"""
Export Data widget for exporting attendance records
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QTableWidget, 
    QTableWidgetItem, QTabWidget, QFormLayout, QGroupBox, QHeaderView, QFileDialog, QDialog, QMessageBox, QDateEdit, QComboBox, QCheckBox
)
from PySide6.QtCore import Qt, QDate
from database import DatabaseManager
import csv


class ExportWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
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
        
        self.setLayout(layout)
    
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