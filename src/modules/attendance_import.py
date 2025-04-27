import pandas as pd
from typing import List, Dict
import logging
import os

class AttendanceImporter:
    def __init__(self, db_connection):
        self.db = db_connection
        self.supported_formats = ['.xlsx', '.xls', '.csv']
        
    def validate_file(self, file_path: str) -> bool:
        """验证文件格式和基本结构"""
        try:
            # 使用os.path来正确获取文件扩展名
            _, ext = os.path.splitext(file_path.lower())
            if ext not in self.supported_formats:
                logging.error(f"不支持的文件格式: {ext}")
                return False
                
            # 读取文件头验证必要字段
            if ext == '.csv':
                df = pd.read_csv(file_path, nrows=0)
            else:
                # 使用openpyxl引擎读取Excel文件，并指定sheet_name
                df = pd.read_excel(file_path, nrows=0, engine='openpyxl', sheet_name=0)
                
            required_fields = ['员工编号', '姓名', '出勤天数']
            missing_fields = [field for field in required_fields if field not in df.columns]
            
            if missing_fields:
                logging.error(f"缺少必要字段: {', '.join(missing_fields)}")
                return False
                
            return True
                
        except Exception as e:
            logging.error(f"文件验证失败: {str(e)}")
            return False
    
    def import_attendance(self, file_path: str, mapping: Dict = None) -> Dict:
        """导入考勤数据"""
        try:
            # 读取文件
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path, engine='openpyxl')
            
            # 数据验证和清洗
            df = self.clean_data(df)
            
            # 应用字段映射
            if mapping:
                # 确保所有必要字段都在映射中
                required_fields = ['员工编号', '姓名', '出勤天数']
                for field in required_fields:
                    if field not in mapping and field not in df.columns:
                        raise ValueError(f"缺少必要字段: {field}")
                df = df.rename(columns=mapping)
            
            # 保存到数据库
            success_count = self.save_to_database(df)
            
            return {
                'status': 'success',
                'total': len(df),
                'success': success_count,
                'failed': len(df) - success_count
            }
            
        except Exception as e:
            logging.error(f"考勤导入失败: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """数据清洗和验证"""
        # 创建副本避免警告
        df = df.copy()
        
        # 移除空行
        df = df.dropna(subset=['员工编号', '姓名'])
        
        # 数据类型转换
        # 使用astype进行强制类型转换
        df['出勤天数'] = pd.to_numeric(df['出勤天数'], errors='coerce')
        if '加班时长' in df.columns:
            df['加班时长'] = pd.to_numeric(df['加班时长'], errors='coerce').fillna(0)
        
        # 删除无效的数值记录
        df = df.dropna(subset=['出勤天数'])
        
        return df
    
    def save_to_database(self, df: pd.DataFrame) -> int:
        """保存考勤数据到数据库"""
        try:
            if self.db is None:
                # 测试模式，直接返回行数
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