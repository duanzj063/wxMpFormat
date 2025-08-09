#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
微信文章格式化与海报生成系统 - 启动脚本
使用uv环境运行应用
"""

import os
import sys
import subprocess

def main():
    """主函数"""
    # 检查是否安装了uv
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 未找到uv，请先安装uv")
        print("安装命令: pip install uv")
        sys.exit(1)
    
    # 检查是否存在pyproject.toml
    if not os.path.exists("pyproject.toml"):
        print("错误: 未找到pyproject.toml文件")
        sys.exit(1)
    
    # 同步依赖
    print("正在同步依赖...")
    try:
        subprocess.run(["uv", "sync"], check=True)
        print("依赖同步完成")
    except subprocess.CalledProcessError:
        print("错误: 依赖同步失败")
        sys.exit(1)
    
    # 启动应用
    print("正在启动应用...")
    print("访问地址: http://127.0.0.1:5000")
    print("按 Ctrl+C 停止服务")
    
    try:
        subprocess.run(["uv", "run", "python", "app.py"])
    except KeyboardInterrupt:
        print("\n应用已停止")
    except subprocess.CalledProcessError as e:
        print(f"错误: 应用启动失败 - {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()