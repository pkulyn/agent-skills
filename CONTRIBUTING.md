# 贡献指南

感谢你对 Agent Skills 的贡献！请遵循以下规范。

## 新建 Skill 流程

1. 使用管理工具创建脚手架：
   ```bash
   python skill-manager.py init <skill-id> --name "Display Name" --category <category>
   ```

2. 编辑 `SKILL.md`，填写完整内容和frontmatter

3. 运行校验：
   ```bash
   python skill-manager.py validate
   ```

4. 初始化git并提交：
   ```bash
   cd <skill-id>
   git add .
   git commit -m "feat: initial skill scaffold"
   ```

5. 创建GitHub仓库并推送

6. 更新本文件 README.md 中的 Skill 表格

## 命名规范

- **目录名**：kebab-case（全小写，连字符分隔），如 `gov-doc-writer`
- **SKILL.md name**：与目录名一致
- **文件名**：kebab-case，`.md` 后缀

## Frontmatter 规范

每个 SKILL.md 必须包含以下字段：

| 字段 | 必须 | 说明 |
|---|---|---|
| `name` | 是 | kebab-case，匹配目录名 |
| `description` | 是 | 功能描述 + 触发条件 |
| `license` | 推荐 | 默认 MIT |
| `metadata.version` | 是 | semver 三段式 |
| `metadata.category` | 是 | 见 README 分类表 |
| `metadata.type` | 推荐 | tool-wrapper / code-generator / prompt-skill |
| `metadata.author` | 推荐 | 作者 |
| `metadata.tags` | 推荐 | 标签列表 |
| `model` | 推荐 | 默认 inherit |

## 提交规范

使用 Conventional Commits：

- `feat:` 新功能/skill
- `fix:` 修复bug
- `docs:` 文档更新
- `refactor:` 重构
- `chore:` 杂项

示例：`feat: add gov-doc-writer skill`

## 质量检查

提交前必须运行：

```bash
python skill-manager.py validate
```

确保：
- 0 errors
- SKILL.md frontmatter 完整
- 无硬编码密钥/凭证
