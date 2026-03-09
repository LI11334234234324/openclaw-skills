#!/usr/bin/env python3
"""
Jupyter Notebook to HTML Converter
将 .ipynb 文件转换为带 MathJax 公式渲染的 HTML
支持批量转换、自定义模板、版本检查等功能
"""

import argparse
import subprocess
import sys
import tempfile
import shutil
import os
import json
import logging
from pathlib import Path
from packaging import version
from datetime import datetime

# 全局日志记录器
logger = None

def setup_logging(log_file=None):
    """设置日志记录"""
    global logger
    logger = logging.getLogger('jupyter_to_html')
    logger.setLevel(logging.INFO)

    # 清除现有的处理器
    logger.handlers.clear()

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    if log_file:
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger

def load_config(config_file):
    """从 JSON 配置文件加载默认参数"""
    if not os.path.exists(config_file):
        return {}

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  警告: 无法加载配置文件 {config_file}: {e}")
        return {}

def check_dependencies():
    """检查必要的依赖和版本"""
    try:
        result = subprocess.run(['jupyter', 'nbconvert', '--version'],
                              capture_output=True, text=True, check=True)
        version_str = result.stdout.strip().split()[-1]
        print(f"✓ nbconvert 版本: {version_str}")

        if version.parse(version_str) < version.parse("6.0"):
            print("⚠️  警告: nbconvert 版本 < 6.0，某些功能可能不可用")
            return True
        return True
    except FileNotFoundError:
        print("❌ 错误: 未找到 jupyter 命令，请确保已安装。")
        print("   安装命令: pip install jupyter nbconvert")
        return False
    except Exception as e:
        print(f"⚠️  无法检查版本: {e}")
        return True

def validate_path(file_path):
    """验证路径合法性"""
    path = Path(file_path)

    # 检查路径是否包含非法字符
    if not path.is_absolute():
        path = path.resolve()

    try:
        # 测试路径的有效性
        str(path)
        return path
    except (ValueError, TypeError) as e:
        raise ValueError(f"❌ 路径非法: {file_path} - {e}")

def get_file_size(file_path):
    """获取文件大小（MB）"""
    return os.path.getsize(file_path) / (1024 * 1024)

def convert(input_file, output_file=None, execute=False, no_input=False,
           clear_output=False, theme='light', embed_resources=False,
           template=None, timeout=600, verbose=False):
    """转换单个 Jupyter Notebook 到 HTML"""

    try:
        input_path = validate_path(input_file)
    except ValueError as e:
        print(e)
        return False

    if not input_path.exists():
        print(f"❌ 文件不存在: {input_file}")
        return False

    if not input_path.suffix.lower() == '.ipynb':
        print(f"❌ 不是有效的notebook文件: {input_file}")
        return False

    # 获取文件大小，用于进度提示
    file_size = get_file_size(input_path)

    if output_file:
        try:
            output_path = validate_path(output_file)
        except ValueError as e:
            print(e)
            return False
    else:
        output_path = input_path.with_suffix('.html')

    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 基础命令：标准使用 --to html
    cmd = ['jupyter', 'nbconvert', '--to', 'html', str(input_path)]

    # 添加功能选项
    if execute:
        cmd.append('--execute')

    if no_input:
        cmd.append('--TemplateExporter.exclude_input=True')
        cmd.append('--TemplateExporter.exclude_prompt=True')

    if clear_output:
        cmd.append('--ClearOutputPreprocessor.enabled=True')

    if theme in ['light', 'dark']:
        cmd.append(f'--HTMLExporter.theme={theme}')

    if embed_resources:
        cmd.append('--embed-resources')

    if template:
        cmd.append(f'--template={template}')

    # 指定输出文件 (使用绝对路径)
    cmd.extend(['--output', str(output_path.absolute())])

    size_str = f"({file_size:.1f}MB)" if file_size > 0.1 else ""
    print(f"🔄 转换: {input_path.name} {size_str} → {output_path.name}")

    # 显示转换选项
    options = []
    if execute:
        options.append("执行代码")
    if no_input:
        options.append("隐藏输入")
    if clear_output:
        options.append("清除输出")
    if theme == 'dark':
        options.append("深色主题")
    if embed_resources:
        options.append("内嵌资源")
    if options:
        print(f"   选项: {', '.join(options)}")

    # 记录日志
    if logger:
        logger.info(f"开始转换: {input_path} (大小: {file_size:.1f}MB)")

    try:
        start_time = datetime.now()
        if verbose:
            print(f"🔍 命令: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=timeout)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        output_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✅ 转换成功: {output_path.absolute()}")
        print(f"   输出文件大小: {output_size:.1f}MB")
        print(f"   耗时: {duration:.2f}秒")

        if logger:
            logger.info(f"转换成功: {output_path} (输出大小: {output_size:.1f}MB, 耗时: {duration:.2f}秒)")

        return True
    except subprocess.TimeoutExpired:
        print(f"❌ 超时: 转换耗时过长（>{timeout}秒），可能是大文件或代码执行耗时")
        if logger:
            logger.error(f"转换超时 (>{timeout}秒): {input_path}")
        return False
    except FileNotFoundError:
        print("❌ 错误: 未找到 jupyter 命令，请确保已安装。")
        if logger:
            logger.error("未找到 jupyter 命令")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ 执行失败:")
        error_msg = e.stderr if e.stderr else e.stdout
        print(error_msg)
        if logger:
            logger.error(f"转换失败: {input_path}\n{error_msg}")
        return False

