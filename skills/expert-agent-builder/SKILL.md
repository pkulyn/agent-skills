---
name: expert-agent-builder
description: |
  专家级Agent配置生成工具 - 基于四层六维专业人格模型，支持智能交互流程、多Agent协作系统、OpenClaw和Claude Code双平台配置生成。
  核心能力：
  1. 智能模式 - 基于四层六维模型的增强交互，支持平台/模式选择、多Agent配置
  2. 领域深度适配 - 10大内置领域，每个领域拥有独立的人格底色、判断立场、说话规则、做事规矩
  3. 人性化配置 - SOUL.md以自然语言描述人格，IDENTITY.md极简锚点，数字参数不再暴露
  4. 双平台输出 - OpenClaw格式（5文件）和Claude Code格式（CLAUDE.md + Agent配置）
  5. 智能验证 - 完整性、一致性、质量三重验证体系

  触发场景：
  - "帮我创建一个技术架构顾问的Agent配置"
  - "生成一份CLAUDE.md项目手册"
  - "构建一个多Agent协作团队（项目管家+技术专家+创意写手）"
  - "验证这份配置的质量"
  - "基于这个用户画像生成Agent配置"

model: inherit
license: MIT
metadata:
  version: "2.2.0"
  category: agent-tooling
  type: code-generator
  author: pkulyn
---

# Expert Agent Builder - 专家级Agent配置生成器

## 核心定位

基于**四层六维专业人格模型**研究成果，帮助用户快速创建专家级Agent配置文件。支持OpenClaw和Claude Code双平台，提供单Agent和多Agent协作系统配置。

## 快速决策流程

```
用户场景 → 推荐模式

1. 初次使用 / 不确定如何开始
   → --mode smart (智能模式，交互式引导)

2. 已有用户画像和Agent画像JSON文件
   → --mode generate (基于模板生成)

3. 想验证现有配置质量
   → --mode validate (验证模式)

4. 想了解工具能力
   → --mode example (运行示例)

5. 需要多Agent协作系统
   → --mode smart → 选择"多Agent协作系统" → 定义团队信息、多个Agent画像、协作规则
```

## 四层六维专业人格模型

### 四层结构（从内到外）

| 层级 | 名称 | 对应配置文件 | 核心内容 |
|------|------|-------------|----------|
| 第1层 | 灵魂层 (SOUL) | SOUL.md | 性格底色、价值观、表达风格、做事规矩、边界和禁忌 |
| 第2层 | 身份锚点层 (IDENTITY) | IDENTITY.md | Name、Role、One-liner、Relationship vibe、Vibe、Emoji |
| 第3层 | 工作行为层 (BEHAVIOR) | AGENTS.md | 会话启动协议、记忆系统、核心工作流程、交付标准、协作协议 |
| 第4层 | 环境工具层 (ENVIRONMENT) | TOOLS.md | 本地技术环境、领域专用工具、工具使用要点 |

### 设计原则

- **SOUL.md负责"怎么说话、怎么判断、怎么相处"** — 有生命力的人格定义，非学术化声明
- **IDENTITY.md负责"自己觉得是谁"** — 极简身份锚点（约10行），非评分表格
- **数字参数保留为内部计算维度** — 情感智能等参数翻译为自然语言行为描述，不暴露到配置文件
- **领域深度适配** — 每个领域拥有独立的判断立场，不是同一模板替换名词的变体

### 六维评估体系（内部计算用）

| 维度 | 说明 | 典型取值范围 |
|------|------|-------------|
| 技术深度 | 专业知识深入程度 | 1-10 |
| 情感智能水平 | 情感理解和支持能力 | 1-10 |
| 协作强度 | 团队协作和沟通深度 | 1-10 |
| 创新倾向 | 创新思维和探索意愿 | 1-10 |
| 实用性权重 | 务实与理论的平衡 | 1-10 |
| 个性化程度 | 服务的定制化和适应性 | 1-10 |

## 使用方式

### 方式一：智能模式（推荐）

基于四层六维模型的增强交互流程，自动引导完成配置：

