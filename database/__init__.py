"""
Database module for the attendance system using SQLite
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional


class DatabaseManager:
    def __init__(self, db_path: str = "attendance.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create staff table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff (
                staff_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                position TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create attendance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_id TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (staff_id) REFERENCES staff (staff_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_staff(self, staff_id: str, name: str, position: str):
        """Add a new staff member to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO staff (staff_id, name, position) VALUES (?, ?, ?)",
                (staff_id, name, position)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Staff ID already exists
            return False
        finally:
            conn.close()
    
    def get_staff(self, staff_id: str) -> Optional[tuple]:
        """Get staff information by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT staff_id, name, position FROM staff WHERE staff_id = ?", (staff_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result
    
    def log_attendance(self, staff_id: str) -> bool:
        """Log attendance for a staff member - first entry is sign-in, second is sign-out"""
        # Check if staff exists
        staff = self.get_staff(staff_id)
        if not staff:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")
        
        # Check how many attendance records exist for this staff member today
        cursor.execute(
            "SELECT COUNT(*) FROM attendance WHERE staff_id = ? AND date = ?",
            (staff_id, date)
        )
        count = cursor.fetchone()[0]
        
        # Determine if this is a sign-in (first entry) or sign-out (second entry)
        if count == 0:
            # First entry of the day - sign in
            action = "Sign In"
        elif count == 1:
            # Second entry of the day - sign out
            action = "Sign Out"
        else:
            # More than 2 entries - still treat as sign out
            action = "Sign Out"
        
        cursor.execute(
            "INSERT INTO attendance (staff_id, date, time) VALUES (?, ?, ?)",
            (staff_id, date, time)
        )
        
        conn.commit()
        conn.close()
        
        # Return action type for the UI to use
        return action
    
    def get_daily_attendance_count(self, staff_id: str, date: str) -> int:
        """Get the count of attendance records for a staff member on a given date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM attendance WHERE staff_id = ? AND date = ?",
            (staff_id, date)
        )
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def get_all_attendance(self) -> List[tuple]:
        """Get all attendance records"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.staff_id, s.name, a.date, a.time
            FROM attendance a
            LEFT JOIN staff s ON a.staff_id = s.staff_id
            ORDER BY a.timestamp DESC
        ''')
        results = cursor.fetchall()
        
        conn.close()
        return results
    
    def get_all_staff(self) -> List[tuple]:
        """Get all staff members"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT staff_id, name, position FROM staff ORDER BY name")
        results = cursor.fetchall()
        
        conn.close()
        return results