#!/usr/bin/env python3
"""
Jupyter Notebook to HTML Converter
将 .ipynb 文件转换为带 MathJax 公式渲染的 HTML
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def convert(input_file, output_file=None, execute=False, no_input=False, 
           clear_output=False, theme='light', embed_resources=False):
    """转换 Jupyter Notebook 到 HTML"""
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_file}")
        return False
    
    # 确定输出文件名
    if output_file:
        output_path = Path(output_file)
    else:
        output_path = input_path.with_suffix('.html')
    
    # 构建命令
    cmd = ['jupyter', 'nbconvert', '--to', 'html_notebook', str(input_path)]
    
    # 添加选项
    if execute:
        cmd.append('--execute')
    
    if no_input:
        cmd.append('--to')
        cmd.append('html')
        cmd.append('--TemplateExporter.exclude_input=True')
    
    if clear_output:
        cmd.append('--ClearOutputPreprocessor.enabled=True')
    
    if theme:
        cmd.extend([f'--HTMLExporter.theme={theme}'])
    
    if embed_resources:
        cmd.append('--embed-resources')
    
    # 指定输出
    cmd.extend(['--output', str(output_path)])
    
    print(f"🔄 转换: {input_path.name} → {output_path.name}")
    print(f"📋 命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if result.returncode == 0:
            print(f"✅ 转换成功: {output_path.absolute()}")
            return True
        else:
            print(f"❌ 转换失败: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ 错误: 未找到 jupyter 命令")
        print("   请安装: pip install jupyter nbconvert")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ 执行失败: {e.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='将 Jupyter Notebook 转换为 HTML',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s input.ipynb
  %(prog)s input.ipynb output.html
  %(prog)s input.ipynb --execute          # 执行后转换
  %(prog)s input.ipynb --no-input        # 隐藏代码输入
  %(prog)s input.ipynb --embed-resources # 内嵌资源
        """
    )
    
    parser.add_argument('input', help='输入的 .ipynb 文件')
    parser.add_argument('output', nargs='?', help='输出的 HTML 文件（可选）')
    parser.add_argument('-e', '--execute', action='store_true', 
                        help='执行 notebook 后转换')
    parser.add_argument('-n', '--no-input', action='store_true',
                        help='隐藏代码输入，仅显示输出和文本')
    parser.add_argument('-c', '--clear-output', action='store_true',
                        help='清除输出后转换')
    parser.add_argument('-t', '--theme', choices=['light', 'dark'], default='light',
                        help='HTML 主题 (默认: light)')
    parser.add_argument('--embed', dest='embed_resources', action='store_true',
                        help='内嵌资源（图片等）到 HTML')
    
    args = parser.parse_args()
    
    success = convert(
        args.input,
        args.output,
        execute=args.execute,
        no_input=args.no_input,
        clear_output=args.clear_output,
        theme=args.theme,
        embed_resources=args.embed_resources
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
