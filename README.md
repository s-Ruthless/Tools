# Tools Collection

这是一个实用工具集合，旨在提高工作效率。

## 工具列表

### 1. DeleteTool (文件批量删除工具)
- **位置**: `/DeleteTool`
- **功能**: 用于批量删除指定文件夹中特定类型的文件
- **依赖**: 
  - Python 3.x
  - PyQt6
  ```bash
  pip install PyQt6
  ```
- **特点**:
  - 支持文件夹选择
  - 支持多种常见文件类型
  - 支持子文件夹搜索
  - 实时删除日志
  - 支持手动输入文件扩展名
  - 用户友好界面
- **注意事项**:
  - 使用前请注意备份重要文件
  - 执行前请仔细确认删除参数

### 2. ImageConvert (图片批量转换工具)
- **位置**: `/ImageConvert`
- **功能**: 批量转换图片格式，支持多种常见图片格式之间的相互转换
- **依赖**: 
  - Python 3.x
  - PyQt6
  ```bash
  pip install PyQt6
  ```
  - Pillow (PIL)
  ```bash
  pip install Pillow
  ```
- **特点**:
  - 现代化图形界面
  - 支持单个/多个文件或文件夹转换
  - 支持PNG、JPEG、BMP、GIF、TIFF、ICO、WebP格式
  - 源格式自动检测与验证
  - 自定义目标文件夹
  - 实时进度显示与转换日志
  - 智能文件命名与目录结构保持
- **注意事项**:
  - 确保安装所需依赖
  - 大量文件转换时请耐心等待
  - JPEG格式转换会自动处理透明通道

### 3. PackagingTool (Python程序打包工具)
- **位置**: `/PackagingTool`
- **功能**: 将Python程序打包为独立的可执行文件(exe)
- **依赖**: 
  - Python 3.x
  - tkinter (Python 标准库，无需安装)
  - PyInstaller
  ```bash
  pip install pyinstaller
  ```
- **特点**:
  - 图形界面操作
  - 支持选择Python源文件
  - 支持自定义图标
  - 可选是否显示控制台窗口
  - 自定义输出程序名称
  - 自动检测并安装PyInstaller
  - 实时打包进度显示
  - 详细的打包日志
  - 打包完成自动打开输出目录
  - 支持管理员权限打包
- **注意事项**:
  - 确保Python环境正确配置
  - 打包时可能需要管理员权限
  - 部分杀毒软件可能误报，建议添加信任

## 使用说明
每个工具都在其独立目录中，包含完整的源代码和资源文件。

## 贡献
欢迎反馈问题和功能建议。

## 作者
s-Ruthless

## 许可
MIT License 