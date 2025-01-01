"""
图片批量转换工具 (Batch Image Conversion Tool)
功能：支持多种格式图片的批量转换
作者：s-Ruthless
创建时间：2024-01-01
最后修改：2024-01-01
版本：1.0
"""

import os
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QComboBox, QCheckBox, QTextEdit, QFileDialog,
                            QFrame, QDialog, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PIL import Image


class CustomMessageBox(QDialog):
    """自定义消息框"""
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("")
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


class ConvertWorker(QThread):
    """转换工作线程"""
    progress = pyqtSignal(str)  # 进度信号
    finished = pyqtSignal(int)  # 完成信号
    error = pyqtSignal(str)     # 错误信号
    no_matching_files = pyqtSignal()  # 无匹配文件信号

    def __init__(self, source_paths, source_format, target_format, target_folder=None, quality=95):
        super().__init__()
        self.source_paths = source_paths
        self.source_format = source_format.lower() if source_format != "自动检测" else None
        self.target_format = target_format.lower()
        self.target_folder = target_folder
        self.quality = quality
        self.is_running = True
        self.total_files = 0
        self.converted_files = 0

    def run(self):
        try:
            # 首先计算总文件数
            self.total_files = self._count_files()
            
            # 如果没有找到匹配的文件，发出信号并返回
            if self.total_files == 0:
                self.no_matching_files.emit()
                return

            converted_count = 0
            for source_path in self.source_paths:
                if not self.is_running:
                    break

                if os.path.isfile(source_path):
                    if self._is_valid_source_file(source_path):
                        self._convert_file(source_path)
                        converted_count += 1
                elif os.path.isdir(source_path):
                    for root, _, files in os.walk(source_path):
                        for file in files:
                            if not self.is_running:
                                break
                            file_path = os.path.join(root, file)
                            if self._is_valid_source_file(file_path):
                                self._convert_file(file_path)
                                converted_count += 1

            self.finished.emit(converted_count)
        except Exception as e:
            self.error.emit(str(e))

    def _count_files(self):
        """计算需要转换的文件总数"""
        count = 0
        for source_path in self.source_paths:
            if os.path.isfile(source_path):
                if self._is_valid_source_file(source_path):
                    count += 1
            elif os.path.isdir(source_path):
                for root, _, files in os.walk(source_path):
                    for file in files:
                        if self._is_valid_source_file(os.path.join(root, file)):
                            count += 1
        return count

    def _is_valid_source_file(self, filepath):
        """检查是否为有效的源文件"""
        ext = os.path.splitext(filepath)[1].lower()
        if self.source_format is None:  # 自动检测模式
            return ext in {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.ico'}
        else:
            # 根据选择的源格式进行验证
            format_map = {
                'png': '.png',
                'jpeg': ('.jpg', '.jpeg'),
                'jpg': ('.jpg', '.jpeg'),
                'bmp': '.bmp',
                'gif': '.gif',
                'tiff': '.tiff',
                'ico': '.ico',
                'webp': '.webp'
            }
            valid_extensions = format_map.get(self.source_format, ())
            if isinstance(valid_extensions, str):
                valid_extensions = (valid_extensions,)
            return ext in valid_extensions

    def _convert_file(self, source_path):
        try:
            # 获取目标路径
            filename = os.path.splitext(os.path.basename(source_path))[0]
            
            if self.target_folder:
                # 如果指定了目标文件夹，保持源文件的相对路径结构
                if os.path.isdir(self.source_paths[0]):
                    # 获取相对路径
                    rel_path = os.path.relpath(os.path.dirname(source_path), self.source_paths[0])
                    # 在目标文件夹中创建相同的目录结构
                    target_dir = os.path.join(self.target_folder, rel_path)
                    os.makedirs(target_dir, exist_ok=True)
                    target_path = os.path.join(target_dir, f"{filename}.{self.target_format}")
                else:
                    # 单个文件或多个文件的情况
                    target_path = os.path.join(self.target_folder, f"{filename}.{self.target_format}")
            else:
                # 如果没有指定目标文件夹，使用源文件所在目录
                target_path = os.path.join(os.path.dirname(source_path), f"{filename}.{self.target_format}")

            # 如果目标文件已存在，添加后缀
            counter = 1
            base_target_path = target_path
            while os.path.exists(target_path):
                target_path = os.path.join(
                    os.path.dirname(base_target_path),
                    f"{filename}_{counter}.{self.target_format}"
                )
                counter += 1

            # 转换图片
            with Image.open(source_path) as img:
                if self.target_format == 'jpg' or self.target_format == 'jpeg':
                    # JPEG不支持透明通道，需要特殊处理
                    if img.mode in ('RGBA', 'LA'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1])
                        background.save(target_path, quality=self.quality)
                    else:
                        img.convert('RGB').save(target_path, quality=self.quality)
                else:
                    img.save(target_path)

            self.converted_files += 1
            progress = int((self.converted_files / self.total_files) * 100)
            self.progress.emit(f"已转换: {source_path} -> {target_path} ({progress}%)")
        except Exception as e:
            self.progress.emit(f"转换失败: {source_path} - {str(e)}")

    def stop(self):
        """停止转换"""
        self.is_running = False


class ImageConvertApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图片批量转换工具")
        self.setMinimumSize(900, 700)  # 增加窗口尺寸
        # 设置窗口图标
        self.setWindowIcon(QIcon("ImageConvert.ico"))
        
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
            QPushButton#convertButton {
                background-color: #2ecc71;
                font-size: 14px;
                padding: 10px 25px;
                min-height: 20px;
            }
            QPushButton#convertButton:hover {
                background-color: #27ae60;
            }
            QPushButton#convertButton:disabled {
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
            QProgressBar {
                border: none;
                background-color: #f0f2f5;
                border-radius: 6px;
                text-align: center;
                font-size: 12px;
                color: #2c3e50;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 6px;
            }
        """)

        # 创建中央部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 标题
        title_label = QLabel("图片批量转换工具")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px;
            color: #2c3e50;
            font-weight: bold;
            margin: 5px 0px;
            padding: 5px;
        """)
        main_layout.addWidget(title_label)

        # 文件选择区域
        file_frame = QFrame()
        file_layout = QVBoxLayout(file_frame)
        file_layout.setContentsMargins(15, 8, 15, 8)
        file_layout.setSpacing(6)
        
        file_title = QLabel("文件选择")
        file_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        file_layout.addWidget(file_title)
        
        file_input_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        self.file_path.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e1e8ed;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        file_input_layout.addWidget(self.file_path)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        select_file_button = QPushButton("选择文件")
        select_file_button.setFixedSize(100, 36)
        select_file_button.setCursor(Qt.CursorShape.PointingHandCursor)
        select_file_button.clicked.connect(self.select_files)
        
        select_folder_button = QPushButton("选择文件夹")
        select_folder_button.setFixedSize(120, 36)
        select_folder_button.setCursor(Qt.CursorShape.PointingHandCursor)
        select_folder_button.clicked.connect(self.select_folder)
        
        for button in [select_file_button, select_folder_button]:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 0 15px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #2475a8;
                }
            """)
        
        button_layout.addWidget(select_file_button)
        button_layout.addWidget(select_folder_button)
        file_input_layout.addLayout(button_layout)
        file_layout.addLayout(file_input_layout)
        
        main_layout.addWidget(file_frame)

        # 添加间隔
        spacer = QWidget()
        spacer.setFixedHeight(10)  # 减小区域间距
        main_layout.addWidget(spacer)

        # 格式选择区域
        format_frame = QFrame()
        format_layout = QVBoxLayout(format_frame)
        format_layout.setContentsMargins(15, 8, 15, 8)
        format_layout.setSpacing(6)
        
        # 源格式选择
        source_format_title = QLabel("源文件格式")
        source_format_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        format_layout.addWidget(source_format_title)
        
        self.source_format_combo = QComboBox()
        self.source_format_combo.addItems([
            "自动检测",
            "PNG - 便携式网络图形",
            "JPEG/JPG - 联合图像专家组",
            "BMP - 位图",
            "GIF - 图形交换格式",
            "TIFF - 标签图像文件格式",
            "ICO - 图标",
            "WebP - 网页图片格式"
        ])
        self.source_format_combo.setFixedHeight(45)
        self.source_format_combo.setStyleSheet("""
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
        # 添加源格式改变事件处理
        self.source_format_combo.currentIndexChanged.connect(self.on_source_format_changed)
        format_layout.addWidget(self.source_format_combo)
        
        # 添加间隔（源格式和目标格式之间）
        spacer = QWidget()
        spacer.setFixedHeight(12)  # 减小间距
        format_layout.addWidget(spacer)
        
        # 目标格式选择
        target_format_title = QLabel("目标格式")
        target_format_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        format_layout.addWidget(target_format_title)
        
        self.target_format_combo = QComboBox()
        self.target_format_combo.addItems([
            "PNG - 便携式网络图形",
            "JPEG - 联合图像专家组",
            "BMP - 位图",
            "GIF - 图形交换格式",
            "TIFF - 标签图像文件格式",
            "ICO - 图标",
            "WebP - 网页图片格式"
        ])
        self.target_format_combo.setFixedHeight(45)
        self.target_format_combo.setStyleSheet("""
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
        format_layout.addWidget(self.target_format_combo)
        
        # 添加间隔（目标格式和目标文件夹之间）
        spacer = QWidget()
        spacer.setFixedHeight(12)  # 减小间距
        format_layout.addWidget(spacer)
        
        # 目标文件夹选择
        target_folder_title = QLabel("目标文件夹")
        target_folder_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        format_layout.addWidget(target_folder_title)
        
        target_folder_input_layout = QHBoxLayout()
        target_folder_input_layout.setSpacing(8)
        
        # 路径输入框
        self.target_folder_path = QLineEdit()
        self.target_folder_path.setReadOnly(True)
        self.target_folder_path.setMinimumWidth(300)
        self.target_folder_path.setFixedHeight(45)  # 增加输入框高度
        self.target_folder_path.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e1e8ed;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        target_folder_input_layout.addWidget(self.target_folder_path, 1)
        
        # 选择文件夹按钮
        select_target_folder_button = QPushButton("选择文件夹")
        select_target_folder_button.setFixedSize(120, 45)  # 增加按钮高度
        select_target_folder_button.setCursor(Qt.CursorShape.PointingHandCursor)
        select_target_folder_button.clicked.connect(self.select_target_folder)
        select_target_folder_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                padding: 0 15px;
                min-height: 36px;  /* 确保最小高度 */
                line-height: 36px;  /* 文字垂直居中 */
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
        target_folder_input_layout.addWidget(select_target_folder_button)
        
        format_layout.addLayout(target_folder_input_layout)
        
        # 添加间隔
        spacer = QWidget()
        spacer.setFixedHeight(4)  # 减小间距
        format_layout.addWidget(spacer)
        
        main_layout.addWidget(format_frame)

        # 添加间隔
        spacer = QWidget()
        spacer.setFixedHeight(8)
        main_layout.addWidget(spacer)

        # 转换按钮容器
        convert_container = QWidget()
        convert_layout = QVBoxLayout(convert_container)
        convert_layout.setContentsMargins(0, 0, 0, 8)  # 上边距设为0，保持下边距8px
        convert_layout.setSpacing(0)
        
        self.convert_button = QPushButton("开始转换")
        self.convert_button.setFixedSize(110, 45)
        self.convert_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.convert_button.clicked.connect(self.start_convert)
        self.convert_button.setStyleSheet("""
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
        convert_layout.addWidget(self.convert_button, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(convert_container)

        # 进度条
        progress_frame = QFrame()
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(15, 8, 15, 8)
        progress_layout.setSpacing(6)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e1e8ed;
                border-radius: 6px;
                background-color: #f0f2f5;
                text-align: center;
                font-size: 12px;
                color: #2c3e50;
                padding: 2px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 4px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        main_layout.addWidget(progress_frame)

        # 日志区域
        log_frame = QFrame()
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(15, 8, 15, 8)
        log_layout.setSpacing(6)
        
        log_title = QLabel("转换日志")
        log_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        log_layout.addWidget(log_title)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(150)  # 设置日志区域固定高度
        self.log_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e1e8ed;
                border-radius: 6px;
                background-color: white;
                padding: 8px;
                font-size: 13px;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        main_layout.addWidget(log_frame)

        # 设置阴影效果
        for frame in [file_frame, format_frame, progress_frame, log_frame]:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setXOffset(0)
            shadow.setYOffset(2)
            shadow.setColor(QColor(0, 0, 0, 20))
            frame.setGraphicsEffect(shadow)

        # 调整整体布局的间距
        main_layout.setSpacing(4)  # 减小布局间距
        main_layout.setContentsMargins(15, 8, 15, 8)  # 减小整体边距

        # 初始化成员变量
        self.selected_paths = []
        self.worker = None

    def select_files(self):
        """选择文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择图片文件",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp *.ico)"
        )
        if files:
            self.selected_paths = files
            self.file_path.setText("; ".join(files))
            # 设置目标文件夹为第一个文件所在的目录
            first_file_dir = os.path.dirname(files[0])
            self.target_folder_path.setText(first_file_dir)

    def select_folder(self):
        """选择源文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择源文件夹")
        if folder:
            self.selected_paths = [folder]
            self.file_path.setText(folder)
            # 更新目标文件夹路径
            self.target_folder_path.setText(folder)

    def select_target_folder(self):
        """选择目标文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择目标文件夹")
        if folder:
            # 检查是否选择了源文件夹或源文件所在目录作为目标
            if os.path.isdir(self.selected_paths[0]):
                source_folder = self.selected_paths[0]
            else:
                source_folder = os.path.dirname(self.selected_paths[0])

            if folder == source_folder:
                dialog = CustomMessageBox("目标文件夹不能与源文件夹相同！\n请选择其他文件夹。", self)
                dialog.exec()
                return
            self.target_folder_path.setText(folder)

    def log_message(self, message):
        """添加日志消息"""
        self.log_text.append(message)

    def on_source_format_changed(self):
        """源格式改变时的处理"""
        if self.selected_paths:
            # 创建临时工作线程来验证文件
            source_format = self.source_format_combo.currentText().split(' - ')[0]
            temp_worker = ConvertWorker(self.selected_paths, source_format, "png")  # 目标格式无关紧要
            file_count = temp_worker._count_files()
            
            if file_count == 0 and source_format != "自动检测":
                dialog = CustomMessageBox(
                    f"在选择的位置中未找到 {source_format} 格式的文件！\n请重新选择源格式或更改文件位置。",
                    self
                )
                dialog.exec()
                # 重置为自动检测
                self.source_format_combo.setCurrentText("自动检测")

    def start_convert(self):
        """开始转换"""
        if not self.selected_paths:
            dialog = CustomMessageBox("请先选择要转换的文件或文件夹！", self)
            dialog.exec()
            return

        # 获取源格式和目标格式
        source_format = self.source_format_combo.currentText().split(' - ')[0]
        target_format = self.target_format_combo.currentText().split(' - ')[0]

        # 获取目标文件夹
        target_folder = self.target_folder_path.text() or None

        # 验证是否有匹配的源文件
        temp_worker = ConvertWorker(self.selected_paths, source_format, target_format)
        file_count = temp_worker._count_files()
        
        if file_count == 0:
            if source_format == "自动检测":
                dialog = CustomMessageBox("在选择的位置中未找到任何支持的图片文件！", self)
            else:
                dialog = CustomMessageBox(
                    f"在选择的位置中未找到 {source_format} 格式的文件！\n请重新选择源格式或更改文件位置。",
                    self
                )
            dialog.exec()
            return

        # 禁用按钮
        self.convert_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_text.clear()

        # 创建并启动工作线程
        self.worker = ConvertWorker(self.selected_paths, source_format, target_format, target_folder)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_convert_finished)
        self.worker.error.connect(self.on_convert_error)
        self.worker.no_matching_files.connect(self.on_no_matching_files)
        self.worker.start()

    def on_progress(self, message):
        """处理进度更新"""
        self.log_message(message)
        # 从消息中提取进度百分比
        if "%" in message:
            try:
                progress = int(message.split("(")[-1].split("%")[0])
                self.progress_bar.setValue(progress)
            except:
                pass

    def on_convert_finished(self, count):
        """转换完成处理"""
        self.log_message(f"\n共转换了 {count} 个文件")
        self.progress_bar.setValue(100)
        dialog = CustomMessageBox(f"成功转换了 {count} 个文件！", self)
        dialog.exec()
        self.convert_button.setEnabled(True)

    def on_convert_error(self, error_msg):
        """转换错误处理"""
        self.log_message(f"\n错误：{error_msg}")
        dialog = CustomMessageBox(f"转换失败：{error_msg}", self)
        dialog.exec()
        self.convert_button.setEnabled(True)

    def on_no_matching_files(self):
        """处理无匹配文件的情况"""
        source_format = self.source_format_combo.currentText().split(' - ')[0]
        if source_format == "自动检测":
            dialog = CustomMessageBox("在选择的位置中未找到任何支持的图片文件！", self)
        else:
            dialog = CustomMessageBox(
                f"在选择的位置中未找到 {source_format} 格式的文件！\n请重新选择源格式或更改文件位置。",
                self
            )
        dialog.exec()
        self.convert_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageConvertApp()
    window.show()
    sys.exit(app.exec()) 