# Agent Skills

Claude Code Agent Skill 集合，由 pkulyn 开发维护。

## Skills 一览

| Skill | 版本 | 分类 | 类型 | 说明 |
|---|---|---|---|---|
| [bili2obsidian](skills/bili2obsidian/) | 1.1.0 | media-processing | tool-wrapper | 提取Bilibili视频字幕并保存到Obsidian知识库 |
| [expert-agent-builder](skills/expert-agent-builder/) | 2.2.0 | agent-tooling | code-generator | 专家级Agent配置生成工具 - 基于四层六维专业人格模型 |
| [gov-doc-writer](skills/gov-doc-writer/) | 1.0.0 | writing | prompt-skill | 政务文稿起草智能助手 - 五阶段工作流 |
| [llm-wiki](skills/llm-wiki/) | 3.1.0 | knowledge-management | prompt-skill | 知识库Wiki管理员 - 结构化知识管理 |

## 安装

### Claude Code 插件安装（推荐）

```bash
claude plugin add https://github.com/pkulyn/agent-skills
```

### 手动安装

```bash
git clone https://github.com/pkulyn/agent-skills.git
# 然后在 Claude Code 的 settings.json 中配置 skills 路径
```

### 更新

```bash
# 插件模式
claude plugin update agent-skills

# 手动模式
cd agent-skills && git pull
```

## 管理工具

使用 `skill-manager.py` 管理所有skill：

```bash
python skill-manager.py list                           # 列出所有skill
python skill-manager.py status [SKILL_ID]              # 查看详细状态
python skill-manager.py sync                           # 扫描磁盘，更新清单
python skill-manager.py pull                           # 从远程拉取更新
python skill-manager.py diff                           # 查看远程未拉取的commit
python skill-manager.py init <ID> --name --category    # 创建新skill
python skill-manager.py validate [--fix]               # 校验frontmatter + 密钥扫描
python skill-manager.py doctor                         # 一键巡检
python skill-manager.py archive <ID>                   # 归档废弃skill
```

## Skill结构规范

每个skill位于 `skills/<skill-id>/` 目录下，以 `SKILL.md` 为唯一入口：

```
skills/<skill-id>/
├── SKILL.md              # 必须 - 入口文件，YAML frontmatter + 使用说明
├── README.md             # 推荐
├── LICENSE               # 推荐 (MIT)
├── references/           # 可选 - 详细参考文档
├── scripts/              # 可选 - 辅助脚本 (含 requirements.txt)
├── templates/            # 可选 - 模板文件
└── memory/               # 可选 - 用户偏好记忆
```

### SKILL.md Frontmatter 规范

```yaml
---
name: {kebab-case-id}                # 必须，kebab-case，必须匹配目录名
description: |                        # 必须，功能+触发条件
  One-paragraph description...
license: MIT                          # 推荐
metadata:                             # 推荐
  version: "1.0.0"                    # 必须，semver三段式
  category: {category}                # 必须
  type: tool-wrapper|code-generator|prompt-skill  # 推荐
  author: pkulyn                      # 推荐
  tags: [tag1, tag2]                  # 推荐
model: inherit                        # 推荐
---
```

### 分类体系

| Category | 说明 |
|---|---|
| `media-processing` | 媒体处理 |
| `agent-tooling` | Agent配置/工具 |
| `writing` | 写作/文稿 |
| `knowledge-management` | 知识管理 |
| `data-processing` | 数据处理 |
| `document-generation` | 文档生成 |
| `productivity` | 生产力工具 |
| `dev-tools` | 开发工具 |

## 前置条件

- Python 3.12+
- Git 2.x
- PyYAML 6.0+ (用于frontmatter解析)

## License

MIT
