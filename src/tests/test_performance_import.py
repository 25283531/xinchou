import unittest
import pandas as pd
import os
from src.modules.performance_import import PerformanceImporter

class TestPerformanceImporter(unittest.TestCase):
    def setUp(self):
        """测试前准备工作"""
        self.db_connection = None  # 使用空数据库连接进行测试
        self.importer = PerformanceImporter(self.db_connection)
        
        # 创建测试数据文件
        self.test_excel_path = "test_performance.xlsx"
        
        # 创建测试Excel文件
        test_data = {
            '员工编号': ['001', '002', '003'],
            '姓名': ['张三', '李四', '王五'],
            '绩效得分': [90, 85, 95]
        }
        df = pd.DataFrame(test_data)
        df.to_excel(self.test_excel_path, index=False)
        
    def tearDown(self):
        """测试后清理工作"""
        # 删除测试文件
        if os.path.exists(self.test_excel_path):
            os.remove(self.test_excel_path)
    
    def test_validate_file(self):
        """测试文件格式验证"""
        # 测试Excel文件验证
        self.assertTrue(self.importer.validate_file(self.test_excel_path))
        
        # 测试不支持的文件格式
        self.assertFalse(self.importer.validate_file("test.txt"))
        
        # 测试缺少必要字段的文件
        invalid_data = {
            '员工编号': ['001'],
            '姓名': ['张三']  # 缺少绩效得分字段
        }
        invalid_file = "invalid_performance.xlsx"
        pd.DataFrame(invalid_data).to_excel(invalid_file, index=False)
        self.assertFalse(self.importer.validate_file(invalid_file))
        os.remove(invalid_file)
    
    def test_clean_data(self):
        """测试数据清洗功能"""
        test_data = {
            '员工编号': ['001', '002', '003', '004'],
            '姓名': ['张三', '李四', '王五', None],
            '绩效得分': ['90', '85', 'invalid', None]
        }
        df = pd.DataFrame(test_data)
        
        cleaned_df = self.importer.clean_data(df)
        
        # 验证空值和无效数据处理
        self.assertEqual(len(cleaned_df), 2)  # 应该只剩下2行有效数据
        
        # 验证数据类型转换
        self.assertTrue(pd.api.types.is_numeric_dtype(cleaned_df['绩效得分']))
    
    def test_import_performance(self):
        """测试绩效数据导入"""
        # 测试正常导入
        result = self.importer.import_performance(self.test_excel_path, "2024-01")
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['total'], 3)
        
        # 测试字段映射
        mapping = {
            '员工编号': 'emp_id',
            '绩效得分': 'score'
        }
        result = self.importer.import_performance(self.test_excel_path, "2024-01", mapping)
        self.assertEqual(result['status'], 'success')