# LLM-Wiki

> AI Agent 驱动的 Obsidian 知识库 Wiki 管理系统

[![版本](https://img.shields.io/badge/version-3.1-blue.svg)](https://github.com/pkulyn/LLM-Wiki)
[![许可证](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![语言](https://img.shields.io/badge/lang-中文-important.svg)]()

## 这是什么？

LLM-Wiki 是一个为 AI Agent（如 Claude Code、OpenClaw）设计的**知识库 Wiki 管理技能定义**。它将 Andrej Karpathy 提出的 LLM Wiki 设计模式落地为可执行的 Agent 工作流程，实现从原始材料到结构化知识库的自动化构建。

核心思想：**一次录入，永久更新** — 知识只需整合到 Wiki 一次，然后由 Agent 持续维护和更新。

## 核心特性

- **四大工作流程**：INGEST（单文件摄入）、BATCH（批量处理）、QUERY（知识查询）、LINT（健康检查）
- **幂等性保证**：通过 MD5 哈希比对和 registry.json 注册表，重复处理不会创建重复页面
- **增量更新**：仅处理新增或修改的文件，跳过未变化的内容
- **回滚机制**：快照 + manifest.json 支持一键撤销批量操作
- **实体别名检测**：自动识别「悟鸣AI」=「悟鸣」、「MCP协议」=「MCP」等别名，合并到同一实体
- **客观质量检查**：9项客观检查清单替代主观评分，确保产出一致性
- **结构化知识图谱**：摘要 → 实体 → 主题三层架构，双向链接交叉引用

## 知识库架构

```
pkulyn_vault/
├── claude.md                # 约束架构层（Agent行为准则）
├── Wiki/                    # Wiki层 — Agent 完全控制
│   ├── index.md             # 全局导航索引
│   ├── log.md               # 操作日志
│   ├── .state/              # 状态管理
│   │   ├── registry.json    # 文件处理注册表（幂等性核心）
│   │   └── errors/          # 批量任务错误记录
│   ├── .snapshots/          # 回滚快照
│   ├── entities/            # 实体页面（人物、组织、工具、概念等）
│   ├── topics/              # 主题页面（领域聚合）
│   └── summaries/           # 原始材料摘要
├── Clippings/               # 只读 — 网页剪藏
├── Bilibili/                # 只读 — 视频字幕
└── [其他原始材料]            # 只读 — Agent 不可修改
```

## 工作流程概览

### INGEST — 单文件摄入

```
原始材料 → 内容有效性检查 → 创建摘要 → 提取实体 → 更新主题 → 更新索引 → 记录日志
```

### BATCH — 批量处理

```
扫描源文件 → 哈希比对（新增/需更新/跳过）→ 创建快照 → 分批执行INGEST
→ 冲突处理 → 错误隔离 → 质量检查 → 生成报告 → 回滚选项
```

### QUERY — 知识查询

```
搜索Wiki → 阅读相关页面 → 综合答案+引用 → 存储高质量答案
```

### LINT — 健康检查

```
检查矛盾/过时信息/孤立页面/无效链接/重复实体 → 批量修复
```

## 实体类型体系

| 类型 | 适用范围 | 示例 |
|------|----------|------|
| 人物 | UP主、开发者、研究者 | 悟鸣、Andrej Karpathy |
| 组织 | 公司、团队、社区 | 润泽科技、Anthropic |
| 工具 | 软件、平台、插件、Skill | OpenClaw、Claude Code |
| 概念 | 理论、方法、框架 | 12-Factor AgentOps |
| 地点 | 地理位置 | - |
| 事件 | 会议、发布、里程碑 | - |
| 武器装备 | 军事装备 | F-22战斗机 |

## 快速开始

### 前置条件

- Obsidian 知识库（或任意 Markdown 文件集）
- AI Agent 环境（Claude Code、OpenClaw 等）
- [可选] `wiki-curator-watcher.js` 文件监控服务

### 安装

1. 将 `SKILL.md` 复制到你的 Agent 配置目录或技能库中
2. 在知识库根目录创建 `Wiki/` 目录结构（Agent 会自动维护）
3. 配置 Agent 使用此技能

```bash
# 目录结构示例
mkdir -p Wiki/{entities,topics,summaries,reports,.state,.snapshots}
```

### 使用

在你的 AI Agent 中触发 LLM-Wiki 技能：

**单文件摄入**：
```
请摄入这个文件：Clippings/某篇文章.md
```

**批量处理**：
```
批量处理 Bilibili/ 文件夹下所有文件
```

**知识查询**：
```
Wiki中关于Agent工程化的内容有哪些？
```

**健康检查**：
```
对Wiki执行LINT检查
```

### 批量处理配置选项

| 参数 | 可选值 | 默认值 | 说明 |
|------|--------|--------|------|
| source | 路径/文件列表 | 必填 | 源文件位置 |
| auto_create_entities | true/false/"ask" | "ask" | 自动创建实体 |
| conflict_strategy | merge/overwrite/skip/ask | merge | 冲突处理策略 |
| incremental | true/false | true | 仅处理新增/修改文件 |
| batch_size | 5-50 | 10 | 每批处理数量 |

## 幂等性设计

通过 `registry.json` 注册表实现：

```
文件在registry中？
├── 否 → 标记:新增 → 完整执行INGEST
└── 是 → 哈希相同？
    ├── 是 → 跳过（已处理）
    └── 否 → 标记:需更新 → 创建快照 → 增量更新
```

**增量更新同步**：源文件变化时，同步更新摘要 → 实体 → 主题 → 交叉引用，确保数据一致性。

## 质量检查清单

每个生成的页面通过9项客观检查：

| # | 检查项 | 标准 |
|---|--------|------|
| 1 | frontmatter完整性 | 含title/date/source_hash/tags |
| 2 | frontmatter格式 | type中文值、日期无引号、tags数组格式 |
| 3 | 关联实体数量 | 摘要3-8个 |
| 4 | 关联主题数量 | 摘要3-5个 |
| 5 | 双链有效性 | 所有[[链接]]指向存在的页面 |
| 6 | 命名规范 | 文件名符合YYYY-MM-DD_{名称}.md |
| 7 | 章节完整性 | 包含模板要求的所有章节 |
| 8 | 实体去重 | 无同名或别名重复实体 |
| 9 | 结构一致性 | 章节无重复，顺序正确，标题统一中文 |

评级：A(9/9) / B(7-8) / C(5-6) / D(<5)

## 版本历史

### v3.1 (2026-04-23)

基于两轮实测（batch-20260423-170000 + 幂等性验证）的10项优化：

| 编号 | 优先级 | 变更项 |
|------|--------|--------|
| P0-1 | P0 | 新增实体别名检测规则 |
| P0-2 | P0 | 7种实体类型规范（含"工具"，强制中文） |
| P0-3 | P0 | 实体页面merge整理规则 |
| P1-4 | P1 | 快照创建强制校验 |
| P1-5 | P1 | 增量更新测试方法 |
| P1-6 | P1 | 客观质量检查清单替代主观评分 |
| P1-7 | P1 | index.md精确统计规则 |
| P2-8 | P2 | frontmatter格式一致性校验 |
| P2-9 | P2 | 章节标题统一中文 |
| P2-10 | P2 | 主题语义校验即时化 |

### v3.0 (2026-04-22)

- 完整的幂等性、增量更新、回滚、冲突处理机制
- BATCH批量处理模式（分批执行、错误隔离、断点续传）
- 内容有效性判定标准
- 文件路径双重校验规范

### v1.0 - v2.0 (2026-04-10 ~ 2026-04-13)

- 初始架构设计
- 基础INGEST/QUERY/LINT工作流程
- 单文件处理模式

## 设计理念

本项目受 [Andrej Karpathy 的 LLM Wiki 构建指南](https://karpathy.bearblog.dev/how-i-use-ai-to-build-wiki/) 启发，核心设计原则：

1. **Agent 不可修改原始材料** — 所有操作在 Wiki 层进行
2. **知识只需录入一次** — 后续通过增量更新维护
3. **结构优于搜索** — 三层架构（摘要/实体/主题）+ 双向链接比全文搜索更可靠
4. **可验证优于可信** — 幂等性、质量检查、回滚机制确保数据可靠性
5. **批量友好** — 支持大规模文件批量处理，单文件失败不影响整体

## 致谢

- [Andrej Karpathy](https://karpathy.bearblog.dev/) — LLM Wiki 设计模式
- [Obsidian](https://obsidian.md/) — 知识库工具
- [OpenClaw](https://github.com/open-webui/open-webui) — 开源 AI Agent 平台
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — AI 编程助手

## 许可证

[MIT License](LICENSE)
