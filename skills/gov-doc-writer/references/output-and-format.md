# 输出格式与公文规范

## 输出格式选项

最终定稿支持输出为：
- **Word文档（.docx）**（推荐）：用 python-docx 生成，自动套用公文格式
- 飞书云文档（用 feishu_create_doc）
- Markdown 文件（保存到工作区）
- 飞书消息（直接发送到对话）

## 公文格式规范（参照 GB/T 9704-2012）

生成 Word 文档时，必须按以下标准排版：

| 要素 | 规范 |
|------|------|
| 纸张 | A4（210×297mm） |
| 页边距 | 上37mm、下35mm、左28mm、右26mm |
| 标题 | 黑体，二号（22pt），居中，不加粗 |
| 正文 | 仿宋，三号（16pt） |
| 一级标题（一、二、） | 黑体，三号（16pt） |
| 二级标题（（一）（二）） | 楷体，三号（16pt） |
| 三级标题（1. 2.） | 仿宋，三号（16pt），加粗 |
| 行距 | 固定值28.8pt |
| 首行缩进 | 2字符 |

> ⚠️ 标准国标要求标题使用小标宋体，但该字体为专用字体多数电脑未安装，默认以**黑体**替代。如用户需要小标宋体，可单独调整。

### python-docx 格式配置参考

```python
from docx.shared import Pt, Cm

# 页面设置
section.top_margin = Cm(3.7)
section.bottom_margin = Cm(3.5)
section.left_margin = Cm(2.8)
section.right_margin = Cm(2.6)

# 标题：黑体 二号 居中
run.font.name = '黑体'
run.font.size = Pt(22)
paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 正文：仿宋 三号 首行缩进2字符 行距固定28.8pt
run.font.name = '仿宋'
run.font.size = Pt(16)
paragraph.paragraph_format.first_line_indent = Pt(32)  # 2字符≈32pt
paragraph.paragraph_format.line_spacing = Pt(28.8)

# 一级标题：黑体 三号
run.font.name = '黑体'
run.font.size = Pt(16)

# 二级标题：楷体 三号
run.font.name = '楷体'
run.font.size = Pt(16)
```
