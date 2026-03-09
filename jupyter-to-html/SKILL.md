---
name: jupyter-to-html
description: "将 Jupyter Notebook (.ipynb) 转换为带 MathJax 公式渲染的 HTML 文件，方便打印和分享。"
---

<role>
你是文档转换专家，将 Jupyter Notebook 转换为美观的 HTML 页面，支持数学公式渲染。
</role>

## Dependencies

- Python 3
- nbconvert (必需): `pip install nbconvert`
- pandoc (必需): 用于 Markdown 转换
- MathJax: nbconvert 自带，HTML 中自动加载

## 安装

```bash
# 安装 nbconvert
pip install nbconvert

# 确保 pandoc 已安装
# Ubuntu/Debian: sudo apt install pandoc
# macOS: brew install pandoc
# Windows: choco install pandoc
```

## 使用方式

### 基本转换

```bash
# 将 ipynb 转换为 HTML（默认不包含输出）
jupyter nbconvert --to html_notebook --execute input.ipynb --output output.html

# 仅转换，不执行（保留原有输出）
jupyter nbconvert --to html_notebook input.ipynb --output output.html

# 包含执行输出（重新运行代码）
jupyter nbconvert --to html_notebook --execute input.ipynb
```

### 高级选项

```bash
# 指定模板（可自定义模板目录）
jupyter nbconvert --to html input.ipynb --template full

# 移除代码单元格的输入，仅显示输出
jupyter nbconvert --to html input.ipynb --TagRemovePreprocessor.remove_input_tags=show_output

# 移除代码单元格（仅保留文本）
jupyter nbconvert --to html input.ipynb --to html_text_only

# 自定义 CSS 样式
jupyter nbconvert --to html input.ipynb --HTMLExporter.theme=light

# 禁用 Markdown 单元格
jupyter nbconvert --to html input.ipynb --disable-prettyprints
```

### Python 脚本方式

```bash
# 使用脚本（支持更多选项）
python3 jupyter_to_html.py input.ipynb [output.html]
```

## 配置选项

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--execute` | 是否执行 notebook | 否 |
| `--template` | 模板: full, basic, lab | full |
| `--theme` | 主题: light, dark | light |
| `--no-input` | 隐藏代码输入 | 否 |
| `--clear-output` | 清除输出后转换 | 否 |

## 输出说明

- HTML 文件包含内联 CSS 样式
- 数学公式通过 MathJax 自动渲染
- 代码高亮使用 highlight.js
- 支持响应式布局

## 常见问题

**Q: 数学公式不显示？**
A: 确保网络连接正常（MathJax 从 CDN 加载），或使用 `--embed-resources` 打包

**Q: 图片不显示？**
A: 使用 `--embed-resources` 将图片转为 base64 内嵌

**Q: 中文显示乱码？**
A: 添加 `--application=pdf` 或在 HTML 头指定 UTF-8 编码
