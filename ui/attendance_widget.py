"""
Attendance widget for staff to log attendance
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from database import DatabaseManager
from datetime import datetime


class AttendanceWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("SEC(NYSC) Attendance System")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px; color: #1E3A8A;")  # Dark blue
        layout.addWidget(title_label)
        
        # Create a group box for attendance input
        attendance_group = QGroupBox("Log Attendance")
        attendance_group.setStyleSheet("""
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
        attendance_layout = QVBoxLayout()
        
        # Staff ID input
        id_layout = QHBoxLayout()
        id_label = QLabel("Staff ID:")
        id_label.setStyleSheet("color: #1E3A8A;")  # Dark blue
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter your staff ID")
        self.id_input.setStyleSheet("""
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
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.id_input)
        attendance_layout.addLayout(id_layout)
        
        # Or fingerprint option
        fingerprint_label = QLabel("Or use fingerprint scanner")
        fingerprint_label.setAlignment(Qt.AlignCenter)
        fingerprint_label.setStyleSheet("color: #1E3A8A;")  # Dark blue
        attendance_layout.addWidget(fingerprint_label)
        
        # Submit button
        self.submit_button = QPushButton("Log Attendance")
        self.submit_button.clicked.connect(self.log_attendance)
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;  /* Light blue */
                color: white;
                border: none;
                padding: 10px;
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
        attendance_layout.addWidget(self.submit_button)
        
        # Feedback message
        self.feedback_label = QLabel()
        self.feedback_label.setAlignment(Qt.AlignCenter)
        self.feedback_label.setStyleSheet("color: green; font-weight: bold; margin: 10px;")
        attendance_layout.addWidget(self.feedback_label)
        
        attendance_group.setLayout(attendance_layout)
        layout.addWidget(attendance_group)
        
        # Set the layout
        self.setLayout(layout)
    
    def log_attendance(self):
        staff_id = self.id_input.text().strip()
        
        if not staff_id:
            QMessageBox.warning(self, "Input Error", "Please enter your staff ID")
            return
        
        # Get current time to check for late arrival
        now = datetime.now()
        current_time = now.time()
        late_arrival_time = datetime.strptime("08:30", "%H:%M").time()
        
        # Try to log attendance in the database - returns the action type (Sign In/Sign Out)
        action = self.db.log_attendance(staff_id)
        
        if action:
            # Get staff information
            staff_info = self.db.get_staff(staff_id)
            if staff_info:
                staff_name = staff_info[1]  # Name is the second element in the tuple
                
                if action == "Sign In":
                    if current_time > late_arrival_time:
                        # Late arrival after 8:30am
                        minutes_late = (datetime.combine(now.date(), current_time) - 
                                        datetime.combine(now.date(), late_arrival_time)).seconds // 60
                        feedback_text = f"{staff_name}, you are {minutes_late} minutes late"
                        self.feedback_label.setStyleSheet("color: orange; font-weight: bold; margin: 10px;")
                    else:
                        # On-time arrival
                        feedback_text = f"{staff_name}, you have successfully signed in, have a nice day!"
                        self.feedback_label.setStyleSheet("color: green; font-weight: bold; margin: 10px;")
                else:  # Sign Out
                    feedback_text = f"{staff_name}, signed out successfully, bye!"
                    self.feedback_label.setStyleSheet("color: green; font-weight: bold; margin: 10px;")
            else:
                feedback_text = "Attendance logged successfully!\nHave a nice day at work!"
                self.feedback_label.setStyleSheet("color: green; font-weight: bold; margin: 10px;")
        else:
            # Staff ID doesn't exist in the database
            feedback_text = "Invalid staff ID. Please check and try again."
            self.feedback_label.setStyleSheet("color: red; font-weight: bold; margin: 10px;")
        
        self.feedback_label.setText(feedback_text)
        
        # Clear the input field
        self.id_input.clear()
        
        # Clear the feedback message after 5 seconds
        QTimer.singleShot(5000, self.clear_feedback_message)
    
    def clear_feedback_message(self):
        """Clear the feedback message after a delay"""
        self.feedback_label.setText("")