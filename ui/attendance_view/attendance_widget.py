"""
Attendance widget for staff to log attendance
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QMessageBox, QGroupBox, QStackedLayout
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QPainter, QColor
from database import DatabaseManager
from datetime import datetime


class BackgroundWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.background_image = QPixmap("images/building.jpg")
        if self.background_image.isNull():
            # Create a default background if image is not found
            self.background_image = QPixmap(800, 200)
            self.background_image.fill(QColor("#E0F2FE"))
        
        self.setMinimumHeight(200)
        self.setMaximumHeight(300)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        # Scale the background to match widget size
        scaled_bg = self.background_image.scaled(
            self.width(), self.height(), 
            Qt.KeepAspectRatioByExpanding, 
            Qt.SmoothTransformation
        )
        painter.drawPixmap(0, 0, scaled_bg)


class AttendanceWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Create background container
        bg_widget = BackgroundWidget()
        bg_layout = QVBoxLayout(bg_widget)
        
        # Create top layout for logo (top-right aligned)
        top_layout = QHBoxLayout()
        top_layout.addStretch()  # Add stretch to push logo to the right
        
        # Add logo to top-right
        logo_label = QLabel()
        logo_pixmap = QPixmap("images/logo.png")
        if not logo_pixmap.isNull():
            logo_pixmap = logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("SEC Logo")
            logo_label.setStyleSheet("color: #1E3A8A; font-weight: bold; font-size: 14px;")
        
        top_layout.addWidget(logo_label)
        bg_layout.addLayout(top_layout)
        
        # Add stretch to vertically center the title
        bg_layout.addStretch()
        
        # Add title in the middle of the background
        title_label = QLabel("SEC(NYSC) Attendance System")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white; margin: 10px;")
        bg_layout.addWidget(title_label)
        
        # Add stretch at the bottom
        bg_layout.addStretch()
        
        layout.addWidget(bg_widget)
        
        # Create a group box for attendance input
        attendance_group = QGroupBox("Log Attendance")
        attendance_group.setStyleSheet("""
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
        attendance_layout = QVBoxLayout()
        
        # Staff ID input
        id_layout = QHBoxLayout()
        id_label = QLabel("Staff ID:")
        id_label.setStyleSheet("color: #0F172A; font-weight: bold;")  # Dark blue-gray for better contrast
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter your staff ID")
        self.id_input.setStyleSheet("""
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
        # Connect Enter key press to log attendance
        self.id_input.returnPressed.connect(self.log_attendance)
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.id_input)
        attendance_layout.addLayout(id_layout)
        
        # Or fingerprint option
        fingerprint_label = QLabel("Or use fingerprint scanner")
        fingerprint_label.setAlignment(Qt.AlignCenter)
        fingerprint_label.setStyleSheet("color: #0F172A; font-weight: bold;")  # Dark blue-gray for better contrast
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
        
        # Try to log attendance in the database - returns the action type (Sign In/Sign Out/Already Signed Out)
        action = self.db.log_attendance(staff_id)
        
        if action:
            if action == "Already Signed Out":
                # Staff has already signed out for the day
                staff_info = self.db.get_staff(staff_id)
                if staff_info:
                    staff_name = staff_info[1]  # Name is the second element in the tuple
                    feedback_text = f"{staff_name}, you have signed out already, contact HR if an error was made"
                    self.feedback_label.setStyleSheet("color: #DC2626; font-weight: bold; margin: 10px;")  # Darker red for better contrast
                else:
                    feedback_text = "You have signed out already, contact HR if an error was made"
                    self.feedback_label.setStyleSheet("color: #DC2626; font-weight: bold; margin: 10px;")  # Darker red for better contrast
            else:
                # Get staff information
                staff_info = self.db.get_staff(staff_id)
                if staff_info:
                    staff_name = staff_info[1]  # Name is the second element in the tuple
                    
                    if action == "Sign In":
                        if current_time > late_arrival_time:
                            # Late arrival after 8:30am
                            total_seconds_late = (datetime.combine(now.date(), current_time) - 
                                            datetime.combine(now.date(), late_arrival_time)).seconds
                            hours_late = total_seconds_late // 3600
                            minutes_late = (total_seconds_late % 3600) // 60
                            
                            if hours_late > 0:
                                if minutes_late > 0:
                                    feedback_text = f"{staff_name}, you are {hours_late} hour(s) and {minutes_late} minute(s) late"
                                else:
                                    feedback_text = f"{staff_name}, you are {hours_late} hour(s) late"
                            else:
                                feedback_text = f"{staff_name}, you are {minutes_late} minute(s) late"
                            
                            self.feedback_label.setStyleSheet("color: #DC2626; font-weight: bold; margin: 10px;")  # Red for being late
                        else:
                            # On-time arrival
                            feedback_text = f"{staff_name}, you have successfully signed in, have a nice day!"
                            self.feedback_label.setStyleSheet("color: #16A34A; font-weight: bold; margin: 10px;")  # Green for success
                    else:  # Sign Out
                        feedback_text = f"{staff_name}, signed out successfully, bye!"
                        self.feedback_label.setStyleSheet("color: #16A34A; font-weight: bold; margin: 10px;")  # Green for success
                else:
                    feedback_text = "Attendance logged successfully!\nHave a nice day at work!"
                    self.feedback_label.setStyleSheet("color: #16A34A; font-weight: bold; margin: 10px;")  # Green for success
        else:
            # Staff ID doesn't exist in the database
            feedback_text = "Invalid staff ID. Please check and try again."
            self.feedback_label.setStyleSheet("color: #DC2626; font-weight: bold; margin: 10px;")  # Darker red for better contrast
        
        self.feedback_label.setText(feedback_text)
        
        # Clear the input field
        self.id_input.clear()
        
        # Clear the feedback message after 5 seconds
        QTimer.singleShot(5000, self.clear_feedback_message)
    
    def clear_feedback_message(self):
        """Clear the feedback message after a delay"""
        self.feedback_label.setText("")