import os
import re
import json
import requests
from bs4 import BeautifulSoup
import markdown
from PIL import Image
import io
import base64
from weasyprint import HTML, CSS
import tempfile
import shutil

# 配置信息
API_BASE_URL = "http://27.159.93.56:8198/v1/"
API_KEY = "1"
MODEL_NAME = "GLM-4.5-Air"

# 文件路径
INPUT_ARTICLE_FILE = "文章.md"
PROMPT_FILE = "提示词.md"
OUTPUT_DIR = "output"
OUTPUT_ARTICLE_FILE = os.path.join(OUTPUT_DIR, "文章_公众号版.md")
TEMP_HTML_FILE = os.path.join(OUTPUT_DIR, "cover_temp.html")

def ensure_output_dir():
    """确保输出目录存在"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def read_file(file_path):
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")
        return None

def write_file(file_path, content, mode='w'):
    """写入文件内容"""
    try:
        ensure_output_dir()
        with open(file_path, mode, encoding='utf-8') as f:
            f.write(content)
        print(f"文件已保存: {file_path}")
    except Exception as e:
        print(f"写入文件 {file_path} 时出错: {e}")

def call_llm_api(prompt, system_prompt="", memory=""):
    """调用GLM-4.5-Air API"""
    url = f"{API_BASE_URL}chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if memory:
        messages.append({"role": "system", "content": f"记忆内容: {memory}"})
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": 2000,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"调用API时出错: {e}")
        return None

def extract_title_from_article(article_content):
    """从文章内容中提取标题"""
    # 尝试从Markdown中提取标题
    lines = article_content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()
    
    # 如果没有找到标题，使用默认标题
    return "Untitled"

def convert_markdown_to_wechat(article_content):
    """将Markdown转换为公众号格式"""
    system_prompt = "请将以下文章内容转换为适合微信公众号发布的格式，保持专业性和可读性。"
    return call_llm_api(article_content, system_prompt)

def generate_cover_html(title, prompt_content):
    """生成封面HTML"""
    system_prompt = "你是一位专业的网页和营销视觉设计师，根据用户提供的标题内容生成公众号封面HTML代码。"
    user_prompt = f"请根据这个标题：{title}生成一个适合微信公众号的封面HTML代码。"
    return call_llm_api(user_prompt, system_prompt, prompt_content)

def html_to_png(html_content, output_path):
    """将HTML转换为PNG图片"""
    try:
        # 使用WeasyPrint将HTML转换为PDF
        pdf = HTML(string=html_content).write_pdf()
        
        # 将PDF转换为PNG
        image = Image.open(io.BytesIO(pdf))
        
        # 如果需要，可以调整图片大小
        # image = image.resize((1200, 630))  # 公众号封面推荐尺寸
        
        # 保存为PNG
        image.save(output_path, 'PNG')
        print(f"封面图片已保存: {output_path}")
        return True
    except Exception as e:
        print(f"HTML转PNG时出错: {e}")
        return False

def main():
    """主函数"""
    print("开始生成公众号文章和封面...")
    
    # 1. 读取输入文件
    article_content = read_file(INPUT_ARTICLE_FILE)
    if not article_content:
        print("无法读取输入文章文件")
        return
    
    prompt_content = read_file(PROMPT_FILE)
    if not prompt_content:
        print("无法读取提示词文件")
        return
    
    # 2. 生成公众号文章
    print("正在生成公众号文章...")
    wechat_article = convert_markdown_to_wechat(article_content)
    if wechat_article:
        write_file(OUTPUT_ARTICLE_FILE, wechat_article)
    else:
        print("生成公众号文章失败")
        return
    
    # 3. 提取标题
    title = extract_title_from_article(wechat_article)
    print(f"提取的标题: {title}")
    
    # 4. 生成封面HTML
    print("正在生成封面HTML...")
    cover_html = generate_cover_html(title, prompt_content)
    if not cover_html:
        print("生成封面HTML失败")
        return
    
    # 5. 保存临时HTML文件
    write_file(TEMP_HTML_FILE, cover_html)
    
    # 6. 将HTML转换为PNG
    print("正在将HTML转换为PNG...")
    safe_title = re.sub(r'[^\w\u4e00-\u9fa5]', '_', title)
    output_image_path = os.path.join(OUTPUT_DIR, f"{safe_title}-公众号封面.png")
    
    if html_to_png(cover_html, output_image_path):
        print("公众号文章和封面生成完成!")
        print(f"文章路径: {OUTPUT_ARTICLE_FILE}")
        print(f"封面路径: {output_image_path}")
    else:
        print("封面生成失败")

if __name__ == "__main__":
    main()
