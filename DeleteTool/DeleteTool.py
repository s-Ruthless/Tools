"""
文件批量删除工具 (Batch File Deletion Tool)
功能：用于批量删除指定文件夹中特定类型的文件
作者：s-Ruthless
创建时间：2024-12-31
最后修改：2024-12-31
版本：1.0
"""

import os
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QComboBox, QCheckBox, QTextEdit, QFileDialog,
                            QMessageBox, QFrame, QDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette
from PyQt6.QtWidgets import QGraphicsDropShadowEffect


class CustomMessageBox(QDialog):
    """自定义消息框"""
    def __init__(self, title, message, icon_type="info", parent=None):
        super().__init__(parent)
        self.setWindowTitle("")  # 移除标题
        self.setFixedSize(400, 180)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 内容框
        content_frame = QFrame(self)
        content_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
            }
        """)
        
        # 阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 40))
        content_frame.setGraphicsEffect(shadow)

        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(20)

        # 消息内容
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                line-height: 1.4;
            }
        """)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)

        ok_button = QPushButton("确定")
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_button.setFixedSize(100, 36)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2475a8;
            }
        """)
        ok_button.clicked.connect(self.accept)

        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addStretch()

        content_layout.addWidget(message_label)
        content_layout.addLayout(button_layout)
        layout.addWidget(content_frame)


class CustomConfirmDialog(QDialog):
    """自定义确认对话框"""
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("")  # 移除标题
        self.setFixedSize(450, 200)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 内容框
        content_frame = QFrame(self)
        content_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
            }
        """)
        
        # 阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 40))
        content_frame.setGraphicsEffect(shadow)

        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(20)

        # 消息内容
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                line-height: 1.4;
            }
        """)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        cancel_button = QPushButton("取消")
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.setFixedSize(100, 36)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #2c3e50;
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                border-color: #bdc3c7;
            }
            QPushButton:pressed {
                background-color: #f0f2f5;
            }
        """)
        cancel_button.clicked.connect(self.reject)

        confirm_button = QPushButton("确认删除")
        confirm_button.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_button.setFixedSize(100, 36)
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        confirm_button.clicked.connect(self.accept)

        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(confirm_button)
        button_layout.addStretch()

        content_layout.addWidget(message_label)
        content_layout.addLayout(button_layout)
        layout.addWidget(content_frame)


class DeleteWorker(QThread):
    """删除文件的工作线程"""
    progress = pyqtSignal(str)  # 进度信号
    finished = pyqtSignal(int)  # 完成信号，传递删除文件数量
    error = pyqtSignal(str)     # 错误信号

    def __init__(self, folder, extensions, include_subfolders):
        super().__init__()
        self.folder = folder
        self.extensions = extensions
        self.include_subfolders = include_subfolders

    def run(self):
        try:
            deleted_count = 0
            if self.include_subfolders:
                # 包含子文件夹的情况
                for root, _, files in os.walk(self.folder):
                    for file in files:
                        if any(file.lower().endswith(ext.lower()) for ext in self.extensions):
                            file_path = os.path.join(root, file)
                            os.remove(file_path)
                            self.progress.emit(f"已删除: {file_path}")
                            deleted_count += 1
            else:
                # 不包含子文件夹的情况
                for file in os.listdir(self.folder):
                    file_path = os.path.join(self.folder, file)
                    if os.path.isfile(file_path) and any(file.lower().endswith(ext.lower()) for ext in self.extensions):
                        os.remove(file_path)
                        self.progress.emit(f"已删除: {file_path}")
                        deleted_count += 1

            self.finished.emit(deleted_count)
        except Exception as e:
            self.error.emit(str(e))


class BatchDeleteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件批量删除工具")
        self.setMinimumSize(800, 600)
        # 设置窗口图标
        self.setWindowIcon(QIcon("deletetool.ico"))
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QLabel {
                color: #2c3e50;
                font-size: 12px;
            }
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e1e8ed;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
                min-height: 16px;
                selection-background-color: #3498db;
            }
            QLineEdit:hover {
                border: 2px solid #ccd6dd;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #f8f9fa;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 6px;
                border: none;
                background-color: #3498db;
                color: white;
                font-weight: bold;
                font-size: 13px;
                min-height: 16px;
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
            QPushButton#deleteButton {
                background-color: #e74c3c;
                font-size: 14px;
                padding: 10px 25px;
                min-height: 20px;
            }
            QPushButton#deleteButton:hover {
                background-color: #c0392b;
            }
            QPushButton#deleteButton:disabled {
                background-color: #bdc3c7;
            }
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #e1e8ed;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
                min-height: 16px;
                selection-background-color: #3498db;
            }
            QComboBox:hover {
                border: 2px solid #ccd6dd;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
                width: 0;
            }
            QTextEdit {
                border: none;
                background-color: white;
                font-size: 13px;
                padding: 10px;
                font-family: 'Consolas', 'Microsoft YaHei UI';
                line-height: 1.5;
                selection-background-color: #3498db;
                border-radius: 6px;
            }
            QFrame {
                background-color: white;
                border-radius: 8px;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f2f5;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #ccd6dd;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #bdc3c7;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        # 创建中央部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 标题
        title_label = QLabel("文件批量删除工具")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px;
            color: #2c3e50;
            font-weight: bold;
            margin: 5px 0px;
            padding: 5px;
        """)
        main_layout.addWidget(title_label)

        # 文件夹选择区域
        folder_frame = QFrame()
        folder_layout = QVBoxLayout(folder_frame)
        folder_layout.setContentsMargins(15, 10, 15, 10)
        folder_layout.setSpacing(8)
        
        folder_title = QLabel("选择文件夹")
        folder_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        folder_layout.addWidget(folder_title)
        
        folder_input_layout = QHBoxLayout()
        folder_input_layout.setSpacing(8)
        self.folder_path = QLineEdit()
        self.folder_path.setPlaceholderText("请选择要处理的文件夹...")
        folder_button = QPushButton("浏览...")
        folder_button.setFixedWidth(80)
        folder_button.clicked.connect(self.select_folder)
        folder_input_layout.addWidget(self.folder_path)
        folder_input_layout.addWidget(folder_button)
        folder_layout.addLayout(folder_input_layout)
        
        main_layout.addWidget(folder_frame)

        # 文件类型选择区域
        type_frame = QFrame()
        type_layout = QVBoxLayout(type_frame)
        type_layout.setContentsMargins(15, 10, 15, 10)
        type_layout.setSpacing(8)
        
        type_title = QLabel("文件类型")
        type_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        type_layout.addWidget(type_title)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.get_file_types())
        self.type_combo.setFixedHeight(45)
        self.type_combo.currentIndexChanged.connect(self.on_type_selected)
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
            QComboBox::down-arrow {
                image: url(ImageConvert/icons/down-arrow.png);
                width: 12px;
                height: 12px;
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
        
        self.extension_input = QLineEdit()
        self.extension_input.setPlaceholderText("手动输入文件扩展名，多个用逗号分隔...")
        
        type_layout.addWidget(self.type_combo)
        separator_label = QLabel("或")
        separator_label.setStyleSheet("color: #7f8c8d; font-weight: bold;")
        type_layout.addWidget(separator_label)
        type_layout.addWidget(self.extension_input)
        
        main_layout.addWidget(type_frame)

        # 选项区域
        options_frame = QFrame()
        options_layout = QVBoxLayout(options_frame)
        options_layout.setContentsMargins(15, 10, 15, 10)
        options_layout.setSpacing(8)
        
        options_title = QLabel("选项")
        options_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        options_layout.addWidget(options_title)
        
        self.include_subfolders = QCheckBox("包含子文件夹")
        self.include_subfolders.setStyleSheet("""
            QCheckBox {
                color: #2c3e50;
                font-size: 13px;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border: 2px solid #e1e8ed;
                border-radius: 6px;
                background-color: white;
            }
            QCheckBox::indicator:hover {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
                image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M9.707 14.293l-3-3c-.391-.391-1.023-.391-1.414 0s-.391 1.023 0 1.414l3.707 3.707c.391.391 1.023.391 1.414 0l7.707-7.707c.391-.391.391-1.023 0-1.414s-1.023-.391-1.414 0l-7 7z'/%3E%3C/svg%3E");
            }
            QCheckBox::indicator:checked:hover {
                background-color: #2980b9;
                border-color: #2980b9;
            }
        """)
        options_layout.addWidget(self.include_subfolders)
        
        main_layout.addWidget(options_frame)

        # 删除按钮
        self.delete_button = QPushButton("开始删除")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.delete_files)
        self.delete_button.setFixedHeight(35)
        button_container = QHBoxLayout()
        button_container.addStretch()
        button_container.addWidget(self.delete_button)
        button_container.addStretch()
        main_layout.addLayout(button_container)

        # 日志区域
        log_frame = QFrame()
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(15, 10, 15, 10)
        log_layout.setSpacing(8)
        
        log_title = QLabel("操作日志")
        log_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        log_layout.addWidget(log_title)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        main_layout.addWidget(log_frame)

        # 设置阴影效果
        for frame in [folder_frame, type_frame, options_frame, log_frame]:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setXOffset(0)
            shadow.setYOffset(2)
            shadow.setColor(QColor(0, 0, 0, 20))
            frame.setGraphicsEffect(shadow)

        # 设置伸缩因子
        main_layout.setStretch(4, 1)

    def get_file_types(self):
        """获取文件类型列表"""
        return [
            "选择文件类型...",
            ".txt - 文本文件",
            ".doc,.docx - Word文档",
            ".xls,.xlsx - Excel表格",
            ".ppt,.pptx - PowerPoint演示文稿",
            ".pdf - PDF文档",
            ".jpg,.jpeg - JPEG图片",
            ".png - PNG图片",
            ".gif - GIF图片",
            ".bmp - BMP图片",
            ".tiff - TIFF图片",
            ".psd - Photoshop文件",
            ".ai - Illustrator文件",
            ".mp3 - MP3音频",
            ".wav - WAV音频",
            ".flac - FLAC音频",
            ".mp4 - MP4视频",
            ".avi - AVI视频",
            ".mkv - MKV视频",
            ".mov - MOV视频",
            ".wmv - WMV视频",
            ".zip - ZIP压缩包",
            ".rar - RAR压缩包",
            ".7z - 7Z压缩包",
            ".tar - TAR归档文件",
            ".gz - GZIP压缩文件",
            ".exe - 可执行文件",
            ".msi - Windows安装包",
            ".dll - 动态链接库",
            ".sys - 系统文件",
            ".tmp,.temp - 临时文件",
            ".log - 日志文件",
            ".bak - 备份文件",
            ".old - 旧文件",
            ".ini - 配置文件",
            ".cfg - 配置文件",
            ".html,.htm - 网页文件",
            ".css - 样式表文件",
            ".js - JavaScript文件",
            ".php - PHP文件",
            ".asp - ASP文件",
            ".jsp - JSP文件",
            ".xml - XML文件",
            ".json - JSON文件",
            ".sql - SQL文件",
            ".db - 数据库文件",
            ".py - Python源代码",
            ".java - Java源代码",
            ".cpp - C++源代码",
            ".h - C/C++头文件"
        ]

    def select_folder(self):
        """选择文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.folder_path.setText(folder)

    def on_type_selected(self, index):
        """文件类型选择处理"""
        if index > 0:
            selected = self.type_combo.currentText()
            ext = selected.split(' - ')[0]
            self.extension_input.setText(ext)

    def log_message(self, message):
        """添加日志消息"""
        self.log_text.append(message)

    def delete_files(self):
        """删除文件操作"""
        folder = self.folder_path.text()
        if not folder:
            dialog = CustomMessageBox("提示", "请先选择文件夹！", "info", self)
            dialog.exec()
            return

        extensions = [ext.strip() for ext in self.extension_input.text().split(',') if ext.strip()]
        if not extensions:
            dialog = CustomMessageBox("提示", "请输入要删除的文件扩展名！", "info", self)
            dialog.exec()
            return

        # 确认对话框
        confirm_dialog = CustomConfirmDialog(
            "确认操作",
            f"确定要删除以下文件吗？\n\n路径：{folder}\n类型：{', '.join(extensions)}",
            self
        )

        if confirm_dialog.exec() == QDialog.DialogCode.Accepted:
            # 禁用按钮
            self.delete_button.setEnabled(False)
            
            # 创建并启动工作线程
            self.worker = DeleteWorker(folder, extensions, self.include_subfolders.isChecked())
            self.worker.progress.connect(self.log_message)
            self.worker.finished.connect(self.on_delete_finished)
            self.worker.error.connect(self.on_delete_error)
            self.worker.start()

    def on_delete_finished(self, count):
        """删除完成处理"""
        self.log_message(f"\n共删除了 {count} 个文件")
        dialog = CustomMessageBox("完成", f"成功删除了 {count} 个文件！", "info", self)
        dialog.exec()
        self.delete_button.setEnabled(True)

    def on_delete_error(self, error_msg):
        """删除错误处理"""
        self.log_message(f"\n错误：{error_msg}")
        dialog = CustomMessageBox("错误", f"操作失败：{error_msg}", "error", self)
        dialog.exec()
        self.delete_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BatchDeleteApp()
    window.show()
    sys.exit(app.exec())