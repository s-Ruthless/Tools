"""
图片批量转换工具 (Image Batch Conversion Tool)
功能：支持多种格式图片的批量转换
作者：s-Ruthless
创建时间：2024-12-31
最后修改：2024-12-31
版本：1.0
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import threading


class ImageConvertApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片批量转换工具")
        self.root.geometry("800x650")  # 调整窗口大小
        self.root.configure(bg="#ffffff")  # 改为白色背景

        # 支持的图片格式
        self.supported_formats = {
            "PNG": ".png",
            "JPEG": ".jpg",
            "BMP": ".bmp",
            "GIF": ".gif",
            "TIFF": ".tiff",
            "ICO": ".ico",
            "WebP": ".webp"
        }

        # 初始化变量
        self.select_mode = tk.StringVar(value="folder")
        self.selected_files = []

        # 设置样式
        self.setup_styles()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")  # 减小内边距
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
        
        # 设置框架样式 - 简化边框
        style.configure("TLabelframe",
                       background="#ffffff",
                       padding=8,
                       relief="groove",  # 更改为groove样式
                       borderwidth=1)
        
        style.configure("TLabelframe.Label",
                       font=('Microsoft YaHei UI', 9, 'bold'),
                       background="#ffffff",
                       foreground="#1565C0")

        # 设置单选按钮样式
        style.configure("TRadiobutton",
                       font=('Microsoft YaHei UI', 9),
                       background="#ffffff")
        
        # 设置转换按钮特殊样式
        style.configure("Convert.TButton",
                       padding=(20, 8),
                       font=('Microsoft YaHei UI', 10, 'bold'),
                       background="#2196F3",
                       borderwidth=0,
                       relief="flat")
        
        style.map("Convert.TButton",
                  foreground=[('active', '#ffffff'),
                             ('disabled', '#999999')],
                  background=[('active', '#1976D2'),
                             ('disabled', '#cccccc')])

        # 设置进度条样式
        style.configure("TProgressbar",
                       thickness=16,
                       background="#2196F3",
                       troughcolor="#f0f0f0",
                       borderwidth=0)

        # 设置组合框样式
        style.configure("TCombobox",
                       font=('Microsoft YaHei UI', 9),
                       padding=2)
        
        # 设置Entry样式 - 简化边框
        style.configure("TEntry",
                       font=('Microsoft YaHei UI', 9, 'bold'),
                       padding=5,
                       relief="groove",
                       borderwidth=1)

    def create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = ttk.Label(
            self.main_frame,
            text="图片批量转换工具",
            font=('Microsoft YaHei UI', 16, 'bold'),  # 增大标题字号
            foreground="#1565C0"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # 源文件选择区域
        source_frame = ttk.LabelFrame(self.main_frame, text="源文件选择")
        source_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        
        # 选择模式
        mode_frame = ttk.Frame(source_frame)
        mode_frame.grid(row=0, column=0, columnspan=4, padx=5, pady=5)
        
        ttk.Label(mode_frame, text="选择模式:").pack(side=tk.LEFT, padx=5)
        modes = [
            ("文件夹", "folder"),
            ("单个文件", "single"),
            ("多个文件", "multiple")
        ]
        
        for text, mode in modes:
            ttk.Radiobutton(
                mode_frame,
                text=text,
                variable=self.select_mode,
                value=mode,
                command=self.update_source_button
            ).pack(side=tk.LEFT, padx=10)

        # 源文件路径显示和选择按钮
        path_frame = ttk.Frame(source_frame)
        path_frame.grid(row=1, column=0, columnspan=4, padx=5, pady=2)
        
        self.source_path = tk.StringVar()
        source_entry = ttk.Entry(
            path_frame,
            textvariable=self.source_path,
            width=55,
            style="TEntry",  # 应用新样式
            font=('Microsoft YaHei UI', 9, 'bold')  # 加粗字体
        )
        source_entry.pack(side=tk.LEFT, padx=5)
        
        self.source_btn = ttk.Button(
            path_frame,
            text="选择文件夹",
            command=self.select_source,
            width=12
        )
        self.source_btn.pack(side=tk.LEFT, padx=5)

        # 已选文件列表
        self.file_listbox = tk.Listbox(
            source_frame,
            height=5,
            width=75,
            selectmode=tk.EXTENDED,
            font=('Microsoft YaHei UI', 9),
            bg='white',
            relief="solid",  # 实线边框
            borderwidth=1,
            highlightthickness=0  # 移除焦点边框
        )
        self.file_listbox.grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # 滚动条
        file_scrollbar = ttk.Scrollbar(source_frame, orient="vertical", command=self.file_listbox.yview)
        file_scrollbar.grid(row=2, column=4, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=file_scrollbar.set)

        # 目标文件夹选择
        target_frame = ttk.LabelFrame(self.main_frame, text="目标文件夹")
        target_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        
        self.target_path = tk.StringVar()
        target_entry = ttk.Entry(
            target_frame,
            textvariable=self.target_path,
            width=55,
            style="TEntry",  # 应用新样式
            font=('Microsoft YaHei UI', 9, 'bold')  # 加粗字体
        )
        target_entry.grid(row=0, column=0, padx=5, pady=5)
        
        target_btn = ttk.Button(
            target_frame,
            text="选择文件夹",
            command=lambda: self.select_folder(self.target_path),
            width=12
        )
        target_btn.grid(row=0, column=1, padx=5, pady=5)

        # 格式选择
        format_frame = ttk.LabelFrame(self.main_frame, text="转换选项")
        format_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        
        options_frame = ttk.Frame(format_frame)
        options_frame.grid(row=0, column=0, padx=5, pady=5)
        
        # 源格式选择
        ttk.Label(options_frame, text="源格式:").grid(row=0, column=0, padx=5)
        self.source_format_var = tk.StringVar(value="所有格式")
        source_formats = ["所有格式"] + list(self.supported_formats.keys())
        source_format_combo = ttk.Combobox(
            options_frame,
            textvariable=self.source_format_var,
            values=source_formats,
            state="readonly",
            width=12
        )
        source_format_combo.grid(row=0, column=1, padx=5)
        
        # 目标格式选择
        ttk.Label(options_frame, text="目标格式:").grid(row=0, column=2, padx=5)
        self.format_var = tk.StringVar(value="PNG")
        format_combo = ttk.Combobox(
            options_frame,
            textvariable=self.format_var,
            values=list(self.supported_formats.keys()),
            state="readonly",
            width=12
        )
        format_combo.grid(row=0, column=3, padx=5)

        # 质量选择（仅用于JPEG）
        ttk.Label(options_frame, text="图片质量:").grid(row=0, column=4, padx=5)
        self.quality_var = tk.IntVar(value=95)
        quality_spin = ttk.Spinbox(
            options_frame,
            from_=1,
            to=100,
            textvariable=self.quality_var,
            width=8
        )
        quality_spin.grid(row=0, column=5, padx=5)

        # 转换按钮
        convert_btn = ttk.Button(
            self.main_frame,
            text="开始转换",
            command=self.start_conversion,
            style="Convert.TButton"
        )
        convert_btn.grid(row=4, column=0, columnspan=2, pady=8)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.main_frame,
            variable=self.progress_var,
            maximum=100,
            style="TProgressbar"
        )
        self.progress_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))

        # 日志区域
        log_frame = ttk.LabelFrame(self.main_frame, text="转换日志")
        log_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建日志文本框的容器框架
        log_container = ttk.Frame(log_frame)
        log_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_container.grid_columnconfigure(0, weight=1)
        log_container.grid_rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(
            log_container,
            height=8,
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
        self.main_frame.grid_rowconfigure(6, weight=1)

    def update_source_button(self):
        """根据选择模式更新源文件选择按钮文本"""
        mode = self.select_mode.get()
        if mode == "folder":
            self.source_btn.configure(text="选择文件夹")
        elif mode == "single":
            self.source_btn.configure(text="选择文件")
        else:
            self.source_btn.configure(text="选择文件")

    def select_source(self):
        """根据选择模式选择源文件或文件夹"""
        mode = self.select_mode.get()
        
        if mode == "folder":
            folder = filedialog.askdirectory()
            if folder:
                self.source_path.set(folder)
                self.selected_files = []
                self.update_file_list()
        else:
            filetypes = [("图片文件", [f"*{ext}" for ext in self.supported_formats.values()])]
            if mode == "single":
                files = filedialog.askopenfilename(filetypes=filetypes)
                if files:
                    self.selected_files = [files]
            else:  # multiple
                files = filedialog.askopenfilenames(filetypes=filetypes)
                if files:
                    self.selected_files = list(files)
            
            if self.selected_files:
                self.source_path.set("已选择 {} 个文件".format(len(self.selected_files)))
                self.update_file_list()

    def update_file_list(self):
        """更新文件列表显示"""
        self.file_listbox.delete(0, tk.END)
        
        if self.select_mode.get() == "folder":
            folder = self.source_path.get()
            if folder and os.path.exists(folder):
                for root, _, files in os.walk(folder):
                    for file in files:
                        if self.is_supported_file(file):
                            full_path = os.path.join(root, file)
                            self.file_listbox.insert(tk.END, os.path.relpath(full_path, folder))
        else:
            for file in self.selected_files:
                self.file_listbox.insert(tk.END, os.path.basename(file))

    def is_supported_file(self, filename):
        """检查文件是否为支持的格式"""
        source_format = self.source_format_var.get()
        if source_format == "所有格式":
            return filename.lower().endswith(tuple(f.lower() for f in self.supported_formats.values()))
        else:
            return filename.lower().endswith(self.supported_formats[source_format].lower())

    def select_folder(self, path_var):
        """选择文件夹"""
        folder = filedialog.askdirectory()
        if folder:
            path_var.set(folder)

    def log_message(self, message):
        """添加日志消息"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def get_files_to_convert(self):
        """获取需要转换的文件列表"""
        if self.select_mode.get() == "folder":
            folder = self.source_path.get()
            if not folder:
                return []
            
            files = []
            for root, _, filenames in os.walk(folder):
                for filename in filenames:
                    if self.is_supported_file(filename):
                        files.append(os.path.join(root, filename))
            return files
        else:
            return self.selected_files

    def convert_images(self):
        """执行图片转换"""
        target_dir = self.target_path.get()
        target_format = self.supported_formats[self.format_var.get()]
        quality = self.quality_var.get()
        source_format = self.source_format_var.get()

        if not target_dir:
            messagebox.showerror("错误", "请选择目标文件夹！")
            return

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # 获取要转换的文件
        image_files = self.get_files_to_convert()
        if not image_files:
            messagebox.showinfo("提示", "未找到需要转换的图片文件！")
            return

        # 检查是否有符合源格式要求的文件
        if source_format != "所有格式":
            valid_files = [f for f in image_files if f.lower().endswith(self.supported_formats[source_format].lower())]
            if not valid_files:
                messagebox.showwarning("警告", f"选中的文件中没有 {source_format} 格式的图片！")
                return
            image_files = valid_files

        total_files = len(image_files)
        converted_count = 0
        failed_count = 0

        for image_path in image_files:
            try:
                # 更新进度
                self.progress_var.set((converted_count + failed_count) / total_files * 100)
                self.root.update_idletasks()

                # 构建目标文件路径
                if self.select_mode.get() == "folder":
                    source_dir = self.source_path.get()
                    rel_path = os.path.relpath(image_path, source_dir)
                else:
                    rel_path = os.path.basename(image_path)
                
                base_name = os.path.splitext(rel_path)[0]
                target_path = os.path.join(target_dir, base_name + target_format)

                # 确保目标目录存在
                os.makedirs(os.path.dirname(target_path), exist_ok=True)

                # 转换图片
                with Image.open(image_path) as img:
                    if img.mode in ('RGBA', 'LA') and target_format.lower() == '.jpg':
                        # 处理带透明通道的图片转换为JPG
                        bg = Image.new('RGB', img.size, (255, 255, 255))
                        bg.paste(img, mask=img.split()[-1])
                        bg.save(target_path, quality=quality, optimize=True)
                    else:
                        if target_format.lower() == '.jpg':
                            img.convert('RGB').save(target_path, quality=quality, optimize=True)
                        else:
                            img.save(target_path)

                self.log_message(f"成功转换: {rel_path}")
                converted_count += 1

            except Exception as e:
                self.log_message(f"转换失败: {rel_path} - {str(e)}")
                failed_count += 1

        # 完成后更新进度条和显示结果
        self.progress_var.set(100)
        self.log_message(f"\n转换完成！\n成功: {converted_count} 个文件\n失败: {failed_count} 个文件")
        messagebox.showinfo("完成", f"转换完成！\n成功: {converted_count} 个文件\n失败: {failed_count} 个文件")

    def start_conversion(self):
        """在新线程中启动转换过程"""
        threading.Thread(target=self.convert_images, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConvertApp(root)
    root.mainloop() 