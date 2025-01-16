"""
报纸下载工具 (Newspaper Download Tool)
功能：支持多种报纸的批量下载
作者：s-Ruthless
创建时间：2025-01-16
最后修改：2025-01-16
版本：1.0
"""

import sys
import os
import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QCalendarWidget, QListWidget, QTextEdit, 
                            QPushButton, QLabel, QCheckBox, QGroupBox, QProgressBar,
                            QFileDialog, QSpinBox, QToolButton, QMenu, QGridLayout,
                            QLineEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDate
from PyQt6.QtGui import QTextCharFormat, QColor, QFont, QAction
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt6.QtCore import QObject
import urllib3
from functools import partial
from PyQt6.QtGui import QIcon

# 禁用 urllib3 的警告信息
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NewspaperDownloader(QObject):
    progress_signal = pyqtSignal(str)  # 添加信号定义
    
    def __init__(self):
        super().__init__()
        self.download_folder = ""
        # 统一的headers配置
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/pdf,text/html,*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _get_page_content(self, url):
        """统一的页面获取方法"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            self.progress_signal.emit(f"获取页面失败: {str(e)}")
            return None

    def _format_title(self, newspaper, date, page_num, page_title=""):
        """统一的标题格式化方法"""
        date_str = date.strftime("%Y%m%d")
        page_num = page_num.zfill(2)
        return f"{newspaper}_{date_str}_第{page_num}版_{page_title}".strip('_')

    def get_people_daily_links(self, date):
        """获取人民日报PDF链接"""
        try:
            self.progress_signal.emit("正在获取人民日报版面...")
            
            # 修改日期格式以匹配新的URL结构
            year_month = date.strftime("%Y%m")
            day = date.strftime("%d")
            year_month_day = date.strftime("%Y%m%d")
            
            # 构建新的URL格式
            base_url = f"http://paper.people.com.cn/rmrb/pc/layout/{year_month}/{day}/"
            index_url = f"{base_url}node_01.html"
            
            response = self.session.get(index_url)
            response.raise_for_status()
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            pdf_links = []
            pages = soup.select('div.swiper-slide a#pageLink')
            
            if not pages:
                self.progress_signal.emit("未找到版面信息")
                return []
            
            # 遍历每个版面
            for page in pages:
                try:
                    page_url = page.get('href')
                    if not page_url:
                        continue
                        
                    # 获取版面号和标题
                    page_text = page.text.strip()
                    if '版：' in page_text:
                        page_num = page_text.split('版：')[0].strip()
                        page_title = page_text.split('版：')[1].strip()
                        
                        # 访问版面页面
                        page_full_url = f"{base_url}{page_url}"
                        page_response = self.session.get(page_full_url)
                        page_response.raise_for_status()
                        page_response.encoding = 'utf-8'
                        page_soup = BeautifulSoup(page_response.text, 'html.parser')
                        
                        # 在版面页面中查找PDF下载链接
                        pdf_link = page_soup.select_one('a[href*="attachement"][href$=".pdf"]')
                        if pdf_link and 'href' in pdf_link.attrs:
                            pdf_href = pdf_link['href']
                            # 提取PDF文件ID
                            pdf_file_id = pdf_href.split('/')[-1]
                            
                            # 构建完整的PDF URL
                            pdf_url = f"http://paper.people.com.cn/rmrb/pc/attachement/{year_month}/{day}/{pdf_file_id}"
                            title = f"人民日报_{year_month_day}_第{page_num.zfill(2)}版_{page_title}"
                            
                            pdf_links.append((title, pdf_url))
                        
                except Exception as e:
                    self.progress_signal.emit(f"处理版面出错: {str(e)}")
                    continue
            
            self.progress_signal.emit(f"找到 {len(pdf_links)} 个版面")
            return pdf_links
            
        except Exception as e:
            self.progress_signal.emit(f"获取人民日报版面出错: {str(e)}")
            return []

    def get_economic_daily_links(self, date):
        """获取经济日报PDF链接"""
        try:
            self.progress_signal.emit("正在获取经济日报版面...")
            year_month = date.strftime("%Y%m")
            day = date.strftime("%d")
            year_month_day = date.strftime("%Y%m%d")
            
            # 构建新的URL格式
            base_url = f"http://paper.ce.cn/pc/layout/{year_month}/{day}/"
            index_url = f"{base_url}node_01.html"
            
            response = self.session.get(index_url)
            response.raise_for_status()
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            pdf_links = []
            pages = soup.select('ul#layoutlist li.posRelative')
            
            if not pages:
                self.progress_signal.emit("未找到版面信息")
                return []
            
            for page in pages:
                try:
                    # 获取版面信息
                    title_link = page.select_one('a:not(.pdf)')
                    if not title_link:
                        continue
                        
                    title_text = title_link.text.strip()
                    if '版：' in title_text:
                        page_num = title_text.split('第')[1].split('版')[0].strip()
                        page_title = title_text.split('版：')[1].strip()
                        
                        # 获取PDF链接
                        hidden_input = page.select_one('input[type="hidden"]')
                        if hidden_input and hidden_input.get('value'):
                            pdf_href = hidden_input.get('value')
                            if pdf_href.startswith('../../../'):
                                pdf_href = pdf_href.replace('../../../', '')
                            
                            # 构建完整的PDF URL
                            pdf_url = f"http://paper.ce.cn/pc/{pdf_href}"
                            title = f"经济日报_{year_month_day}_第{page_num.zfill(2)}版_{page_title}"
                            
                            pdf_links.append((title, pdf_url))
                
                except Exception as e:
                    self.progress_signal.emit(f"处理版面出错: {str(e)}")
                    continue
            
            self.progress_signal.emit(f"找到 {len(pdf_links)} 个版面")
            return pdf_links
            
        except Exception as e:
            self.progress_signal.emit(f"获取经济日报版面出错: {str(e)}")
            return []

    def get_legal_daily_links(self, date):
        """获取法治日报PDF链接"""
        try:
            self.progress_signal.emit("正在获取法治日报版面...")
            date_str = date.strftime("%Y%m%d")
            
            index_url = f"http://epaper.legaldaily.com.cn/fzrb/content/{date_str}/Page01TB.htm"
            
            response = self.session.get(index_url)
            response.raise_for_status()
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            pdf_links = []
            # 修改选择器，选择表格中的所有版面链接
            pages = soup.select('td a.atitle')
            
            if not pages:
                self.progress_signal.emit("未找到版面信息")
                return []
            
            for page in pages:
                try:
                    title_text = page.text.strip()
                    if ':' in title_text:
                        page_num, page_title = title_text.split(':', 1)
                        page_num = page_num.strip()
                        page_title = page_title.strip()
                        
                        # 构建PDF URL
                        pdf_url = f"http://epaper.legaldaily.com.cn/fzrb/PDF/{date_str}/{page_num.zfill(2)}.pdf"
                        title = f"法治日报_{date_str}_第{page_num.zfill(2)}版_{page_title}"
                        
                        pdf_links.append((title, pdf_url))
                except Exception as e:
                    self.progress_signal.emit(f"处理版面出错: {str(e)}")
                    continue
            
            self.progress_signal.emit(f"找到 {len(pdf_links)} 个版面")
            return pdf_links
            
        except Exception as e:
            self.progress_signal.emit(f"获取法治日报版面出错: {str(e)}")
            return []

    def get_worker_daily_links(self, date):
        """获取工人日报PDF链接"""
        try:
            self.progress_signal.emit("正在获取工人日报版面...")
            date_str = date.strftime("%Y/%m/%d")
            year_month_day = date.strftime("%Y%m%d")
            
            index_url = f"https://www.workercn.cn/papers/grrb/{date_str}/1/page.html"
            
            response = self.session.get(index_url)
            response.raise_for_status()
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            pdf_links = []
            pages = soup.select('ul#pageUrl li')
            
            if not pages:
                self.progress_signal.emit("未找到版面信息")
                return []
            
            for page in pages:
                try:
                    page_num = page.select_one('a:not(.pdf)').text.strip()
                    pdf_link = page.select_one('a.pdf')
                    
                    if pdf_link and 'href' in pdf_link.attrs:
                        pdf_url = f"https://www.workercn.cn{pdf_link['href']}"
                        page_title = "头版" if page_num == "1" else ""
                        
                        title = f"工人日报_{year_month_day}_第{page_num.zfill(2)}版_{page_title}"
                        pdf_links.append((title, pdf_url))
                
                except Exception as e:
                    self.progress_signal.emit(f"处理版面出错: {str(e)}")
                    continue
            
            self.progress_signal.emit(f"找到 {len(pdf_links)} 个版面")
            return pdf_links
            
        except Exception as e:
            self.progress_signal.emit(f"获取工人日报版面出错: {str(e)}")
            return []

    def get_science_daily_links(self, date):
        """获取科技日报PDF链接"""
        try:
            self.progress_signal.emit("正在获取科技日报版面...")
            date_str = date.strftime("%Y-%m/%d")
            year_month_day = date.strftime("%Y%m%d")
            
            index_url = f"https://digitalpaper.stdaily.com/http_www.kjrb.com/kjrb/html/{date_str}/node_2.htm"
            
            response = self.session.get(index_url)
            response.raise_for_status()
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            pdf_links = []
            pages = soup.select('div.bmname div a#pageLink')
            
            if not pages:
                self.progress_signal.emit("未找到版面信息")
                return []
            
            for page in pages:
                try:
                    title_text = page.text.strip()
                    if '：' in title_text:
                        page_num = title_text.split('第')[1].split('版')[0].strip()
                        page_title = title_text.split('：')[1].strip()
                        
                        pdf_url = f"https://digitalpaper.stdaily.com/http_www.kjrb.com/kjrb/images/{date_str}/{page_num}/KJRB{year_month_day}{page_num}.pdf"
                        title = f"科技日报_{year_month_day}_第{page_num}版_{page_title}"
                        
                        pdf_links.append((title, pdf_url))
                
                except Exception as e:
                    self.progress_signal.emit(f"处理版面出错: {str(e)}")
                    continue
            
            self.progress_signal.emit(f"找到 {len(pdf_links)} 个版面")
            return pdf_links
            
        except Exception as e:
            self.progress_signal.emit(f"获取科技日报版面出错: {str(e)}")
            return []

    def get_xinhua_daily_links(self, date):
        """获取新华日报PDF链接"""
        try:
            self.progress_signal.emit("正在获取新华日报版面...")
            year_month = date.strftime("%Y%m")
            day = date.strftime("%d")
            year_month_day = date.strftime("%Y%m%d")
            
            # 构建新的URL格式
            base_url = f"https://xh.xhby.net/pc/layout/{year_month}/{day}/"
            index_url = f"{base_url}node_1.html"
            
            response = self.session.get(index_url)
            response.raise_for_status()
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            pdf_links = []
            pages = soup.select('div.Chunkiconlist p')
            
            if not pages:
                self.progress_signal.emit("未找到版面信息")
                return []
            
            for page in pages:
                try:
                    # 获取版面信息
                    title_link = page.select_one('a:first-child')
                    pdf_link = page.select_one('a[href$=".pdf"]')
                    
                    if title_link and pdf_link:
                        title_text = title_link.text.strip()
                        if '版：' in title_text:
                            page_num = title_text.split('第')[1].split('版')[0].strip()
                            page_title = title_text.split('版：')[1].strip()
                            
                            # 获取PDF链接
                            pdf_href = pdf_link['href']
                            if pdf_href.startswith('../../../'):
                                pdf_href = pdf_href.replace('../../../', '')
                            
                            # 构建完整的PDF URL
                            pdf_url = f"https://xh.xhby.net/pc/{pdf_href}"
                            title = f"新华日报_{year_month_day}_第{page_num.zfill(2)}版_{page_title}"
                            
                            pdf_links.append((title, pdf_url))
                
                except Exception as e:
                    self.progress_signal.emit(f"处理版面出错: {str(e)}")
                    continue
            
            self.progress_signal.emit(f"找到 {len(pdf_links)} 个版面")
            return pdf_links
            
        except Exception as e:
            self.progress_signal.emit(f"获取新华日报版面出错: {str(e)}")
            return []

    # ... (其他报纸的下载方法保持不变)

class DownloaderThread(QThread):
    progress_signal = pyqtSignal(str)
    
    def __init__(self, newspaper_types, date, download_dir, max_workers=10):  # 增加并发数
        super().__init__()
        self.newspaper_types = newspaper_types
        self.date = date
        self.download_dir = download_dir
        self.max_workers = max_workers
        self.timeout = 30  # 增加超时时间
        self.chunk_size = 2 * 1024 * 1024  # 增加到2MB
        
        # 初始化下载器
        self.downloader = NewspaperDownloader()
        self.downloader.download_folder = download_dir
        self.downloader.progress_signal = self.progress_signal
        
        self.is_running = True
        # 优化session配置
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/pdf,text/html,*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        })
        # 设置连接池参数
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=20,    # 连接池大小
            pool_maxsize=20,       # 最大连接数
            max_retries=3          # 重试次数
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def download_file(self, url, filename):
        """优化的文件下载方法"""
        try:
            response = self.session.get(
                url,
                stream=True,
                verify=False,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                file_path = os.path.join(self.download_dir, filename)
                
                # 使用with确保文件正确关闭
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=self.chunk_size):
                        if not chunk or not self.is_running:
                            break
                        f.write(chunk)
                
                # 验证文件大小
                if os.path.getsize(file_path) > 0:
                    return True, filename
                else:
                    os.remove(file_path)  # 删除空文件
                    return False, filename
            return False, filename
            
        except Exception as e:
            self.progress_signal.emit(f"下载出错: {str(e)}")
            return False, filename

    def download_files_with_threadpool(self, files_to_download):
        """优化的并发下载方法"""
        if not files_to_download or not self.is_running:
            return

        total = len(files_to_download)
        completed = 0
        failed = 0
        
        try:
            self.progress_signal.emit(f"开始下载 {total} 个文件...")
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                for file_info in files_to_download:
                    if not self.is_running:
                        break
                    try:
                        url = file_info[1]
                        filename = f"{file_info[0]}.pdf"
                        future = executor.submit(self.download_file, url, filename)
                        futures.append(future)
                    except Exception as e:
                        self.progress_signal.emit(f"创建下载任务失败: {str(e)}")
                        failed += 1

                # 处理完成的任务
                for future in as_completed(futures):
                    if not self.is_running:
                        self.progress_signal.emit("用户取消下载")
                        # 取消所有未完成的任务
                        for f in futures:
                            if not f.done():
                                f.cancel()
                        executor.shutdown(wait=False)
                        return
                        
                    completed += 1
                    try:
                        success, filename = future.result()
                        if not success:
                            failed += 1
                    except Exception as e:
                        failed += 1
                        self.progress_signal.emit(f"下载任务异常: {str(e)}")

            # 只有在正常完成时才输出最终结果
            if self.is_running:
                if failed > 0:
                    self.progress_signal.emit(
                        f"下载完成，共 {total} 个文件，成功 {total-failed} 个，失败 {failed} 个"
                    )
                else:
                    self.progress_signal.emit(f"全部 {total} 个文件下载成功")

        except Exception as e:
            self.progress_signal.emit(f"下载系统错误: {str(e)}")

    def run(self):
        try:
            if 'people' in self.newspaper_types and self.is_running:
                self.progress_signal.emit("开始下载人民日报...")
                links = self.downloader.get_people_daily_links(self.date)
                if links and self.is_running:
                    self.download_files_with_threadpool(links)

            if 'economic' in self.newspaper_types and self.is_running:
                self.progress_signal.emit("开始下载经济日报...")
                links = self.downloader.get_economic_daily_links(self.date)
                if links and self.is_running:
                    self.download_files_with_threadpool(links)

            if 'legal' in self.newspaper_types and self.is_running:
                self.progress_signal.emit("开始下载法治日报...")
                links = self.downloader.get_legal_daily_links(self.date)
                if links and self.is_running:
                    self.download_files_with_threadpool(links)

            if 'worker' in self.newspaper_types and self.is_running:
                self.progress_signal.emit("开始下载工人日报...")
                links = self.downloader.get_worker_daily_links(self.date)
                if links and self.is_running:
                    self.download_files_with_threadpool(links)

            if 'science' in self.newspaper_types and self.is_running:
                self.progress_signal.emit("开始下载科技日报...")
                links = self.downloader.get_science_daily_links(self.date)
                if links and self.is_running:
                    self.download_files_with_threadpool(links)

            if 'xinhua' in self.newspaper_types and self.is_running:
                self.progress_signal.emit("开始下载新华日报...")
                links = self.downloader.get_xinhua_daily_links(self.date)
                if links and self.is_running:
                    self.download_files_with_threadpool(links)

            if self.is_running:
                self.progress_signal.emit("所有文件下载完成")
                
        except Exception as e:
            self.progress_signal.emit(f"下载出错: {str(e)}")

    def stop(self):
        """停止下载"""
        self.is_running = False

class NewspaperDownloaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(__file__), "NewpaperDownTool.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.init_ui()
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
    def init_ui(self):
        """初始化UI"""
        # 设置窗口标题和大小
        self.setWindowTitle("报纸下载器")
        self.setMinimumSize(800, 600)
        
        # 创建主窗口部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # 创建左侧面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 下载选项组
        download_group = QGroupBox("下载选项")
        download_layout = QVBoxLayout(download_group)
        
        # 创建网格布局用于报纸选择
        newspaper_layout = QGridLayout()
        
        # 报纸选择
        self.people_daily_cb = QCheckBox("人民日报")
        self.economic_daily_cb = QCheckBox("经济日报")
        self.legal_daily_cb = QCheckBox("法治日报")
        self.worker_daily_cb = QCheckBox("工人日报")
        self.science_daily_cb = QCheckBox("科技日报")
        self.xinhua_daily_cb = QCheckBox("新华日报")
        
        # 创建右侧复选框的容器布局
        economic_container = QWidget()
        economic_layout = QHBoxLayout(economic_container)
        economic_layout.setContentsMargins(50, 0, 0, 0)
        economic_layout.addWidget(self.economic_daily_cb)
        economic_layout.addStretch()

        worker_container = QWidget()
        worker_layout = QHBoxLayout(worker_container)
        worker_layout.setContentsMargins(50, 0, 0, 0)
        worker_layout.addWidget(self.worker_daily_cb)
        worker_layout.addStretch()

        xinhua_container = QWidget()
        xinhua_layout = QHBoxLayout(xinhua_container)
        xinhua_layout.setContentsMargins(50, 0, 0, 0)
        xinhua_layout.addWidget(self.xinhua_daily_cb)
        xinhua_layout.addStretch()

        # 将复选框添加到网格布局中
        newspaper_layout.addWidget(self.people_daily_cb, 0, 0)
        newspaper_layout.addWidget(economic_container, 0, 1)
        newspaper_layout.addWidget(self.legal_daily_cb, 1, 0)
        newspaper_layout.addWidget(worker_container, 1, 1)
        newspaper_layout.addWidget(self.science_daily_cb, 2, 0)
        newspaper_layout.addWidget(xinhua_container, 2, 1)
        
        # 添加选择按钮布局
        selection_layout = QHBoxLayout()
        selection_layout.setSpacing(10)  # 按钮之间的间距
        selection_layout.setContentsMargins(0, 5, 0, 5)
        
        # 创建三个小按钮
        select_all_btn = QPushButton("全选")
        invert_select_btn = QPushButton("反选")
        clear_select_btn = QPushButton("清空")
        
        # 设置按钮样式和大小
        for btn in [select_all_btn, invert_select_btn, clear_select_btn]:
            btn.setFixedSize(60, 24)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    color: #333333;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    padding: 0px;
                    font-size: 12px;
                    font-weight: normal;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                    border-color: #999999;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                    border-color: #666666;
                }
            """)
        
        # 添加按钮到布局，使用固定间距
        selection_layout.addWidget(select_all_btn)
        selection_layout.addSpacing(15)  # 全选和反选之间的固定间距
        selection_layout.addWidget(invert_select_btn)
        selection_layout.addSpacing(15)  # 反选和清空之间的固定间距
        selection_layout.addWidget(clear_select_btn)
        selection_layout.addStretch()  # 添加弹性空间推动按钮靠左
        
        # 将选择按钮布局添加到下载选项布局中
        download_layout.addLayout(newspaper_layout)
        download_layout.addLayout(selection_layout)
        
        # 连接按钮信号
        select_all_btn.clicked.connect(self.select_all_newspapers)
        invert_select_btn.clicked.connect(self.invert_newspaper_selection)
        clear_select_btn.clicked.connect(self.clear_newspaper_selection)
        
        # 下载目录选择
        dir_group = QGroupBox("下载目录")
        dir_layout = QHBoxLayout(dir_group)  # 改为水平布局

        # 创建目录输入框
        self.dir_edit = QLineEdit()
        self.dir_edit.setReadOnly(False)  # 允许编辑
        self.dir_edit.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
                min-height: 25px;
            }
            QLineEdit:hover {
                border-color: #999999;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)

        # 创建选择目录按钮
        select_dir_btn = QPushButton("浏览...")
        select_dir_btn.setFixedSize(60, 40)  # 设置固定宽度和高度
        select_dir_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 0px;
                font-size: 12px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        select_dir_btn.clicked.connect(self.select_download_dir)

        # 添加到布局
        dir_layout.addWidget(self.dir_edit, stretch=1)  # 文本框占据更多空间
        dir_layout.addWidget(select_dir_btn)

        # 下载控制
        control_group = QGroupBox("下载控制")
        control_layout = QVBoxLayout(control_group)
        
        # 添加按钮
        self.download_btn = QPushButton("开始下载")
        self.cancel_btn = QPushButton("取消下载")
        
        # 设置初始状态
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        # 添加按钮到布局
        control_layout.addWidget(self.download_btn)
        control_layout.addWidget(self.cancel_btn)
        
        # 连接按钮信号
        self.download_btn.clicked.connect(self.start_download)
        self.cancel_btn.clicked.connect(self.cancel_download)
        
        # 添加组到左侧布局
        left_layout.addWidget(download_group)
        left_layout.addWidget(dir_group)
        left_layout.addWidget(control_group)
        left_layout.addStretch()
        
        # 创建右侧面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 日历
        calendar_label = QLabel("选择日期：")
        self.calendar = QCalendarWidget()
        
        # 设置日历基本属性
        self.calendar.setNavigationBarVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.SingleLetterDayNames)
        
        # 设置日期范围（从2000年开始）
        min_date = QDate(2000, 1, 1)  # 从2000年1月1日开始
        max_date = QDate.currentDate()  # 到今天为止
        
        self.calendar.setMinimumDate(min_date)
        self.calendar.setMaximumDate(max_date)
        self.calendar.setSelectedDate(max_date)

        # 设置年份下拉按钮
        year_button = self.calendar.findChild(QToolButton, "qt_calendar_yearbutton")
        if year_button:
            year_button.setFixedWidth(85)
            year_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            year_button.setStyleSheet("""
                QToolButton {
                    border-radius: 4px;
                    min-width: 85px;
                    max-width: 85px;
                    text-align: center;
                    background-color: white;
                    border: 1px solid #cccccc;
                    padding: 2px;
                }
                QToolButton:hover {
                    background-color: #f5f5f5;
                    border-color: #2196F3;
                }
                QToolButton::menu-indicator {
                    image: none;
                }
            """)
            
            # 创建年份菜单
            year_menu = QMenu(self)
            year_menu.setStyleSheet("""
                QMenu {
                    background-color: white;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 2px;
                    min-width: 85px;
                    max-width: 85px;
                }
                QMenu::item {
                    padding: 3px 0px;
                    text-align: center;
                    margin: 0px;
                    min-width: 85px;
                    max-width: 85px;
                    font-family: "Microsoft YaHei";
                    font-size: 12px;
                    height: 20px;
                    line-height: 20px;
                }
                QMenu::item:selected {
                    background-color: #f0f0f0;
                }
                QMenu::item:hover {
                    background-color: #f0f0f0;
                }
            """)
            
            # 添加年份选项（从2000年到当前年份）
            start_year = 2000
            end_year = QDate.currentDate().year()
            for year in range(end_year, start_year - 1, -1):  # 倒序排列年份
                action = QAction(str(year), year_menu)
                action.setData(year)  # 存储年份数据
                action.triggered.connect(lambda checked, y=year: self.set_calendar_year(y))
                year_menu.addAction(action)
            
            year_button.setMenu(year_menu)

        # 设置月份下拉按钮样式
        month_button = self.calendar.findChild(QToolButton, "qt_calendar_monthbutton")
        if month_button:
            month_button.setFixedWidth(85)
            month_button.setStyleSheet("""
                QToolButton {
                    border-radius: 4px;
                    min-width: 85px;
                    max-width: 85px;
                    text-align: center;
                    background-color: white;
                    border: 1px solid #cccccc;
                    padding: 2px;
                }
                QToolButton:hover {
                    background-color: #f5f5f5;
                    border-color: #2196F3;
                }
                QToolButton::menu-indicator {
                    image: none;
                }
            """)
            
            # 设置月份菜单样式
            month_menu = month_button.menu()
            if month_menu:
                month_menu.setStyleSheet("""
                    QMenu {
                        background-color: white;
                        border: 1px solid #cccccc;
                        border-radius: 4px;
                        padding: 2px;
                        min-width: 85px;
                        max-width: 85px;
                    }
                    QMenu::item {
                        padding: 3px 0px;
                        text-align: center;
                        margin: 0px;
                        min-width: 85px;
                        max-width: 85px;
                        font-family: "Microsoft YaHei";
                        font-size: 12px;
                        height: 20px;
                        line-height: 20px;
                    }
                    QMenu::item:selected {
                        background-color: #f0f0f0;
                    }
                    QMenu::item:hover {
                        background-color: #f0f0f0;
                    }
                """)
        
        # 连接信号
        self.calendar.clicked.connect(self.on_date_clicked)
        self.calendar.currentPageChanged.connect(self.on_calendar_page_changed)
        
        # 限制月份选择
        month_button = self.calendar.findChild(QToolButton, "qt_calendar_monthbutton")
        if month_button:
            month_menu = month_button.menu()
            if month_menu:
                current_date = QDate.currentDate()
                # 只显示到当前月份
                for action in month_menu.actions():
                    month = int(action.data()) if action.data() else 0
                    if month > current_date.month():
                        action.setVisible(False)
        
        # 设置最大日期为当前日期
        self.calendar.setMaximumDate(QDate.currentDate())
        
        # 设置日历样式
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            
            /* 月份年份选择按钮 */
            QCalendarWidget QToolButton#qt_calendar_monthbutton,
            QCalendarWidget QToolButton#qt_calendar_yearbutton {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 4px;
                color: #333333;
                font-weight: bold;
                padding: 4px 25px 4px 10px;
                margin: 2px;
                min-width: 85px;  /* 固定宽度为85px */
                max-width: 85px;  /* 固定宽度为85px */
                text-align: left;
            }
            
            QCalendarWidget QToolButton#qt_calendar_monthbutton:hover,
            QCalendarWidget QToolButton#qt_calendar_yearbutton:hover {
                background-color: #f5f5f5;
                border-color: #2196F3;
            }
            
            /* 下拉菜单样式 */
            QCalendarWidget QMenu {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 4px 0px;
                margin: 2px;
                min-width: 85px;  /* 与按钮宽度一致 */
                max-width: 85px;  /* 固定宽度 */
            }
            
            /* 下拉菜单项样式 */
            QCalendarWidget QMenu::item {
                padding: 3px 10px;
                min-width: 65px;  /* 与按钮宽度一致 */
                max-width: 65px;  /* 固定宽度 */
                color: #333333;
                background: transparent;
                border: none;
                text-align: center;
            }
            
            /* 下拉菜单项选中和悬停样式 */
            QCalendarWidget QMenu::item:selected,
            QCalendarWidget QMenu::item:hover {
                background-color: #f0f0f0;
                color: #333333;
                border: none;
            }
            
            /* 移除下拉箭头的默认样式 */
            QCalendarWidget QToolButton::menu-indicator,
            QCalendarWidget QToolButton::down-arrow {
                image: none;
                width: 0px;
                height: 0px;
                padding: 0px;
                margin: 0px;
            }
            
            /* 添加自定义下拉箭头 */
            QCalendarWidget QToolButton#qt_calendar_monthbutton::after,
            QCalendarWidget QToolButton#qt_calendar_yearbutton::after {
                content: "▼";
                position: absolute;
                right: 8px;
                top: 7px;
                color: #666666;
                font-size: 10px;
            }
            
            /* 日期表格样式 */
            QCalendarWidget QTableView {
                selection-background-color: #e41e2b;
                selection-color: white;
                outline: none;
            }
            
            /* 选中日期样式 */
            QCalendarWidget QTableView::item:selected {
                background-color: #e41e2b;
                color: white;
                font-weight: bold;
            }
            
            /* 悬停样式 - 不使用红色 */
            QCalendarWidget QTableView::item:hover:!selected {
                background-color: transparent;
            }
            
            /* 选中日期的悬停样式 */
            QCalendarWidget QTableView::item:selected:hover {
                background-color: #e41e2b;
                color: white;
            }
            
            /* 导航栏样式 */
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #f8f8f8;
                border-bottom: 1px solid #cccccc;
                padding: 4px;
            }
        """)
        
        # 设置当前日期为选中状态并高亮
        current_date = QDate.currentDate()
        self.calendar.setSelectedDate(current_date)
        self.calendar.setMaximumDate(current_date)
        
        # 初始化进度条为0
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        
        # 下载日志
        log_label = QLabel("下载日志：")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)  # 设置自定义右键菜单
        self.log_text.customContextMenuRequested.connect(self.show_log_context_menu)  # 连接右键菜单信号
        
        right_layout.addWidget(calendar_label)
        right_layout.addWidget(self.calendar)
        right_layout.addWidget(log_label)
        right_layout.addWidget(self.log_text)
        
        # 添加左右面板到主布局
        layout.addWidget(left_panel, 1)
        layout.addWidget(right_panel, 2)
        
        # 设置默认下载目录
        self.download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self.update_dir_label()
        
        # 连接复选框的状态改变信号
        self.people_daily_cb.stateChanged.connect(self.reset_progress)
        self.economic_daily_cb.stateChanged.connect(self.reset_progress)
        self.legal_daily_cb.stateChanged.connect(self.reset_progress)
        self.worker_daily_cb.stateChanged.connect(self.reset_progress)
        self.science_daily_cb.stateChanged.connect(self.reset_progress)
        self.xinhua_daily_cb.stateChanged.connect(self.reset_progress)
        
        # 连接日历的日期改变信号
        self.calendar.clicked.connect(self.on_date_changed)
        
        # 连接月份年份变化信号
        self.calendar.currentPageChanged.connect(self.on_calendar_page_changed)
        
        # 设置整体样式
        self.setStyleSheet("""
            /* 主窗口样式 */
            QMainWindow {
                background-color: #f0f0f0;
            }
            
            /* 分组框样式 */
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 7px;
                padding: 0px 5px 0px 5px;
            }
            
            /* 按钮样式 */
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            
            /* 进度条样式 */
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                text-align: center;
                min-height: 20px;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
            
            /* 文本框样式 */
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            
            /* 复选框样式 */
            QCheckBox {
                spacing: 8px;
                padding: 4px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #cccccc;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #2196F3;
                border-radius: 3px;
                background-color: #2196F3;
                image: url(check.png);
            }
            
            /* 日历样式补充 */
            QCalendarWidget QTableView {
                selection-background-color: #e41e2b;
                selection-color: white;
                outline: none;  /* 去掉选中的虚线边框 */
            }
            QCalendarWidget QTableView::item:selected {
                background-color: #e41e2b;
                color: white;
                font-weight: bold;
                border: none;  /* 去掉选中的边框 */
            }
            QCalendarWidget QTableView::item:hover {
                background-color: #f0f0f0;
                border: none;  /* 去掉悬停的边框 */
            }
        """)

    def select_download_dir(self):
        """选择下载目录"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择下载目录",
            self.dir_edit.text() or self.download_dir,
            QFileDialog.Option.ShowDirsOnly
        )
        if dir_path:
            self.download_dir = dir_path
            self.dir_edit.setText(dir_path)

    def update_dir_label(self):
        """更新目录显示"""
        self.dir_edit.setText(self.download_dir)
        
    def log_message(self, message):
        """添加日志消息"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{current_time}] {message}")
        # 滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def start_download(self):
        """开始下载"""
        # 检查日期是否有效
        selected_date = self.calendar.selectedDate().toPyDate()
        current_date = datetime.now().date()
        
        if selected_date > current_date:
            self.log_message("错误：不能选择未来的日期！")
            return
        
        # 检查是否选择了报纸
        newspaper_types = []
        if self.people_daily_cb.isChecked():
            newspaper_types.append('people')
        if self.economic_daily_cb.isChecked():
            newspaper_types.append('economic')
        if self.legal_daily_cb.isChecked():
            newspaper_types.append('legal')
        if self.worker_daily_cb.isChecked():
            newspaper_types.append('worker')
        if self.science_daily_cb.isChecked():
            newspaper_types.append('science')
        if self.xinhua_daily_cb.isChecked():
            newspaper_types.append('xinhua')
        
        if not newspaper_types:
            self.log_message("错误：请至少选择一种报纸！")
            return
        
        # 获取选择的日期
        date_str = selected_date.strftime("%Y-%m-%d")
        
        # 在下载目录下创建日期子文件夹
        date_folder = os.path.join(self.download_dir, date_str)
        try:
            if not os.path.exists(date_folder):
                os.makedirs(date_folder)
                self.log_message(f"创建日期文件夹: {date_str}")
        except Exception as e:
            self.log_message(f"创建日期文件夹失败: {str(e)}")
            return
        
        # 更新UI状态
        self.download_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        
        # 创建并启动下载线程
        self.download_thread = DownloaderThread(newspaper_types, selected_date, date_folder)
        self.download_thread.progress_signal.connect(self.log_message)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()

    def cancel_download(self):
        """取消下载"""
        if hasattr(self, 'download_thread') and self.download_thread.isRunning():
            self.download_thread.stop()
            self.cancel_btn.setEnabled(False)
            self.log_message("正在取消下载...")
            # 不要立即启用下载按钮，等待线程完全停止

    def download_finished(self):
        """下载完成后的处理"""
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

    def get_highlighted_date_format(self):
        """获取高亮日期的格式"""
        format = QTextCharFormat()
        format.setBackground(QColor("#e41e2b"))  # 使用标准红色
        format.setForeground(Qt.GlobalColor.white)
        format.setFontWeight(QFont.Weight.Bold)
        return format

    def on_date_clicked(self, date):
        """当日期被点击时的处理"""
        # 清除所有日期的格式
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        # 设置选中日期的格式
        self.calendar.setDateTextFormat(date, self.get_highlighted_date_format())

    def reset_progress(self):
        """重置下载状态"""
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

    def on_date_changed(self, date):
        """当日期改变时的处理"""
        # 处理日期高亮
        self.on_date_clicked(date)
        # 重置状态
        self.reset_progress()

    def set_calendar_year(self, year):
        """设置日历年份"""
        try:
            # 获取当前显示的月份
            current_date = self.calendar.selectedDate()
            current_month = current_date.month()
            
            # 创建新的日期
            new_date = QDate(year, current_month, 1)  # 先设置为1号避免日期无效
            
            # 检查是否是当前年份，如果是则限制月份
            if year == QDate.currentDate().year():
                if current_month > QDate.currentDate().month():
                    current_month = QDate.currentDate().month()
                    new_date = QDate(year, current_month, 1)
            
            # 设置新日期
            self.calendar.setSelectedDate(new_date)
            self.calendar.setCurrentPage(year, current_month)
            
            # 更新月份菜单
            self.update_month_menu(year)
            
            # 触发日期改变事件
            self.on_date_clicked(new_date)
        except Exception as e:
            print(f"设置年份出错: {str(e)}")  # 添加错误日志

    def update_month_menu(self, year):
        """更新月份菜单"""
        month_button = self.calendar.findChild(QToolButton, "qt_calendar_monthbutton")
        if month_button:
            month_menu = month_button.menu()
            if month_menu:
                current_date = QDate.currentDate()
                for action in month_menu.actions():
                    month = int(action.data()) if action.data() else 0
                    # 如果是当前年份，只显示到当前月份
                    if year == current_date.year():
                        action.setVisible(month <= current_date.month())
                    else:
                        action.setVisible(True)

    def on_calendar_page_changed(self, year, month):
        """当日历页面改变时（年份或月份变化）"""
        current_date = QDate.currentDate()
        
        # 清除所有日期的格式
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        # 获取当前选中的日期
        selected_date = self.calendar.selectedDate()
        
        # 如果选中日期在当前显示的月份，重新应用高亮
        if selected_date.year() == year and selected_date.month() == month:
            self.calendar.setDateTextFormat(selected_date, self.get_highlighted_date_format())
        
        # 处理月份菜单
        month_button = self.calendar.findChild(QToolButton, "qt_calendar_monthbutton")
        if month_button and month_button.menu():
            month_menu = month_button.menu()
            for action in month_menu.actions():
                month_num = int(action.data()) if action.data() else 0
                # 如果是当前年份，只显示到当前月份
                if year == current_date.year():
                    action.setVisible(month_num <= current_date.month())
                else:
                    action.setVisible(True)
        
        # 更新选中日期
        if year == current_date.year() and month > current_date.month():
            # 如果超过当前月份，设置为当前月份的第一天
            new_date = QDate(year, current_date.month(), 1)
            self.calendar.setSelectedDate(new_date)
            self.calendar.setDateTextFormat(new_date, self.get_highlighted_date_format())

    def show_log_context_menu(self, pos):
        """显示日志区域的右键菜单"""
        context_menu = QMenu(self)
        clear_action = QAction("清空日志", self)
        clear_action.triggered.connect(self.clear_log)
        context_menu.addAction(clear_action)
        
        # 在鼠标位置显示菜单
        context_menu.exec(self.log_text.mapToGlobal(pos))

    def clear_log(self):
        """清空日志内容"""
        self.log_text.clear()

    def select_all_newspapers(self):
        """全选所有报纸"""
        for checkbox in [
            self.people_daily_cb,
            self.economic_daily_cb,
            self.legal_daily_cb,
            self.worker_daily_cb,
            self.science_daily_cb,
            self.xinhua_daily_cb
        ]:
            checkbox.setChecked(True)

    def invert_newspaper_selection(self):
        """反选报纸"""
        for checkbox in [
            self.people_daily_cb,
            self.economic_daily_cb,
            self.legal_daily_cb,
            self.worker_daily_cb,
            self.science_daily_cb,
            self.xinhua_daily_cb
        ]:
            checkbox.setChecked(not checkbox.isChecked())

    def clear_newspaper_selection(self):
        """清空选择"""
        for checkbox in [
            self.people_daily_cb,
            self.economic_daily_cb,
            self.legal_daily_cb,
            self.worker_daily_cb,
            self.science_daily_cb,
            self.xinhua_daily_cb
        ]:
            checkbox.setChecked(False)

    def init_calendar(self):
        """初始化日历控件"""
        current_date = QDate.currentDate()
        self.calendar.setSelectedDate(current_date)
        
        # 设置年份范围
        min_date = QDate(current_date.year() - 1, 1, 1)  # 去年1月1日
        max_date = current_date  # 今天
        
        self.calendar.setDateRange(min_date, max_date)
        self.calendar.clicked.connect(self.on_date_clicked)

def main():
    app = QApplication(sys.argv)
    window = NewspaperDownloaderGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 