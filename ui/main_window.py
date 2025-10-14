"""
Main window for the attendance system
"""

import os
import hashlib
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QStackedWidget, QMenuBar,
    QMessageBox, QLineEdit, QDialog, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt
from .attendance_widget import AttendanceWidget
from .admin_widget import AdminWidget


class AttendanceMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SEC(NYSC) Attendance System")
        self.setGeometry(100, 100, 800, 600)
        
        # Set blue and white color theme with improved contrast
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QLabel {
                color: #0F172A;  /* Darker blue-gray for better contrast */
                font-weight: bold;
            }
            QMenuBar {
                background-color: #1E3A8A;  /* Dark blue */
                color: white;
            }
            QMenuBar::item {
                background: transparent;
                color: white;
            }
            QMenuBar::item:selected {
                background: #3B82F6;  /* Light blue */
            }
            QMenuBar::item:pressed {
                background: #2563EB;  /* Medium blue */
            }
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
        
        # Create a stacked widget to switch between attendance and admin views
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create the attendance and admin widgets
        self.attendance_widget = AttendanceWidget()
        self.admin_widget = AdminWidget()
        
        # Add widgets to the stacked widget
        self.stacked_widget.addWidget(self.attendance_widget)
        self.stacked_widget.addWidget(self.admin_widget)
        
        # Initially show the attendance widget
        self.stacked_widget.setCurrentWidget(self.attendance_widget)
        
        # Create menu bar
        self.create_menu_bar()
    
    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # Admin menu
        admin_menu = menu_bar.addMenu("Admin")
        
        # Add actions to switch between views
        admin_action = admin_menu.addAction("Admin Panel")
        admin_action.triggered.connect(self.request_password)
        
        attendance_action = admin_menu.addAction("Attendance View")
        attendance_action.triggered.connect(self.show_attendance_view)
        
        # Add Password Change action
        change_password_action = admin_menu.addAction("Change Password")
        change_password_action.triggered.connect(self.change_password)
    
    def get_password_hash(self):
        # Get the password hash from the file, or create a default one
        password_file = "admin_password.txt"
        if os.path.exists(password_file):
            with open(password_file, 'r') as f:
                return f.read().strip()
        else:
            # Create a default password hash: admin -> 'admin' (initial password)
            default_hash = hashlib.sha256("admin".encode()).hexdigest()
            with open(password_file, 'w') as f:
                f.write(default_hash)
            return default_hash

    def verify_password(self, password):
        password_hash = self.get_password_hash()
        input_hash = hashlib.sha256(password.encode()).hexdigest()
        return input_hash == password_hash

    def set_new_password(self, new_password):
        password_file = "admin_password.txt"
        new_hash = hashlib.sha256(new_password.encode()).hexdigest()
        with open(password_file, 'w') as f:
            f.write(new_hash)

    def request_password(self):
        # Create a dialog to request password
        dialog = QDialog(self)
        dialog.setWindowTitle("Admin Panel - Password Required")
        dialog.setModal(True)
        dialog.resize(300, 150)

        layout = QVBoxLayout()

        label = QLabel("Please enter the admin password:")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_input)

        button_layout = QHBoxLayout()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.Accepted:
            password = password_input.text()
            
            # Check if password is correct
            if self.verify_password(password):
                self.show_admin_panel()
            else:
                QMessageBox.warning(self, "Access Denied", "Incorrect password. Access denied.")

    def change_password(self):
        # Create a dialog to change password
        dialog = QDialog(self)
        dialog.setWindowTitle("Change Admin Password")
        dialog.setModal(True)
        dialog.resize(350, 200)

        layout = QVBoxLayout()

        label = QLabel("Enter current password:")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        current_password_input = QLineEdit()
        current_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(current_password_input)

        new_password_label = QLabel("Enter new password:")
        new_password_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(new_password_label)

        new_password_input = QLineEdit()
        new_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(new_password_input)

        confirm_password_label = QLabel("Confirm new password:")
        confirm_password_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(confirm_password_label)

        confirm_password_input = QLineEdit()
        confirm_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(confirm_password_input)

        button_layout = QHBoxLayout()

        ok_button = QPushButton("Change Password")
        ok_button.clicked.connect(dialog.accept)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.Accepted:
            current_password = current_password_input.text()
            new_password = new_password_input.text()
            confirm_password = confirm_password_input.text()
            
            # Verify current password is correct
            if not self.verify_password(current_password):
                QMessageBox.warning(self, "Password Change Failed", "Current password is incorrect.")
                return
            
            # Check if new password and confirmation match
            if new_password != confirm_password:
                QMessageBox.warning(self, "Password Change Failed", "New passwords do not match.")
                return
            
            # Check if new password is empty
            if not new_password:
                QMessageBox.warning(self, "Password Change Failed", "Password cannot be empty.")
                return
            
            # Set the new password
            self.set_new_password(new_password)
            QMessageBox.information(self, "Password Changed", "Admin password has been changed successfully.")

    def show_admin_panel(self):
        self.stacked_widget.setCurrentWidget(self.admin_widget)
        self.setWindowTitle("SEC(NYSC) Attendance System - Admin Panel")
    
    def show_attendance_view(self):
        self.stacked_widget.setCurrentWidget(self.attendance_widget)
        self.setWindowTitle("SEC(NYSC) Attendance System")