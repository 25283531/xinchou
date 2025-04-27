import sqlite3
import os
import shutil
from datetime import datetime
import logging

class Database:
    def __init__(self):
        # 确保数据库目录存在
        db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        self.db_path = os.path.join(db_dir, 'xinchou.db')
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """连接到数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self._create_tables()
            return True
        except Exception as e:
            logging.error(f"数据库连接失败: {str(e)}")
            return False
            
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            
    def _create_tables(self):
        """创建数据库表"""
        # 员工信息表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_id TEXT UNIQUE,           -- 工号
                name TEXT NOT NULL,           -- 姓名
                id_card TEXT UNIQUE,          -- 身份证号
                hire_date DATE,              -- 入职日期
                emp_type TEXT,               -- 员工类型
                status INTEGER DEFAULT 1,     -- 状态(1:在职, 0:离职)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 考勤记录表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_id TEXT NOT NULL,         -- 工号
                date DATE NOT NULL,           -- 日期
                check_in TIME,               -- 上班时间
                check_out TIME,              -- 下班时间
                status TEXT,                 -- 考勤状态
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
            )
        ''')
        
        # 绩效记录表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_id TEXT NOT NULL,         -- 工号
                month TEXT NOT NULL,          -- 月份(YYYY-MM)
                score DECIMAL(5,2),          -- 绩效得分
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (emp_id) REFERENCES employees(emp_id),
                UNIQUE(emp_id, month)
            )
        ''')
        
        # 用户表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,     -- 用户名
                password TEXT NOT NULL,            -- 密码
                avatar_path TEXT,                  -- 头像路径
                security_question TEXT,            -- 密码重置问题
                security_answer TEXT,              -- 密码重置答案
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建默认管理员账户
        self._create_default_admin()
        
        # 奖惩记录表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS rewards_punishments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_id TEXT NOT NULL,         -- 工号
                name TEXT NOT NULL,           -- 姓名
                month TEXT NOT NULL,          -- 月份(YYYY-MM)
                type TEXT NOT NULL,           -- 类型(奖励/惩罚)
                amount DECIMAL(10,2),         -- 金额
                reason TEXT,                  -- 原因
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
            )
        ''')
        
        # 薪酬项表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS salary_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,           -- 项目名称
                level INTEGER NOT NULL,       -- 项目级数
                amount DECIMAL(10,2),         -- 金额
                remark TEXT,                  -- 备注
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 社保配置组表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS insurance_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,           -- 配置组名称
                location TEXT NOT NULL,       -- 社保所在地
                base_amount DECIMAL(10,2),    -- 缴纳基数
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 社保项目表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS insurance_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,    -- 所属配置组ID
                name TEXT NOT NULL,           -- 项目名称
                company_rate DECIMAL(5,2),    -- 公司缴纳比例
                personal_rate DECIMAL(5,2),   -- 个人缴纳比例
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES insurance_groups(id)
            )
        ''')
        
        self.conn.commit()
        
    def _create_default_admin(self):
        """创建默认管理员账户"""
        try:
            # 检查是否已存在管理员账户
            self.cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            if not self.cursor.fetchone():
                # 使用 SHA256 加密密码
                import hashlib
                hashed_password = hashlib.sha256('admin'.encode()).hexdigest()
                
                # 插入默认管理员账户
                self.cursor.execute('''
                    INSERT INTO users (username, password, security_question, security_answer)
                    VALUES (?, ?, ?, ?)
                ''', ('admin', hashed_password, '默认安全问题：您的默认密码是什么？', 'admin'))
                
                self.conn.commit()
        except Exception as e:
            logging.error(f"创建默认管理员账户失败: {str(e)}")
    
    def backup_database(self, backup_path: str) -> bool:
        """备份数据库"""
        try:
            # 确保备份目录存在
            os.makedirs(backup_path, exist_ok=True)
            
            # 生成备份文件名
            backup_file = os.path.join(
                backup_path, 
                f'xinchou_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
            )
            
            # 关闭当前连接
            self.close()
            
            # 复制数据库文件
            shutil.copy2(self.db_path, backup_file)
            
            # 重新连接数据库
            self.connect()
            
            return True
        except Exception as e:
            logging.error(f"数据库备份失败: {str(e)}")
            # 确保数据库重新连接
            self.connect()
            return False