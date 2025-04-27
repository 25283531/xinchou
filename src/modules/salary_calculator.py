from typing import Dict, List
import math

class SalaryCalculator:
    def __init__(self, db_connection):
        self.db = db_connection
        self.tax_brackets = [
            (0, 3000, 0.03),
            (3000, 12000, 0.1),
            (12000, 25000, 0.2),
            (25000, 35000, 0.25),
            (35000, 55000, 0.3),
            (55000, 80000, 0.35),
            (80000, float('inf'), 0.45)
        ]
    
    def calculate_salary(self, emp_id: str, year: int, month: int) -> Dict:
        """计算单个员工的薪资"""
        try:
            # 获取员工基本信息和薪资组配置
            emp_info = self.get_employee_info(emp_id)
            group_config = self.get_salary_group_config(emp_info['salary_group'])
            attendance = self.get_attendance(emp_id, year, month)
            
            # 计算各项薪资
            base_salary = self.calculate_base_salary(group_config, attendance)
            performance = self.calculate_performance(group_config, attendance)
            overtime_pay = self.calculate_overtime(group_config, attendance)
            social_security = self.calculate_social_security(group_config, base_salary)
            
            # 计算应纳税所得额
            taxable_income = base_salary + performance + overtime_pay - social_security
            tax = self.calculate_tax(taxable_income)
            
            # 计算实发工资
            net_salary = taxable_income - tax
            
            return {
                'emp_id': emp_id,
                'year': year,
                'month': month,
                'base_salary': base_salary,
                'performance': performance,
                'overtime_pay': overtime_pay,
                'social_security': social_security,
                'tax': tax,
                'net_salary': net_salary
            }
            
        except Exception as e:
            logging.error(f"薪资计算失败: {str(e)}")
            return None
    
    def calculate_tax(self, income: float) -> float:
        """计算个人所得税"""
        tax = 0
        for lower, upper, rate in self.tax_brackets:
            if income > lower:
                taxable = min(income - lower, upper - lower)
                tax += taxable * rate
        return tax