---
name: expert-agent-builder
description: >
  专家级Agent配置生成工具。基于四层六维专业人格模型，生成OpenClaw或Claude Code双平台配置。
  支持单Agent和多Agent协作系统。10大内置领域，每个领域拥有独立判断立场和做事规矩。
  触发场景：创建Agent配置、生成CLAUDE.md、构建多Agent团队、验证配置质量。
  不触发：单纯的文本写作、代码开发、问答咨询（除非明确要求"生成Agent配置"）。
triggers:
  - Agent配置
  - 创建Agent
  - 生成CLAUDE.md
  - 多Agent团队
  - 验证配置
  - 四层六维
  - Expert Agent Builder
  - OpenClaw配置
  - Agent人格
model: inherit
license: MIT
metadata:
  version: "2.3.0"
  category: agent-tooling
  type: code-generator
  author: pkulyn
---

# Expert Agent Builder - 专家级Agent配置生成器

基于**四层六维专业人格模型**，帮助用户快速创建专家级Agent配置文件。支持OpenClaw和Claude Code双平台，提供单Agent和多Agent协作系统配置。

## 快速路由

```
用户场景 → 推荐模式

1. 初次使用 / 不确定如何开始
   → --mode smart (智能模式，交互式引导)

2. 已有用户画像和Agent画像JSON文件
   → --mode generate (基于模板生成)
   → 详见 [cli-reference.md](references/cli-reference.md)

3. 想验证现有配置质量
   → --mode validate (验证模式)

4. 想了解工具能力
   → --mode example (运行示例)

5. 需要多Agent协作系统
   → --mode smart → 选择"多Agent协作系统"
```

## 四层六维专业人格模型

### 四层结构（从内到外）

| 层级 | 名称 | 配置文件 | 核心内容 |
|------|------|----------|----------|
| 第1层 | 灵魂层 (SOUL) | SOUL.md | 性格底色、价值观、表达风格、做事规矩、边界和禁忌 |
| 第2层 | 身份锚点层 (IDENTITY) | IDENTITY.md | Name、Role、One-liner、Relationship vibe、Vibe、Emoji |
| 第3层 | 工作行为层 (BEHAVIOR) | AGENTS.md | 会话启动协议、记忆系统、核心工作流程、交付标准、协作协议 |
| 第4层 | 环境工具层 (ENVIRONMENT) | TOOLS.md | 本地技术环境、领域专用工具、工具使用要点 |

### 设计原则

- **SOUL.md负责"怎么说话、怎么判断、怎么相处"** — 有生命力的人格定义
- **IDENTITY.md负责"自己觉得是谁"** — 极简身份锚点（约10行）
- **数字参数保留为内部计算维度** — 情感智能等参数翻译为自然语言行为描述，不暴露到配置文件
- **领域深度适配** — 每个领域拥有独立的判断立场，不是同一模板替换名词

### 六维评估体系（内部计算用）

技术深度 / 情感智能水平 / 协作强度 / 创新倾向 / 实用性权重 / 个性化程度（各1-10分）

## 使用方式

### 推荐方式：智能模式

```bash
python openclaw-config-generator.py --mode smart
```

交互式引导，支持：平台选择（OpenClaw/Claude Code）、Agent模式（单Agent/多Agent）、信息获取方式（交互问答/资料整理/混合）。

### 其他模式

| 模式 | 命令 | 适用场景 |
|------|------|---------|
| 模板生成 | `--mode generate` | 已有JSON画像文件 |
| 验证 | `--mode validate` | 检查现有配置质量 |
| 示例 | `--mode example` | 了解输出格式 |

→ 完整命令行参数和示例见 [cli-reference.md](references/cli-reference.md)

## 输出结构概览

| 格式 | 输出文件 | 说明 |
|------|---------|------|
| OpenClaw | SOUL.md + IDENTITY.md + TOOLS.md + AGENTS.md + USER.md | 5文件配置体系 |
| Claude Code | CLAUDE.md + [Agent名].md | 项目手册+Agent配置 |
| 多Agent | 每个Agent独立目录 + team-config/ | 协作系统配置 |

→ 完整输出结构和模板示例见 [output-structure.md](references/output-structure.md)

## 内置领域（10个）

| 领域 | 核心立场 |
|------|----------|
| 技术架构 | 好的架构是删出来的，不是加出来的 |
| 法律咨询 | 法律不是障碍，是护栏 |
| 商业战略 | 数据不说谎，但数据也不说话 |
| 创意设计 | 好看不等于好用，但难看一定不好用 |
| 医学研究 | 证据等级决定推荐力度 |
| 党政公文写作 | 措辞即立场，政治正确不是口号是底线 |
| 科幻小说创作 | 设定是为故事服务的，不是拿来炫技的 |
| 团队协作管理 | 流程不是目的，协作才是 |
| 评审评估 | 评审不是找茬，是帮东西变好 |
| 知识管理 | 知识不流动就是死知识 |

→ 自定义领域扩展、API示例、故障排除见 [domains-and-advanced.md](references/domains-and-advanced.md)

## 最佳实践

1. **首次使用**：先 `--mode example` 了解格式 → 再 `--mode smart` 交互生成
2. **领域选择**：10个内置领域各有独立判断立场，按实际需求选择
3. **SOUL.md定制**：生成后可根据实际使用体验调整"表达风格"和"做事规矩"
4. **团队配置**：为不同职责成员配置不同领域Agent，确保USER.md事实信息跨Agent一致

## 边界条件

| 场景 | 处理 |
|------|------|
| 模板文件缺失 | 提示并建议切换到 `--mode smart` |
| Python < 3.8 | 提示需要3.8+，提供安装指南 |
| 输出目录非空 | 列出现有文件，询问覆盖/合并/新目录 |
| JSON解析错误 | 指出具体位置，建议交互模式 |
| 验证失败 | 生成分类报告（错误/警告/建议），提供修复建议 |
