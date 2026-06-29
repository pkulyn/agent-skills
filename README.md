# Agent Skills

A collection of Claude Code Agent Skills, developed and maintained by pkulyn.

[English](README.md) ｜ [中文](README.zh-CN.md)

## Skills

| Skill | Version | Category | Type | Description |
|---|---|---|---|---|
| [bili2obsidian](skills/bili2obsidian/) | 1.1.0 | media-processing | tool-wrapper | Extract Bilibili video subtitles and save to Obsidian vault |
| [expert-agent-builder](skills/expert-agent-builder/) | 2.2.0 | agent-tooling | code-generator | Expert Agent config generator based on the four-layer six-dimension persona model |
| [gov-doc-writer](skills/gov-doc-writer/) | 1.0.0 | writing | prompt-skill | Government document drafting assistant with a five-stage workflow |
| [llm-wiki](skills/llm-wiki/) | 3.1.0 | knowledge-management | prompt-skill | Knowledge base Wiki manager for structured knowledge management |
| [my-design](skills/my-design/) | 1.0.0 | design | code-generator | Type, enter, ship a design — PPT slides, interactive prototypes, animation demos, web/infographic |

## Installation

### Claude Code plugin install (recommended)

```bash
claude plugin add https://github.com/pkulyn/agent-skills
```

### Manual install

```bash
git clone https://github.com/pkulyn/agent-skills.git
# Then configure the skills path in Claude Code's settings.json
```

### Update

```bash
# Plugin mode
claude plugin update agent-skills

# Manual mode
cd agent-skills && git pull
```

## Management tool

Use `skill-manager.py` to manage all skills:

```bash
python skill-manager.py list                           # List all skills
python skill-manager.py status [SKILL_ID]              # Show detailed status
python skill-manager.py sync                           # Scan disk, update manifest
python skill-manager.py pull                           # Pull updates from remote
python skill-manager.py diff                           # Show un-pulled remote commits
python skill-manager.py init <ID> --name --category    # Create a new skill
python skill-manager.py validate [--fix]               # Validate frontmatter + secret scan
python skill-manager.py doctor                         # One-click health check
python skill-manager.py archive <ID>                   # Archive a deprecated skill
```

## Skill structure

Each skill lives in `skills/<skill-id>/` with `SKILL.md` as the single entry point:

```
skills/<skill-id>/
├── SKILL.md              # required - entry file, YAML frontmatter + usage docs
├── README.md             # recommended
├── LICENSE               # recommended (MIT)
├── references/           # optional - detailed reference docs
├── scripts/              # optional - helper scripts (with requirements.txt)
├── templates/            # optional - template files
└── memory/               # optional - user preference memory
```

### SKILL.md frontmatter spec

```yaml
---
name: {kebab-case-id}                # required, kebab-case, must match directory name
description: |                        # required, function + trigger conditions
  One-paragraph description...
license: MIT                          # recommended
metadata:                             # recommended
  version: "1.0.0"                    # required, semver three-part
  category: {category}                # required
  type: tool-wrapper|code-generator|prompt-skill  # recommended
  author: pkulyn                      # recommended
  tags: [tag1, tag2]                  # recommended
model: inherit                        # recommended
---
```

### Categories

| Category | Description |
|---|---|
| `media-processing` | Media processing |
| `agent-tooling` | Agent config / tools |
| `writing` | Writing / documents |
| `knowledge-management` | Knowledge management |
| `design` | Design / UI / prototypes |
| `data-processing` | Data processing |
| `document-generation` | Document generation |
| `productivity` | Productivity tools |
| `dev-tools` | Dev tools |

## Prerequisites

- Python 3.12+
- Git 2.x
- PyYAML 6.0+ (for frontmatter parsing)

## License

MIT
