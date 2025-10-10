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
        
        # Check if the old staff table exists and migrate if needed
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='staff';")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # Check if the old schema has the 'position' column and no 'department' column
            cursor.execute("PRAGMA table_info(staff)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'position' in columns and 'department' not in columns:
                # Old schema exists - backup data and recreate table
                cursor.execute("SELECT staff_id, name, position, created_at FROM staff")
                old_data = cursor.fetchall()
                
                # Drop old table
                cursor.execute("DROP TABLE staff")
                
                # Create new staff table with department column
                cursor.execute('''
                    CREATE TABLE staff (
                        staff_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        department TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Migrate old data (mapping position to department)
                for row in old_data:
                    staff_id, name, position, created_at = row
                    cursor.execute(
                        "INSERT INTO staff (staff_id, name, department, created_at) VALUES (?, ?, ?, ?)",
                        (staff_id, name, position, created_at)
                    )
            elif 'department' not in columns:
                # Create new staff table if it doesn't have the required column
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS staff (
                        staff_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        department TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
        else:
            # Create new staff table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS staff (
                    staff_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    department TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        # Check if the old attendance table exists and migrate if needed
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='attendance';")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # Check if the old schema has the 'time' column and no 'time_in'/'time_out' columns
            cursor.execute("PRAGMA table_info(attendance)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'time' in columns and 'time_in' not in columns:
                # Old schema exists - backup data and recreate table
                cursor.execute("SELECT staff_id, date, time FROM attendance")
                old_data = cursor.fetchall()
                
                # Drop old table
                cursor.execute("DROP TABLE attendance")
                
                # Create new attendance table with time_in and time_out columns
                cursor.execute('''
                    CREATE TABLE attendance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        staff_id TEXT NOT NULL,
                        date TEXT NOT NULL,
                        time_in TEXT,
                        time_out TEXT,
                        timestamp_in DATETIME,
                        timestamp_out DATETIME,
                        FOREIGN KEY (staff_id) REFERENCES staff (staff_id),
                        UNIQUE(staff_id, date)
                    )
                ''')
                
                # Migrate old data (for now, putting all old time values as time_in)
                for row in old_data:
                    staff_id, date, time = row
                    cursor.execute(
                        "INSERT OR IGNORE INTO attendance (staff_id, date, time_in) VALUES (?, ?, ?)",
                        (staff_id, date, time)
                    )
            elif 'time_in' not in columns:
                # Create new attendance table if it doesn't have the required columns
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS attendance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        staff_id TEXT NOT NULL,
                        date TEXT NOT NULL,
                        time_in TEXT,
                        time_out TEXT,
                        timestamp_in DATETIME,
                        timestamp_out DATETIME,
                        FOREIGN KEY (staff_id) REFERENCES staff (staff_id),
                        UNIQUE(staff_id, date)
                    )
                ''')
        else:
            # Create new attendance table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    staff_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time_in TEXT,
                    time_out TEXT,
                    timestamp_in DATETIME,
                    timestamp_out DATETIME,
                    FOREIGN KEY (staff_id) REFERENCES staff (staff_id),
                    UNIQUE(staff_id, date)
                )
            ''')
        
        conn.commit()
        conn.close()
    
    def add_staff(self, staff_id: str, name: str, department: str):
        """Add a new staff member to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO staff (staff_id, name, department) VALUES (?, ?, ?)",
                (staff_id, name, department)
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
        
        cursor.execute("SELECT staff_id, name, department FROM staff WHERE staff_id = ?", (staff_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result
    
    def log_attendance(self, staff_id: str):
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
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if there's already an attendance record for this staff member today
        cursor.execute(
            "SELECT time_in, time_out FROM attendance WHERE staff_id = ? AND date = ?",
            (staff_id, date)
        )
        result = cursor.fetchone()
        
        if result is None:
            # First entry of the day - sign in
            cursor.execute(
                "INSERT INTO attendance (staff_id, date, time_in, timestamp_in) VALUES (?, ?, ?, ?)",
                (staff_id, date, time, timestamp)
            )
            conn.commit()
            conn.close()
            return "Sign In"
        else:
            time_in, time_out = result
            if time_out is None:
                # Second entry of the day - sign out
                cursor.execute(
                    "UPDATE attendance SET time_out = ?, timestamp_out = ? WHERE staff_id = ? AND date = ?",
                    (time, timestamp, staff_id, date)
                )
                conn.commit()
                conn.close()
                return "Sign Out"
            else:
                # Already signed out for the day - don't log anything
                conn.close()
                return "Already Signed Out"
    
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
            SELECT a.staff_id, s.name, s.department, a.date, a.time_in, a.time_out
            FROM attendance a
            LEFT JOIN staff s ON a.staff_id = s.staff_id
            ORDER BY a.timestamp_in DESC
        ''')
        results = cursor.fetchall()
        
        conn.close()
        return results
    
    def get_all_staff(self) -> List[tuple]:
        """Get all staff members"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT staff_id, name, department FROM staff ORDER BY name")
        results = cursor.fetchall()
        
        conn.close()
        return results