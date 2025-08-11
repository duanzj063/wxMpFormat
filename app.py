from flask import Flask, render_template, request, jsonify, send_file
import os
import re
import json
import requests
import markdown
from datetime import datetime
import tempfile
import uuid
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/posters', exist_ok=True)

def normalize_api_url(url):
    """规范化API URL，自动补全缺失的路径"""
    if not url:
        return url
    
    url = url.strip()
    
    # 移除末尾的斜杠
    url = url.rstrip('/')
    
    # 如果已经是完整的API路径，直接返回
    if url.endswith('/chat/completions'):
        return url
    
    # OpenAI格式自动补全
    if 'openai.com' in url:
        if '/v1/' in url:
            url = url.replace('/v1/', '/v1/chat/completions')
        else:
            url = url + '/v1/chat/completions'
    # 智谱AI格式自动补全
    elif 'bigmodel.cn' in url:
        if '/api/paas/v4' in url:
            url = url.replace('/api/paas/v4', '/api/paas/v4/chat/completions')
        elif '/v4/' in url:
            url = url.replace('/v4/', '/v4/chat/completions')
        else:
            url = url + '/api/paas/v4/chat/completions'
    
    return url

# 全局配置
config = {
    'ai_service_url': normalize_api_url(os.getenv('API_BASE_URL', 'https://api.openai.com/v1/chat/completions')),
    'ai_api_key': os.getenv('API_KEY', ''),
    'ai_model': os.getenv('MODEL_NAME', 'gpt-3.5-turbo')
}



@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/config')
def config_page():
    """配置页面"""
    return render_template('config.html')

