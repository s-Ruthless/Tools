"""
文件批量删除工具 (Batch File Deletion Tool)
功能：用于批量删除指定文件夹中特定类型的文件
作者：s-Ruthless
创建时间：2024-12-31
最后修改：2024-12-31
版本：1.0
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import tkinter.font as tkfont


class BatchDeleteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件批量删除工具")
        self.root.geometry("800x650")  # 调整窗口大小
        self.root.configure(bg="#ffffff")  # 改为白色背景

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

        # 设置删除按钮特殊样式
        style.configure("Delete.TButton",
                       padding=(20, 8),
                       font=('Microsoft YaHei UI', 10, 'bold'),
                       background="#2196F3",
                       borderwidth=0,
                       relief="flat")
        
        style.map("Delete.TButton",
                  foreground=[('active', '#ffffff'),
                             ('disabled', '#999999')],
                  background=[('active', '#1976D2'),
                             ('disabled', '#cccccc')])

        # 设置Combobox样式
        style.configure("TCombobox",
                       font=('Microsoft YaHei UI', 9),
                       padding=2)

        # 设置Checkbutton样式
        style.configure("TCheckbutton",
                       font=('Microsoft YaHei UI', 9),
                       background="#ffffff")

    def create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = ttk.Label(
            self.main_frame,
            text="文件批量删除工具",
            font=('Microsoft YaHei UI', 16, 'bold'),
            foreground="#1565C0"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # 选择文件夹区域
        folder_frame = ttk.LabelFrame(self.main_frame, text="选择文件夹")
        folder_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))

        self.folder_path = tk.StringVar()
        path_entry = ttk.Entry(
            folder_frame,
            textvariable=self.folder_path,
            width=55,
            style="TEntry"
        )
        path_entry.grid(row=0, column=0, padx=5, pady=5)

        folder_btn = ttk.Button(
            folder_frame,
            text="浏览...",
            command=self.select_folder,
            width=12
        )
        folder_btn.grid(row=0, column=1, padx=5, pady=5)

        # 文件类型选择区域
        ext_frame = ttk.LabelFrame(self.main_frame, text="文件类型")
        ext_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))

        # 更新常见文件类型列表
        self.common_extensions = [
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

        type_frame = ttk.Frame(ext_frame)
        type_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

        self.ext_type = ttk.Combobox(
            type_frame,
            values=self.common_extensions,
            width=35,
            font=('Microsoft YaHei UI', 9),
            state="readonly"
        )
        self.ext_type.set(self.common_extensions[0])
        self.ext_type.grid(row=0, column=0, padx=5)
        self.ext_type.bind('<<ComboboxSelected>>', self.on_type_selected)

        ttk.Label(type_frame, text="或手动输入扩展名:").grid(row=0, column=1, padx=5)
        self.extensions = ttk.Entry(
            type_frame,
            width=20,
            style="TEntry"
        )
        self.extensions.grid(row=0, column=2, padx=5)

        # 选项区域
        options_frame = ttk.LabelFrame(self.main_frame, text="选项")
        options_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))

        self.include_subfolders = tk.BooleanVar(value=False)
        self.subfolder_check = ttk.Checkbutton(
            options_frame,
            text="包含子文件夹",
            variable=self.include_subfolders
        )
        self.subfolder_check.grid(row=0, column=0, padx=5, pady=5)

        # 删除按钮
        self.delete_btn = ttk.Button(
            self.main_frame,
            text="开始删除",
            command=self.delete_files,
            style="Delete.TButton"
        )
        self.delete_btn.grid(row=4, column=0, columnspan=2, pady=15)

        # 日志显示区域
        log_frame = ttk.LabelFrame(self.main_frame, text="操作日志")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 8))

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

    def on_type_selected(self, event):
        """
        文件类型下拉框选择事件处理函数
        当用户从下拉框选择文件类型时，自动填充扩展名输入框
        Args:
            event: 事件对象
        """
        selected = self.ext_type.get()
        if selected == self.common_extensions[0]:
            return

        # 从选择的文本中提取扩展名
        ext = selected.split(' - ')[0]
        self.extensions.delete(0, tk.END)
        self.extensions.insert(0, ext)

    def select_folder(self):
        """
        文件夹选择对话框
        打开系统文件夹选择对话框，让用户选择要处理的文件夹
        """
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def delete_files(self):
        """
        文件删除的主要处理函数
        执行实际的文件删除操作，包括：
        1. 验证用户输入
        2. 遍历文件夹
        3. 删除符合条件的文件
        4. 记录操作日志
        """
        folder = self.folder_path.get()
        if not folder:
            messagebox.showerror("错误", "请先选择文件夹！")
            return

        extensions = [ext.strip() for ext in self.extensions.get().split(',') if ext.strip()]
        if not extensions:
            messagebox.showerror("错误", "请输入要删除的文件扩展名！")
            return

        try:
            deleted_count = 0
            if self.include_subfolders.get():
                # 包含子文件夹的情况
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        if any(file.lower().endswith(ext.lower()) for ext in extensions):
                            file_path = os.path.join(root, file)
                            os.remove(file_path)
                            self.log_text.insert(tk.END, f"已删除: {file_path}\n")
                            deleted_count += 1
            else:
                # 不包含子文件夹的情况
                for file in os.listdir(folder):
                    file_path = os.path.join(folder, file)
                    if os.path.isfile(file_path) and any(file.lower().endswith(ext.lower()) for ext in extensions):
                        os.remove(file_path)
                        self.log_text.insert(tk.END, f"已删除: {file_path}\n")
                        deleted_count += 1

            self.log_text.insert(tk.END, f"\n共删除了 {deleted_count} 个文件\n")
            self.log_text.see(tk.END)
            messagebox.showinfo("完成", f"成功删除了 {deleted_count} 个文件！")

        except Exception as e:
            messagebox.showerror("错误", f"删除过程中出现错误：{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = BatchDeleteApp(root)
    root.mainloop()