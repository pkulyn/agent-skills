# Claude Code格式示例：技术架构顾问

本示例展示如何使用Expert Agent Builder生成Claude Code格式的专家级Agent配置文件。

## 示例概述

本示例基于一个典型的技术架构顾问场景：
- **用户**：张明，技术总监，拥有12年大型互联网公司架构设计经验
- **Agent**：资深技术架构顾问，专注于云原生和分布式系统设计
- **专业领域**：技术架构
- **情感智能水平**：7/10
- **技术深度**：8/10
- **协作强度**：7/10

## 文件结构

```
claudecode-example/
├── README.md                        # 本说明文件
├── user-profile.json                # 用户个人信息模板
├── agent-profile.json               # Agent画像模板
└── generated-configs/               # 生成的Claude Code配置文件
    ├── CLAUDE.md                    # 项目手册
    └── 资深技术架构顾问，专注于云原生和分布式系统设计，兼顾技术领导力和团队发展.md  # Agent配置文件
```

## 配置文件说明

### 1. 用户个人信息 (`user-profile.json`)
包含用户的基本信息、专业背景、沟通偏好等：
- 姓名：张明
- 职业头衔：技术总监
- 组织：云创科技有限公司
- 教育背景：清华大学计算机科学硕士、北京大学软件工程学士
- 工作经历：12年大型互联网公司经验
- 沟通偏好：比较正式（7/10），技术细节程度较高（8/10）

### 2. Agent画像 (`agent-profile.json`)
定义Agent的专业身份、核心能力、情感智能参数等：
- 角色定义：资深技术架构顾问，专注于云原生和分布式系统设计
- 经验水平：高级（7-15年经验）
- 领域专长：技术架构
- 核心能力：系统架构设计、技术选型评估、性能优化等
- 情感智能参数：情感智能7/10，技术深度8/10，协作强度7/10

### 3. 生成的Claude Code配置文件

#### `CLAUDE.md` - 项目手册
基于OpenClaw的SOUL.md、IDENTITY.md、TOOLS.md、AGENTS.md、USER.md内容整合生成，包含：
- **项目概述**：基于SOUL.md的核心价值观和世界观
- **核心工作规则**：基于AGENTS.md的协作协议和WORKING BEHAVIOR层
- **标准通用工作流程**：基于AGENTS.md的核心工作流程
- **Agent配置说明**：基于IDENTITY.md的专业身份
- **工具与环境**：基于TOOLS.md的专业工具设置
- **文件命名规范**：基于IDENTITY.md的命名标准
- **常用快捷指令**：基于USER.md的用户偏好

#### `[Agent名称].md` - Agent配置文件
基于OpenClaw的5个配置文件内容整合生成，包含：
- **Frontmatter**：name、description、type、model
- **核心身份定位**：基于SOUL.md的核心真理和IDENTITY.md的专业身份
- **强制遵守规则**：基于AGENTS.md的协作协议和WORKING BEHAVIOR层
- **遵循标准工作流程**：基于AGENTS.md的核心工作流程
- **核心工作职责**：基于IDENTITY.md的关键能力矩阵
- **专业能力与工具**：基于TOOLS.md的专业工具设置
- **用户理解与沟通**：基于USER.md的用户背景和沟通偏好
- **工作质量标准**：基于AGENTS.md的质量标准
- **情感智能与支持**：基于SOUL.md的情感智能价值观
- **快速响应模板**：基于USER.md的沟通偏好

## 如何使用本示例

### 1. 查看生成的配置文件

```bash
# 查看项目手册
cat examples/claudecode-example/generated-configs/CLAUDE.md

# 查看Agent配置文件
cat examples/claudecode-example/generated-configs/资深技术架构顾问，专注于云原生和分布式系统设计，兼顾技术领导力和团队发展.md
```

### 2. 重新生成配置文件

