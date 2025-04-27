import unittest
import pandas as pd
import os
from src.modules.attendance_import import AttendanceImporter

class TestAttendanceImporter(unittest.TestCase):
    def setUp(self):
        """测试前准备工作"""
        self.db_connection = None  # 这里可以使用 SQLite 内存数据库进行测试
        self.importer = AttendanceImporter(self.db_connection)
        
        # 创建测试数据文件
        self.test_csv_path = "test_attendance.csv"
        self.test_excel_path = "test_attendance.xlsx"
        
        # 创建测试CSV文件
        test_data = {
            '员工编号': ['001', '002'],
            '姓名': ['张三', '李四'],
            '出勤天数': [22, 21],
            '加班时长': [8, 12]
        }
        df = pd.DataFrame(test_data)
        df.to_csv(self.test_csv_path, index=False)
        df.to_excel(self.test_excel_path, index=False)
        
    def tearDown(self):
        """测试后清理工作"""
        # 删除测试文件
        if os.path.exists(self.test_csv_path):
            os.remove(self.test_csv_path)
        if os.path.exists(self.test_excel_path):
            os.remove(self.test_excel_path)
    
    def test_validate_file(self):
        """测试文件格式验证"""
        # 测试CSV文件验证
        self.assertTrue(self.importer.validate_file(self.test_csv_path))
        
        # 测试Excel文件验证
        self.assertTrue(self.importer.validate_file(self.test_excel_path))
        
        # 测试不支持的文件格式
        self.assertFalse(self.importer.validate_file("test.txt"))
    
    def test_clean_data(self):
        """测试数据清洗功能"""
        test_data = {
            '员工编号': ['001', '002', '003'],
            '姓名': ['张三', '李四', None],
            '出勤天数': ['22', '21', 'invalid'],
            '加班时长': ['8', None, '12']
        }
        df = pd.DataFrame(test_data)
        
        cleaned_df = self.importer.clean_data(df)
        
        # 验证空值处理
        self.assertEqual(len(cleaned_df), 2)  # 应该只剩下2行有效数据
        
        # 验证数据类型转换
        self.assertTrue(pd.api.types.is_numeric_dtype(cleaned_df['出勤天数']))
        self.assertTrue(pd.api.types.is_numeric_dtype(cleaned_df['加班时长']))
    
    def test_import_attendance(self):
        """测试考勤数据导入"""
        # 测试正常导入
        result = self.importer.import_attendance(self.test_csv_path)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['total'], 2)
        
        # 测试字段映射
        mapping = {
            '员工编号': 'emp_id',
            '姓名': 'name',
            '出勤天数': 'attendance_days'
        }
        result = self.importer.import_attendance(self.test_csv_path, mapping)
        self.assertEqual(result['status'], 'success')