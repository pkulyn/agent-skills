# Expert Agent Builder - Claude Code使用指南

## 概述

本指南介绍如何使用Expert Agent Builder为Claude Code平台生成专家级Agent配置文件。Expert Agent Builder基于四层六维专业人格模型，将OpenClaw的高级专业Agent配置方法论适配到Claude Code平台，帮助用户快速创建具备情感智能和专业深度的专家级Agent配置。

## 1. Claude Code平台简介

Claude Code是一个基于Claude AI模型的代码协作平台，支持通过配置文件定义Agent的行为、工作流程和协作规范。主要配置文件包括：

1. **CLAUDE.md** - 项目手册：定义项目级规范、工作规则、协作流程
2. **Agent配置文件** - 专家级Agent配置：定义特定Agent的专业身份、职责、工具和沟通方式

## 2. Expert Agent Builder与Claude Code集成

Expert Agent Builder通过以下方式将OpenClaw四层六维模型适配到Claude Code平台：

### 2.1 内容映射架构

| OpenClaw配置层 | Claude Code配置文件 | 映射逻辑 |
|----------------|---------------------|----------|
| **表层身份层** (IDENTITY.md) | Agent配置文件Frontmatter + 核心身份定位 | 提取专业身份、个性特征、经验水平 |
| **核心人格层** (SOUL.md) | CLAUDE.md项目概述 + Agent配置情感智能支持 | 提取核心真理、专业价值观、情感智能价值观 |
| **工作行为层** (AGENTS.md) | CLAUDE.md核心工作规则 + Agent配置强制遵守规则 | 提取工作流程、协作协议、质量标准 |
| **环境理解层** (TOOLS.md + USER.md) | CLAUDE.md工具与环境 + Agent配置用户理解与沟通 | 提取专业工具设置、用户信息、沟通偏好 |

### 2.2 生成的双配置文件

1. **CLAUDE.md** - 项目手册
   - 项目概述：基于SOUL.md的核心价值观
   - 核心工作规则：基于AGENTS.md的协作协议
   - 标准通用工作流程：基于AGENTS.md的工作流程
   - Agent配置说明：基于IDENTITY.md的专业身份
   - 工具与环境：基于TOOLS.md的专业工具设置
   - 文件命名规范：基于IDENTITY.md的命名标准
   - 常用快捷指令：基于USER.md的用户偏好

2. **Agent配置文件** - 专家级Agent配置
   - Frontmatter：name、description、type、model
   - 核心身份定位：基于SOUL.md和IDENTITY.md
   - 强制遵守规则：基于AGENTS.md的协作协议
   - 标准工作流程：基于AGENTS.md的工作流程
   - 核心工作职责：基于IDENTITY.md的关键能力
   - 专业能力与工具：基于TOOLS.md的专业工具
   - 用户理解与沟通：基于USER.md的用户信息
   - 工作质量标准：基于AGENTS.md的质量标准
   - 情感智能与支持：基于SOUL.md的情感智能价值观
   - 快速响应模板：基于USER.md的沟通偏好

## 3. 快速开始

### 3.1 安装要求

1. Python 3.8或更高版本
2. Expert Agent Builder skill（已安装）

### 3.2 基本使用流程

```bash
# 1. 交互式模式（推荐）
python openclaw-config-generator.py --mode interactive

# 2. 生成模式（使用现有模板）
python openclaw-config-generator.py \
  --mode generate \
  --user-profile examples/claudecode-example/user-profile.json \
  --agent-profile examples/claudecode-example/agent-profile.json \
  --output-dir my-claudecode-config \
  --format claudecode

# 3. 双格式输出（OpenClaw + Claude Code）
python openclaw-config-generator.py \
  --mode generate \
  --user-profile user-profile.json \
  --agent-profile agent-profile.json \
  --output-dir my-both-config \
  --format both \
  --claudecode-dir claudecode-config
```

### 3.3 命令行参数说明

