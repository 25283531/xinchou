import pandas as pd
from typing import List, Dict, Tuple
import logging
import os
from datetime import datetime

class PerformanceImporter:
    def __init__(self, db_connection):
        self.db = db_connection
        self.supported_formats = ['.xlsx', '.xls']
        
    def validate_file(self, file_path: str) -> bool:
        """验证文件格式和基本结构"""
        try:
            _, ext = os.path.splitext(file_path.lower())
            if ext not in self.supported_formats:
                logging.error(f"不支持的文件格式: {ext}")
                return False
                
            # 读取文件头验证必要字段
            df = pd.read_excel(file_path, nrows=0, engine='openpyxl')
            
            # 验证必要字段（员工号/身份证号 + 绩效分数）
            required_fields = ['员工编号', '绩效得分']
            missing_fields = [field for field in required_fields if field not in df.columns]
            
            if missing_fields:
                logging.error(f"缺少必要字段: {', '.join(missing_fields)}")
                return False
                
            return True
                
        except Exception as e:
            logging.error(f"文件验证失败: {str(e)}")
            return False
    
    def import_performance(self, file_path: str, month: str, mapping: Dict = None) -> Dict:
        """导入绩效数据"""
        try:
            # 读取文件
            df = pd.read_excel(file_path, engine='openpyxl')
            
            # 数据验证和清洗
            df = self.clean_data(df)
            
            # 应用字段映射
            if mapping:
                df = df.rename(columns=mapping)
            
            # 添加月份信息
            df['月份'] = month
            
            # 保存到数据库
            success_count = self.save_to_database(df)
            
            return {
                'status': 'success',
                'total': len(df),
                'success': success_count,
                'failed': len(df) - success_count
            }
            
        except Exception as e:
            logging.error(f"绩效导入失败: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """数据清洗和验证"""
        df = df.copy()
        
        # 移除空行
        df = df.dropna(subset=['员工编号', '绩效得分'])
        
        # 数据类型转换
        df['绩效得分'] = pd.to_numeric(df['绩效得分'], errors='coerce')
        
        # 删除无效的数值记录
        df = df.dropna(subset=['绩效得分'])
        
        return df
    
    def save_to_database(self, df: pd.DataFrame) -> int:
        """保存绩效数据到数据库"""
        try:
            if self.db is None:
                return len(df)
                
            # TODO: 实现实际的数据库保存逻辑
            # cursor = self.db.cursor()
            # for _, row in df.iterrows():
            #     cursor.execute(...)
            # self.db.commit()
            
            return len(df)
        except Exception as e:
            logging.error(f"保存到数据库失败: {str(e)}")
            return 0
    
    def check_personnel_changes(self, current_data: pd.DataFrame, month: str) -> Tuple[List[str], List[str]]:
        """检查人员变动情况"""
        try:
            # 获取上月日期
            current_date = datetime.strptime(month, "%Y-%m")
            last_month = (current_date.replace(day=1) - pd.Timedelta(days=1)).strftime("%Y-%m")
            
            if self.db is None:
                # 测试模式，返回模拟数据
                return ['001', '002'], ['003', '004']
            
            # TODO: 从数据库获取上月数据
            # last_month_data = pd.read_sql(f"SELECT 员工编号 FROM performance WHERE month = '{last_month}'", self.db)
            # 
            # current_emp_set = set(current_data['员工编号'])
            # last_month_emp_set = set(last_month_data['员工编号'])
            # 
            # new_employees = list(current_emp_set - last_month_emp_set)
            # removed_employees = list(last_month_emp_set - current_emp_set)
            
            # 返回新增和减少的员工编号列表
            return [], []
            
        except Exception as e:
            logging.error(f"检查人员变动失败: {str(e)}")
    
    def validate_employee_info(self, df: pd.DataFrame) -> List[Dict[str, str]]:
        """验证员工号码和姓名是否匹配"""
        mismatched_employees = []
        
        try:
            if self.db is None:
                return []
                
            for _, row in df.iterrows():
                # 从数据库查询员工信息
                cursor = self.db.cursor()
                cursor.execute(
                    "SELECT name FROM employees WHERE emp_id = ? AND status = 1",
                    (row['员工编号'],)
                )
                result = cursor.fetchone()
                
                # 如果找到员工，但姓名不匹配
                if result and result[0] != row['姓名']:
                    mismatched_employees.append({
                        'emp_id': row['员工编号'],
                        'uploaded_name': row['姓名'],
                        'db_name': result[0]
                    })
                    
            return mismatched_employees
            
        except Exception as e:
            logging.error(f"验证员工信息失败: {str(e)}")