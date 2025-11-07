"""
Dashboard widget showing key metrics for the attendance system
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame, QGridLayout, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database import DatabaseManager
from datetime import datetime


class MetricCard(QFrame):
    """Custom card widget for displaying metrics"""
    def __init__(self, title, count, description, color="#3B82F6"):
        super().__init__()
        
        # Set basic styling without complex CSS that might cause rendering issues
        self.setFixedSize(220, 150)
        self.setCursor(Qt.PointingHandCursor)
        
        # Set frame styling
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 8px;
            }}
        """)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Create title label
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(f"color: #0F172A; font-size: 16px; font-weight: bold;")
        self.title_label.setWordWrap(True)
        
        # Create count label
        self.count_label = QLabel(str(count))
        self.count_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(28)
        font.setBold(True)
        self.count_label.setFont(font)
        self.count_label.setStyleSheet(f"color: {color};")
        
        # Create description label
        self.desc_label = QLabel(description)
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.desc_label.setStyleSheet("color: #0F172A; font-size: 12px;")
        self.desc_label.setWordWrap(True)
        
        # Add widgets to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.count_label)
        layout.addWidget(self.desc_label)
        
        # Add stretch to push content up
        layout.addStretch()
        
        self.setLayout(layout)
    
    def update_count(self, new_count):
        """Update the count displayed on the card"""
        self.count_label.setText(str(new_count))


class DashboardWidget(QWidget):
    def __init__(self, admin_widget_instance):
        super().__init__()
        self.db = DatabaseManager()
        self.admin_widget = admin_widget_instance
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Dashboard title
        title_label = QLabel("Attendance Dashboard")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            margin: 15px 10px 25px 10px; 
            color: #0F172A;
            border-bottom: 2px solid #3B82F6;
            padding-bottom: 10px;
        """)
        layout.addWidget(title_label)
        
        # Create metrics cards
        metrics_layout = QGridLayout()
        metrics_layout.setSpacing(20)
        
        # Total Staff Card
        self.total_staff_card = MetricCard(
            "Total Staff",
            self.get_total_staff_count(),
            "Click to view all staff",
            color="#3B82F6"
        )
        
        # Staff Late Today Card
        self.late_staff_card = MetricCard(
            "Staff Late Today", 
            self.get_late_staff_count_today(),
            "Click to view today's late arrivals",
            color="#3B82F6"
        )
        
        # Total Departments Card
        self.total_depts_card = MetricCard(
            "Total Departments",
            self.get_total_departments_count(),
            "Click to manage departments",
            color="#3B82F6"
        )
        
        # Connect click events if admin_widget_instance is provided
        if self.admin_widget:
            self.total_staff_card.mousePressEvent = lambda event: self.go_to_departments_overview()
            self.late_staff_card.mousePressEvent = lambda event: self.go_to_late_attendance()
            self.total_depts_card.mousePressEvent = lambda event: self.go_to_manage_departments()
        
        # Add cards to grid
        metrics_layout.addWidget(self.total_staff_card, 0, 0, Qt.AlignCenter)
        metrics_layout.addWidget(self.late_staff_card, 0, 1, Qt.AlignCenter)
        metrics_layout.addWidget(self.total_depts_card, 0, 2, Qt.AlignCenter)
        
        layout.addLayout(metrics_layout)
        
        # Add a refresh button
        refresh_button = QPushButton("Refresh Metrics")
        refresh_button.clicked.connect(self.refresh_metrics)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                margin-top: 30px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        refresh_button.setMaximumWidth(150)
        layout.addWidget(refresh_button, alignment=Qt.AlignCenter)
        
        layout.addStretch()  # Push everything up
        
        self.setLayout(layout)
    
    def get_total_staff_count(self):
        """Get total number of staff in the system"""
        return self.db.get_total_staff_count()
    
    def get_late_staff_count_today(self):
        """Get number of staff who were late today"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get all attendance records for today
        records = self.db.get_all_attendance(date_from=today, date_to=today)
        
        # Count late arrivals (after 8:30 AM)
        late_count = 0
        late_time = "08:30:00"
        
        for record in records:
            time_in = record[4]  # Time in is at index 4
            if time_in and time_in > late_time:
                late_count += 1
        
        return late_count
    
    def get_total_departments_count(self):
        """Get total number of departments"""
        return self.db.get_total_departments_count()
    
    def refresh_metrics(self):
        """Refresh all metric values"""
        self.total_staff_card.update_count(self.get_total_staff_count())
        self.late_staff_card.update_count(self.get_late_staff_count_today())
        self.total_depts_card.update_count(self.get_total_departments_count())
    
    def go_to_departments_overview(self):
        """Navigate to departments overview page"""
        self.admin_widget.show_widget("Departments Overview")
    
    def go_to_late_attendance(self):
        """Navigate to attendance records with late filter activated"""
        if self.admin_widget:
            self.admin_widget.show_attendance_records_for_today_with_late_filter()
    
    def go_to_manage_departments(self):
        """Navigate to manage departments page"""
        self.admin_widget.show_widget("Manage Departments")