"""
Main window for the attendance system
"""

from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QStackedWidget, QMenuBar
)
from PySide6.QtCore import Qt
from .attendance_widget import AttendanceWidget
from .admin_widget import AdminWidget


class AttendanceMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SEC(NYSC) Attendance System")
        self.setGeometry(100, 100, 800, 600)
        
        # Set blue and white color theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
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
        admin_action.triggered.connect(self.show_admin_panel)
        
        attendance_action = admin_menu.addAction("Attendance View")
        attendance_action.triggered.connect(self.show_attendance_view)
    
    def show_admin_panel(self):
        self.stacked_widget.setCurrentWidget(self.admin_widget)
        self.setWindowTitle("SEC(NYSC) Attendance System - Admin Panel")
    
    def show_attendance_view(self):
        self.stacked_widget.setCurrentWidget(self.attendance_widget)
        self.setWindowTitle("SEC(NYSC) Attendance System")