| 参数 | 说明 | 默认值 | 选项 |
|------|------|--------|------|
| `--mode` | 运行模式 | interactive | interactive, generate, validate, example |
| `--format` | 输出格式 | openclaw | openclaw, claudecode, both |
| `--claudecode-dir` | Claude Code输出目录 | claudecode-config | 任意目录名 |
| `--user-profile` | 用户个人信息JSON文件 | - | 文件路径 |
| `--agent-profile` | Agent画像JSON文件 | - | 文件路径 |
| `--output-dir` | 输出目录 | generated-config | 目录路径 |
| `--domain` | 专业领域 | 技术架构 | 任意领域名称 |
| `--optimization-level` | 优化级别 | medium | low, medium, high |

## 4. 配置文件详解

### 4.1 用户个人信息模板 (`user-profile.json`)

```json
{
  "basic_info": {
    "name": { "value": "张明" },
    "professional_title": { "value": "技术总监" },
    "organization": { "value": "云创科技有限公司" },
    "industry": { "value": "互联网科技" }
  },
  "background": {
    "education": { "value": ["清华大学计算机科学硕士"] },
    "work_experience": { "value": ["云创科技有限公司技术总监（2020-至今）"] }
  },
  "communication_preferences": {
    "formality_level": { "value": 7 },
    "technical_detail_level": { "value": 8 }
  }
}
```

### 4.2 Agent画像模板 (`agent-profile.json`)

```json
{
  "professional_identity": {
    "domain_expertise": { "value": "技术架构" },
    "experience_level": { "value": "高级（7-15年经验）" },
    "role_definition": { "value": "资深技术架构顾问，专注于云原生和分布式系统设计" }
  },
  "key_competencies": {
    "value": ["系统架构设计", "技术选型评估", "性能优化"]
  },
  "specialization_parameters": {
    "technical_depth": { "value": 8 },
    "emotional_intelligence_level": { "value": 7 },
    "collaboration_intensity": { "value": 7 }
  }
}
```

### 4.3 生成的Claude Code配置文件

#### 4.3.1 CLAUDE.md结构

```markdown
# CLAUDE.md - [项目名称]项目手册

## 项目概述
[基于SOUL.md的核心价值观和世界观]

## 核心工作规则（所有Agent 100%强制遵守）
### 1. 智能协作
[基于AGENTS.md的协作协议]

### 2. 专业精神
[基于SOUL.md的专业价值观]

### 3. 情感智能
[基于SOUL.md的情感智能价值观]

### 4. 求真务实
[基于SOUL.md的核心真理和原则]

### 5. 真诚开放
[基于SOUL.md的沟通价值观]

## 标准通用工作流程（全项目统一执行）
[基于AGENTS.md的核心工作流程]

## Agent配置说明
[基于IDENTITY.md的专业身份]

## 工具与环境
[基于TOOLS.md的专业工具设置]

## 文件命名规范
[基于IDENTITY.md的命名标准]

## 常用快捷指令
[基于USER.md的用户偏好]
```

#### 4.3.2 Agent配置文件结构

```markdown
---
name: [Agent名称]
description: [Agent描述]
type: general-purpose
model: inherit
---

# [Agent名称] - [Agent标题]

## 核心身份定位
[基于SOUL.md的核心真理和IDENTITY.md的专业身份]

## 强制遵守规则（无条件执行）
[基于AGENTS.md的协作协议和WORKING BEHAVIOR层]

## 遵循标准工作流程（所有任务闭环执行）
[基于AGENTS.md的核心工作流程和PROCESS STANDARDIZATION层]

## 核心工作职责
[基于IDENTITY.md的关键能力矩阵和CORE PERSONALITY层]

## 专业能力与工具
[基于TOOLS.md的专业工具设置和ENVIRONMENT CONTEXT层]

## 用户理解与沟通
[基于USER.md的用户背景、偏好和USER CONTEXT层]

## 工作质量标准
[基于AGENTS.md的质量标准和QUALITY ASSURANCE层]

## 情感智能与支持
[基于SOUL.md的情感智能价值观和EMOTIONAL INTELLIGENCE层]

## 快速响应模板
[基于USER.md的沟通偏好和COMMUNICATION PATTERNS层]
```

