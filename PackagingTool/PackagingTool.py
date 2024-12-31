"""
Python程序打包工具 (Python Program Packaging Tool)
功能：将Python程序打包为独立的exe可执行文件
作者：s-Ruthless
创建时间：2024-12-31
最后修改：2024-12-31
版本：1.0
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import sys
import shutil


class PackagingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python程序打包工具")
        self.root.geometry("700x500")
        self.root.configure(bg="#ffffff")

        # 初始化变量
        self.python_file = tk.StringVar()
        self.icon_file = tk.StringVar()
        self.output_name = tk.StringVar()
        self.console_var = tk.BooleanVar(value=False)

        # 设置样式
        self.setup_styles()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 创建界面元素
        self.create_widgets()
        
        # 配置网格权重
        self.configure_grid()

    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')

        # 基础样式
        style.configure(".",
                       background="#ffffff",
                       foreground="#333333",
                       font=('Microsoft YaHei UI', 9))
        
        # 设置按钮样式
        style.configure("TButton",
                       padding=(10, 5),
                       font=('Microsoft YaHei UI', 9),
                       background="#4CAF50",
                       foreground="#ffffff",
                       borderwidth=0,
                       relief="flat")
        
        style.map("TButton",
                  foreground=[('active', '#ffffff'),
                             ('disabled', '#999999')],
                  background=[('active', '#45a049'),
                             ('disabled', '#cccccc')])

        # 设置标签样式
        style.configure("TLabel",
                       font=('Microsoft YaHei UI', 9),
                       background="#ffffff")
        
        # 设置框架样式
        style.configure("TLabelframe",
                       background="#ffffff",
                       padding=8,
                       relief="groove",
                       borderwidth=1)
        
        style.configure("TLabelframe.Label",
                       font=('Microsoft YaHei UI', 9, 'bold'),
                       background="#ffffff",
                       foreground="#1565C0")

        # 设置Entry样式
        style.configure("TEntry",
                       font=('Microsoft YaHei UI', 9, 'bold'),
                       padding=5,
                       relief="groove",
                       borderwidth=1)

        # 设置打包按钮特殊样式
        style.configure("Package.TButton",
                       padding=(20, 8),
                       font=('Microsoft YaHei UI', 10, 'bold'),
                       background="#2196F3",
                       borderwidth=0,
                       relief="flat")
        
        style.map("Package.TButton",
                  foreground=[('active', '#ffffff'),
                             ('disabled', '#999999')],
                  background=[('active', '#1976D2'),
                             ('disabled', '#cccccc')])

    def create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = ttk.Label(
            self.main_frame,
            text="Python程序打包工具",
            font=('Microsoft YaHei UI', 16, 'bold'),
            foreground="#1565C0"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # Python文件选择
        file_frame = ttk.LabelFrame(self.main_frame, text="程序文件")
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        
        ttk.Entry(
            file_frame,
            textvariable=self.python_file,
            width=50,
            style="TEntry"
        ).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Button(
            file_frame,
            text="选择文件",
            command=self.select_python_file,
            width=12
        ).grid(row=0, column=1, padx=5, pady=5)

        # 图标选择
        icon_frame = ttk.LabelFrame(self.main_frame, text="程序图标")
        icon_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        
        ttk.Entry(
            icon_frame,
            textvariable=self.icon_file,
            width=50,
            style="TEntry"
        ).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Button(
            icon_frame,
            text="选择图标",
            command=self.select_icon_file,
            width=12
        ).grid(row=0, column=1, padx=5, pady=5)

        # 输出设置
        output_frame = ttk.LabelFrame(self.main_frame, text="输出设置")
        output_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        
        ttk.Label(output_frame, text="程序名称:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(
            output_frame,
            textvariable=self.output_name,
            width=30,
            style="TEntry"
        ).grid(row=0, column=1, padx=5, pady=5)

        ttk.Checkbutton(
            output_frame,
            text="显示控制台窗口",
            variable=self.console_var
        ).grid(row=0, column=2, padx=5, pady=5)

        # 打包按钮
        package_btn = ttk.Button(
            self.main_frame,
            text="开始打包",
            command=self.start_packaging,
            style="Package.TButton"
        )
        package_btn.grid(row=4, column=0, columnspan=2, pady=15)

        # 日志区域
        log_frame = ttk.LabelFrame(self.main_frame, text="打包日志")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建日志文本框的容器框架
        log_container = ttk.Frame(log_frame)
        log_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_container.grid_columnconfigure(0, weight=1)
        log_container.grid_rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(
            log_container,
            height=10,
            font=('Microsoft YaHei UI', 9),
            wrap=tk.WORD,
            background="#ffffff",
            relief="groove",
            borderwidth=1,
            highlightthickness=0
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(log_container, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)

        # 配置日志框架的权重
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)

    def configure_grid(self):
        """配置网格权重"""
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(5, weight=1)

    def select_python_file(self):
        """选择Python文件"""
        file = filedialog.askopenfilename(
            filetypes=[("Python Files", "*.py")]
        )
        if file:
            self.python_file.set(file)
            # 自动设置输出名称（不管是否已有值都更新）
            default_name = os.path.splitext(os.path.basename(file))[0]
            self.output_name.set(default_name)
            # 清空日志
            self.log_text.delete(1.0, tk.END)
            self.log_message(f"已选择文件: {file}")
            self.log_message(f"默认输出名称: {default_name}")

    def select_icon_file(self):
        """选择图标文件"""
        file = filedialog.askopenfilename(
            filetypes=[("Icon Files", "*.ico")]
        )
        if file:
            self.icon_file.set(file)

    def log_message(self, message):
        """添加日志消息"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def check_pyinstaller(self):
        """检查是否安装了PyInstaller"""
        try:
            # 使用 pip list 命令检查
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return "pyinstaller" in result.stdout.lower()
        except Exception:
            return False

    def install_pyinstaller(self):
        """安装PyInstaller"""
        try:
            self.log_message("正在安装 PyInstaller...")
            # 使用 pip install 命令安装
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", "pyinstaller"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 实时输出安装日志
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log_message(output.strip())
            
            # 获取错误输出
            _, stderr = process.communicate()
            if stderr:
                self.log_message(f"安装过程信息：\n{stderr}")
            
            if process.returncode == 0:
                self.log_message("PyInstaller 安装成功！")
                return True
            else:
                raise Exception(f"安装失败，返回码：{process.returncode}")
        except Exception as e:
            self.log_message(f"PyInstaller 安装失败: {str(e)}")
            return False

    def package_program(self):
        """执行打包操作"""
        try:
            python_file = self.python_file.get()
            icon_file = self.icon_file.get()
            output_name = self.output_name.get()
            show_console = self.console_var.get()

            if not python_file:
                messagebox.showerror("错误", "请选择要打包的Python文件！")
                return
            
            if not output_name:
                messagebox.showerror("错误", "请输入输出程序名称！")
                return

            # 检查并安装PyInstaller
            if not self.check_pyinstaller():
                self.log_message("未检测到 PyInstaller，准备安装...")
                if not self.install_pyinstaller():
                    messagebox.showerror("错误", "PyInstaller 安装失败，无法继续打包！")
                    return
            else:
                self.log_message("检测到 PyInstaller 已安装")

            # 构建命令
            cmd = [
                sys.executable,
                "-m",
                "PyInstaller",
                "--noconfirm",
                "--clean",
                "--onefile",
                "--noupx",  # 禁用UPX压缩
                "--disable-windowed-traceback",  # 禁用窗口化错误回溯
                "--debug=all"  # 添加调试信息
            ]

            # 添加图标（检查图标文件是否存在且有效）
            if icon_file and os.path.exists(icon_file):
                try:
                    # 验证图标文件
                    with open(icon_file, 'rb') as f:
                        header = f.read(4)
                        if header.startswith(b'\x00\x00\x01\x00'):  # ICO文件头标识
                            # 创建临时图标文件
                            temp_icon = os.path.join(os.path.dirname(python_file), "temp_icon.ico")
                            import shutil
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
                            # 解析输出类型
                            if "ERROR:" in line or "Error:" in line:
                                self.log_message(f"错误: {line}")
                            elif "WARNING:" in line or "Warning:" in line:
                                self.log_message(f"警告: {line}")
                            elif "INFO:" in line:
                                # 只显示重要的INFO信息
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
                        messagebox.showinfo("完成", "程序打包成功！\n已自动打开输出目录。\n\n注意：如果杀毒软件报警，请将程序添加到白名单。")
                    except Exception as e:
                        raise Exception(f"移动文件或清理临时文件时出错: {str(e)}")
                else:
                    raise Exception("未找到输出文件")
            else:
                # 获取最后的错误信息
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
            messagebox.showerror("错误", error_msg)
        finally:
            self.log_message("\n打包过程结束。")
            # 启用所有按钮
            for child in self.main_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.configure(state='normal')

    def start_packaging(self):
        """在新线程中启动打包过程"""
        # 禁用打包按钮
        for child in self.main_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.configure(state='disabled')
        
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        
        # 启动打包线程
        threading.Thread(target=self.package_program, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = PackagingApp(root)
    root.mainloop() 