def convert_batch(input_pattern, output_dir=None, timeout=600, verbose=False, **kwargs):
    """批量转换 Notebook 文件"""
    from glob import glob

    # 扩展通配符
    files = glob(input_pattern, recursive=True)

    if not files:
        print(f"❌ 未找到匹配的文件: {input_pattern}")
        if logger:
            logger.error(f"未找到匹配的文件: {input_pattern}")
        return False

    print(f"📂 找到 {len(files)} 个文件")
    if logger:
        logger.info(f"批量转换: 找到 {len(files)} 个文件")

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 输出目录: {output_dir.absolute()}")
        if logger:
            logger.info(f"输出目录: {output_dir.absolute()}")
    else:
        output_dir = None

    success_count = 0
    failed_count = 0
    total_time = 0

    for idx, input_file in enumerate(files, 1):
        print(f"\n[{idx}/{len(files)}] ", end="")

        output_file = None
        if output_dir:
            output_file = output_dir / (Path(input_file).stem + '.html')

        start = datetime.now()
        if convert(input_file, output_file=output_file, timeout=timeout, verbose=verbose, **kwargs):
            success_count += 1
        else:
            failed_count += 1
        elapsed = (datetime.now() - start).total_seconds()
        total_time += elapsed

    print(f"\n📊 批量转换完成!")
    print(f"   成功: {success_count}/{len(files)}")
    print(f"   失败: {failed_count}/{len(files)}")
    print(f"   总耗时: {total_time:.2f}秒")
    print(f"   平均耗时: {total_time/len(files):.2f}秒/个")

    if logger:
        logger.info(f"批量转换完成: 成功 {success_count}/{len(files)}, 失败 {failed_count}/{len(files)}, 总耗时 {total_time:.2f}秒")

    return failed_count == 0

