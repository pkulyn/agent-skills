---
name: bili2obsidian
description: 提取Bilibili视频字幕并保存到Obsidian知识库
license: MIT
metadata:
  version: "1.1.0"
  category: media-processing
  type: tool-wrapper
  author: pkulyn
---

# Bilibili字幕提取Skill

## 功能

从Bilibili视频提取字幕，保存为Markdown到Obsidian知识库。英文字幕由智能体自动翻译。

## 命令

- `/bili extract <url>` - 提取指定视频的字幕
- `/bili batch <fav_url>` - 批量提取收藏夹字幕
- `/bili course <course_url>` - 批量提取付费课程字幕

## 工作流程

### 步骤1：提取字幕

运行bili2obsidian提取字幕，生成Markdown文档：

```bash
cd d:/cc_projects/bili2obsidian && python bili2obsidian.py extract "<URL>"
cd d:/cc_projects/bili2obsidian && python bili2obsidian.py batch "<收藏夹URL>"
cd d:/cc_projects/bili2obsidian && python bili2obsidian.py course "<课程URL>"
```

### 步骤2：翻译英文字幕（智能体后处理）

字幕提取完成后，检查输出中是否标记了 `⚠️ 英文字幕，需要翻译`。如果有：

1. 读取该Markdown文件
2. 找到 `## 字幕` 部分的内容
3. 将英文原文逐条翻译为中文，保持时间戳格式 `[MM:SS]` 不变
4. 在每条原文下方插入翻译行，格式为：`         **翻译**: <中文翻译>`
5. 在原文行前加 `**原文**:` 标记，形成双语对照
6. 保存文件

翻译规则：
- 保持技术术语的准确性（如API、CLI等可保留原文）
- 翻译要自然流畅，符合中文表达习惯
- 时间戳 `[MM:SS]` 格式严格保持不变
- 每次翻译后保存文件并确认

## 配置

```json
{
  "bili2obsidian": {
    "obsidian_vault_path": "D:/pkulyn_vault",
    "output_folder": "Bilibili"
  }
}
```

## 依赖

- bilibili-api-python >= 16.0.0