## 5. 验证配置质量

### 5.1 验证方法

```bash
# 验证Claude Code配置
python openclaw-config-generator.py \
  --mode validate \
  --config-dir my-claudecode-config \
  --validation-level strict \
  --config-format claudecode
```

### 5.2 验证项目

1. **文件完整性验证**
   - CLAUDE.md文件存在性
   - Agent配置文件存在性
   - 文件格式正确性

2. **内容完整性验证**
   - 必需章节存在性
   - 章节内容充实度
   - 专业术语准确性

3. **一致性验证**
   - 参数值一致性
   - 专业领域一致性
   - 情感智能水平一致性

4. **质量验证**
   - 情感表达自然度
   - 专业深度适当性
   - 实用性和可操作性

## 6. 在Claude Code中使用配置

### 6.1 部署配置

1. **CLAUDE.md部署**
   ```bash
   # 将CLAUDE.md复制到项目根目录
   cp my-claudecode-config/CLAUDE.md /path/to/your/project/
   ```

2. **Agent配置文件部署**
   ```bash
   # 将Agent配置文件复制到.agents/目录
   cp my-claudecode-config/[Agent名称].md /path/to/your/project/.agents/
   ```

### 6.2 配置激活

1. **项目级配置激活**
   - CLAUDE.md在项目根目录自动生效
   - 所有Agent必须遵守项目中定义的规则和流程

2. **Agent配置激活**
   - 在Claude Code中引用Agent配置文件
   - 通过Agent名称调用特定专家

### 6.3 使用示例

```bash
# 在Claude Code中调用专家级Agent
@技术架构顾问 请帮我设计一个微服务架构

# 使用快捷指令
@项目管家 检查项目目录结构
@文稿专家 润色这份技术方案
@创意写手 继续写下一章
```

## 7. 最佳实践

### 7.1 配置优化建议

1. **专业领域选择**
   - 根据实际需求选择专业领域
   - 考虑团队技能和项目复杂度
   - 平衡专业深度和广度

2. **情感智能设置**
   - 技术团队：情感智能7-8/10
   - 创意团队：情感智能8-9/10
   - 管理团队：情感智能6-7/10

3. **技术深度设置**
   - 初级项目：技术深度6-7/10
   - 中级项目：技术深度7-8/10
   - 高级项目：技术深度8-9/10

### 7.2 团队协作配置

1. **多角色配置**
   - 为不同职责的团队成员配置不同的Agent
   - 确保角色间的协作协议一致性
   - 建立清晰的职责边界

2. **统一工作流程**
   - 所有Agent使用相同的工作流程
   - 建立标准化的质量审核机制
   - 实现无缝的任务交接

### 7.3 持续优化

1. **反馈收集**
   - 定期收集用户使用反馈
   - 记录Agent交互的质量和效果
   - 识别配置的不足和改进点

2. **配置迭代**
   - 根据反馈调整用户偏好
   - 优化Agent画像参数
   - 更新专业领域知识

3. **版本管理**
   - 对配置文件进行版本控制
   - 记录配置变更和优化理由
   - 建立配置回滚机制

## 8. 故障排除

### 8.1 常见问题

1. **配置文件生成失败**
   - 检查JSON文件格式
   - 验证必需字段完整性
   - 检查文件编码（UTF-8）

2. **配置验证失败**
   - 检查必需章节是否存在
   - 验证参数值范围
   - 检查一致性规则

3. **Claude Code不识别配置**
   - 检查文件位置是否正确
   - 验证文件命名规范
   - 检查Claude Code版本兼容性

### 8.2 调试方法

