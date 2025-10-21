"""
Lateness report widget for displaying staff late attendance
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QTableWidget, 
    QTableWidgetItem, QTabWidget, QFormLayout, QGroupBox, QHeaderView, 
    QDateEdit, QMessageBox
)
from PySide6.QtCore import Qt
from database import DatabaseManager
from datetime import datetime


class LatenessReportWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Lateness Report")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px; color: #0F172A;")
        layout.addWidget(title_label)
        
        # Report parameters form
        params_group = QGroupBox("Report Parameters")
        params_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #1E3A8A;
                border-radius: 5px;
                margin: 10px 0px;
                padding-top: 15px;
                color: #0F172A;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: #0F172A;
                font-weight: bold;
            }
        """)
        params_layout = QHBoxLayout()
        
        # Month and Year selection
        month_year_layout = QVBoxLayout()
        
        month_year_label = QLabel("Select Month/Year:")
        month_year_label.setStyleSheet("color: #0F172A; font-weight: bold;")
        month_year_layout.addWidget(month_year_label)
        
        # Use QDateEdit to select month/year
        self.month_selector = QDateEdit()
        self.month_selector.setDate(datetime.now().date())
        self.month_selector.setDisplayFormat("MMMM yyyy")
        self.month_selector.setCalendarPopup(True)
        self.month_selector.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 1px solid #3B82F6;
                border-radius: 4px;
                color: #0F172A;
                background-color: white;
            }
            QDateEdit:focus {
                border: 2px solid #1E3A8A;
            }
        """)
        month_year_layout.addWidget(self.month_selector)
        
        params_layout.addLayout(month_year_layout)
        
        # Minimum late count selection
        min_late_layout = QVBoxLayout()
        
        min_late_label = QLabel("Minimum Late Count:")
        min_late_label.setStyleSheet("color: #0F172A; font-weight: bold;")
        min_late_layout.addWidget(min_late_label)
        
        self.min_late_input = QLineEdit("1")
        self.min_late_input.setPlaceholderText("e.g., 1 or 3")
        self.min_late_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #3B82F6;
                border-radius: 4px;
                color: #0F172A;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #1E3A8A;
            }
        """)
        min_late_layout.addWidget(self.min_late_input)
        
        params_layout.addLayout(min_late_layout)
        
        # Generate button
        generate_button = QPushButton("Generate Report")
        generate_button.clicked.connect(self.generate_report)
        generate_button.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        
        right_layout = QVBoxLayout()
        right_layout.addWidget(generate_button)
        right_layout.addStretch()  # Push button to top
        
        params_layout.addLayout(right_layout)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Staff ID", "Name", "Department", "Late Arrivals"])
        self.results_table.setStyleSheet("""
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
        
        # Set column widths
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Staff ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Department
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Late Arrivals
        
        layout.addWidget(QLabel("Lateness Report Results"))
        layout.addWidget(self.results_table)
        
        self.setLayout(layout)
    
    def generate_report(self):
        """Generate the lateness report based on selected parameters"""
        try:
            # Get selected month and year
            selected_date = self.month_selector.date()
            year = selected_date.year()
            month = selected_date.month()
            
            # Get minimum late count
            try:
                min_late_count = int(self.min_late_input.text().strip())
                if min_late_count < 1:
                    min_late_count = 1
            except ValueError:
                min_late_count = 1
                self.min_late_input.setText("1")
            
            # Get the lateness data from database
            late_staff = self.db.get_staff_with_late_attendance(year, month, min_late_count)
            
            # Clear existing data in table
            self.results_table.setRowCount(0)
            
            if late_staff:
                for row_idx, (staff_id, name, department, late_count) in enumerate(late_staff):
                    self.results_table.insertRow(row_idx)
                    
                    # Add staff ID
                    id_item = QTableWidgetItem(staff_id)
                    id_item.setTextAlignment(Qt.AlignCenter)
                    self.results_table.setItem(row_idx, 0, id_item)
                    
                    # Add name
                    name_item = QTableWidgetItem(name)
                    name_item.setTextAlignment(Qt.AlignCenter)
                    self.results_table.setItem(row_idx, 1, name_item)
                    
                    # Add department
                    dept_item = QTableWidgetItem(department)
                    dept_item.setTextAlignment(Qt.AlignCenter)
                    self.results_table.setItem(row_idx, 2, dept_item)
                    
                    # Add late count
                    count_item = QTableWidgetItem(str(late_count))
                    count_item.setTextAlignment(Qt.AlignCenter)
                    self.results_table.setItem(row_idx, 3, count_item)
                
                # Connect the table to show details when a row is double-clicked
                # Set up connection only once to avoid multiple connections
                if not hasattr(self, '_table_connected') or not self._table_connected:
                    # If we haven't connected before, just connect
                    self.results_table.cellDoubleClicked.connect(self.show_detailed_report)
                    self._table_connected = True
                else:
                    # If already connected, just refresh the data without reconnection
                    pass  # The connection is already in place
            else:
                # Show message if no late staff found
                self.results_table.setRowCount(1)
                for col in range(4):
                    item = QTableWidgetItem("No staff found with late arrivals matching criteria")
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
                    self.results_table.setItem(0, col, item)
                
                # Span the message across all columns
                self.results_table.setSpan(0, 0, 1, 4)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while generating the report: {str(e)}")
    
    def show_detailed_report(self, row, column):
        """Show detailed late attendance for the selected staff member"""
        try:
            # Get the staff ID from the selected row
            staff_id_item = self.results_table.item(row, 0)
            if staff_id_item:
                staff_id = staff_id_item.text()
                
                # Get selected month and year
                selected_date = self.month_selector.date()
                year = selected_date.year()
                month = selected_date.month()
                
                # Show detailed report
                self.show_detailed_late_attendance(staff_id, year, month)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while showing details: {str(e)}")
    
    def show_detailed_late_attendance(self, staff_id, year, month):
        """Show detailed late attendance for a specific staff member"""
        details = self.db.get_late_attendance_details(staff_id, year, month)
        
        if details:
            # Create a dialog to show the details
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Detailed Late Attendance - {staff_id}")
            dialog.resize(800, 400)
            
            layout = QVBoxLayout()
            
            # Create details table
            details_table = QTableWidget()
            details_table.setColumnCount(5)
            details_table.setHorizontalHeaderLabels(["Date", "Time In", "Minutes Late", "Department", "Name"])
            details_table.setStyleSheet("""
                QTableWidget {
                    border: 1px solid #3B82F6;
                }
                QHeaderView::section {
                    background-color: #1E3A8A;
                    color: white;
                    padding: 4px;
                }
            """)
            
            for row_idx, (s_id, name, dept, date, time_in, minutes_late) in enumerate(details):
                details_table.insertRow(row_idx)
                
                # Add date
                date_item = QTableWidgetItem(date)
                date_item.setTextAlignment(Qt.AlignCenter)
                details_table.setItem(row_idx, 0, date_item)
                
                # Add time in
                time_item = QTableWidgetItem(time_in)
                time_item.setTextAlignment(Qt.AlignCenter)
                details_table.setItem(row_idx, 1, time_item)
                
                # Add minutes late
                late_item = QTableWidgetItem(str(minutes_late))
                late_item.setTextAlignment(Qt.AlignCenter)
                details_table.setItem(row_idx, 2, late_item)
                
                # Add department
                dept_item = QTableWidgetItem(dept)
                dept_item.setTextAlignment(Qt.AlignCenter)
                details_table.setItem(row_idx, 3, dept_item)
                
                # Add name
                name_item = QTableWidgetItem(name)
                name_item.setTextAlignment(Qt.AlignCenter)
                details_table.setItem(row_idx, 4, name_item)
            
            # Make columns resizable
            header = details_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Time In
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Minutes Late
            header.setSectionResizeMode(3, QHeaderView.Stretch)  # Department
            header.setSectionResizeMode(4, QHeaderView.Stretch)  # Name
            
            layout.addWidget(details_table)
            
            # Add close button
            close_button = QPushButton("Close")
            close_button.clicked.connect(dialog.close)
            close_button.setStyleSheet("""
                QPushButton {
                    background-color: #3B82F6;
                    color: white;
                    border: none;
                    padding: 8px;
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
            
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(close_button)
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            dialog.exec()
        else:
            QMessageBox.information(self, "No Details", f"No late attendance details found for {staff_id} in the selected period.")
    
    def show_late_details(self, staff_id, year, month):
        """Show detailed late attendance for a specific staff member"""
        details = self.db.get_late_attendance_details(staff_id, year, month)
        
        if details:
            # Create a dialog to show the details
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Late Attendance Details - {staff_id}")
            dialog.resize(700, 400)
            
            layout = QVBoxLayout()
            
            # Create details table
            details_table = QTableWidget()
            details_table.setColumnCount(5)
            details_table.setHorizontalHeaderLabels(["Date", "Time In", "Minutes Late", "Department", "Name"])
            details_table.setStyleSheet("""
                QTableWidget {
                    border: 1px solid #3B82F6;
                }
                QHeaderView::section {
                    background-color: #1E3A8A;
                    color: white;
                    padding: 4px;
                }
            """)
            
            for row_idx, (s_id, name, dept, date, time_in, minutes_late) in enumerate(details):
                details_table.insertRow(row_idx)
                
                # Add date
                date_item = QTableWidgetItem(date)
                date_item.setTextAlignment(Qt.AlignCenter)
                details_table.setItem(row_idx, 0, date_item)
                
                # Add time in
                time_item = QTableWidgetItem(time_in)
                time_item.setTextAlignment(Qt.AlignCenter)
                details_table.setItem(row_idx, 1, time_item)
                
                # Add minutes late
                late_item = QTableWidgetItem(str(minutes_late))
                late_item.setTextAlignment(Qt.AlignCenter)
                details_table.setItem(row_idx, 2, late_item)
                
                # Add department
                dept_item = QTableWidgetItem(dept)
                dept_item.setTextAlignment(Qt.AlignCenter)
                details_table.setItem(row_idx, 3, dept_item)
                
                # Add name
                name_item = QTableWidgetItem(name)
                name_item.setTextAlignment(Qt.AlignCenter)
                details_table.setItem(row_idx, 4, name_item)
            
            # Make columns resizable
            header = details_table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)
            
            layout.addWidget(details_table)
            dialog.setLayout(layout)
            dialog.exec()