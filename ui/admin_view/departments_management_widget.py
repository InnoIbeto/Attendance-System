"""
Departments Management widget for managing departments
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QTableWidget, 
    QTableWidgetItem, QTabWidget, QFormLayout, QGroupBox, QHeaderView, QFileDialog, QDialog, QMessageBox, QDateEdit, QComboBox
)
from PySide6.QtCore import Qt, QDate
from database import DatabaseManager
import sqlite3


class DepartmentsManagementWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
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
        self.dept_table.setColumnCount(5)  # ID, Name, Description, Edit, Delete
        self.dept_table.setHorizontalHeaderLabels(["ID", "Name", "Description", "Edit", "Delete"])
        self.dept_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #3B82F6;  /* Light blue */
                alternate-background-color: #F0F9FF;  /* Very light blue */
                selection-background-color: #BAE6FD;  /* Lighter blue for selected items */
                color: black;  /* Black text for table data */
            }
            QHeaderView::section {
                background-color: #1E3A8A;  /* Dark blue */
                color: white;
                padding: 4px;
                border: 1px solid #3B82F6;  /* Light blue */
            }
        """)
        
        # Department table sizing - Proportional column sizing (ID smallest, Name largest, Description 1/2 of name, Edit/Delete fixed)
        header = self.dept_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # Proportional resizing
        self.dept_table.setColumnWidth(0, 80)   # ID (smallest)
        self.dept_table.setColumnWidth(1, 200)  # Name (largest)
        self.dept_table.setColumnWidth(2, 150)  # Description (1/2 of name)
        self.dept_table.setColumnWidth(3, 80)   # Edit button (fixed width)
        self.dept_table.setColumnWidth(4, 80)   # Delete button (fixed width)
        
        departments_label = QLabel("Departments")
        departments_label.setAlignment(Qt.AlignCenter)
        departments_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0px 5px 0px; color: #0F172A;")
        layout.addWidget(departments_label)
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
        
        self.setLayout(layout)
        
        # Load initial departments
        self.refresh_departments()
    
    def add_department(self):
        """Add a new department"""
        name = self.dept_name_input.text().strip()
        description = self.dept_description_input.text().strip()
        
        if not name:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Input Error", "Department name cannot be empty!")
            return
            
        # Check if department already exists
        existing_depts = self.db.get_all_departments()
        for dept_id, dept_name, dept_desc in existing_depts:
            if dept_name.lower() == name.lower():
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Error", f"Department '{name}' already exists!")
                return
        
        success = self.db.add_department(name, description)
        if success:
            self.dept_name_input.clear()
            self.dept_description_input.clear()
            
            # Refresh the department list
            self.refresh_departments()
            
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Success", f"Department '{name}' added successfully!")
        else:
            from PySide6.QtWidgets import QMessageBox
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
            self.dept_table.setCellWidget(row_idx, 3, edit_btn)
            
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
            self.dept_table.setCellWidget(row_idx, 4, delete_btn)

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
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", "Department not found!")
            return
        
        dept_id, current_name, current_description = dept_info
        
        # Create dialog for editing
        from PySide6.QtWidgets import QDialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Department")
        dialog.setModal(True)
        dialog.resize(300, 150)
        
        from PySide6.QtWidgets import QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QLabel, QVBoxLayout
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
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Input Error", "Department name cannot be empty!")
                return
            
            # Check if department name already exists (excluding this department)
            existing_depts = self.db.get_all_departments()
            for existing_id, existing_name, _ in existing_depts:
                if existing_name.lower() == new_name.lower() and existing_id != dept_id:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Error", f"Department '{new_name}' already exists!")
                    return
            
            success = self.db.update_department(dept_id, new_name, new_description)
            if success:
                # Refresh the department list
                self.refresh_departments()
                
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Success", "Department updated successfully!")
            else:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", "Failed to update department.")
    
    def delete_department(self, dept_id):
        """Delete a department"""
        # Get department info to show in confirmation
        dept_info = self.db.get_department_by_id(dept_id)
        if not dept_info:
            from PySide6.QtWidgets import QMessageBox
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
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self, 
                "Cannot Delete", 
                f"Cannot delete department '{dept_name}' because {staff_count} staff member(s) are assigned to it.\n"
                f"Please reassign these staff members to other departments first."
            )
            return
        
        # Confirm deletion
        from PySide6.QtWidgets import QMessageBox
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
                # Refresh the department list
                self.refresh_departments()
                
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Success", f"Department '{dept_name}' deleted successfully!")
            else:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", "Failed to delete department.")