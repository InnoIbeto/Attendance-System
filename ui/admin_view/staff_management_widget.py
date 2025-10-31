"""
Staff Management widget for managing staff registration and records
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QTableWidget, 
    QTableWidgetItem, QTabWidget, QFormLayout, QGroupBox, QHeaderView, QFileDialog, QDialog, QMessageBox
)
from PySide6.QtCore import Qt
from database import DatabaseManager


class StaffManagementWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
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
        
        self.setLayout(layout)
        
        # Load initial staff data
        self.refresh_staff()

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
                self.staff_id_input.clear()
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
        
        # Update pagination button states after populating data
        self.staff_prev_button.setEnabled(self.staff_current_page > 1)
        self.staff_next_button.setEnabled(self.staff_current_page < self.staff_total_pages)

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