def main():
    parser = argparse.ArgumentParser(
        description='将 Jupyter Notebook 转换为独立、美观的 HTML',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
单个文件转换示例:
  %(prog)s input.ipynb                          # 基础转换
  %(prog)s input.ipynb out.html                 # 指定输出文件名
  %(prog)s input.ipynb --execute                # 自动运行代码后再转换
  %(prog)s input.ipynb --no-input               # 仅保留输出结果（隐藏代码）
  %(prog)s input.ipynb --template lab           # 使用自定义模板

批量转换示例:
  %(prog)s --batch "*.ipynb" -o output_dir/     # 批量转换当前目录
  %(prog)s --batch "**/*.ipynb" -o html_output/ # 递归批量转换
  %(prog)s --batch "*.ipynb" --embed --theme dark # 批量转换带嵌入资源和暗黑主题

高级选项:
  %(prog)s input.ipynb --timeout 1200           # 指定超时时间（秒）
  %(prog)s input.ipynb --log conversion.log     # 保存转换日志
  %(prog)s input.ipynb --config config.json     # 从配置文件加载默认参数
  %(prog)s input.ipynb --verbose                # 显示详细的执行信息
        """
    )

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    parser.add_argument('input', nargs='?', help='输入的 .ipynb 文件或通配符模式')
    parser.add_argument('output', nargs='?', help='输出的 HTML 文件或目录（可选）')

    # 转换选项
    parser.add_argument('-e', '--execute', action='store_true',
                       help='执行 notebook 后转换')
    parser.add_argument('-n', '--no-input', action='store_true',
                       help='隐藏代码单元格，仅显示输出和文本')
    parser.add_argument('-c', '--clear-output', action='store_true',
                       help='清除所有输出后转换')
    parser.add_argument('-t', '--theme', choices=['light', 'dark'], default='light',
                       help='HTML 主题 (默认: light)')
    parser.add_argument('--embed', dest='embed_resources', action='store_true',
                       help='内嵌外部资源（如图片）到单个 HTML 文件中')
    parser.add_argument('--template', type=str, default=None,
                       help='使用自定义HTML模板（如: lab, classic）')

    # 批量处理选项
    parser.add_argument('-b', '--batch', action='store_true',
                       help='批量模式：使用通配符转换多个文件')
    parser.add_argument('-o', '--output-dir', type=str, dest='output_dir',
                       help='批量转换的输出目录')

    # 高级选项
    parser.add_argument('--timeout', type=int, default=600, metavar='SECONDS',
                       help='转换超时时间（秒，默认: 600）')
    parser.add_argument('--log', type=str, default=None, metavar='FILE',
                       help='保存日志到指定文件')
    parser.add_argument('--config', type=str, default=None, metavar='FILE',
                       help='从 JSON 配置文件加载默认参数')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='显示详细的执行信息和命令')

    args = parser.parse_args()

    # 设置日志
    if args.log:
        log_dir = Path(args.log).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        setup_logging(args.log)
        print(f"📝 日志将保存到: {Path(args.log).absolute()}")
    else:
        setup_logging()

    # 从配置文件加载默认参数
    config = {}
    if args.config:
        config = load_config(args.config)
        print(f"📋 从配置文件加载参数: {Path(args.config).absolute()}")

    # 合并配置和命令行参数 (命令行参数优先)
    execute = args.execute or config.get('execute', False)
    no_input = args.no_input or config.get('no_input', False)
    clear_output = args.clear_output or config.get('clear_output', False)
    theme = args.theme if args.theme != 'light' else config.get('theme', 'light')
    embed_resources = args.embed_resources or config.get('embed_resources', False)
    template = args.template or config.get('template', None)
    timeout = args.timeout if args.timeout != 600 else config.get('timeout', 600)
    verbose = args.verbose or config.get('verbose', False)

    if not args.input:
        parser.print_help()
        sys.exit(1)

    if args.batch:
        # 批量转换模式
        success = convert_batch(
            args.input,
            output_dir=args.output_dir or args.output,
            execute=execute,
            no_input=no_input,
            clear_output=clear_output,
            theme=theme,
            embed_resources=embed_resources,
            template=template,
            timeout=timeout,
            verbose=verbose
        )
    else:
        # 单个文件转换模式
        success = convert(
            args.input,
            output_file=args.output,
            execute=execute,
            no_input=no_input,
            clear_output=clear_output,
            theme=theme,
            embed_resources=embed_resources,
            template=template,
            timeout=timeout,
            verbose=verbose
        )

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