1. **详细日志输出**
   ```bash
   python openclaw-config-generator.py --mode generate --debug
   ```

2. **逐步验证**
   ```bash
   # 逐步验证各阶段
   python openclaw-config-generator.py --mode validate --validation-level basic
   python openclaw-config-generator.py --mode validate --validation-level standard
   python openclaw-config-generator.py --mode validate --validation-level strict
   ```

3. **示例对比**
   ```bash
   # 与示例配置对比
   diff my-config/CLAUDE.md examples/claudecode-example/generated-configs/CLAUDE.md
   ```

## 9. 高级功能

### 9.1 批量生成

```bash
# 批量生成多个专业领域的配置
python openclaw-config-generator.py \
  --mode batch \
  --input-dir batch-profiles \
  --output-dir batch-output \
  --format claudecode
```

### 9.2 自定义模板

```bash
# 使用自定义模板
python openclaw-config-generator.py \
  --mode custom \
  --template-dir my-templates \
  --user-profile my-user.json \
  --agent-profile my-agent.json \
  --output-dir custom-config \
  --format claudecode
```

### 9.3 API集成

```python
from openclaw_config_generator import ConfigGenerator

# 创建配置生成器
generator = ConfigGenerator(
    user_profile="user-profile.json",
    agent_profile="agent-profile.json",
    format="claudecode"
)

# 生成配置
config = generator.generate_all()

# 保存配置
generator.save_config("output-directory")
```

## 10. 更新与支持

### 10.1 版本更新

- **v1.0.0** (2026-04-09): 初始版本发布，支持OpenClaw和Claude Code双格式输出
- **后续计划**: 添加更多专业领域模板，增强验证规则，优化内容提取算法

### 10.2 技术支持

- **文档**: 查看项目README.md和docs/目录
- **示例**: 参考examples/claudecode-example/目录
- **问题反馈**: GitHub Issues
- **功能建议**: 社区论坛

### 10.3 社区贡献

1. **贡献新领域模板**
   - 创建新的专业领域模板
   - 提供示例配置文件
   - 编写使用文档

2. **改进验证规则**
   - 添加新的验证规则
   - 优化验证算法
   - 提供验证报告模板

3. **优化用户体验**
   - 改进交互式引导
   - 添加更多示例
   - 提供可视化工具

## 附录

### A. 专业领域支持列表

1. **技术架构**
   - 系统架构设计
   - 技术选型评估
   - 性能优化
   - 云原生架构

2. **法律咨询**
   - 法律研究
   - 合同分析
   - 合规性检查
   - 法律文书模板

3. **商业战略**
   - 市场分析
   - 财务分析
   - 战略规划
   - 竞争分析

4. **创意总监**
   - 创意概念开发
   - 设计系统构建
   - 情感表达优化
   - 创意工具集成

5. **医学研究**
   - 医学文献分析
   - 研究设计指导
   - 临床数据分析
   - 伦理审查支持

### B. 四层六维专业人格模型

| 层级 | 维度 | 描述 |
|------|------|------|
| **表层身份层** | 专业身份 | 行业角色、经验水平、领域专长 |
| | 个性特征 | 沟通风格、情感表达、工作态度 |
| **核心人格层** | 核心真理 | 世界观、价值观、服务理念 |
| | 专业价值观 | 技术伦理、工作哲学、服务原则 |
| **工作行为层** | 工作流程 | 方法论、操作步骤、质量检查 |
| | 协作协议 | 团队协作、信息共享、决策机制 |
| **环境理解层** | 专业工具 | 工作环境、技术工具、分析框架 |
| | 用户理解 | 用户背景、需求偏好、沟通风格 |

### C. 命令行参数参考

完整参数列表：
```bash
python openclaw-config-generator.py --help
```

---

*本指南基于Expert Agent Builder v1.0.0编写，提供了完整的Claude Code配置生成、验证和使用指导。如有问题或建议，请参考项目文档或联系技术支持。*