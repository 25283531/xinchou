from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QLineEdit, QFileDialog)
from PyQt6.QtGui import QPixmap
import hashlib
import shutil
import os

class UserSettingsDialog(QDialog):
    def __init__(self, db, username, parent=None):
        super().__init__(parent)
        self.db = db
        self.username = username
        self.setWindowTitle("用户设置")
        self.setMinimumWidth(400)
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 头像设置
        avatar_layout = QHBoxLayout()
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(100, 100)
        self.load_avatar()
        avatar_layout.addWidget(self.avatar_label)
        
        change_avatar_btn = QPushButton("更换头像")
        change_avatar_btn.clicked.connect(self.change_avatar)
        avatar_layout.addWidget(change_avatar_btn)
        layout.addLayout(avatar_layout)
        
        # 修改密码
        old_password_layout = QHBoxLayout()
        old_password_layout.addWidget(QLabel("原密码:"))
        self.old_password_edit = QLineEdit()
        self.old_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        old_password_layout.addWidget(self.old_password_edit)
        layout.addLayout(old_password_layout)
        
        new_password_layout = QHBoxLayout()
        new_password_layout.addWidget(QLabel("新密码:"))
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        new_password_layout.addWidget(self.new_password_edit)
        layout.addLayout(new_password_layout)
        
        # 安全问题设置
        question_layout = QHBoxLayout()
        question_layout.addWidget(QLabel("安全问题:"))
        self.question_edit = QLineEdit()
        question_layout.addWidget(self.question_edit)
        layout.addLayout(question_layout)
        
        answer_layout = QHBoxLayout()
        answer_layout.addWidget(QLabel("答案:"))
        self.answer_edit = QLineEdit()
        answer_layout.addWidget(self.answer_edit)
        layout.addLayout(answer_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 加载当前设置
        self.load_settings()
    
    def load_avatar(self):
        """加载头像"""
        cursor = self.db.cursor
        cursor.execute(
            "SELECT avatar_path FROM users WHERE username = ?",
            (self.username,)
        )
        result = cursor.fetchone()
        
        if result and result[0] and os.path.exists(result[0]):
            pixmap = QPixmap(result[0])
        else:
            # 使用默认头像
            pixmap = QPixmap("assets/default_avatar.png")
        
        self.avatar_label.setPixmap(pixmap.scaled(100, 100))
    
    def change_avatar(self):
        """更换头像"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择头像",
            "",
            "Image Files (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            # 复制头像到应用目录
            avatar_dir = os.path.join(os.path.dirname(self.db.db_path), "avatars")
            os.makedirs(avatar_dir, exist_ok=True)
            
            new_path = os.path.join(avatar_dir, f"{self.username}{os.path.splitext(file_path)[1]}")
            shutil.copy2(file_path, new_path)
            
            # 更新数据库
            cursor = self.db.cursor
            cursor.execute(
                "UPDATE users SET avatar_path = ? WHERE username = ?",
                (new_path, self.username)
            )
            self.db.conn.commit()
            
            # 更新显示
            self.load_avatar()
    
    def load_settings(self):
        """加载当前设置"""
        cursor = self.db.cursor
        cursor.execute(
            "SELECT security_question, security_answer FROM users WHERE username = ?",
            (self.username,)
        )
        result = cursor.fetchone()
        
        if result:
            self.question_edit.setText(result[0] or "")
            self.answer_edit.setText(result[1] or "")
    
    def save_settings(self):
        """保存设置"""
        old_password = self.old_password_edit.text()
        new_password = self.new_password_edit.text()
        question = self.question_edit.text().strip()
        answer = self.answer_edit.text().strip()
        
        # 如果输入了密码，则修改密码
        if old_password or new_password:
            if not (old_password and new_password):
                QMessageBox.warning(self, "错误", "请同时输入原密码和新密码")
                return
                
            # 验证原密码
            cursor = self.db.cursor
            hashed_old = hashlib.sha256(old_password.encode()).hexdigest()
            cursor.execute(
                "SELECT id FROM users WHERE username = ? AND password = ?",
                (self.username, hashed_old)
            )
            
            if not cursor.fetchone():
                QMessageBox.warning(self, "错误", "原密码错误")
                return
                
            # 更新密码
            hashed_new = hashlib.sha256(new_password.encode()).hexdigest()
            cursor.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (hashed_new, self.username)
            )
        
        # 更新安全问题和答案
        cursor = self.db.cursor
        cursor.execute(
            "UPDATE users SET security_question = ?, security_answer = ? WHERE username = ?",
            (question, answer, self.username)
        )
        
        self.db.conn.commit()
        QMessageBox.information(self, "成功", "设置保存成功")
        self.accept()