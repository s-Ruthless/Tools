"""
密码生成工具 (Password Generation Tool)
功能：支持多种类型的密码生成
作者：s-Ruthless
创建时间：2025-01-11
最后修改：2025-01-11
版本：1.0
"""

import sys
import os
import random
import string
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QComboBox, QSpinBox, QTextEdit, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

class PasswordGenerator:
    """密码生成器类"""
    @staticmethod
    def generate_password(length, password_type):
        if password_type == "纯数字":
            chars = string.digits
        elif password_type == "纯小写字母":
            chars = string.ascii_lowercase
        elif password_type == "纯大写字母":
            chars = string.ascii_uppercase
        elif password_type == "数字 + 小写字母":
            chars = string.digits + string.ascii_lowercase
        elif password_type == "数字 + 大写字母":
            chars = string.digits + string.ascii_uppercase
        elif password_type == "大小写字母":
            chars = string.ascii_letters
        elif password_type == "数字 + 大小写字母":
            chars = string.digits + string.ascii_letters
        else:  # 数字 + 大小写字母 + 特殊字符
            chars = string.digits + string.ascii_letters + "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        return ''.join(random.choice(chars) for _ in range(length))

class PasswordToolApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("密码生成工具")
        self.setFixedSize(500, 600)
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(__file__), "PassWordTool.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 创建主窗口部件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # 密码类型选择区域
        type_frame = QFrame()
        type_layout = QVBoxLayout(type_frame)
        type_layout.setContentsMargins(15, 8, 15, 8)
        type_layout.setSpacing(6)
        
        type_title = QLabel("密码类型")
        type_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        type_layout.addWidget(type_title)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "纯数字",
            "纯小写字母",
            "纯大写字母",
            "数字 + 小写字母",
            "数字 + 大写字母",
            "大小写字母",
            "数字 + 大小写字母",
            "数字 + 大小写字母 + 特殊字符"
        ])
        self.type_combo.setFixedHeight(45)
        self.type_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #e1e8ed;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                font-size: 13px;
                min-width: 150px;
            }
            QComboBox:hover {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #e1e8ed;
                border-radius: 6px;
                background-color: white;
                selection-background-color: #e1e8ed;
                outline: none;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                height: 32px;
                padding-left: 12px;
                background-color: transparent;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e1e8ed;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #e1e8ed;
                color: #2c3e50;
            }
        """)
        type_layout.addWidget(self.type_combo)
        
        # 添加间隔
        spacer = QWidget()
        spacer.setFixedHeight(12)
        type_layout.addWidget(spacer)
        
        # 密码长度设置区域
        length_title = QLabel("密码长度")
        length_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        type_layout.addWidget(length_title)
        
        self.length_spin = QSpinBox()
        self.length_spin.setRange(4, 32)
        self.length_spin.setValue(12)
        self.length_spin.setFixedHeight(45)
        self.length_spin.setStyleSheet("""
            QSpinBox {
                border: 2px solid #e1e8ed;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                font-size: 13px;
                min-width: 150px;
            }
            QSpinBox:hover {
                border: 2px solid #3498db;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: none;
                background: #f8f9fa;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #e9ecef;
            }
        """)
        type_layout.addWidget(self.length_spin)
        
        # 添加间隔
        spacer = QWidget()
        spacer.setFixedHeight(12)
        type_layout.addWidget(spacer)
        
        # 生成数量设置区域
        count_title = QLabel("生成数量")
        count_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        type_layout.addWidget(count_title)
        
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 100)
        self.count_spin.setValue(1)
        self.count_spin.setFixedHeight(45)
        self.count_spin.setStyleSheet("""
            QSpinBox {
                border: 2px solid #e1e8ed;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                font-size: 13px;
                min-width: 150px;
            }
            QSpinBox:hover {
                border: 2px solid #3498db;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: none;
                background: #f8f9fa;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #e9ecef;
            }
        """)
        type_layout.addWidget(self.count_spin)
        
        main_layout.addWidget(type_frame)
        
        # 添加间隔
        spacer = QWidget()
        spacer.setFixedHeight(8)
        main_layout.addWidget(spacer)
        
        # 生成按钮容器
        generate_container = QWidget()
        generate_layout = QVBoxLayout(generate_container)
        generate_layout.setContentsMargins(0, 0, 0, 8)
        generate_layout.setSpacing(0)
        
        self.generate_button = QPushButton("生成密码")
        self.generate_button.setFixedSize(110, 45)
        self.generate_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.generate_button.clicked.connect(self.generate_passwords)
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4757;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                padding: 0;
                min-height: 45px;
                line-height: 45px;
            }
            QPushButton:hover {
                background-color: #ff6b81;
            }
            QPushButton:pressed {
                background-color: #ee5253;
            }
            QPushButton:disabled {
                background-color: #b2bec3;
            }
        """)
        generate_layout.addWidget(self.generate_button, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(generate_container)
        
        # 结果显示区域
        result_frame = QFrame()
        result_layout = QVBoxLayout(result_frame)
        result_layout.setContentsMargins(15, 8, 15, 8)
        result_layout.setSpacing(6)
        
        result_title = QLabel("生成结果")
        result_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        result_layout.addWidget(result_title)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFixedHeight(200)
        self.result_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e1e8ed;
                border-radius: 6px;
                background-color: white;
                padding: 8px;
                font-size: 13px;
                font-family: Consolas, Monaco, monospace;
            }
        """)
        result_layout.addWidget(self.result_text)
        
        main_layout.addWidget(result_frame)
        
        # 设置阴影效果
        for frame in [type_frame, result_frame]:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setXOffset(0)
            shadow.setYOffset(2)
            shadow.setColor(QColor(0, 0, 0, 20))
            frame.setGraphicsEffect(shadow)
        
        # 调整整体布局的间距
        main_layout.setSpacing(4)
        main_layout.setContentsMargins(15, 8, 15, 8)
    
    def generate_passwords(self):
        """生成密码"""
        password_type = self.type_combo.currentText()
        length = self.length_spin.value()
        count = self.count_spin.value()
        
        generator = PasswordGenerator()
        passwords = [generator.generate_password(length, password_type) for _ in range(count)]
        
        # 显示结果
        self.result_text.clear()
        for i, password in enumerate(passwords, 1):
            self.result_text.append(f"密码 {i}：{password}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordToolApp()
    window.show()
    sys.exit(app.exec()) 