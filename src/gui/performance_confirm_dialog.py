from typing import List
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt

class PerformanceConfirmDialog(QDialog):
    def __init__(self, new_employees: List[str], removed_employees: List[str], parent=None):
        super().__init__(parent)
        self.confirmed = False
        
        self.setWindowTitle("绩效考核人员变动确认")
        self.setMinimumWidth(500)
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 添加说明文字
        if new_employees or removed_employees:
            layout.addWidget(QLabel("检测到以下人员变动情况："))
            
            # 新增人员表格
            if new_employees:
                layout.addWidget(QLabel("新增考核人员："))
                new_table = QTableWidget()
                new_table.setColumnCount(1)
                new_table.setHorizontalHeaderLabels(["员工编号"])
                new_table.setRowCount(len(new_employees))
                for i, emp_id in enumerate(new_employees):
                    new_table.setItem(i, 0, QTableWidgetItem(emp_id))
                layout.addWidget(new_table)
            
            # 减少人员表格
            if removed_employees:
                layout.addWidget(QLabel("减少考核人员："))
                removed_table = QTableWidget()
                removed_table.setColumnCount(1)
                removed_table.setHorizontalHeaderLabels(["员工编号"])
                removed_table.setRowCount(len(removed_employees))
                for i, emp_id in enumerate(removed_employees):
                    removed_table.setItem(i, 0, QTableWidgetItem(emp_id))
                layout.addWidget(removed_table)
        else:
            layout.addWidget(QLabel("未检测到人员变动"))
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        confirm_btn = QPushButton("确认无误")
        confirm_btn.clicked.connect(self.accept_changes)
        
        cancel_btn = QPushButton("取消导入")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(confirm_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def accept_changes(self):
        self.confirmed = True
        self.accept()