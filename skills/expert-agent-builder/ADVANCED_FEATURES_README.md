# Expert Agent Builder - 高级功能说明文档

本文档详细介绍 Expert Agent Builder 的三大高级功能：自定义领域管理、模板覆盖机制和智能领域检测。

---

## 目录

1. [功能概览](#功能概览)
2. [自定义领域管理器](#自定义领域管理器)
3. [模板管理器](#模板管理器)
4. [智能领域检测器](#智能领域检测器)
5. [快速开始](#快速开始)
6. [API 参考](#api-参考)

---

## 功能概览

### 三大高级功能

| 功能 | 描述 | 主要用途 |
|------|------|----------|
| **自定义领域管理器** | 通过JSON文件定义新的专业领域 | 扩展系统支持的专业领域 |
| **模板管理器** | 多级模板查找和自定义覆盖 | 自定义生成的配置内容 |
| **智能领域检测器** | 基于关键词和相似度的领域推荐 | 自动识别Agent最适合的领域 |

---

## 自定义领域管理器

### 概述

`CustomDomainManager` 允许你通过 JSON 文件定义全新的专业领域，无需修改源代码即可扩展系统的领域支持。

### 核心功能

- **创建领域**: 通过 JSON 配置创建新领域
- **读取领域**: 获取领域配置信息
- **更新领域**: 修改已有领域配置
- **删除领域**: 移除不再需要的领域
- **列出领域**: 查看所有自定义领域

### 使用示例

```python
from utils.custom_domain_manager import CustomDomainManager

# 初始化管理器
manager = CustomDomainManager(custom_domains_dir="custom_domains")

# 创建新领域
config = {
    "description": "教育规划、学业指导、职业发展咨询",
    "soul_core_truths": [
        "真诚地帮助学生实现教育目标",
        "拥有专业教育观点"
    ],
    "professional_values": [
        "**教育伦理**：所有建议必须符合教育伦理",
        "**个性化发展**：尊重每个学生的独特性"
    ],
    "tools": [
        "**学业评估工具**：学习能力测评、兴趣倾向测试",
        "**教育资源库**：院校数据库、专业介绍"
    ],
    "workflows": [
        "需求评估 → 目标设定 → 方案制定 → 实施跟踪",
        "现状分析 → 问题诊断 → 策略建议 → 效果评估"
    ],
    "formality_level": 7,
    "technical_depth": 7,
    "emotional_intelligence": 9,
    "color_scheme": "green"
}

success = manager.create_domain("教育咨询", config)
print(f"创建结果: {'成功' if success else '失败'}")

# 获取领域配置
domain_config = manager.get_domain("教育咨询")
print(f"描述: {domain_config['description']}")

# 更新领域配置
manager.update_domain("教育咨询", {
    "formality_level": 8,
    "technical_depth": 8
})

# 列出所有自定义领域
domains = manager.list_domains()
print(f"自定义领域: {domains}")

# 删除领域
# manager.delete_domain("教育咨询")
```

### JSON 配置结构

自定义领域的 JSON 配置文件结构如下：

```json
{
  "name": "领域名称",
  "code": "领域代码",
  "description": "领域描述",
  "soul_core_truths": ["核心真理1", "核心真理2", ...],
  "professional_values": ["价值观1", "价值观2", ...],
  "tools": ["工具1", "工具2", ...],
  "workflows": ["流程1", "流程2", ...],
  "formality_level": 7,
  "technical_depth": 8,
  "emotional_intelligence": 7,
  "color_scheme": "blue"
}
```

---

## 模板管理器

### 概述

`TemplateManager` 提供了多级模板查找机制，支持自定义模板覆盖默认模板，实现高度灵活的配置内容定制。

### 核心功能

- **多级模板查找**: 自定义 → 领域特定 → 默认
- **模板变量渲染**: 支持 `{{variable}}` 语法
- **模板缓存**: 提高重复访问性能
- **模板管理**: 保存、删除、列出模板

### 多级查找优先级

模板查找按照以下优先级进行：

1. **自定义模板** (`custom_templates_dir/`) - 最高优先级
2. **领域特定模板** (`domain_templates/{domain}/`) - 中等优先级
3. **默认模板** (`default_templates_dir/`) - 最低优先级

### 使用示例

```python
from utils.template_manager import TemplateManager

# 初始化管理器
manager = TemplateManager(
    custom_templates_dir="my_templates",
    domain_templates_dir="domain_templates",
    default_templates_dir="templates"
)

# 获取模板（自动按优先级查找）
template_content = manager.get_template("soul_template.md", domain="技术架构")

# 渲染模板（替换变量）
rendered = manager.render_template(
    "soul_template.md",
    variables={
        "agent_name": "技术架构顾问",
        "core_truths": "- 真诚服务用户\n- 保持专业标准",
        "user_name": "张三"
    },
    domain="技术架构"
)

print(rendered)

# 保存自定义模板
custom_template = """
# {{title}}

## 自定义配置

{{content}}
"""
manager.save_custom_template("my_custom_template.md", custom_template)

# 列出所有可用模板
templates = manager.list_templates(domain="技术架构")
print(f"自定义: {templates['custom']}")
print(f"领域特定: {templates['domain']}")
print(f"默认: {templates['default']}")
```

### 模板变量语法

模板支持以下变量语法：

- `{{variable}}` - 基本变量替换
- `{{variable:default_value}}` - 带默认值的变量

示例：

```markdown
# {{agent_name}}

## 核心配置

**用户名称**: {{user_name:用户}}

**核心真理**:
{{core_truths}}

**专业价值观**:
{{professional_values}}
```

---

## 智能领域检测器

### 概述

`DomainDetector` 通过分析 Agent 描述文本，基于关键词匹配和文本相似度算法，自动推荐最合适的专业领域。

### 核心功能

- **关键词匹配**: 基于预定义的领域关键词库进行匹配
- **正则模式匹配**: 支持正则表达式模式识别
- **文本相似度**: 使用 SequenceMatcher 计算文本相似度
- **置信度评估**: 提供匹配置信度分数

### 检测算法

领域检测采用多维度评分算法：

1. **关键词匹配评分** (权重最高)
   - 每个领域有预定义的关键词和权重
   - 关键词在描述中出现次数越多，得分越高
   - 前3次出现权重分别为 1.0, 0.5, 0.25

2. **正则模式匹配** (额外加分)
   - 每个领域有特定的正则模式
   - 每个匹配的模式额外加5分

3. **文本相似度** (辅助判断)
   - 使用 Python 的 `difflib.SequenceMatcher`
   - 将相似度（0-1）转换为 0-20 的分数

### 使用示例

```python
from utils.domain_detector import DomainDetector, detect_domain, suggest_domain

# 初始化检测器
detector = DomainDetector()

# 测试描述
description = """
资深云原生架构师，专注于分布式系统设计和微服务架构。
精通Kubernetes、Docker容器化技术，擅长高可用架构设计、性能优化。
拥有10年以上大型互联网系统架构经验。
"""

# 检测领域（返回前3个最匹配的领域）
results = detector.detect_domain(description, top_k=3)

print("检测结果:")
for i, (domain, score) in enumerate(results, 1):
    print(f"  {i}. {domain}: {score}%")

# 便捷函数：直接检测
results = detect_domain(description, top_k=3)

# 便捷函数：获取建议（带置信度阈值）
suggested = suggest_domain(description, threshold=60.0)
if suggested:
    print(f"\n建议领域: {suggested}")
else:
    print("\n置信度不足，无法给出明确建议")

# 获取特定领域的置信度
confidence = detector.get_domain_confidence(description, "技术架构")
print(f"与技术架构的匹配置信度: {confidence}%")
```

### 关键词配置

每个领域都有预定义的关键词和权重，例如：

```python
DOMAIN_KEYWORDS = {
    "技术架构": {
        "keywords": {
            "架构": 5, "系统": 4, "技术": 4, "云原生": 5, "分布式": 5,
            "微服务": 5, "架构师": 5, "技术选型": 4, ...
        },
        "patterns": [
            r"架构.*设计", r"技术.*架构", r"系统.*架构", ...
        ]
    },
    # ... 其他领域
}
```

---

## 快速开始

### 环境准备

确保已安装 Expert Agent Builder 的所有依赖：

```bash
# Python 3.8+
python --version

# 无需额外依赖（使用Python标准库）
```

### 运行演示

执行演示脚本查看所有高级功能：

```bash
python demo_advanced_features.py
```

### 在项目中使用

```python
# 导入所需模块
from utils.custom_domain_manager import CustomDomainManager
from utils.template_manager import TemplateManager
from utils.domain_detector import DomainDetector

# 初始化组件
domain_manager = CustomDomainManager()
template_manager = TemplateManager()
domain_detector = DomainDetector()

# 开始使用...
```

---

## API 参考

### CustomDomainManager

| 方法 | 描述 | 返回类型 |
|------|------|----------|
| `create_domain(name, config)` | 创建新领域 | `bool` |
| `get_domain(name)` | 获取领域配置 | `Optional[Dict]` |
| `update_domain(name, updates)` | 更新领域配置 | `bool` |
| `delete_domain(name)` | 删除领域 | `bool` |
| `list_domains()` | 列出所有领域 | `List[str]` |
| `get_all_domains()` | 获取所有领域配置 | `Dict[str, Dict]` |

### TemplateManager

| 方法 | 描述 | 返回类型 |
|------|------|----------|
| `get_template(name, domain)` | 获取模板内容 | `Optional[str]` |
| `render_template(name, variables, domain)` | 渲染模板 | `Optional[str]` |
| `save_custom_template(name, content)` | 保存自定义模板 | `bool` |
| `delete_custom_template(name)` | 删除自定义模板 | `bool` |
| `list_templates(domain)` | 列出所有模板 | `Dict[str, List]` |
| `clear_cache()` | 清除模板缓存 | `None` |

### DomainDetector

| 方法 | 描述 | 返回类型 |
|------|------|----------|
| `detect_domain(description, top_k)` | 检测领域 | `List[Tuple[str, float]]` |
| `get_domain_confidence(desc, domain)` | 获取置信度 | `float` |
| `suggest_domain(description, threshold)` | 建议领域 | `Optional[str]` |

---

## 最佳实践

### 1. 自定义领域命名

- 使用清晰、描述性的名称
- 避免与内置领域重名
- 使用中文名称便于理解

### 2. 模板设计

- 保持模板简洁清晰
- 使用有意义的变量名
- 提供合理的默认值

### 3. 领域检测

- 提供详细的Agent描述以提高检测准确性
- 结合置信度阈值进行判断
- 对于模糊描述，可返回多个候选领域供用户选择

---

## 故障排除

### 常见问题

#### 1. 自定义领域未生效

**问题**: 创建的自定义领域在生成配置时未使用

**解决**:
- 检查JSON文件格式是否正确
- 确认 `custom_domains_dir` 路径正确
- 验证领域名称拼写

#### 2. 模板变量未替换

**问题**: 生成的配置中变量未被替换

**解决**:
- 检查变量语法是否正确 `{{variable}}`
- 确认变量名拼写
- 确保传递的变量字典包含所需键

#### 3. 领域检测不准确

**问题**: 领域检测结果与预期不符

**解决**:
- 提供更详细的Agent描述
- 使用专业术语和关键词
- 结合 `get_domain_confidence` 进行置信度判断

---

## 更新日志

### v2.1.0 (2026-04-16)

- **新增** 自定义领域管理器 (`CustomDomainManager`)
- **新增** 模板管理器 (`TemplateManager`)
- **新增** 智能领域检测器 (`DomainDetector`)
- **新增** 高级功能演示脚本 (`demo_advanced_features.py`)
- **新增** 高级功能说明文档 (`ADVANCED_FEATURES_README.md`)

---

## 支持与反馈

如有问题或建议，请通过以下方式反馈：

- GitHub Issues: [提交问题](https://github.com/pkulyn/expert-agent-builder/issues)
- 邮箱: [联系作者](mailto:your.email@example.com)

---

*本文档最后更新于 2026-04-16*
