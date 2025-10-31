"""
Admin widget for managing staff and viewing attendance
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt
from ui.admin_view.staff_management_widget import StaffManagementWidget
from ui.admin_view.attendance_records_widget import AttendanceRecordsWidget
from ui.admin_view.departments_management_widget import DepartmentsManagementWidget
from ui.admin_view.export_widget import ExportWidget
from .lateness_report_widget import LatenessReportWidget
from .department_widget import DepartmentWidget


class AdminWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Admin Panel")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px; color: #0F172A;")  # Dark blue-gray for better contrast
        layout.addWidget(title_label)
        
        # Create tab widget for different admin functions
        from PySide6.QtWidgets import QTabWidget
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
        staff_widget = StaffManagementWidget()
        tab_widget.addTab(staff_widget, "Manage Staff")
        
        # Departments tab
        dept_widget = DepartmentsManagementWidget()
        tab_widget.addTab(dept_widget, "Manage Departments")
        
        # Attendance records tab
        attendance_widget = AttendanceRecordsWidget()
        tab_widget.addTab(attendance_widget, "Attendance Records")
        
        # Lateness Report tab
        lateness_report_widget = LatenessReportWidget()
        tab_widget.addTab(lateness_report_widget, "Lateness Report")
        
        # Department View tab
        department_widget = DepartmentWidget()
        tab_widget.addTab(department_widget, "Departments Overview")
        
        # Export tab
        export_widget = ExportWidget()
        tab_widget.addTab(export_widget, "Export Data")
        
        layout.addWidget(tab_widget)
        self.setLayout(layout)