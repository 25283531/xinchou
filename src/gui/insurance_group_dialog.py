from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                            QMessageBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt

class InsuranceGroupDialog(QDialog):
    def __init__(self, db, group_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.group_id = group_id
        self.setup_ui()
        if group_id:
            self.load_group_data()
            
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("社保配置组")
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout()
        
        # 基本信息
        form_layout = QVBoxLayout()
        
        # 配置组名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("配置组名称:"))
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        form_layout.addLayout(name_layout)
        
        # 社保所在地
        location_layout = QHBoxLayout()
        location_layout.addWidget(QLabel("社保所在地:"))
        self.location_edit = QLineEdit()
        location_layout.addWidget(self.location_edit)
        form_layout.addLayout(location_layout)
        
        # 缴纳基数
        base_layout = QHBoxLayout()
        base_layout.addWidget(QLabel("缴纳基数:"))
        self.base_edit = QDoubleSpinBox()
        self.base_edit.setMaximum(999999.99)
        self.base_edit.setDecimals(2)
        base_layout.addWidget(self.base_edit)
        form_layout.addLayout(base_layout)
        
        layout.addLayout(form_layout)
        
        # 社保项目表格
        layout.addWidget(QLabel("社保项目:"))
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(3)
        self.items_table.setHorizontalHeaderLabels(["项目名称", "公司缴纳比例(%)", "个人缴纳比例(%)"])
        layout.addWidget(self.items_table)
        
        # 添加项目按钮
        add_btn = QPushButton("添加项目")
        add_btn.clicked.connect(self.add_item)
        layout.addWidget(add_btn)
        
        # 确定和取消按钮
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_group)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def add_item(self):
        """添加社保项目行"""
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        
        # 添加删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(lambda: self.items_table.removeRow(self.items_table.currentRow()))
        self.items_table.setCellWidget(row, 3, delete_btn)
        
    def load_group_data(self):
        """加载配置组数据"""
        if not self.group_id:
            return
            
        # 加载基本信息
        self.db.cursor.execute('''
            SELECT name, location, base_amount 
            FROM insurance_groups 
            WHERE id = ?
        ''', (self.group_id,))
        group = self.db.cursor.fetchone()
        
        if group:
            self.name_edit.setText(group[0])
            self.location_edit.setText(group[1])
            self.base_edit.setValue(float(group[2]))
            
        # 加载社保项目
        self.db.cursor.execute('''
            SELECT name, company_rate, personal_rate 
            FROM insurance_items 
            WHERE group_id = ?
        ''', (self.group_id,))
        items = self.db.cursor.fetchall()
        
        for item in items:
            row = self.items_table.rowCount()
            self.items_table.insertRow(row)
            self.items_table.setItem(row, 0, QTableWidgetItem(item[0]))
            self.items_table.setItem(row, 1, QTableWidgetItem(str(item[1])))
            self.items_table.setItem(row, 2, QTableWidgetItem(str(item[2])))
            
    def save_group(self):
        """保存配置组"""
        name = self.name_edit.text().strip()
        location = self.location_edit.text().strip()
        base_amount = self.base_edit.value()
        
        if not name or not location:
            QMessageBox.warning(self, "错误", "请填写完整信息")
            return
            
        try:
            self.db.conn.begin()
            
            if self.group_id:
                # 更新配置组
                self.db.cursor.execute('''
                    UPDATE insurance_groups 
                    SET name = ?, location = ?, base_amount = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (name, location, base_amount, self.group_id))
                
                # 删除原有项目
                self.db.cursor.execute('DELETE FROM insurance_items WHERE group_id = ?', (self.group_id,))
            else:
                # 创建新配置组
                self.db.cursor.execute('''
                    INSERT INTO insurance_groups (name, location, base_amount)
                    VALUES (?, ?, ?)
                ''', (name, location, base_amount))
                self.group_id = self.db.cursor.lastrowid
                
            # 保存社保项目
            for row in range(self.items_table.rowCount()):
                item_name = self.items_table.item(row, 0).text().strip()
                company_rate = float(self.items_table.item(row, 1).text())
                personal_rate = float(self.items_table.item(row, 2).text())
                
                self.db.cursor.execute('''
                    INSERT INTO insurance_items (group_id, name, company_rate, personal_rate)
                    VALUES (?, ?, ?, ?)
                ''', (self.group_id, item_name, company_rate, personal_rate))
                
            self.db.conn.commit()
            self.accept()
            
        except Exception as e:
            self.db.conn.rollback()
            QMessageBox.warning(self, "错误", f"保存失败：{str(e)}")