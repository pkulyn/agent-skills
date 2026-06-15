# 命令行参数参考

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
| `--debug` | flag | - | 启用详细日志 |

## 使用示例

### 智能模式（推荐）

```bash
python openclaw-config-generator.py --mode smart
```

交互式引导完成配置，支持平台选择、Agent模式选择、信息获取方式选择。

### 基于模板生成

```bash
# OpenClaw格式
python openclaw-config-generator.py \
  --mode generate \
  --user-profile templates/user-profile-template.json \
  --agent-profile templates/agent-profile-template.json \
  --output-dir generated-config \
  --format openclaw

# Claude Code格式
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

### 验证现有配置

```bash
python openclaw-config-generator.py \
  --mode validate \
  --config-dir generated-config \
  --validation-level strict
```

验证级别：`basic`（文件存在性）→ `standard`（完整性+一致性）→ `strict`（完整一致性+质量检查+SOUL/IDENTITY分工验证）

### 运行示例

```bash
python openclaw-config-generator.py --mode example
```
