import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.db_file = "salary_system.db"
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """初始化数据库连接和表结构"""
        need_create = not os.path.exists(self.db_file)
        self.conn = sqlite3.connect(self.db_file)
        
        if need_create:
            self.create_tables()
    
    def create_tables(self):
        """创建数据库表"""
        cursor = self.conn.cursor()
        
        # 员工表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            emp_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT,
            position TEXT,
            salary_group TEXT,
            entry_date TEXT,
            status INTEGER DEFAULT 1
        )''')
        
        # 薪资组表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS salary_groups (
            group_id TEXT PRIMARY KEY,
            group_name TEXT NOT NULL,
            base_salary REAL,
            performance_rule TEXT,
            social_security_base REAL,
            formula TEXT,
            create_time TEXT
        )''')
        
        # 考勤记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT,
            work_date TEXT,
            attendance_days INTEGER,
            late_times INTEGER,
            overtime_hours REAL,
            FOREIGN KEY (emp_id) REFERENCES employees (emp_id)
        )''')
        
        # 工资记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS salary_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT,
            year INTEGER,
            month INTEGER,
            base_salary REAL,
            performance REAL,
            overtime_pay REAL,
            deductions REAL,
            social_security REAL,
            tax REAL,
            net_salary REAL,
            calculate_time TEXT,
            FOREIGN KEY (emp_id) REFERENCES employees (emp_id)
        )''')
        
        self.conn.commit()