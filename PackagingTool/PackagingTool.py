"""
Python程序打包工具 (Python Program Packaging Tool)
功能：将Python程序打包为独立的exe可执行文件
作者：s-Ruthless
创建时间：2024-12-31
最后修改：2024-12-31
版本：1.0
"""

import os
import sys
import threading
import subprocess
import shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QCheckBox, QTextEdit, QFileDialog, QFrame, QDialog)
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect


class PackageWorker(QObject):
    """打包工作线程的信号处理类"""
    finished = pyqtSignal()
    log_message = pyqtSignal(str)
    show_message = pyqtSignal(str)
    enable_button = pyqtSignal(bool)


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


class PackagingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = PackageWorker()
        self.worker.log_message.connect(self._log_message)
        self.worker.show_message.connect(self._show_message)
        self.worker.enable_button.connect(self._enable_button)
        
        self.setWindowTitle("Python程序打包工具")
        self.setFixedSize(800, 600)
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PackagingTool.ico")
        self.setWindowIcon(QIcon(icon_path))
        
        # 创建主窗口部件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 8, 15, 8)
        main_layout.setSpacing(4)

        # 文件选择区域
        file_frame = QFrame()
        file_layout = QVBoxLayout(file_frame)
        file_layout.setContentsMargins(15, 8, 15, 8)
        file_layout.setSpacing(6)
        
        # Python文件选择
        file_title = QLabel("程序文件")
        file_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        file_layout.addWidget(file_title)
        
        file_input_layout = QHBoxLayout()
        file_input_layout.setSpacing(8)
        
        self.python_file_path = QLineEdit()
        self.python_file_path.setReadOnly(True)
        self.python_file_path.setMinimumWidth(300)
        self.python_file_path.setFixedHeight(45)
        self.python_file_path.setStyleSheet("""
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
        file_input_layout.addWidget(self.python_file_path, 1)
        
        select_file_button = QPushButton("选择文件")
        select_file_button.setFixedSize(120, 45)
        select_file_button.setCursor(Qt.CursorShape.PointingHandCursor)
        select_file_button.clicked.connect(self.select_python_file)
        select_file_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
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
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        file_input_layout.addWidget(select_file_button)
        file_layout.addLayout(file_input_layout)
        main_layout.addWidget(file_frame)

        # 图标选择区域
        icon_frame = QFrame()
        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setContentsMargins(15, 8, 15, 8)
        icon_layout.setSpacing(6)
        
        icon_title = QLabel("程序图标")
        icon_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        icon_layout.addWidget(icon_title)
        
        icon_input_layout = QHBoxLayout()
        icon_input_layout.setSpacing(8)
        
        self.icon_file_path = QLineEdit()
        self.icon_file_path.setReadOnly(True)
        self.icon_file_path.setMinimumWidth(300)
        self.icon_file_path.setFixedHeight(45)
        self.icon_file_path.setStyleSheet("""
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
        icon_input_layout.addWidget(self.icon_file_path, 1)
        
        select_icon_button = QPushButton("选择图标")
        select_icon_button.setFixedSize(120, 45)
        select_icon_button.setCursor(Qt.CursorShape.PointingHandCursor)
        select_icon_button.clicked.connect(self.select_icon_file)
        select_icon_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
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
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        icon_input_layout.addWidget(select_icon_button)
        icon_layout.addLayout(icon_input_layout)
        main_layout.addWidget(icon_frame)

        # 输出设置区域
        output_frame = QFrame()
        output_layout = QVBoxLayout(output_frame)
        output_layout.setContentsMargins(15, 8, 15, 8)
        output_layout.setSpacing(6)
        
        output_title = QLabel("输出设置")
        output_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        output_layout.addWidget(output_title)
        
        output_input_layout = QHBoxLayout()
        output_input_layout.setSpacing(8)
        
        name_label = QLabel("程序名称:")
        name_label.setStyleSheet("color: #2c3e50; font-size: 13px;")
        output_input_layout.addWidget(name_label)
        
        self.output_name = QLineEdit()
        self.output_name.setFixedHeight(45)
        self.output_name.setStyleSheet("""
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
        output_input_layout.addWidget(self.output_name, 1)
        
        self.console_checkbox = QCheckBox("显示控制台窗口")
        self.console_checkbox.setStyleSheet("""
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
        output_input_layout.addWidget(self.console_checkbox)
        output_layout.addLayout(output_input_layout)
        main_layout.addWidget(output_frame)

        # 打包按钮
        package_container = QWidget()
        package_layout = QVBoxLayout(package_container)
        package_layout.setContentsMargins(0, 0, 0, 8)
        package_layout.setSpacing(0)
        
        self.package_button = QPushButton("开始打包")
        self.package_button.setFixedSize(160, 45)
        self.package_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.package_button.clicked.connect(self.start_packaging)
        self.package_button.setStyleSheet("""
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
        package_layout.addWidget(self.package_button, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(package_container)

        # 日志区域
        log_frame = QFrame()
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(15, 8, 15, 8)
        log_layout.setSpacing(6)
        
        log_title = QLabel("打包日志")
        log_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        log_layout.addWidget(log_title)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
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
        for frame in [file_frame, icon_frame, output_frame, log_frame]:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setXOffset(0)
            shadow.setYOffset(2)
            shadow.setColor(QColor(0, 0, 0, 20))
            frame.setGraphicsEffect(shadow)

        # 设置日志区域的伸缩因子
        main_layout.setStretch(4, 1)

    def select_python_file(self):
        """选择Python文件"""
        file, _ = QFileDialog.getOpenFileName(
            self,
            "选择Python文件",
            "",
            "Python Files (*.py)"
        )
        if file:
            self.python_file_path.setText(file)
            # 自动设置输出名称
            default_name = os.path.splitext(os.path.basename(file))[0]
            self.output_name.setText(default_name)
            # 清空日志
            self.log_text.clear()
            self.log_message(f"已选择文件: {file}")
            self.log_message(f"默认输出名称: {default_name}")

    def select_icon_file(self):
        """选择图标文件"""
        file, _ = QFileDialog.getOpenFileName(
            self,
            "选择图标文件",
            "",
            "Icon Files (*.ico)"
        )
        if file:
            self.icon_file_path.setText(file)

    def _log_message(self, message):
        """线程安全的日志更新"""
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def _show_message(self, message):
        """线程安全的显示消息框"""
        dialog = CustomMessageBox(message, self)
        dialog.exec()

    def _enable_button(self, enabled):
        """线程安全的按钮状态更新"""
        self.package_button.setEnabled(enabled)

    def log_message(self, message):
        """发送日志消息信号"""
        self.worker.log_message.emit(message)

    def package_program(self):
        """执行打包操作"""
        try:
            python_file = self.python_file_path.text()
            icon_file = self.icon_file_path.text()
            output_name = self.output_name.text()
            show_console = self.console_checkbox.isChecked()

            if not python_file:
                self.worker.show_message.emit("请选择要打包的Python文件！")
                self.worker.enable_button.emit(True)
                return
            
            if not output_name:
                self.worker.show_message.emit("请输入输出程序名称！")
                self.worker.enable_button.emit(True)
                return

            # 构建命令
            cmd = [
                sys.executable,
                "-m",
                "PyInstaller",
                "--noconfirm",
                "--clean",
                "--onefile",
                "--noupx",
                "--disable-windowed-traceback",
                "--debug=all"
            ]

            # 添加图标
            if icon_file and os.path.exists(icon_file):
                try:
                    with open(icon_file, 'rb') as f:
                        header = f.read(4)
                        if header.startswith(b'\x00\x00\x01\x00'):
                            temp_icon = os.path.join(os.path.dirname(python_file), "temp_icon.ico")
                            shutil.copy2(icon_file, temp_icon)
                            cmd.extend(["--icon", temp_icon])
                            self.log_message("已添加图标文件")
                        else:
                            self.log_message("警告: 无效的图标文件格式，将使用默认图标")
                except Exception as e:
                    self.log_message(f"警告: 读取图标文件时出错，将使用默认图标: {str(e)}")

            # 控制台窗口设置
            if not show_console:
                cmd.append("--noconsole")

            # 输出名称
            cmd.extend(["--name", output_name])

            # Python文件
            cmd.append(python_file)

            # 设置工作目录
            work_dir = os.path.dirname(python_file)
            
            # 执行打包
            self.log_message("开始打包...")
            self.log_message(f"执行命令: {' '.join(cmd)}")
            self.log_message("正在处理，请稍候...")

            # 创建环境变量副本并设置编码
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            
            # 使用subprocess.Popen执行命令
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=work_dir,
                env=env,
                encoding='utf-8',
                errors='replace'
            )

            # 读取输出的函数
            def read_output(pipe, is_error=False):
                try:
                    while True:
                        line = pipe.readline()
                        if not line:
                            break
                        line = line.strip()
                        if line:
                            if "ERROR:" in line or "Error:" in line:
                                self.log_message(f"错误: {line}")
                            elif "WARNING:" in line or "Warning:" in line:
                                self.log_message(f"警告: {line}")
                            elif "INFO:" in line:
                                if any(key in line.lower() for key in [
                                    "building", "copying icon", "appending", "completed successfully"
                                ]):
                                    self.log_message(f"信息: {line}")
                            else:
                                self.log_message(line)
                except Exception as e:
                    self.log_message(f"读取输出时出错: {str(e)}")

            # 启动读取线程
            stdout_thread = threading.Thread(target=read_output, args=(process.stdout,))
            stderr_thread = threading.Thread(target=read_output, args=(process.stderr, True))
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()

            # 等待进程完成
            return_code = process.wait()

            # 等待线程完成
            stdout_thread.join(timeout=1)
            stderr_thread.join(timeout=1)

            # 清理临时图标文件
            try:
                temp_icon = os.path.join(work_dir, "temp_icon.ico")
                if os.path.exists(temp_icon):
                    os.remove(temp_icon)
            except:
                pass

            # 检查结果
            if return_code == 0:
                dist_dir = os.path.join(work_dir, "dist")
                exe_path = os.path.join(dist_dir, f"{output_name}.exe")
                if os.path.exists(exe_path):
                    # 移动exe文件到源文件同级目录
                    target_exe_path = os.path.join(work_dir, f"{output_name}.exe")
                    try:
                        # 如果目标位置已存在同名文件，先删除
                        if os.path.exists(target_exe_path):
                            os.remove(target_exe_path)
                        # 移动文件
                        shutil.move(exe_path, target_exe_path)
                        
                        # 清理临时文件和目录
                        build_dir = os.path.join(work_dir, "build")
                        spec_file = os.path.join(work_dir, f"{output_name}.spec")
                        dist_dir = os.path.join(work_dir, "dist")
                        
                        if os.path.exists(build_dir):
                            shutil.rmtree(build_dir)
                        if os.path.exists(spec_file):
                            os.remove(spec_file)
                        if os.path.exists(dist_dir):
                            shutil.rmtree(dist_dir)
                            
                        self.log_message(f"\n{'='*50}")
                        self.log_message("打包成功！")
                        self.log_message(f"输出文件: {os.path.abspath(target_exe_path)}")
                        self.log_message(f"{'='*50}\n")
                        
                        # 添加提示信息
                        self.log_message("注意事项：")
                        self.log_message("1. 如果杀毒软件报警，请将程序添加到白名单")
                        self.log_message("2. 首次运行可能需要以管理员身份运行")
                        self.log_message("3. 运行前请确保目标计算机已安装所需的运行环境")
                        
                        # 打开输出目录
                        os.startfile(os.path.dirname(target_exe_path))
                        self.worker.show_message.emit("程序打包成功！\n已自动打开输出目录。\n\n注意：如果杀毒软件报警，请将程序添加到白名单。")
                    except Exception as e:
                        raise Exception(f"移动文件或清理临时文件时出错: {str(e)}")
                else:
                    raise Exception("未找到输出文件")
            else:
                stdout, stderr = process.communicate()
                error_details = []
                
                if stdout:
                    error_details.append("标准输出:")
                    error_details.append(stdout.strip())
                
                if stderr:
                    error_details.append("\n错误输出:")
                    error_details.append(stderr.strip())
                
                # 检查日志文件
                warn_file = os.path.join(work_dir, "build", output_name, f"warn-{output_name}.txt")
                if os.path.exists(warn_file):
                    try:
                        with open(warn_file, 'r', encoding='utf-8') as f:
                            warnings = f.read().strip()
                            if warnings:
                                error_details.append("\n警告日志:")
                                error_details.append(warnings)
                    except:
                        pass
                
                error_msg = "\n".join(error_details) if error_details else "未知错误"
                if "WinError 225" in error_msg:
                    error_msg = "打包失败：Windows安全中心阻止了操作\n\n解决方法：\n1. 暂时关闭Windows Defender实时保护\n2. 将打包目录添加到排除项\n3. 使用管理员权限运行打包工具"
                
                raise Exception(f"打包失败，返回码：{return_code}\n{error_msg}")

        except Exception as e:
            error_msg = f"打包过程中出现错误：{str(e)}"
            self.log_message(error_msg)
            self.worker.show_message.emit(error_msg)
        finally:
            self.log_message("\n打包过程结束。")
            self.worker.enable_button.emit(True)

    def start_packaging(self):
        """在新线程中启动打包过程"""
        self.worker.enable_button.emit(False)
        self.log_text.clear()
        threading.Thread(target=self.package_program, daemon=True).start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PackagingApp()
    window.show()
    sys.exit(app.exec()) 