```bash
# 从项目根目录运行
cd D:\cc_projects\openclaw-research\skill

# 生成Claude Code格式配置
python openclaw-config-generator.py \
  --mode generate \
  --user-profile examples/claudecode-example/user-profile.json \
  --agent-profile examples/claudecode-example/agent-profile.json \
  --output-dir my-claudecode-config \
  --format claudecode

# 双格式输出（OpenClaw + Claude Code）
python openclaw-config-generator.py \
  --mode generate \
  --user-profile examples/claudecode-example/user-profile.json \
  --agent-profile examples/claudecode-example/agent-profile.json \
  --output-dir my-both-config \
  --format both \
  --claudecode-dir claudecode-config
```

### 3. 验证生成的配置

```bash
# 验证Claude Code配置
python openclaw-config-generator.py \
  --mode validate \
  --config-dir examples/claudecode-example/generated-configs \
  --validation-level standard
```

## 自定义配置

### 1. 修改用户个人信息

编辑 `user-profile.json` 文件，更新以下字段：
- `basic_info`：姓名、职业头衔、组织等
- `background`：教育背景、工作经历
- `communication_preferences`：沟通偏好、技术细节程度
- `project_context`：项目上下文、技术栈

### 2. 修改Agent画像

编辑 `agent-profile.json` 文件，更新以下字段：
- `professional_identity`：角色定义、经验水平、领域专长
- `core_personality`：个性特征、核心价值观
- `key_competencies`：核心能力列表
- `specialization_parameters`：技术深度、情感智能、协作强度
- `working_behavior`：工作风格、决策模式

### 3. 生成自定义配置

```bash
# 使用自定义配置文件生成Claude Code配置
python openclaw-config-generator.py \
  --mode generate \
  --user-profile my-user-profile.json \
  --agent-profile my-agent-profile.json \
  --output-dir my-custom-config \
  --format claudecode \
  --domain "法律咨询" \
  --optimization-level high
```

## 在Claude Code中使用生成的配置

### 1. 项目级配置
将 `CLAUDE.md` 文件放置在项目根目录，作为项目手册，定义所有Agent必须遵守的工作规则和流程。

### 2. Agent配置
将Agent配置文件（如 `资深技术架构顾问，专注于云原生和分布式系统设计，兼顾技术领导力和团队发展.md`）放置在 `.agents/` 目录中，或直接在Claude Code中引用。

### 3. 使用建议
1. **项目初始化**：在开始新项目时，使用生成的 `CLAUDE.md` 作为项目规范基础
2. **团队协作**：为不同角色的团队成员生成相应的Agent配置文件
3. **专业领域适配**：根据项目需求调整专业领域和优化级别
4. **持续优化**：根据实际使用反馈，调整用户偏好和Agent画像参数

## 基于Expert Agent Builder的方法论

本示例基于Expert Agent Builder方法论，将OpenClaw四层六维专业人格模型适配到Claude Code平台：

| 四层六维模型 | OpenClaw配置层 | Claude Code映射位置 |
|-------------|----------------|-------------------|
| **表层身份层** | IDENTITY.md | Agent配置文件Frontmatter + 核心身份定位 |
| **核心人格层** | SOUL.md | CLAUDE.md项目概述 + Agent配置情感智能支持 |
| **工作行为层** | AGENTS.md | CLAUDE.md核心工作规则 + Agent配置强制遵守规则 |
| **环境理解层** | TOOLS.md + USER.md | CLAUDE.md工具与环境 + Agent配置用户理解与沟通 |

## 技术支持与反馈

- **文档**：查看项目根目录的README.md获取完整使用说明
- **问题反馈**：在GitHub Issues中报告问题
- **功能建议**：通过社区论坛提出功能建议

## 更新日志

- **2026-04-09**：初始版本发布，包含技术架构顾问示例
- **后续计划**：添加更多专业领域示例（法律咨询、商业战略、创意总监等）

---

*本示例基于Expert Agent Builder v1.0.0生成，展示了如何将四层六维专业人格模型应用于Claude Code平台，创建具备情感智能和专业深度的专家级Agent配置。*