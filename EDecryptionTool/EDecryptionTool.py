"""
文本加解密工具 (Text Encryption/Decryption Tool)
功能：提供多种加密解密方式，支持文本的加密和解密
作者：s-Ruthless
创建时间：2024-01-01
最后修改：2024-01-01
版本：1.0
"""

import sys
import base64
import hashlib
import binascii
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QLabel, QTextEdit,
                            QComboBox, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
import os


class EDecryptionTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文本加解密工具")
        self.setFixedSize(800, 600)
        
        # 设置窗口图标
        self.setWindowIcon(QIcon("EDecryptionTool.ico"))
        
        # 创建主窗口部件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 8, 15, 8)
        main_layout.setSpacing(4)

        # 加密方式选择区域
        method_frame = QFrame()
        method_layout = QVBoxLayout(method_frame)
        method_layout.setContentsMargins(15, 8, 15, 8)
        method_layout.setSpacing(6)
        
        method_title = QLabel("加密方式")
        method_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        method_layout.addWidget(method_title)
        
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Base64编码（可解密）",
            "MD5加密（不可解密）",
            "SHA-1加密（不可解密）",
            "SHA-256加密（不可解密）",
            "SHA-512加密（不可解密）",
            "Fernet加密（可解密）",
            "Hex编码（可解密）",
            "URL编码（可解密）"
        ])
        self.method_combo.setFixedHeight(45)
        self.method_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #e1e8ed;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
                color: #2c3e50;
            }
            QComboBox:hover {
                border: 2px solid #3498db;
                background-color: #e1e8ed;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24'%3E%3Cpath fill='%23666' d='M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z'/%3E%3C/svg%3E");
                width: 16px;
                height: 16px;
            }
            QComboBox::down-arrow:hover {
                image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24'%3E%3Cpath fill='%233498db' d='M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z'/%3E%3C/svg%3E");
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
                height: 36px;
                padding-left: 10px;
                background-color: white;
                border: none;
                color: #2c3e50;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e1e8ed;
                border: none;
                color: #2c3e50;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #e1e8ed;
                border: none;
                color: #2c3e50;
            }
        """)
        method_layout.addWidget(self.method_combo)
        main_layout.addWidget(method_frame)

        # 输入区域
        input_frame = QFrame()
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(15, 8, 15, 8)
        input_layout.setSpacing(6)
        
        input_title = QLabel("输入文本")
        input_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        input_layout.addWidget(input_title)
        
        self.input_text = QTextEdit()
        self.input_text.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 2px solid #e1e8ed;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
            }
            QTextEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        input_layout.addWidget(self.input_text)
        main_layout.addWidget(input_frame)

        # 按钮区域
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(15, 8, 15, 8)
        button_layout.setSpacing(10)
        
        self.encrypt_button = QPushButton("加密")
        self.encrypt_button.setFixedSize(160, 45)
        self.encrypt_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.encrypt_button.clicked.connect(self.encrypt_text)
        self.encrypt_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2475a8;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        
        self.decrypt_button = QPushButton("解密")
        self.decrypt_button.setFixedSize(160, 45)
        self.decrypt_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.decrypt_button.clicked.connect(self.decrypt_text)
        self.decrypt_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4757;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
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
        
        button_layout.addStretch()
        button_layout.addWidget(self.encrypt_button)
        button_layout.addWidget(self.decrypt_button)
        button_layout.addStretch()
        main_layout.addWidget(button_frame)

        # 输出区域
        output_frame = QFrame()
        output_layout = QVBoxLayout(output_frame)
        output_layout.setContentsMargins(15, 8, 15, 8)
        output_layout.setSpacing(6)
        
        output_title = QLabel("输出结果")
        output_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        output_layout.addWidget(output_title)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 2px solid #e1e8ed;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
            }
        """)
        output_layout.addWidget(self.output_text)
        main_layout.addWidget(output_frame)

        # 设置阴影效果
        for frame in [method_frame, input_frame, button_frame, output_frame]:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setXOffset(0)
            shadow.setYOffset(2)
            shadow.setColor(QColor(0, 0, 0, 20))
            frame.setGraphicsEffect(shadow)

        # 设置输入输出区域的伸缩因子
        main_layout.setStretch(1, 1)  # 输入区域
        main_layout.setStretch(3, 1)  # 输出区域

    def encrypt_text(self):
        """加密文本"""
        input_text = self.input_text.toPlainText()
        if not input_text:
            self.output_text.setText("请输入要加密的文本")
            return

        method = self.method_combo.currentText().split("（")[0]  # 获取加密方式名称
        try:
            if method == "Base64编码":
                result = base64.b64encode(input_text.encode()).decode()
            elif method == "MD5加密":
                result = hashlib.md5(input_text.encode()).hexdigest()
            elif method == "SHA-1加密":
                result = hashlib.sha1(input_text.encode()).hexdigest()
            elif method == "SHA-256加密":
                result = hashlib.sha256(input_text.encode()).hexdigest()
            elif method == "SHA-512加密":
                result = hashlib.sha512(input_text.encode()).hexdigest()
            elif method == "Fernet加密":
                # 使用密码生成密钥
                password = "your-password".encode()  # 在实际应用中应该让用户输入密码
                salt = b"salt_"  # 在实际应用中应该使用随机salt
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(password))
                f = Fernet(key)
                result = f.encrypt(input_text.encode()).decode()
            elif method == "Hex编码":
                result = binascii.hexlify(input_text.encode()).decode()
            elif method == "URL编码":
                from urllib.parse import quote
                result = quote(input_text)
            
            self.output_text.setText(result)
        except Exception as e:
            self.output_text.setText(f"加密失败：{str(e)}")

    def decrypt_text(self):
        """解密文本"""
        input_text = self.input_text.toPlainText()
        if not input_text:
            self.output_text.setText("请输入要解密的文本")
            return

        method = self.method_combo.currentText().split("（")[0]  # 获取加密方式名称
        try:
            if method == "Base64编码":
                result = base64.b64decode(input_text.encode()).decode()
            elif method in ["MD5加密", "SHA-1加密", "SHA-256加密", "SHA-512加密"]:
                result = "此加密方式不可解密"
            elif method == "Fernet加密":
                # 使用密码生成密钥
                password = "your-password".encode()  # 在实际应用中应该让用户输入密码
                salt = b"salt_"  # 在实际应用中应该使用随机salt
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(password))
                f = Fernet(key)
                result = f.decrypt(input_text.encode()).decode()
            elif method == "Hex编码":
                # 移除所有空白字符
                hex_text = ''.join(input_text.split())
                # 验证是否为有效的十六进制字符串
                if not all(c in '0123456789abcdefABCDEF' for c in hex_text):
                    raise ValueError("输入包含非法的十六进制字符")
                # 如果长度为奇数，在前面补0
                if len(hex_text) % 2 != 0:
                    hex_text = '0' + hex_text
                result = binascii.unhexlify(hex_text.encode()).decode()
            elif method == "URL编码":
                from urllib.parse import unquote
                result = unquote(input_text)
            
            self.output_text.setText(result)
        except ValueError as e:
            self.output_text.setText(f"解密失败：{str(e)}")
        except Exception as e:
            self.output_text.setText(f"解密失败：{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EDecryptionTool()
    window.show()
    sys.exit(app.exec()) 