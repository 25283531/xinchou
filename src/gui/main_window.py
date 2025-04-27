import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(current_dir)

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog
from src.modules.attendance_import import AttendanceImporter

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("薪酬计算系统")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 添加导入按钮
        import_btn = QPushButton("导入考勤数据")
        import_btn.clicked.connect(self.import_attendance)
        layout.addWidget(import_btn)
        
        # 初始化考勤导入器
        self.attendance_importer = AttendanceImporter(None)  # 暂时传入None作为数据库连接
        
    def import_attendance(self):
        """处理考勤数据导入"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择考勤数据文件",
            "",
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv)"
        )
        
        if file_path:
            # 验证文件
            if self.attendance_importer.validate_file(file_path):
                # 导入数据
                result = self.attendance_importer.import_attendance(file_path)
                if result['status'] == 'success':
                    QtWidgets.QMessageBox.information(
                        self,
                        "成功",
                        f"成功导入{result['success']}条记录"
                    )
                else:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "失败",
                        f"导入失败：{result['message']}"
                    )
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "错误",
                    "文件格式不正确或缺少必要字段"
                )

# 启动应用的代码
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())