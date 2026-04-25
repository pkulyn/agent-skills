# 专家级Agent构建器（Expert Agent Builder）

<p align="center">
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  </a>
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  </a>
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" alt="Multi-Platform">
  <img src="https://img.shields.io/badge/version-2.2.0-orange" alt="Version 2.2.0">
  <img src="https://img.shields.io/badge/docs-完整-brightgreen" alt="Docs Complete">
</p>

基于四层六维专业人格模型研究成果开发的配置生成工具，帮助用户快速创建专家级Agent配置文件。

**Claude Code Skill 集成**：本项目已转换为 Claude Code 标准 Skill 格式（SKILL.md），可直接通过 `@expert-agent-builder` 调用。

## 特性

- **智能交互流程**：基于四层六维专业人格模型的增强交互，支持平台/模式选择、混合信息获取方式
- **多Agent协作系统**：支持团队信息收集、多个Agent画像定义、协作规则制定
- **双平台支持**：OpenClaw和Claude Code双平台配置生成
- **智能生成**：基于四层六维专业人格模型生成高质量配置
- **多维度验证**：完整性、一致性、质量三重验证
- **10大专业领域**：技术架构、法律咨询、商业战略、创意设计、医学研究、党政公文写作、科幻小说创作、团队协作管理、评审评估、知识管理
- **领域深度适配**：每个领域拥有独立的人格底色、判断立场、说话规则、做事规矩、禁忌清单
- **人性化配置**：SOUL.md以自然语言描述情感行为倾向，数字参数不再暴露到配置文件
- **YAML Front Matter开关**：可选在生成的Markdown中包含/排除Front Matter元数据
- **多Agent批量生成**：支持一次性批量处理多个Agent配置
- **向后兼容**：保持现有功能完整，新增智能模式为默认选项
- **一键运行**：提供完整的示例和运行脚本
- **高级扩展功能**：
  - **自定义领域管理**：通过JSON配置扩展专业领域支持
  - **模板覆盖机制**：多级模板查找和自定义内容覆盖
  - **智能领域检测**：基于关键词和相似度的自动领域推荐

## 快速开始

### 安装

确保系统中已安装Python 3.8或更高版本。

```bash
python --version
```

### 使用方式

#### 1. 智能模式（推荐）

基于四层六维专业人格模型的增强交互流程：

```bash
python openclaw-config-generator.py --mode smart
```

**智能模式特点**：
- **平台选择**：OpenClaw或Claude Code平台
- **Agent模式**：单Agent或多Agent协作系统
- **信息获取方式**：交互式问答、资料整理、混合模式
- **信息确认**：收集信息后用户确认再生成配置

#### 2. 交互式模式（传统 - 向后兼容）

```bash
python openclaw-config-generator.py --mode interactive
```

#### 3. 生成模式

基于现有模板文件生成配置：

```bash
python openclaw-config-generator.py \
  --mode generate \
  --user-profile templates/user-profile.json \
  --agent-profile templates/agent-profile.json \
  --output-dir my-agent-config
```

#### 4. 验证模式

```bash
python openclaw-config-generator.py \
  --mode validate \
  --config-dir existing-config \
  --validation-level strict
```

#### 5. 示例模式

```bash
python openclaw-config-generator.py --mode example
```

#### 6. 多格式输出支持

1. **OpenClaw格式** (`--format openclaw`)：生成5个配置文件（SOUL.md、IDENTITY.md、TOOLS.md、AGENTS.md、USER.md）
2. **Claude Code格式** (`--format claudecode`)：生成2个配置文件（CLAUDE.md 和 Agent配置文件）
3. **双格式输出** (`--format both`)：同时生成OpenClaw和Claude Code格式配置

#### 7. 批量生成模式

```bash
python openclaw-config-generator.py \
  --mode generate \
  --agent-profiles-dir ./agent_profiles \
  --output-dir ./generated_configs
```

## 配置文件结构

生成的配置包含5个核心文件：

| 文件 | 描述 | 核心内容 |
|------|------|----------|
| `SOUL.md` | Agent灵魂与核心价值观 | 性格底色、价值观、表达风格、做事规矩、边界和禁忌 |
| `IDENTITY.md` | Agent身份锚点 | Name、Role、One-liner、Relationship vibe、Vibe、Emoji |
| `TOOLS.md` | Agent专业工具与工作环境 | 本地技术环境、领域专用工具、工具使用要点 |
| `AGENTS.md` | Agent工作流程与协作方式 | 会话启动协议、记忆系统、核心工作流程、交付标准、协作协议 |
| `USER.md` | Agent对用户的理解与关系管理 | 用户信息、沟通偏好、项目上下文 |

