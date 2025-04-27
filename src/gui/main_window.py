import sys
import os
import pandas as pd

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(current_dir)

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox, QInputDialog
from PyQt6.QtCore import QTimer, QSettings
from src.gui.ui_main import Ui_Dialog
from src.modules.attendance_import import AttendanceImporter
from src.modules.performance_import import PerformanceImporter
from datetime import datetime
from src.gui.performance_confirm_dialog import PerformanceConfirmDialog
from src.gui.employee_mismatch_dialog import EmployeeMismatchDialog
from src.gui.add_employee_dialog import AddEmployeeDialog
from src.gui.login_dialog import LoginDialog
from src.gui.user_settings_dialog import UserSettingsDialog
from src.db.database import Database
from src.modules.reward_import import RewardImporter
from src.gui.insurance_group_dialog import InsuranceGroupDialog

class MainWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        
        # 初始化当前用户名
        self.current_username = None
        
        # 初始化数据库
        self.db = Database()
        if not self.db.connect():
            QMessageBox.critical(self, "错误", "数据库连接失败")
            sys.exit(1)
        
        # 创建登录页面
        self.setup_login_page()
        
        # 初始化导入器
        self.attendance_importer = AttendanceImporter(self.db)
        self.performance_importer = PerformanceImporter(self.db)
        
        # 初始化奖惩导入器
        self.reward_importer = RewardImporter(self.db)
        
        # 连接信号和槽
        self.ui.upload.clicked.connect(self.import_attendance)
        self.ui.upload2.clicked.connect(self.import_performance)
        self.ui.uploadReward.clicked.connect(self.import_reward)
        self.ui.backupDatabase.clicked.connect(self.show_backup_settings)
        self.ui.selectPath.clicked.connect(self.select_backup_path)
        self.ui.backupNow.clicked.connect(self.backup_now)
        self.ui.saveSettings.clicked.connect(self.save_backup_settings)
        self.ui.enableAutoBackup.stateChanged.connect(self.toggle_auto_backup)
        self.ui.userSettings.clicked.connect(self.show_user_settings)
        self.ui.socialInsurance.clicked.connect(self.show_social_insurance)
        self.ui.addInsuranceGroup.clicked.connect(self.add_insurance_group)
        self.ui.socialInsurance_2.clicked.connect(self.show_salary_items)  # 修改这里
        self.ui.addItem.clicked.connect(self.add_salary_item)
        
        # 初始化薪酬项表格
        self.init_salary_items_table()
        
    def show_backup_settings(self):
        """显示备份设置页面"""
        self.ui.stackedWidget.setCurrentWidget(self.ui.backupPage)
        
    def select_backup_path(self):
        """选择备份路径"""
        path = QFileDialog.getExistingDirectory(
            self,
            "选择备份路径",
            self.ui.backupPath.text()
        )
        if path:
            self.ui.backupPath.setText(path)
            
    def backup_now(self):
        """立即备份数据库"""
        backup_path = self.ui.backupPath.text()
        if not backup_path:
            QMessageBox.warning(self, "错误", "请先选择备份路径")
            return
            
        if self.db.backup_database(backup_path):
            QMessageBox.information(self, "成功", "数据库备份成功")
        else:
            QMessageBox.warning(self, "失败", "数据库备份失败")
            
    def save_backup_settings(self):
        """保存备份设置"""
        self.settings.setValue('backup_path', self.ui.backupPath.text())
        self.settings.setValue('auto_backup', self.ui.enableAutoBackup.isChecked())
        self.settings.setValue('backup_interval', self.ui.backupInterval.value())
        QMessageBox.information(self, "成功", "设置保存成功")
        
    def load_backup_settings(self):
        """加载备份设置"""
        self.ui.backupPath.setText(self.settings.value('backup_path', ''))
        self.ui.enableAutoBackup.setChecked(self.settings.value('auto_backup', False, type=bool))
        self.ui.backupInterval.setValue(self.settings.value('backup_interval', 7, type=int))
        
        # 如果启用了自动备份，启动定时器
        if self.ui.enableAutoBackup.isChecked():
            self.start_auto_backup()
            
    def toggle_auto_backup(self, state):
        """切换自动备份状态"""
        if state:
            self.start_auto_backup()
        else:
            self.backup_timer.stop()
            
    def start_auto_backup(self):
        """启动自动备份"""
        interval = self.ui.backupInterval.value()
        self.backup_timer.start(interval * 24 * 60 * 60 * 1000)  # 转换为毫秒
        
    def auto_backup(self):
        """自动备份处理"""
        backup_path = self.ui.backupPath.text()
        if backup_path:
            self.db.backup_database(backup_path)
            
    def closeEvent(self, event):
        """窗口关闭时的处理"""
        self.settings.sync()  # 保存设置
        self.db.close()
        event.accept()

    def disable_buttons(self):
        """禁用所有功能按钮"""
        self.ui.upload.setEnabled(False)
        self.ui.upload2.setEnabled(False)
        self.ui.importRoster.setEnabled(False)
        self.ui.addEmployee.setEnabled(False)
        self.ui.backupDatabase.setEnabled(False)
        self.ui.userSettings.setEnabled(False)
        self.ui.socialInsurance.setEnabled(False)
        self.ui.socialInsurance_2.setEnabled(False)  # 修改这里
    
    def enable_buttons(self):
        """启用所有功能按钮"""
        self.ui.upload.setEnabled(True)
        self.ui.upload2.setEnabled(True)
        self.ui.importRoster.setEnabled(True)
        self.ui.addEmployee.setEnabled(True)
        self.ui.backupDatabase.setEnabled(True)
        self.ui.userSettings.setEnabled(True)
        self.ui.socialInsurance.setEnabled(True)
        self.ui.socialInsurance_2.setEnabled(True)  # 修改这里
        self.ui.salaryItems.setEnabled(False)
    
    def enable_buttons(self):
        """启用所有功能按钮"""
        self.ui.upload.setEnabled(True)
        self.ui.upload2.setEnabled(True)
        self.ui.importRoster.setEnabled(True)
        self.ui.addEmployee.setEnabled(True)
        self.ui.backupDatabase.setEnabled(True)
        self.ui.userSettings.setEnabled(True)
        self.ui.socialInsurance.setEnabled(True)
        self.ui.salaryItems.setEnabled(True)
    
    def show_social_insurance(self):
        """显示社保配置页面"""
        self.ui.stackedWidget.setCurrentWidget(self.ui.socialInsurancePage)
        self.load_insurance_groups()
        
    def load_insurance_groups(self):
        """加载社保配置组"""
        self.ui.insuranceTable.setRowCount(0)
        
        # 查询所有配置组
        self.db.cursor.execute('''
            SELECT id, name, location, base_amount 
            FROM insurance_groups
            ORDER BY created_at DESC
        ''')
        groups = self.db.cursor.fetchall()
        
        for group in groups:
            row = self.ui.insuranceTable.rowCount()
            self.ui.insuranceTable.insertRow(row)
            
            # 设置数据
            self.ui.insuranceTable.setItem(row, 0, QtWidgets.QTableWidgetItem(group[1]))  # 名称
            self.ui.insuranceTable.setItem(row, 1, QtWidgets.QTableWidgetItem(group[2]))  # 所在地
            self.ui.insuranceTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(group[3])))  # 基数
            
            # 添加编辑和删除按钮
            btn_widget = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout(btn_widget)
            edit_btn = QtWidgets.QPushButton("编辑")
            delete_btn = QtWidgets.QPushButton("删除")
            
            edit_btn.clicked.connect(lambda checked, i=group[0]: self.edit_insurance_group(i))
            delete_btn.clicked.connect(lambda checked, i=group[0]: self.delete_insurance_group(i))
            
            layout.addWidget(edit_btn)
            layout.addWidget(delete_btn)
            layout.setContentsMargins(0, 0, 0, 0)
            
            self.ui.insuranceTable.setCellWidget(row, 3, btn_widget)
            
    def add_insurance_group(self):
        """添加社保配置组"""
        dialog = InsuranceGroupDialog(self.db, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_insurance_groups()
            
    def edit_insurance_group(self, group_id):
        """编辑社保配置组"""
        dialog = InsuranceGroupDialog(self.db, group_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_insurance_groups()
            
    def delete_insurance_group(self, group_id):
        """删除社保配置组"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这个社保配置组吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.conn.begin()
                # 删除相关的社保项目
                self.db.cursor.execute('DELETE FROM insurance_items WHERE group_id = ?', (group_id,))
                # 删除配置组
                self.db.cursor.execute('DELETE FROM insurance_groups WHERE id = ?', (group_id,))
                self.db.conn.commit()
                self.load_insurance_groups()
                QMessageBox.information(self, "成功", "社保配置组删除成功")
            except Exception as e:
                self.db.conn.rollback()
                QMessageBox.warning(self, "错误", f"删除失败：{str(e)}")
    
    def show_salary_items(self):
        """显示薪酬项设置页面"""
        self.ui.stackedWidget.setCurrentWidget(self.ui.salaryItemsPage)
        self.load_salary_items()
        
    def init_salary_items_table(self):
        """初始化薪酬项表格"""
        self.ui.itemsTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.ui.itemsTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        
    def load_salary_items(self):
        """加载薪酬项数据"""
        self.ui.itemsTable.setRowCount(0)
        
        # 查询所有薪酬项
        self.db.cursor.execute('SELECT id, name, level, amount, remark FROM salary_items')
        items = self.db.cursor.fetchall()
        
        for item in items:
            row = self.ui.itemsTable.rowCount()
            self.ui.itemsTable.insertRow(row)
            
            # 设置数据
            self.ui.itemsTable.setItem(row, 0, QtWidgets.QTableWidgetItem(item[1]))  # 名称
            self.ui.itemsTable.setItem(row, 1, QtWidgets.QTableWidgetItem(str(item[2])))  # 级数
            self.ui.itemsTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(item[3])))  # 金额
            self.ui.itemsTable.setItem(row, 3, QtWidgets.QTableWidgetItem(item[4]))  # 备注
            
            # 添加编辑和删除按钮
            btn_widget = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout(btn_widget)
            edit_btn = QtWidgets.QPushButton("编辑")
            delete_btn = QtWidgets.QPushButton("删除")
            
            edit_btn.clicked.connect(lambda checked, i=item[0]: self.edit_salary_item(i))
            delete_btn.clicked.connect(lambda checked, i=item[0]: self.delete_salary_item(i))
            
            layout.addWidget(edit_btn)
            layout.addWidget(delete_btn)
            layout.setContentsMargins(0, 0, 0, 0)
            
            self.ui.itemsTable.setCellWidget(row, 4, btn_widget)
            
    def add_salary_item(self):
        """添加薪酬项"""
        name, ok = QInputDialog.getText(self, "添加薪酬项", "项目名称:")
        if not ok or not name:
            return
            
        level, ok = QInputDialog.getInt(self, "添加薪酬项", "项目级数:", 1, 1, 100)
        if not ok:
            return
            
        amount, ok = QInputDialog.getDouble(self, "添加薪酬项", "金额:", 0, 0, 1000000, 2)
        if not ok:
            return
            
        remark, ok = QInputDialog.getText(self, "添加薪酬项", "备注:")
        if not ok:
            return
            
        try:
            self.db.cursor.execute('''
                INSERT INTO salary_items (name, level, amount, remark)
                VALUES (?, ?, ?, ?)
            ''', (name, level, amount, remark))
            self.db.conn.commit()
            self.load_salary_items()
            QMessageBox.information(self, "成功", "薪酬项添加成功")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"添加失败：{str(e)}")
            
    def edit_salary_item(self, item_id):
        """编辑薪酬项"""
        # 获取当前数据
        self.db.cursor.execute('SELECT name, level, amount, remark FROM salary_items WHERE id = ?', (item_id,))
        item = self.db.cursor.fetchone()
        if not item:
            return
            
        name, ok = QInputDialog.getText(self, "编辑薪酬项", "项目名称:", text=item[0])
        if not ok:
            return
            
        level, ok = QInputDialog.getInt(self, "编辑薪酬项", "项目级数:", item[1], 1, 100)
        if not ok:
            return
            
        amount, ok = QInputDialog.getDouble(self, "编辑薪酬项", "金额:", item[2], 0, 1000000, 2)
        if not ok:
            return
            
        remark, ok = QInputDialog.getText(self, "编辑薪酬项", "备注:", text=item[3])
        if not ok:
            return
            
        try:
            self.db.cursor.execute('''
                UPDATE salary_items 
                SET name = ?, level = ?, amount = ?, remark = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (name, level, amount, remark, item_id))
            self.db.conn.commit()
            self.load_salary_items()
            QMessageBox.information(self, "成功", "薪酬项更新成功")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"更新失败：{str(e)}")
            
    def delete_salary_item(self, item_id):
        """删除薪酬项"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这个薪酬项吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.cursor.execute('DELETE FROM salary_items WHERE id = ?', (item_id,))
                self.db.conn.commit()
                self.load_salary_items()
                QMessageBox.information(self, "成功", "薪酬项删除成功")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"删除失败：{str(e)}")
            
    def setup_insurance_ui(self):
        """设置社保配置界面"""
        # 创建社保配置按钮
        self.ui.socialInsurance = QtWidgets.QPushButton(self)
        self.ui.socialInsurance.setText("社保配置")
        self.ui.socialInsurance.setGeometry(20, 430, 160, 40)
        self.ui.leftMenu.addWidget(self.ui.socialInsurance)
        
        # 创建社保配置页面
        self.ui.socialInsurancePage = QtWidgets.QWidget()
        self.ui.stackedWidget.addWidget(self.ui.socialInsurancePage)
        
        # 创建页面布局
        layout = QtWidgets.QVBoxLayout(self.ui.socialInsurancePage)
        
        # 创建标题和按钮组
        header_layout = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("社保配置")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title)
        
        self.ui.addInsuranceGroup = QtWidgets.QPushButton("添加配置组")
        header_layout.addWidget(self.ui.addInsuranceGroup)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 创建社保配置表格
        self.ui.insuranceTable = QtWidgets.QTableWidget()
        self.ui.insuranceTable.setColumnCount(4)
        self.ui.insuranceTable.setHorizontalHeaderLabels(["配置组名称", "社保所在地", "缴纳基数", "操作"])
        self.ui.insuranceTable.horizontalHeader().setStretchLastSection(True)
        self.ui.insuranceTable.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.ResizeToContents
        )
        self.ui.insuranceTable.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.ui.insuranceTable.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )
        layout.addWidget(self.ui.insuranceTable)
        
    def setup_login_page(self):
        """设置登录页面"""
        # 创建登录页面
        self.ui.loginPage = QtWidgets.QWidget()
        self.ui.stackedWidget.addWidget(self.ui.loginPage)
        
        # 创建页面布局
        layout = QtWidgets.QVBoxLayout(self.ui.loginPage)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # 创建登录表单
        form_layout = QtWidgets.QFormLayout()
        
        # 用户名输入框
        self.ui.username = QtWidgets.QLineEdit()
        form_layout.addRow("用户名：", self.ui.username)
        
        # 密码输入框
        self.ui.password = QtWidgets.QLineEdit()
        self.ui.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        form_layout.addRow("密码：", self.ui.password)
        
        # 添加表单到布局
        layout.addLayout(form_layout)
        
        # 登录按钮
        self.ui.loginButton = QtWidgets.QPushButton("登录")
        self.ui.loginButton.clicked.connect(self.do_login)
        layout.addWidget(self.ui.loginButton)
        
        # 禁用所有功能按钮
        self.disable_buttons()
        
        # 显示登录页面
        self.show_login_page()
        
    def show_login_page(self):
        """显示登录页面"""
        self.ui.stackedWidget.setCurrentWidget(self.ui.loginPage)
        
    def do_login(self):
        """处理登录"""
        username = self.ui.username.text().strip()
        password = self.ui.password.text()
        
        if not username or not password:
            QMessageBox.warning(self, "错误", "请输入用户名和密码")
            return
            
        # 验证用户名和密码
        self.db.cursor.execute(
            'SELECT password_hash FROM users WHERE username = ?',
            (username,)
        )
        result = self.db.cursor.fetchone()
        
        if result and result[0] == password:  # 这里应该使用proper密码哈希验证
            self.current_username = username
            self.enable_buttons()
            self.ui.stackedWidget.setCurrentWidget(self.ui.page)  # 切换到主页面
            QMessageBox.information(self, "成功", "登录成功")
        else:
            QMessageBox.warning(self, "错误", "用户名或密码错误")
            
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

