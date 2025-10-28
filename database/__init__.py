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
        
        # Create departments table if it doesn't exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='departments';")
        departments_table_exists = cursor.fetchone()
        if not departments_table_exists:
            cursor.execute('''
                CREATE TABLE departments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        # Create staff table if it doesn't exist (with department_id)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='staff';")
        staff_table_exists = cursor.fetchone()
        if not staff_table_exists:
            cursor.execute('''
                CREATE TABLE staff (
                    staff_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    department_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (department_id) REFERENCES departments (id)
                )
            ''')
        
        # Create attendance table if it doesn't exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='attendance';")
        attendance_table_exists = cursor.fetchone()
        if not attendance_table_exists:
            cursor.execute('''
                CREATE TABLE attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    staff_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    department TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time_in TEXT,
                    time_out TEXT,
                    timestamp_in DATETIME,
                    timestamp_out DATETIME,
                    UNIQUE(staff_id, date)
                )
            ''')
        
        conn.commit()
        conn.close()
    
    def add_staff(self, staff_id: str, name: str, department: str):
        """Add a new staff member to the database - updated to work with department name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get department_id based on department name
            cursor.execute("SELECT id FROM departments WHERE name = ?", (department,))
            dept_result = cursor.fetchone()
            
            if not dept_result:
                # Department doesn't exist, create it
                cursor.execute("INSERT INTO departments (name) VALUES (?)", (department,))
                department_id = cursor.lastrowid
            else:
                department_id = dept_result[0]
            
            cursor.execute(
                "INSERT INTO staff (staff_id, name, department_id) VALUES (?, ?, ?)",
                (staff_id, name, department_id)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Staff ID already exists
            return False
        finally:
            conn.close()
    
    def get_staff(self, staff_id: str) -> Optional[tuple]:
        """Get staff information by ID - updated to work with department_id"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Join staff with departments to get department name
        cursor.execute("""
            SELECT s.staff_id, s.name, d.name 
            FROM staff s
            JOIN departments d ON s.department_id = d.id
            WHERE s.staff_id = ?
        """, (staff_id,))
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
            # Get staff information to store with the attendance record
            staff_info = self.get_staff(staff_id)
            if staff_info:
                name = staff_info[1]
                department = staff_info[2]
            else:
                name = "Unknown"
                department = "Unknown"
            
            # First entry of the day - sign in
            cursor.execute(
                "INSERT INTO attendance (staff_id, name, department, date, time_in, timestamp_in) VALUES (?, ?, ?, ?, ?, ?)",
                (staff_id, name, department, date, time, timestamp)
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
    
    def get_all_attendance(self, limit: int = None, offset: int = 0, date_from: str = None, date_to: str = None, department: str = None, staff_id: str = None) -> List[tuple]:
        """Get all attendance records with optional filters and pagination"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build the query with optional filters
        query = """
            SELECT a.staff_id, a.name, a.department, a.date, a.time_in, a.time_out
            FROM attendance a
            WHERE 1=1
        """
        params = []
        
        if date_from:
            query += " AND a.date >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND a.date <= ?"
            params.append(date_to)
            
        if department:
            query += " AND a.department = ?"
            params.append(department)
            
        if staff_id:
            query += " AND a.staff_id = ?"
            params.append(staff_id)
        
        query += " ORDER BY a.timestamp_in DESC"
        
        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        conn.close()
        return results
    
    def get_total_attendance_count(self, date_from: str = None, date_to: str = None, department: str = None, staff_id: str = None) -> int:
        """Get the total count of attendance records for pagination with filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build the count query with optional filters
        query = "SELECT COUNT(*) FROM attendance a WHERE 1=1"
        params = []
        
        if date_from:
            query += " AND a.date >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND a.date <= ?"
            params.append(date_to)
            
        if department:
            query += " AND a.department = ?"
            params.append(department)
            
        if staff_id:
            query += " AND a.staff_id = ?"
            params.append(staff_id)
        
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def get_all_staff(self, limit: int = None, offset: int = 0) -> List[tuple]:
        """Get all staff members - updated to work with department_id"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Join staff with departments to get department name
        query = """
            SELECT s.staff_id, s.name, d.name 
            FROM staff s
            JOIN departments d ON s.department_id = d.id
            ORDER BY s.name
        """
        
        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            cursor.execute(query, (limit, offset))
        else:
            cursor.execute(query)
        
        results = cursor.fetchall()
        
        conn.close()
        return results
    
    def get_total_staff_count(self) -> int:
        """Get the total count of staff members for pagination"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM staff")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def update_staff(self, staff_id: str, name: str, department: str) -> bool:
        """Update staff information - updated to work with department name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get department_id based on department name
            cursor.execute("SELECT id FROM departments WHERE name = ?", (department,))
            dept_result = cursor.fetchone()
            
            if not dept_result:
                # Department doesn't exist, create it
                cursor.execute("INSERT INTO departments (name) VALUES (?)", (department,))
                department_id = cursor.lastrowid
            else:
                department_id = dept_result[0]
            
            cursor.execute(
                "UPDATE staff SET name = ?, department_id = ? WHERE staff_id = ?",
                (name, department_id, staff_id)
            )
            conn.commit()
            updated = cursor.rowcount > 0
            conn.close()
            return updated
        except Exception as e:
            conn.close()
            return False
    
    def add_department(self, name: str, description: str = "") -> bool:
        """Add a new department to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO departments (name, description) VALUES (?, ?)",
                (name, description)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Department name already exists
            return False
        finally:
            conn.close()

    def get_department_by_id(self, dept_id: int) -> Optional[tuple]:
        """Get department information by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, description FROM departments WHERE id = ?", (dept_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result
    
    def get_department_by_name(self, name: str) -> Optional[tuple]:
        """Get department information by name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, description FROM departments WHERE name = ?", (name,))
        result = cursor.fetchone()
        
        conn.close()
        return result

    def get_all_departments(self, limit: int = None, offset: int = 0) -> List[tuple]:
        """Get all departments with pagination support"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT id, name, description FROM departments ORDER BY name"
        
        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            cursor.execute(query, (limit, offset))
        else:
            cursor.execute(query)
        
        results = cursor.fetchall()
        
        conn.close()
        return results
    
    def get_total_departments_count(self) -> int:
        """Get the total count of departments for pagination"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM departments")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count

    def update_department(self, dept_id: int, name: str, description: str = "") -> bool:
        """Update department information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE departments SET name = ?, description = ? WHERE id = ?",
                (name, description, dept_id)
            )
            conn.commit()
            updated = cursor.rowcount > 0
            conn.close()
            return updated
        except Exception as e:
            conn.close()
            return False

    def delete_department(self, dept_id: int) -> bool:
        """Delete a department (only if no staff are assigned to it)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if any staff are assigned to this department
            cursor.execute("SELECT COUNT(*) FROM staff WHERE department_id = ?", (dept_id,))
            staff_count = cursor.fetchone()[0]
            
            if staff_count > 0:
                # Cannot delete department with assigned staff
                conn.close()
                return False
            
            cursor.execute("DELETE FROM departments WHERE id = ?", (dept_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
            conn.close()
            return deleted
        except Exception as e:
            conn.close()
            return False

    def get_late_attendance_count_for_month(self, staff_id: str, year: int, month: int) -> int:
        """Get the count of late attendance for a staff member in a specific month"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Define late arrival time (after 8:30 AM)
        late_time = "08:30:00"
        
        # Format the date range for the specific month
        start_date = f"{year:04d}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1:04d}-01-01"  # Next year, January
        else:
            end_date = f"{year:04d}-{month+1:02d}-01"  # Next month

        query = """
            SELECT COUNT(*) 
            FROM attendance 
            WHERE staff_id = ? 
            AND date >= ? 
            AND date < ? 
            AND time_in > ? 
            AND time_in IS NOT NULL
        """
        
        cursor.execute(query, (staff_id, start_date, end_date, late_time))
        late_count = cursor.fetchone()[0]
        
        conn.close()
        return late_count

    def get_total_late_attendance_count(self, year: int, month: int, min_late_count: int = 1) -> int:
        """Get the total count of staff with late attendance for pagination"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Define late arrival time (after 8:30 AM)
        late_time = "08:30:00"
        
        # Format the date range for the specific month
        start_date = f"{year:04d}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1:04d}-01-01"  # Next year, January
        else:
            end_date = f"{year:04d}-{month+1:02d}-01"  # Next month

        # Count staff members with late attendance above the threshold
        query_count = """
            SELECT COUNT(*) 
            FROM (
                SELECT 
                    staff_id,
                    COUNT(*) as late_count
                FROM attendance 
                WHERE date >= ? 
                AND date < ? 
                AND time_in > ? 
                AND time_in IS NOT NULL
                GROUP BY staff_id
                HAVING late_count >= ?
            )
        """
        
        cursor.execute(query_count, (start_date, end_date, late_time, min_late_count))
        count = cursor.fetchone()[0]
        
        conn.close()
        return count

    def get_staff_with_late_attendance(self, year: int, month: int, min_late_count: int = 1, limit: int = None, offset: int = 0) -> List[tuple]:
        """Get staff who were late more than a specified number of times in a month"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Define late arrival time (after 8:30 AM)
        late_time = "08:30:00"
        
        # Format the date range for the specific month
        start_date = f"{year:04d}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1:04d}-01-01"  # Next year, January
        else:
            end_date = f"{year:04d}-{month+1:02d}-01"  # Next month

        # First, get the count of late arrivals by staff_id
        query_count = """
            SELECT 
                staff_id,
                COUNT(*) as late_count
            FROM attendance 
            WHERE date >= ? 
            AND date < ? 
            AND time_in > ? 
            AND time_in IS NOT NULL
            GROUP BY staff_id
            HAVING late_count >= ?
            ORDER BY late_count DESC, staff_id
        """
        
        if limit is not None:
            query_count += " LIMIT ? OFFSET ?"
            params = (start_date, end_date, late_time, min_late_count, limit, offset)
        else:
            params = (start_date, end_date, late_time, min_late_count)
        
        cursor.execute(query_count, params)
        late_counts = cursor.fetchall()
        
        results = []
        for staff_id, late_count in late_counts:
            # Get the most recent name and department for this staff member in this month
            # (to show the current name rather than the name at each late arrival)
            query_details = """
                SELECT name, department
                FROM attendance
                WHERE staff_id = ? 
                AND date >= ? 
                AND date < ?
                AND time_in IS NOT NULL
                ORDER BY timestamp_in DESC
                LIMIT 1
            """
            cursor.execute(query_details, (staff_id, start_date, end_date))
            detail_row = cursor.fetchone()
            
            if detail_row:
                name, department = detail_row
            else:
                # Fallback: get name from staff table
                staff_info = self.get_staff(staff_id)
                if staff_info:
                    name, department = staff_info[1], staff_info[2]
                else:
                    name, department = "Unknown", "Unknown"
            
            results.append((staff_id, name, department, late_count))
        
        conn.close()
        return results

    def get_late_attendance_details(self, staff_id: str, year: int, month: int) -> List[tuple]:
        """Get detailed late attendance records for a specific staff member in a month"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Define late arrival time (after 8:30 AM)
        late_time = "08:30:00"
        
        # Format the date range for the specific month
        start_date = f"{year:04d}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1:04d}-01-01"  # Next year, January
        else:
            end_date = f"{year:04d}-{month+1:02d}-01"  # Next month

        query = """
            SELECT 
                staff_id, 
                name, 
                department, 
                date, 
                time_in,
                CASE 
                    WHEN time_in > '08:30:00' THEN 
                        (strftime('%s', time_in) - strftime('%s', '08:30:00')) / 60 
                    ELSE 0 
                END as minutes_late
            FROM attendance 
            WHERE staff_id = ? 
            AND date >= ? 
            AND date < ? 
            AND time_in > ? 
            AND time_in IS NOT NULL
            ORDER BY date, time_in
        """
        
        cursor.execute(query, (staff_id, start_date, end_date, late_time))
        results = cursor.fetchall()
        
        conn.close()
        return results

    def delete_staff(self, staff_id: str) -> bool:
        """Delete a staff member (attendance records remain for audit purposes)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Delete only the staff record, not the attendance records
            # This allows us to keep historical attendance for audit purposes
            # while preventing the staff member from logging new attendance
            cursor.execute("DELETE FROM staff WHERE staff_id = ?", (staff_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
            conn.close()
            return deleted
        except Exception as e:
            conn.close()
            return False