### SOUL.md 设计理念

SOUL.md是Agent的灵魂定义，采用"有主见"设计原则：

- **性格底色**：领域特有的性格倾向（自然语言描述，非评分数字）
- **价值观**：领域立场 + 领域原则（每个领域的"有主见"视角不同）
- **表达风格**：说话的语气、态度、直接程度（如"正式规范，不越线"或"善用比喻，少用抽象概念"）
- **做事规矩**：方法论、证据导向、有主见坚持（如"数据驱动决策，不凭感觉"、"有疑义的地方主动标注"）
- **边界和禁忌**：行业红线 + 通用安全边界

### IDENTITY.md 设计理念

IDENTITY.md是极简的身份锚点（约10行），只回答"自己觉得是谁"：

```
Name: [Agent名称]
Role: [一句话角色定义]
One-liner: [最能代表这个Agent的一句话]
Relationship vibe: [与用户的关系感]
Vibe: [整体氛围]
Emoji: [签名Emoji]
```

## 专业领域支持

### 技术架构
- 系统架构设计、技术选型评估、性能优化
- 立场：好的架构是删出来的，不是加出来的

### 法律咨询
- 法律研究、合同分析、合规性检查
- 立场：法律不是障碍，是护栏

### 商业战略
- 市场分析、财务分析、战略规划
- 立场：数据不说谎，但数据也不说话——解读得靠人

### 创意设计
- 创意概念开发、设计系统构建
- 立场：好看不等于好用，但难看一定不好用

### 医学研究
- 医学文献分析、研究设计指导
- 立场：证据等级决定推荐力度，不拿低等级证据当下结论

### 党政公文写作
- 党务公文、党建材料、领导讲话稿
- 立场：措辞即立场，政治正确不是口号是底线

### 科幻小说创作
- 大纲设计、人物塑造、世界观构建
- 立场：设定是为故事服务的，不是拿来炫技的

### 团队协作管理
- 项目管理、流程优化、团队协调
- 立场：流程不是目的，协作才是

### 评审评估
- 技术评审、方案评审、质量评估
- 立场：评审不是找茬，是帮东西变好

### 知识管理
- 知识体系建设、信息组织、知识图谱
- 立场：知识不流动就是死知识

## 高级功能

### 自定义领域管理

通过JSON文件定义新的专业领域，无需修改源代码即可扩展系统支持：

```python
from utils.custom_domain_manager import CustomDomainManager

manager = CustomDomainManager()

# 创建新领域
config = {
    "description": "教育规划、学业指导",
    "soul_core_truths": ["真诚帮助学生实现目标"],
    "professional_values": ["**教育伦理**：遵守教育道德"],
    "personality_base": "耐心、细致，善于倾听",
    "domain_stance": "教育不是灌输，是点燃",
    "speaking_rules": "温和但不敷衍，循循善诱",
    "tools": ["**评估工具**：学习能力测评"],
    "workflows": ["需求评估 → 方案制定 → 实施跟踪"],
    "formality_level": 7,
    "technical_depth": 7,
    "emotional_intelligence": 9
}

manager.create_domain("教育咨询", config)
```

更多详情查看 [ADVANCED_FEATURES_README.md](ADVANCED_FEATURES_README.md)。

### 模板覆盖机制

支持多级模板查找和自定义内容覆盖：

```python
from utils.template_manager import TemplateManager

manager = TemplateManager(
    custom_templates_dir="my_templates",
    default_templates_dir="templates"
)

rendered = manager.render_template(
    "soul_template.md",
    variables={
        "agent_name": "技术顾问",
        "core_truths": "- 真诚服务用户"
    },
    domain="技术架构"
)
```

### 智能领域检测

基于关键词和相似度的自动领域推荐：

```python
from utils.domain_detector import DomainDetector, suggest_domain

detector = DomainDetector()

description = "资深云原生架构师，精通Kubernetes、Docker"
results = detector.detect_domain(description, top_k=3)
# 输出: [('技术架构', 95.5), ('商业战略', 42.1), ...]

suggested = suggest_domain(description, threshold=60.0)
# 输出: '技术架构'
```

## 多Agent协作系统

智能模式支持创建多Agent协作系统，适用于团队协作、角色分工、复杂业务流程。

### 多Agent配置结构