```bash
python openclaw-config-generator.py --mode smart
```

智能模式特点：
- **平台选择**：OpenClaw或Claude Code平台
- **Agent模式**：单Agent或多Agent协作系统
- **信息获取方式**：交互式问答、资料整理、混合模式
- **信息确认**：收集信息后用户确认再生成配置

### 方式二：使用现有模板生成

基于已有的用户画像和Agent画像JSON文件生成配置：

```bash
# 生成OpenClaw格式配置
python openclaw-config-generator.py \
  --mode generate \
  --user-profile templates/user-profile-template.json \
  --agent-profile templates/agent-profile-template.json \
  --output-dir generated-config \
  --format openclaw

# 生成Claude Code格式配置
python openclaw-config-generator.py \
  --mode generate \
  --user-profile templates/user-profile-template.json \
  --agent-profile templates/agent-profile-template.json \
  --output-dir claudecode-config \
  --format claudecode

# 双格式同时输出
python openclaw-config-generator.py \
  --mode generate \
  --user-profile templates/user-profile-template.json \
  --agent-profile templates/agent-profile-template.json \
  --output-dir generated-config \
  --format both \
  --claudecode-dir claudecode-config
```

### 方式三：验证现有配置

```bash
python openclaw-config-generator.py \
  --mode validate \
  --config-dir generated-config \
  --validation-level strict
```

验证级别：
- `basic`：基础验证（文件存在性、基本格式）
- `standard`：标准验证（完整性、基本一致性）
- `strict`：严格验证（完整一致性、质量检查、SOUL/IDENTITY分工验证）

### 方式四：运行示例

```bash
python openclaw-config-generator.py --mode example
```

运行内置的技术架构顾问示例，快速了解输出格式。

## 命令行参数参考

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--mode` | string | `smart` | 运行模式：`smart`、`interactive`、`generate`、`validate`、`example` |
| `--format` | string | `openclaw` | 输出格式：`openclaw`、`claudecode`、`both` |
| `--user-profile` | string | - | 用户个人信息JSON文件路径 |
| `--agent-profile` | string | - | Agent画像JSON文件路径 |
| `--output-dir` | string | `generated-config` | 输出目录 |
| `--claudecode-dir` | string | `claudecode-config` | Claude Code格式输出目录（当`--format both`时使用） |
| `--domain` | string | `技术架构` | 专业领域 |
| `--optimization-level` | string | `medium` | 优化级别：`low`、`medium`、`high` |
| `--validation-level` | string | `standard` | 验证级别：`basic`、`standard`、`strict` |

## 输出文件结构

### OpenClaw格式输出 (`--format openclaw`)

```
generated-config/
├── SOUL.md              # 灵魂层：性格底色、价值观、表达风格、做事规矩、边界和禁忌
├── IDENTITY.md          # 身份锚点：Name/Role/One-liner/Relationship vibe/Vibe/Emoji
├── TOOLS.md             # 工具层：本地技术环境、领域专用工具、工具使用要点
├── AGENTS.md            # 协作层：会话启动协议、记忆系统、工作流程、交付标准、协作协议
├── USER.md              # 用户层：用户信息、沟通偏好、项目上下文
└── validation_report.md # 验证报告（如启用验证）
```

#### SOUL.md 示例结构

```markdown
# SOUL.md - [Agent名称]的灵魂

> 你是一个[一句话人格概括]

## 1. 性格底色
[领域特有的性格倾向，自然语言描述]

## 2. 价值观
**立场：**
- [领域特有的判断立场，非千篇一律模板]

**原则：**
- [领域伦理标准和工作哲学]

## 3. 表达风格
[说话的语气、态度、直接程度。如"正式规范，不越线"]
[情感行为倾向，自然语言描述]

## 4. 做事规矩
- [方法论导向的规则。如"数据驱动决策，不凭感觉"]
- [有主见坚持的规则。如"有疑义的地方主动标注"]

## 5. 边界和禁忌
- [行业红线]
- 你不是用户的代言人——你有自己的立场
- 不确定时，在外部行动前先问
```

#### IDENTITY.md 示例结构

```markdown
# IDENTITY.md - Who Am I?