@app.route('/api/format-article', methods=['POST'])
def format_article():
    """格式化文章为Markdown"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        use_ai = data.get('useAiFormat', False)  # 修复：使用与前端一致的参数名
        
        if not content:
            return jsonify({'error': '内容不能为空'}), 400
        
        print(f"格式化文章 - 内容长度: {len(content)}, 使用AI: {use_ai}")
        
        # 根据选择使用不同的格式化方式
        if use_ai:
            print("开始AI格式化...")
            formatted_content = format_text_with_ai(content)
            if not formatted_content:
                return jsonify({'error': 'AI服务调用失败，请检查配置'}), 500
            method = 'AI排版'
        else:
            print("开始规则格式化...")
            formatted_content = format_text_to_markdown(content)
            method = '规则排版'
        
        print(f"格式化完成 - 方法: {method}, 内容长度: {len(formatted_content)}")
        
        return jsonify({
            'success': True,
            'formatted_content': formatted_content,
            'method': method
        })
    
    except Exception as e:
        print(f"格式化错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-poster', methods=['POST'])
def generate_poster():
    """生成海报"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        poster_type = data.get('poster_type', '小红书')  # 小红书 或 公众号
        
        if not content:
            return jsonify({'error': '内容不能为空'}), 400
        
        # 调用AI生成海报HTML
        poster_html = generate_poster_html(content, poster_type)
        
        if not poster_html:
            return jsonify({'error': 'AI服务调用失败，请检查配置'}), 500
        
        # 保存HTML文件
        poster_id = str(uuid.uuid4())
        poster_filename = f'poster_{poster_id}.html'
        poster_path = os.path.join('static/posters', poster_filename)
        
        with open(poster_path, 'w', encoding='utf-8') as f:
            f.write(poster_html)
        
        return jsonify({
            'success': True,
            'poster_id': poster_id,
            'poster_url': f'/static/posters/{poster_filename}',
            'download_url': f'/api/download-poster/{poster_id}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-poster/<poster_id>')
def download_poster(poster_id):
    """下载海报"""
    try:
        poster_filename = f'poster_{poster_id}.html'
        poster_path = os.path.join('static/posters', poster_filename)
        
        if not os.path.exists(poster_path):
            return jsonify({'error': '海报文件不存在'}), 404
        
        return send_file(poster_path, as_attachment=True, download_name=f'poster_{poster_id}.html')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """配置管理"""
    global config
    
    if request.method == 'GET':
        # 返回配置（隐藏敏感信息）
        safe_config = config.copy()
        if safe_config['ai_api_key']:
            safe_config['ai_api_key'] = '*' * 20
        return jsonify(safe_config)
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # 更新配置
            if 'ai_service_url' in data:
                config['ai_service_url'] = data['ai_service_url']
            if 'ai_api_key' in data:
                config['ai_api_key'] = data['ai_api_key']
            elif 'ai_api_key' not in data and os.getenv('API_KEY', '').strip():
                # 如果前端没有发送api_key字段，且环境变量中有默认密钥，则使用默认密钥
                config['ai_api_key'] = os.getenv('API_KEY', '')
            if 'ai_model' in data:
                config['ai_model'] = data['ai_model']
            
            return jsonify({'success': True, 'message': '配置更新成功'})
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/config/defaults', methods=['GET'])
def api_config_defaults():
    """获取默认配置信息（用于表单初始化）"""
    try:
        # 从环境变量获取默认配置，但不显示真实的API密钥
        defaults = {
            'ai_service_url': os.getenv('API_BASE_URL', 'https://api.openai.com/v1/chat/completions'),
            'ai_model': os.getenv('MODEL_NAME', 'gpt-3.5-turbo'),
            'has_api_key': bool(os.getenv('API_KEY', '').strip())  # 只返回是否有密钥，不返回具体值
        }
        return jsonify(defaults)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-ai', methods=['POST'])
def test_ai():
    """测试AI服务连接"""
    try:
        if not config['ai_api_key']:
            return jsonify({'error': 'AI API密钥未配置'}), 400
        
        # 发送测试请求
        headers = {
            'Authorization': f'Bearer {config["ai_api_key"]}',
            'Content-Type': 'application/json'
        }
        
        test_data = {
            'model': config['ai_model'],
            'messages': [{'role': 'user', 'content': '你好，这是一个测试消息'}],
            'max_tokens': 50,
            'stream': False
        }
        
        # 直接使用配置的API URL
        api_url = config['ai_service_url']
        
        response = requests.post(api_url, headers=headers, json=test_data, timeout=10)
        
        if response.status_code == 200:
            return jsonify({'success': True, 'message': 'AI服务连接正常'})
        else:
            error_detail = ''
            try:
                error_response = response.json()
                error_detail = f": {error_response}"
            except:
                error_detail = f": {response.text[:200]}"
            return jsonify({'error': f'AI服务返回错误 {response.status_code}{error_detail}'}), 500
    
    except Exception as e:
        return jsonify({'error': f'连接失败: {str(e)}'}), 500

def format_text_to_markdown(text):
    """将文本格式化为Markdown"""
    # 清理文本
    text = text.strip()
    
    # 分割成行
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 检测标题（基于常见模式）
        if re.match(r'^[一二三四五六七八九十\d]+[、.]', line):
            formatted_lines.append(f'## {line}')
        elif re.match(r'^[\d]+\.', line):
            formatted_lines.append(f'### {line}')
        elif line.endswith('：') or line.endswith(':'):
            formatted_lines.append(f'### {line}')
        elif len(line) < 30 and not line.endswith('。'):
            # 可能是标题
            formatted_lines.append(f'## {line}')
        else:
            # 普通段落
            formatted_lines.append(line)
        
        formatted_lines.append('')  # 添加空行
    
    return '\n'.join(formatted_lines)

def format_text_with_ai(text):
    """使用AI格式化文章为Markdown"""
    try:
        print(f"开始AI格式化，文本长度: {len(text)}")
        print(f"AI配置 - URL: {config['ai_service_url']}, Model: {config['ai_model']}, API Key存在: {bool(config['ai_api_key'])}")
        
        # 检查AI配置
        if not config['ai_api_key']:
            print("错误: AI API密钥未配置")
            return None
            
        # 构建AI提示词
        prompt = f"""请将以下文章内容格式化为适合微信公众号发布的Markdown格式。要求：

1. 识别并标记标题层级（使用 # ## ### 等）
2. 保持段落结构清晰
3. 适当添加强调和重点标记
4. 保持原文内容不变，只调整格式
5. 确保排版美观易读

原文内容：
{text}

请直接返回格式化后的Markdown内容，不要添加任何解释或说明。"""
        
        # 调用AI服务
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {config["ai_api_key"]}'
        }
        
        payload = {
            'model': config['ai_model'],
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.3,
            'max_tokens': 2000,
            'stream': False
        }
        
        # 直接使用配置的API URL
        api_url = config['ai_service_url']
        print(f"发送请求到: {api_url}")
        
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"API响应内容: {result}")
            if 'choices' in result and len(result['choices']) > 0:
                formatted_content = result['choices'][0]['message']['content'].strip()
                print(f"格式化成功，内容长度: {len(formatted_content)}")
                return formatted_content
            else:
                print("错误: API响应中没有choices字段或choices为空")
        else:
            print(f"API请求失败: {response.status_code}, {response.text}")
        
        return None
        
    except Exception as e:
        print(f"AI格式化错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_poster_html(content, poster_type):
    """调用AI生成海报HTML"""
    try:
        if not config['ai_api_key']:
            return None
        
        # 读取完整的提示词模板
        system_prompt = load_prompt_template()
        
        # 构建user prompt，将提示词模板和用户输入结合
        user_prompt = f"""请根据以下完整的提示词模板和用户输入，生成一个完整的HTML页面：

## 完整提示词模板：
{system_prompt}

## 用户输入：
- 封面类型：{poster_type}
- 文章内容：{content}

请严格按照提示词模板中的规则进行分析和设计，生成一个完整的HTML页面代码。HTML页面应该包含所有必要的CSS样式和JavaScript代码，可以直接在浏览器中运行。

要求：
1. 从文章内容中自动提取或生成一个合适的标题
2. 根据封面类型（小红书/公众号）选择合适的框架
3. 根据内容特点自动匹配最适合的视觉风格
4. 生成完整的HTML+CSS+JS代码
5. 包含下载功能
6. 确保代码可直接在浏览器中运行"""
        
        headers = {
            'Authorization': f'Bearer {config["ai_api_key"]}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': config['ai_model'],
            'messages': [
                {'role': 'system', 'content': '你是一位专业的网页和营销视觉设计师，擅长根据提示词生成完整的HTML页面。'},
                {'role': 'user', 'content': user_prompt}
            ],
            'max_tokens': 16000,
            'temperature': 0.7
        }
        
        # 直接使用配置的API URL
        api_url = config['ai_service_url']
        print(f"发送海报生成请求到: {api_url}")
        print(f"User prompt长度: {len(user_prompt)}")
        
        response = requests.post(api_url, headers=headers, json=data, timeout=600)
        
        print(f"海报生成API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"海报生成API响应: {result}")
            if 'choices' in result and len(result['choices']) > 0:
                html_content = result['choices'][0]['message']['content'].strip()
                print(f"生成HTML内容长度: {len(html_content)}")
                
                # 确保返回的是完整的HTML内容
                if not html_content.startswith('<!DOCTYPE html>'):
                    # 如果不是完整的HTML，包装一下
                    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>海报</title>
    {html_content}
</head>
<body>
</body>
</html>"""
                
                return html_content
            else:
                print("错误: 海报生成API响应中没有choices字段或choices为空")
                return None
        else:
            print(f'海报生成API错误: {response.status_code}, {response.text}')
            return None
    
    except Exception as e:
        print(f'生成海报HTML失败: {str(e)}')
        import traceback
        traceback.print_exc()
        return None

def load_prompt_template():
    """加载提示词模板"""
    try:
        with open('prompt/提示词.md', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        # 如果文件不存在，返回简化版提示词
        return """
你是一位优秀的网页和营销视觉设计师。请根据用户提供的文章内容，生成对应类型的HTML封面代码。

要求：
1. 从文章内容中自动提取或生成合适的标题
2. 生成完整的HTML代码，包含CSS样式
3. 确保代码可以直接在浏览器中运行
4. 根据内容类型自动选择合适的视觉风格
5. 包含下载功能
"""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)