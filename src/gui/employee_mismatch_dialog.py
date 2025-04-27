from typing import List, Dict
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QPushButton, 
                           QLabel, QTableWidget, QTableWidgetItem)

class EmployeeMismatchDialog(QDialog):
    def __init__(self, mismatched_employees: List[Dict[str, str]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("员工信息核对")
        self.setMinimumWidth(600)
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 添加说明文字
        layout.addWidget(QLabel("以下人员信息与系统记录不符，请核对后重新上传："))
        
        # 创建表格
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["员工编号", "上传文件中姓名", "系统记录姓名"])
        
        # 添加数据
        table.setRowCount(len(mismatched_employees))
        for i, emp in enumerate(mismatched_employees):
            table.setItem(i, 0, QTableWidgetItem(emp['emp_id']))
            table.setItem(i, 1, QTableWidgetItem(emp['uploaded_name']))
            table.setItem(i, 2, QTableWidgetItem(emp['db_name']))
        
        layout.addWidget(table)
        
        # 添加取消按钮
        cancel_btn = QPushButton("取消上传")
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        
        self.setLayout(layout)