from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QLineEdit, QDateEdit, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt, QDate

class AddEmployeeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加员工")
        self.setMinimumWidth(400)
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 添加表单字段
        # 姓名
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("姓名*:"))
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # 工号
        empid_layout = QHBoxLayout()
        empid_layout.addWidget(QLabel("工号:"))
        self.empid_edit = QLineEdit()
        empid_layout.addWidget(self.empid_edit)
        layout.addLayout(empid_layout)
        
        # 身份证号
        idcard_layout = QHBoxLayout()
        idcard_layout.addWidget(QLabel("身份证号:"))
        self.idcard_edit = QLineEdit()
        idcard_layout.addWidget(self.idcard_edit)
        layout.addLayout(idcard_layout)
        
        # 入职日期
        hire_date_layout = QHBoxLayout()
        hire_date_layout.addWidget(QLabel("入职日期:"))
        self.hire_date_edit = QDateEdit()
        self.hire_date_edit.setDate(QDate.currentDate())
        hire_date_layout.addWidget(self.hire_date_edit)
        layout.addLayout(hire_date_layout)
        
        # 员工类型
        emp_type_layout = QHBoxLayout()
        emp_type_layout.addWidget(QLabel("员工类型:"))
        self.emp_type_combo = QComboBox()
        self.emp_type_combo.addItems(["正式工", "临时工", "实习生"])
        emp_type_layout.addWidget(self.emp_type_combo)
        layout.addLayout(emp_type_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_employee)
        
        add_another_btn = QPushButton("再添加一人")
        add_another_btn.clicked.connect(self.add_another)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(add_another_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def validate_input(self) -> bool:
        """验证输入数据"""
        name = self.name_edit.text().strip()
        empid = self.empid_edit.text().strip()
        idcard = self.idcard_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "错误", "姓名为必填项")
            return False
            
        if not empid and not idcard:
            QMessageBox.warning(self, "错误", "工号和身份证号至少填写一项")
            return False
            
        return True
    
    def save_employee(self):
        """保存员工信息"""
        if not self.validate_input():
            return
            
        # TODO: 保存到数据库
        self.accept()
    
    def add_another(self):
        """保存当前员工并打开新的添加界面"""
        if not self.validate_input():
            return
            
        # TODO: 保存到数据库
        
        # 清空表单
        self.name_edit.clear()
        self.empid_edit.clear()
        self.idcard_edit.clear()
        self.hire_date_edit.setDate(QDate.currentDate())
        self.emp_type_combo.setCurrentIndex(0)