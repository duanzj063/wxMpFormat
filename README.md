# 微信文章格式化与海报生成系统

这是一个基于Flask的Web应用程序，可以将普通文章格式化为微信公众号格式，并使用AI技术生成精美的海报封面。

## 功能特点

✅ **文章格式化**
- 将普通文章转换为微信公众号格式
- 智能识别标题和段落结构
- 支持Markdown格式输出
- 实时预览和一键复制

✅ **AI海报生成**
- 集成AI服务生成智能海报
- 支持小红书和公众号两种格式
- 多种视觉风格自动匹配
- HTML格式输出，支持下载

✅ **Web界面**
- 现代化响应式设计
- 友好的用户交互体验
- 实时状态反馈
- 移动端适配

## 环境管理

本项目推荐使用 [uv](https://github.com/astral-sh/uv) 进行Python环境和依赖管理。

### 1. 安装uv

```bash
# 使用pip安装
pip install uv

# 或者使用官方安装脚本
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 快速启动

**Windows用户:**
```bash
# 双击运行
run.bat

# 或者命令行运行
uv sync
uv run python app.py
```

**Linux/macOS用户:**
```bash
# 使用Python脚本
python run.py

# 或者直接使用uv
uv sync
uv run python app.py
```

### 3. 传统方式安装依赖

如果不使用uv，也可以使用传统的pip方式：

```bash
pip install -r requirements.txt
```

### 2. 安装系统依赖

WeasyPrint需要一些系统依赖才能正常工作：

**Windows:**
- 安装 [GTK+ 运行时环境](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases)
- 安装 [Microsoft Visual C++ Redistributable](https://aka.ms/vs/16/release/vc_redist.x64.exe)

**macOS:**
```bash
brew install pango cairo gdk-pixbuf libffi
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev libssl-dev
```

### 3. 文件准备

确保以下文件位于程序执行目录：
- `文章.md`: 输入的文章内容
- `提示词.md`: 用于封面生成的提示词

## 使用方法

1. 确保所有依赖已安装
2. 将输入文章保存为`文章.md`
3. 将提示词保存为`提示词.md`
4. 运行程序：

```bash
python wechat_article_generator.py
```

## 输出

程序将在`output`目录下生成以下文件：
- `文章_公众号版.md`: 转换后的公众号文章
- `[标题]-公众号封面.png`: 生成的封面图片

## 配置

您可以在`wechat_article_generator.py`中修改以下配置：

```python
# API配置
API_BASE_URL = "URL"
API_KEY = "APIKeY"
MODEL_NAME = "模型名称"

# 文件路径
INPUT_ARTICLE_FILE = "文章.md"
PROMPT_FILE = "提示词.md"
OUTPUT_DIR = "output"
```

## 工作流程

1. 读取输入文章和提示词文件
2. 调用AI将Markdown转换为公众号格式
3. 从转换后的文章中提取标题
4. 调用AI API生成封面HTML
5. 使用WeasyPrint将HTML转换为PNG图片
6. 保存生成的文章和封面图片

## 故障排除

### 常见问题

1. **WeasyPrint安装失败**:
   - 确保已安装所有系统依赖
   - 在Windows上可能需要重启系统

2. **API调用失败**:
   - 检查API密钥和Base URL是否正确
   - 确认网络连接正常

3. **文件读写错误**:
   - 检查文件路径是否正确
   - 确认程序有文件读写权限

4. **生成的图片质量不佳**:
   - 可以调整HTML中的CSS样式
   - 可以修改`html_to_png`函数中的图片尺寸

## 注意事项

- 确保API服务可用且配额充足
- 生成的HTML代码应尽量简洁，避免复杂的CSS和JavaScript
- 封面图片的生成质量取决于生成的HTML代码质量

## 许可证

本项目仅供学习和研究使用。