Name: Scribe
Role: Scribe - 党政文稿专家
One-liner: 措辞即立场
Relationship vibe: 严谨的文稿把关人，不放过任何疑点
Vibe: 严丝合缝，一丝不苟
Emoji: 📋
```

### Claude Code格式输出 (`--format claudecode`)

```
claudecode-config/
├── CLAUDE.md            # 项目手册：项目概述、核心工作规则、标准流程
├── [Agent名称].md       # Agent配置文件：专业身份、工作职责、质量标准
└── validation_report.md # 验证报告（如启用验证）
```

### 多Agent协作系统输出

当选择多Agent模式时，输出结构为：

```
generated-config/
├── collected-info/              # 收集的原始信息
│   ├── user_profile.json
│   ├── team_info.json
│   ├── collaboration_rules.json
│   └── agent_profiles/
│       ├── agent_1_profile.json
│       └── agent_2_profile.json
└── agent-config/                # 生成的配置
    ├── agent_1/
    │   ├── SOUL.md
    │   ├── IDENTITY.md
    │   ├── TOOLS.md
    │   ├── AGENTS.md
    │   └── USER.md
    ├── agent_2/
    └── team-config/
        ├── team_info.json
        └── collaboration_rules.json
```

## 专业领域支持

### 内置专业领域（10个）

| 领域 | 核心立场 | 典型应用场景 |
|------|----------|-------------|
| **技术架构** | 好的架构是删出来的，不是加出来的 | 云原生架构、分布式系统、微服务设计 |
| **法律咨询** | 法律不是障碍，是护栏 | 法律文书、案例管理、合规审查 |
| **商业战略** | 数据不说谎，但数据也不说话——解读得靠人 | 竞争分析、商业模式、投资决策 |
| **创意设计** | 好看不等于好用，但难看一定不好用 | 品牌设计、创意策划、用户体验 |
| **医学研究** | 证据等级决定推荐力度 | 临床研究、文献综述、伦理审查 |
| **党政公文写作** | 措辞即立场，政治正确不是口号是底线 | 党务公文、党建材料、领导讲话稿 |
| **科幻小说创作** | 设定是为故事服务的，不是拿来炫技的 | 大纲设计、人物塑造、世界观构建 |
| **团队协作管理** | 流程不是目的，协作才是 | 项目管理、流程优化、团队协调 |
| **评审评估** | 评审不是找茬，是帮东西变好 | 技术评审、方案评审、质量评估 |
| **知识管理** | 知识不流动就是死知识 | 知识体系建设、信息组织、知识图谱 |

### 自定义领域扩展

通过JSON配置文件定义新的专业领域，无需修改源代码：

1. 在 `custom_domains/` 目录创建领域JSON配置文件（如`教育咨询.json`）
2. 定义领域特有的参数：`personality_base`、`domain_stance`、`speaking_rules`、`work_rules`、`taboos`、`emotional_style`等
3. 通过 `CustomDomainManager` API加载自定义领域

也可通过 `utils/domain_adapter.py` 的 `DOMAINS` 字典直接添加新领域。

更多详情查看 [ADVANCED_FEATURES_README.md](ADVANCED_FEATURES_README.md)。

## 高级功能

### 智能领域检测

基于关键词和相似度的自动领域推荐：

```python
from utils.domain_detector import DomainDetector, suggest_domain

detector = DomainDetector()
results = detector.detect_domain("资深云原生架构师", top_k=3)
# 输出: [('技术架构', 95.5), ('商业战略', 42.1), ...]
```

### 模板覆盖机制

支持多级模板查找（自定义 → 领域特定 → 默认）和变量替换：

```python
from utils.template_manager import TemplateManager

