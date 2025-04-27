from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QLineEdit, QMessageBox)
from PyQt6.QtCore import pyqtSignal
import hashlib

class LoginDialog(QDialog):
    loginSuccess = pyqtSignal()  # 登录成功信号
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("用户登录")
        self.setMinimumWidth(300)
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 用户名输入
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("用户名:"))
        self.username_edit = QLineEdit()
        username_layout.addWidget(self.username_edit)
        layout.addLayout(username_layout)
        
        # 密码输入
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("密码:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(self.password_edit)
        layout.addLayout(password_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        login_btn = QPushButton("登录")
        login_btn.clicked.connect(self.login)
        
        forgot_btn = QPushButton("忘记密码")
        forgot_btn.clicked.connect(self.forgot_password)
        
        button_layout.addWidget(login_btn)
        button_layout.addWidget(forgot_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def login(self):
        """处理登录"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username or not password:
            QMessageBox.warning(self, "错误", "用户名和密码不能为空")
            return
        
        # 密码加密
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # 验证用户名和密码
        cursor = self.db.cursor
        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND password = ?",
            (username, hashed_password)
        )
        
        if cursor.fetchone():
            self.loginSuccess.emit()
            self.accept()
        else:
            QMessageBox.warning(self, "错误", "用户名或密码错误")
    
    def forgot_password(self):
        """处理忘记密码"""
        dialog = ResetPasswordDialog(self.db, self)
        dialog.exec()