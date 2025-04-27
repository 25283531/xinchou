from typing import Dict, List
import json
from datetime import datetime

class SalaryGroup:
    def __init__(self, db_connection):
        self.db = db_connection
        
    def create_group(self, group_data: Dict) -> bool:
        """创建新的薪资组"""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                INSERT INTO salary_groups 
                (group_id, group_name, base_salary, performance_rule, 
                social_security_base, formula, create_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                group_data['group_id'],
                group_data['group_name'],
                group_data['base_salary'],
                json.dumps(group_data['performance_rule']),
                group_data['social_security_base'],
                group_data['formula'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            self.db.commit()
            return True
        except Exception as e:
            logging.error(f"创建薪资组失败: {str(e)}")
            return False
    
    def validate_formula(self, formula: str) -> bool:
        """验证薪资计算公式"""
        try:
            # 检查基本语法
            allowed_operators = ['+', '-', '*', '/', '(', ')', '.']
            allowed_keywords = ['基本工资', '绩效工资', '加班工资', '社保', '个税']
            
            # 简单的词法分析
            tokens = formula.split()
            for token in tokens:
                if (not any(keyword in token for keyword in allowed_keywords) and
                    not token.replace('.','').isdigit() and
                    token not in allowed_operators):
                    return False
            
            return True
        except:
            return False