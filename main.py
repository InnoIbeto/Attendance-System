"""
Attendance System for NYSC
Entry point of the application
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QLineEdit
from PySide6.QtCore import Qt
from ui.main_window import AttendanceMainWindow


def main():
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = AttendanceMainWindow()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()