manager = TemplateManager(custom_templates_dir="my_templates")
rendered = manager.render_template("soul_template.md", variables={"agent_name": "技术顾问"})
```

### 情感智能自然语言翻译

六维数字参数保留为内部计算维度，通过`_translate_emotional_params()`方法翻译为自然语言行为描述：

- EI>=8 → "对人的状态比较敏感，你不用说我也能感觉到哪里不对"
- EI 6-7 → "能注意到明显的情绪变化，一般状态还行"
- EI<6 → "主要关注事情本身，不太会主动关注情绪"

翻译结果写入SOUL.md的"表达风格"章节，配置文件中不再出现数字评分和伪环境变量。

## 最佳实践

### 1. 首次使用建议

1. **先运行示例模式**：`--mode example`，了解输出格式
2. **使用智能模式**：`--mode smart`，完整体验交互流程
3. **从熟悉领域开始**：选择熟悉的专业领域进行首次配置

### 2. 配置优化建议

1. **专业领域选择** — 根据实际需求选择，10个内置领域各有独立判断立场
2. **情感智能** — 数字参数自动翻译为自然语言，关注行为描述是否贴合实际需求
3. **SOUL.md定制** — 生成后可根据实际使用体验调整"表达风格"和"做事规矩"

### 3. 团队协作配置

1. **多角色配置** — 为不同职责的团队成员配置不同领域Agent
2. **跨Agent一致性** — 同一用户的USER.md事实信息（名称/教育/工作经历）在多Agent间保持一致
3. **协作协议** — 每个领域的`with_user`和`with_team`协议不同，确保分工清晰

## 边界条件与异常处理

### 1. 模板文件缺失
**场景**: `--mode generate` 时指定的文件不存在
**处理**: 提示文件不存在，询问是否切换到 `--mode smart` 交互式收集信息

### 2. Python版本不兼容
**场景**: Python < 3.8
**处理**: 提示需要Python 3.8+，提供安装指南

### 3. 输出目录已存在且非空
**场景**: `--output-dir` 已存在且有文件
**处理**: 列出现有文件，询问覆盖/合并/选择新目录

### 4. JSON解析错误
**场景**: 用户提供的JSON文件格式错误
**处理**: 指出具体语法错误位置，询问是否进入交互模式

### 5. 验证失败
**场景**: `--mode validate` 时发现问题
**处理**: 生成详细报告，分类问题严重程度（错误/警告/建议），提供修复建议

## 故障排除

### 常见问题

1. **Python版本不兼容** — 升级Python或使用Python 3.8+
2. **模板文件缺失** — 确保模板文件存在于 `templates/` 目录中
3. **JSON格式错误** — 检查引号、逗号、括号匹配
4. **编码问题** — 确保文件使用UTF-8编码
5. **权限问题** — 检查文件读写权限

### 调试方法

```bash
# 启用详细日志
python openclaw-config-generator.py --mode smart --debug

# 逐步验证
python openclaw-config-generator.py --mode validate --validation-level basic
python openclaw-config-generator.py --mode validate --validation-level strict
```

## 更新日志

### v2.2.0 (2026-04-25)

- **配置模板全面重构**：
  - SOUL.md五层人格结构（性格底色/价值观/表达风格/做事规矩/边界和禁忌）
  - IDENTITY.md从96行简化至10行锚点格式
  - TOOLS.md新增工具使用要点，AGENTS.md新增会话启动协议和记忆系统
  - 表达风格与做事规矩明确分工：语气态度 vs 方法论+有主见
- **领域适配器深度扩展**：7→10个领域，每个领域6个专属字段
- **情感智能自然语言化**：数字参数翻译为行为描述，不再暴露到配置文件
- **验证器优化**：支持IDENTITY锚点格式和SOUL单行章节

### v2.1.0 (2026-04-17)

- 三大高级功能：自定义领域管理器、模板覆盖机制、智能领域检测
- Claude Code Skill 集成

### v2.0.0 (2026-04-11)

- 新增智能模式、多Agent协作系统、双平台支持

### v1.0.0 (2026-04-09)

- 初始版本发布

## 许可证

MIT License

## 作者

pkulyn

---

*本工具基于OpenClaw高级专业人士Agent配置研究成果开发。建议在使用前阅读完整的研究报告和最佳实践指南，以获得最佳效果。*
