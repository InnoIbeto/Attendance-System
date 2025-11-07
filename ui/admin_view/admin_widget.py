"""
Admin widget for managing staff and viewing attendance
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QScrollArea, QGroupBox
)
from PySide6.QtCore import Qt
from ui.admin_view.staff_management_widget import StaffManagementWidget
from ui.admin_view.attendance_records_widget import AttendanceRecordsWidget
from ui.admin_view.departments_management_widget import DepartmentsManagementWidget
from ui.admin_view.export_widget import ExportWidget
from .lateness_report_widget import LatenessReportWidget
from .department_widget import DepartmentWidget
from .dashboard_widget import DashboardWidget


class SidebarButton(QPushButton):
    """Custom button for sidebar navigation"""
    def __init__(self, text):
        super().__init__(text)
        self.setFixedHeight(40)
        self.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: 1px solid #1E3A8A;
                border-radius: 5px;
                padding: 6px 2px;  /* Much reduced horizontal padding */
                text-align: center;  /* Centered text */
                font-weight: bold;
                font-size: 14px;   /* Increased font size */
                margin: 2px 1px;   /* Minimal margins */
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
            QPushButton:checked {
                background-color: #0F172A;
                color: white;
            }
        """)


class AdminWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_widget = None
        self.init_ui()
    
    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create sidebar
        sidebar = self.create_sidebar()
        sidebar.setFixedWidth(270)  # Standard width
        
        # Create content area
        self.content_area = QFrame()
        self.content_area.setFrameShape(QFrame.NoFrame)
        self.content_area.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #1E3A8A;
                border-radius: 5px;
                padding: 0px;
            }
        """)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        self.content_area.setLayout(content_layout)
        
        # Add sidebar and content area to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_area, 1)  # Main content takes remaining space
        
        self.setLayout(main_layout)
        
        # Show the dashboard by default
        self.show_dashboard()

    def create_sidebar(self):
        # Create sidebar container
        sidebar = QFrame()
        sidebar.setFrameShape(QFrame.NoFrame)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #1E3A8A;  /* Dark blue background */
                border-radius: 5px;
                min-width: 270px;
                max-width: 270px;
            }
        """)
        
        # Create scroll area for the sidebar
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1E3A8A;  /* Dark blue background to match sidebar */
            }
            QScrollBar:vertical {
                background: #E2E8F0;
                width: 12px;
                border-radius: 5px;
                margin: 10px 0px 10px 0px;
            }
            QScrollBar::handle:vertical {
                background: #94A3B8;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #64748B;
            }
        """)
        
        # Create scroll content widget
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #1E3A8A;")  # Dark blue background to match sidebar
        scroll_content.setFixedWidth(260)  # Explicitly set content width to prevent overflow
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(3, 10, 3, 10)  # Further reduced side margins to 3px
        sidebar_layout.setSpacing(8)  # Further reduced spacing between sections to 8px
        
        # Title for sidebar - aligned with other elements
        sidebar_title = QLabel("ADMIN PANEL")
        sidebar_title.setAlignment(Qt.AlignCenter)
        sidebar_title.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            color: white; 
            margin-top: 1ex;
            padding-top: 5px;  
            margin-bottom: 1ex;
            padding-bottom: 5px;
            /* background-color: #1E3A8A;   Match sidebar background */
        """)
        # Removed fixed width constraints to allow proper layout
        sidebar_layout.addWidget(sidebar_title)
        
        # Staff Management Section
        staff_group = QGroupBox("Staff Management")
        staff_group.setFlat(True)  # Remove frame for more compact appearance
        staff_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: white;
                margin-top: 1ex;
                padding-top: 5px;   /* Reduced padding */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 2px;    /* Reduced padding */
                color: white;
                font-weight: bold;
            }
        """)
        staff_layout = QVBoxLayout()
        staff_btn = SidebarButton("Manage Staff")
        staff_btn.clicked.connect(lambda: self.show_widget("Manage Staff"))
        staff_layout.addWidget(staff_btn)
        staff_group.setLayout(staff_layout)
        sidebar_layout.addWidget(staff_group)
        
        # Attendance Section
        attendance_group = QGroupBox("Attendance")
        attendance_group.setFlat(True)  # Remove frame for more compact appearance
        attendance_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: white;
                margin-top: 1ex;
                padding-top: 5px;   /* Reduced padding */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 2px;    /* Reduced padding */
                color: white;
                font-weight: bold;
            }
        """)
        attendance_layout = QVBoxLayout()
        attendance_records_btn = SidebarButton("Attendance Records")
        attendance_records_btn.clicked.connect(lambda: self.show_widget("Attendance Records"))
        lateness_report_btn = SidebarButton("Lateness Report")
        lateness_report_btn.clicked.connect(lambda: self.show_widget("Lateness Report"))
        
        attendance_layout.addWidget(attendance_records_btn)
        attendance_layout.addWidget(lateness_report_btn)
        attendance_group.setLayout(attendance_layout)
        sidebar_layout.addWidget(attendance_group)
        
        # Department Section
        dept_group = QGroupBox("Departments")
        dept_group.setFlat(True)  # Remove frame for more compact appearance
        dept_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: white;
                margin-top: 1ex;
                padding-top: 5px;   /* Reduced padding */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 2px;    /* Reduced padding */
                color: white;
                font-weight: bold;
            }
        """)
        dept_layout = QVBoxLayout()
        dept_management_btn = SidebarButton("Manage Departments")
        dept_management_btn.clicked.connect(lambda: self.show_widget("Manage Departments"))
        dept_overview_btn = SidebarButton("Departments Overview")
        dept_overview_btn.clicked.connect(lambda: self.show_widget("Departments Overview"))
        
        dept_layout.addWidget(dept_management_btn)
        dept_layout.addWidget(dept_overview_btn)
        dept_group.setLayout(dept_layout)
        sidebar_layout.addWidget(dept_group)
        
        # Data Management Section
        data_group = QGroupBox("Data Management")
        data_group.setFlat(True)  # Remove frame for more compact appearance
        data_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: white;
                margin-top: 1ex;
                padding-top: 5px;   /* Reduced padding */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 2px;    /* Reduced padding */
                color: white;
                font-weight: bold;
            }
        """)
        data_layout = QVBoxLayout()
        export_btn = SidebarButton("Export Data")
        export_btn.clicked.connect(lambda: self.show_widget("Export Data"))
        
        data_layout.addWidget(export_btn)
        data_group.setLayout(data_layout)
        sidebar_layout.addWidget(data_group)
        
        # Add stretch to push content up
        sidebar_layout.addStretch()
        
        scroll_content.setLayout(sidebar_layout)
        scroll_area.setWidget(scroll_content)  # Ensure the scroll area properly contains the content
        
        # Add scroll area to sidebar frame
        sidebar_layout_final = QVBoxLayout()
        sidebar_layout_final.addWidget(scroll_area)
        sidebar.setLayout(sidebar_layout_final)
        
        return sidebar

    def show_dashboard(self):
        # Clear current content
        for i in reversed(range(self.content_area.layout().count())):
            widget = self.content_area.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Create and show the dashboard widget
        widget = DashboardWidget(self)
        
        # Add the widget to the content area
        self.content_area.layout().addWidget(widget)

    def show_widget(self, widget_name, activate_late_filter=False):
        # Clear current content
        for i in reversed(range(self.content_area.layout().count())):
            widget = self.content_area.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Create title (except for dashboard which has its own title)
        if widget_name != "Dashboard":
            title_label = QLabel(f"{widget_name}")
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("""
                font-size: 20px; 
                font-weight: bold; 
                margin: 15px 10px 10px 10px; 
                color: #0F172A;
                border-bottom: 2px solid #3B82F6;
                padding-bottom: 10px;
            """)
            
            self.content_area.layout().addWidget(title_label)
        
        # Create and show the selected widget
        if widget_name == "Manage Staff":
            widget = StaffManagementWidget()
        elif widget_name == "Attendance Records":
            widget = AttendanceRecordsWidget(apply_late_filter=activate_late_filter, 
                                           date_filter_today=activate_late_filter)  # Apply today's date when late filter is activated
        elif widget_name == "Lateness Report":
            widget = LatenessReportWidget()
        elif widget_name == "Manage Departments":
            widget = DepartmentsManagementWidget()
        elif widget_name == "Departments Overview":
            widget = DepartmentWidget()
        elif widget_name == "Export Data":
            widget = ExportWidget()
        elif widget_name == "Dashboard":
            widget = DashboardWidget(self)
        else:
            widget = QLabel(f"Content for {widget_name} would go here")
            widget.setAlignment(Qt.AlignCenter)
        
        # Add the widget to the content area
        self.content_area.layout().addWidget(widget)

    def show_attendance_records_for_today_with_late_filter(self):
        """Show attendance records for today with late arrivals only"""
        from PySide6.QtCore import QDate
        from ui.admin_view.attendance_records_widget import AttendanceRecordsWidget
        # Clear current content
        for i in reversed(range(self.content_area.layout().count())):
            widget = self.content_area.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Create title
        title_label = QLabel("Attendance Records")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            margin: 15px 10px 10px 10px; 
            color: #0F172A;
            border-bottom: 2px solid #3B82F6;
            padding-bottom: 10px;
        """)
        
        self.content_area.layout().addWidget(title_label)
        
        # Create widget with both filters
        widget = AttendanceRecordsWidget(apply_late_filter=True, date_filter_today=True)
        
        # Add the widget to the content area
        self.content_area.layout().addWidget(widget)