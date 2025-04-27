import pandas as pd
from datetime import datetime

class RewardImporter:
    def __init__(self, db):
        self.db = db
        
    def validate_file(self, file_path):
        """验证文件格式"""
        try:
            df = pd.read_excel(file_path)
            required_columns = ['工号', '姓名', '类型', '金额', '原因']
            return all(col in df.columns for col in required_columns)
        except Exception:
            return False
            
    def validate_employee_info(self, df):
        """验证员工信息"""
        mismatched_employees = []
        cursor = self.db.cursor
        
        for _, row in df.iterrows():
            emp_id = str(row['工号'])
            name = row['姓名']
            
            # 查询员工信息
            cursor.execute('''
                SELECT name, id_card 
                FROM employees 
                WHERE emp_id = ?
            ''', (emp_id,))
            result = cursor.fetchone()
            
            if not result or result[0] != name:
                mismatched_employees.append({
                    'emp_id': emp_id,
                    'name': name,
                    'db_name': result[0] if result else '未找到'
                })
                
        return mismatched_employees
        
    def import_rewards(self, file_path, month):
        """导入奖惩数据"""
        try:
            df = pd.read_excel(file_path)
            cursor = self.db.cursor
            success_count = 0
            
            for _, row in df.iterrows():
                cursor.execute('''
                    INSERT INTO rewards_punishments 
                    (emp_id, name, month, type, amount, reason)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    str(row['工号']),
                    row['姓名'],
                    month,
                    row['类型'],
                    float(row['金额']),
                    row['原因']
                ))
                success_count += 1
                
            self.db.conn.commit()
            return {'status': 'success', 'success': success_count}
        except Exception as e:
            self.db.conn.rollback()
            return {'status': 'error', 'message': str(e)}