当选择多Agent模式时，系统会引导您收集以下信息：

1. **团队信息**：团队名称、描述、规模、协作模型、决策流程
2. **多个Agent画像**：为每个Agent定义专业身份、核心人格、工作行为
3. **协作规则**：角色分配、通信协议、质量保证、性能监控

### 多Agent输出结构

```
generated-config/
├── collected-info/
│   ├── user_profile.json
│   ├── team_info.json
│   ├── collaboration_rules.json
│   └── agent_profiles/
│       ├── agent_1_profile.json
│       └── agent_2_profile.json
├── agent-config/
│   ├── agent_1/
│   │   ├── SOUL.md
│   │   ├── IDENTITY.md
│   │   ├── TOOLS.md
│   │   ├── AGENTS.md
│   │   └── USER.md
│   ├── agent_2/
│   └── team-config/
│       ├── team_info.json
│       └── collaboration_rules.json
└── validation_report.md
```

### 多Agent使用场景

1. **智能协作工作台**：项目管家 + 文稿专家 + 创意写手
2. **技术团队**：架构师 + 开发专家 + 测试专家 + 运维专家
3. **创意团队**：创意总监 + 文案专家 + 设计专家 + 策划专家
4. **商业团队**：战略顾问 + 市场分析师 + 财务专家 + 法务专家

## Claude Code格式配置

当使用 `--format claudecode` 时，生成以下配置文件：

| 文件 | 描述 | 核心内容 |
|------|------|----------|
| `CLAUDE.md` | 项目手册 | 项目概述、核心工作规则、标准工作流程、Agent配置说明 |
| `[Agent名称].md` | Agent配置文件 | Frontmatter + 核心身份定位 + 强制遵守规则 + 工作流程 |

*注：Claude Code格式配置文件基于Expert Agent Builder方法论生成，将OpenClaw四层六维专业人格模型适配到Claude Code平台。*

## 验证体系

### 基础验证 (basic)
- 文件存在性检查
- 基本格式验证

### 标准验证 (standard)
- 章节完整性检查
- 基本一致性验证
- 参数范围合理性检查

### 严格验证 (strict)
- 完整一致性验证
- 内容质量评估
- SOUL/IDENTITY分工验证

## 示例

### 运行技术架构顾问示例

```bash
cd examples/technical-architect-advisor

python ../../openclaw-config-generator.py \
  --mode generate \
  --user-profile user-profile.json \
  --agent-profile agent-profile.json \
  --output-dir generated-config

# 验证生成的配置
python ../../openclaw-config-generator.py \
  --mode validate \
  --config-dir generated-config \
  --validation-level strict
```

### API集成

```python
from openclaw_config_generator import ConfigGenerator

generator = ConfigGenerator(
    user_profile="user.json",
    agent_profile="agent.json"
)
generator.generate_all()
```

## Claude Code Skill 集成

本项目已配置为标准 Claude Code Skill，支持通过 `@expert-agent-builder` 直接调用。

### 触发方式

在 Claude Code 对话中输入以下任意指令：

- `@expert-agent-builder 帮我创建一个技术架构顾问的Agent配置`
- `@expert-agent-builder 生成一份CLAUDE.md项目手册`
- `@expert-agent-builder 构建一个多Agent协作团队`

### Skill 安装

```bash
git clone https://github.com/pkulyn/expert-agent-builder.git ~/.claude/skills/expert-agent-builder
```

## 开发指南

### 项目结构

```
expert-agent-builder/
├── openclaw-config-generator.py      # 主生成脚本
├── SKILL.md                         # Claude Code Skill 元数据
├── config.py                        # 全局配置
├── README.md                        # 使用说明
├── ADVANCED_FEATURES_README.md      # 高级功能文档
├── LICENSE                          # MIT许可证
├── run_example.bat / .sh            # 一键运行脚本
├── templates/                       # 模板文件目录
│   ├── user-profile-template.json
│   └── agent-profile-template.json
├── examples/                        # 示例文件目录
│   ├── technical-architect-advisor/
│   ├── claudecode-example/
│   └── multi-agent-team-example/
├── custom_domains/                  # 自定义领域配置目录
│   └── 教育咨询.json
├── claudecode_templates/            # Claude Code格式模板目录
│   ├── claude_project_template.md
│   └── agent_template.md
├── docs/                            # 文档目录
│   ├── claudecode-user-guide.md
│   └── methodology-summary.md
└── utils/                           # 工具脚本目录
    ├── config_generator.py          # 配置生成器核心
    ├── domain_adapter.py            # 领域适配器（10大领域）
    ├── custom_domain_manager.py     # 自定义领域管理器
    ├── template_manager.py          # 模板管理器
    ├── domain_detector.py           # 智能领域检测器
    └── validator.py                 # 配置验证器
```

