from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QLineEdit, QMessageBox)
import hashlib

class ResetPasswordDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("重置密码")
        self.setMinimumWidth(300)
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 用户名输入
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("用户名:"))
        self.username_edit = QLineEdit()
        username_layout.addWidget(self.username_edit)
        layout.addLayout(username_layout)
        
        # 安全问题显示
        self.question_label = QLabel("")
        layout.addWidget(self.question_label)
        
        # 答案输入
        answer_layout = QHBoxLayout()
        answer_layout.addWidget(QLabel("答案:"))
        self.answer_edit = QLineEdit()
        answer_layout.addWidget(self.answer_edit)
        layout.addLayout(answer_layout)
        
        # 新密码输入
        new_password_layout = QHBoxLayout()
        new_password_layout.addWidget(QLabel("新密码:"))
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        new_password_layout.addWidget(self.new_password_edit)
        layout.addLayout(new_password_layout)
        
        # 确认密码输入
        confirm_layout = QHBoxLayout()
        confirm_layout.addWidget(QLabel("确认密码:"))
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
        confirm_layout.addWidget(self.confirm_edit)
        layout.addLayout(confirm_layout)
        
        # 按钮
        reset_btn = QPushButton("重置密码")
        reset_btn.clicked.connect(self.reset_password)
        layout.addWidget(reset_btn)
        
        self.setLayout(layout)
        
        # 连接用户名变化信号
        self.username_edit.textChanged.connect(self.load_security_question)
    
    def load_security_question(self):
        """加载安全问题"""
        username = self.username_edit.text().strip()
        if username:
            cursor = self.db.cursor
            cursor.execute(
                "SELECT security_question FROM users WHERE username = ?",
                (username,)
            )
            result = cursor.fetchone()
            if result:
                self.question_label.setText(f"安全问题: {result[0]}")
            else:
                self.question_label.setText("未找到该用户")
    
    def reset_password(self):
        """重置密码"""
        username = self.username_edit.text().strip()
        answer = self.answer_edit.text().strip()
        new_password = self.new_password_edit.text()
        confirm = self.confirm_edit.text()
        
        if not all([username, answer, new_password, confirm]):
            QMessageBox.warning(self, "错误", "所有字段都必须填写")
            return
            
        if new_password != confirm:
            QMessageBox.warning(self, "错误", "两次输入的密码不一致")
            return
            
        # 验证答案
        cursor = self.db.cursor
        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND security_answer = ?",
            (username, answer)
        )
        
        if cursor.fetchone():
            # 更新密码
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            cursor.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (hashed_password, username)
            )
            self.db.conn.commit()
            
            QMessageBox.information(self, "成功", "密码重置成功")
            self.accept()
        else:
            QMessageBox.warning(self, "错误", "安全问题答案错误")