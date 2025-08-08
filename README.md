# 公众号文章与封面生成器

这是一个基于Python的程序，可以根据输入的Markdown文章自动生成适合微信公众号发布的文章格式，并创建相应的公众号封面图片。

## 功能特点

- 将Markdown文章转换为公众号格式
- 根据文章标题生成公众号封面HTML
- 将HTML封面转换为PNG图片
- 保存生成的公众号文章和封面图片到本地

## 前置准备

### 1. 安装依赖

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
