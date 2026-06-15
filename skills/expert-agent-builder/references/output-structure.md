# 输出文件结构

## OpenClaw格式 (`--format openclaw`)

```
generated-config/
├── SOUL.md              # 灵魂层：性格底色、价值观、表达风格、做事规矩、边界和禁忌
├── IDENTITY.md          # 身份锚点：Name/Role/One-liner/Relationship vibe/Vibe/Emoji
├── TOOLS.md             # 工具层：本地技术环境、领域专用工具、工具使用要点
├── AGENTS.md            # 协作层：会话启动协议、记忆系统、工作流程、交付标准、协作协议
├── USER.md              # 用户层：用户信息、沟通偏好、项目上下文
└── validation_report.md # 验证报告（如启用验证）
```

### SOUL.md 结构

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

### IDENTITY.md 结构

```markdown
# IDENTITY.md - Who Am I?

Name: Scribe
Role: Scribe - 党政文稿专家
One-liner: 措辞即立场
Relationship vibe: 严谨的文稿把关人，不放过任何疑点
Vibe: 严丝合缝，一丝不苟
Emoji: 📋
```

## Claude Code格式 (`--format claudecode`)

```
claudecode-config/
├── CLAUDE.md            # 项目手册：项目概述、核心工作规则、标准流程
├── [Agent名称].md       # Agent配置文件：专业身份、工作职责、质量标准
└── validation_report.md # 验证报告（如启用验证）
```

## 多Agent协作系统输出

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