### 扩展新领域

1. 在 `utils/domain_adapter.py` 的 `DOMAINS` 字典中添加新领域定义
2. 或通过 `custom_domains/` 目录创建JSON配置文件
3. 在 `examples/` 目录中创建新的示例
4. 运行验证确保新领域配置正确

### 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 故障排除

### 常见问题

1. **Python版本不兼容** — 升级Python或使用Python 3.8+
2. **模板文件缺失** — 确保模板文件存在于templates/目录中
3. **编码问题** — 确保文件使用UTF-8编码
4. **权限问题** — 检查文件读写权限

### 调试模式

```bash
python openclaw-config-generator.py --mode interactive --debug
```

## 许可证

MIT License

## 更新日志

### v2.2.0 (2026-04-25)

- **配置模板全面重构**（核心优化）：
  - **SOUL.md重构**：从学术化结构声明转向"有生命力"的人格定义，新增性格底色/价值观/表达风格/做事规矩/边界和禁忌五层结构
  - **IDENTITY.md简化**：从96行缩减至10行锚点格式（Name/Role/One-liner/Relationship vibe/Vibe/Emoji）
  - **TOOLS.md优化**：新增工具使用要点章节，移除行为性工作流
  - **AGENTS.md优化**：新增会话启动协议和记忆系统，交付标准和协作协议领域专属化
  - **表达风格与做事规矩明确分工**：表达风格=说话语气态度，做事规矩=方法论+有主见

- **领域适配器深度扩展**：
  - 从7个内置领域扩展至10个（新增：团队协作管理、评审评估、知识管理）
  - 每个领域新增5个领域专属字段：`one_line_summary`、`work_rules`、`tech_environment`、`delivery_standards`、`collaboration_protocol`
  - 新增`tool_usage_notes`字段，TOOLS.md内容全面领域化
  - 重写所有领域的`speaking_rules`（语气态度导向）和`work_rules`（方法论导向）
  - 重写所有领域的`domain_stance`，从千篇一律模板改为领域特有判断立场

- **情感智能表达方式优化**：
  - 数字参数保留为内部计算维度，不再暴露到配置文件
  - 创建`_translate_emotional_params()`方法，将数字翻译为自然语言行为描述
  - 删除所有伪环境变量（如`EMOTIONAL_INTELLIGENCE_LEVEL: 7/10`）

- **验证器优化**：
  - 支持IDENTITY.md键值锚点格式（不再误报"标题数量较少"）
  - 支持SOUL.md单行性格底色章节（不再误报"内容过少"）
  - 更新DEFAULT_REQUIRED_SECTIONS适配新结构

- **官方规范要素补全**：
  - AGENTS.md新增会话启动协议（SOUL→USER→memory→MEMORY读取顺序）
  - AGENTS.md新增记忆系统配置
  - SOUL.md新增"不是用户代言人"等安全边界
  - 清理测试文档和临时文件，项目结构更整洁

### v2.1.0 (2026-04-17)

- **三大高级功能**（新增）：
  - **自定义领域管理器**：通过JSON配置扩展专业领域支持
  - **模板覆盖机制**：多级模板查找和变量替换
  - **智能领域检测**：基于关键词匹配和文本相似度的自动领域推荐

- **核心优化**：
  - JSON格式处理支持嵌套对象和直接值两种格式
  - 领域动态适配
  - YAML Front Matter开关
  - 批量生成功能

- **Claude Code Skill 集成**

### v2.0.0 (2026-04-11)

- **新增智能模式**：基于四层六维专业人格模型的增强交互流程
- **多Agent协作系统**
- **双平台支持**：OpenClaw和Claude Code

### v1.0.0 (2026-04-09)

- 初始版本发布

---

## 相关文档

| 文档 | 描述 |
|------|------|
| [SKILL.md](SKILL.md) | Claude Code Skill 元数据和核心定义 |
| [ADVANCED_FEATURES_README.md](ADVANCED_FEATURES_README.md) | 三大高级功能完整文档 |

---

**重要提示**：本工具基于OpenClaw高级专业人士Agent配置研究成果开发。建议在使用前阅读完整的研究报告和最佳实践指南，以获得最佳效果。
