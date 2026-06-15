---
name: bili2obsidian
description: >
  提取Bilibili视频字幕并保存到Obsidian知识库。支持单视频提取、收藏夹批量提取、付费课程批量提取。
  英文字幕自动翻译为双语对照格式。
  触发场景：提到B站/Bilibili视频字幕提取、视频笔记、收藏夹批量下载字幕、课程字幕提取。
  不触发：仅下载视频/音频文件、B站评论分析、视频内容摘要（非字幕提取）。
triggers:
  - Bilibili
  - B站
  - 字幕提取
  - 视频字幕
  - 收藏夹字幕
  - 付费课程字幕
  - bili extract
  - bili batch
  - bili course
license: MIT
metadata:
  version: "1.3.0"
  category: media-processing
  type: tool-wrapper
  author: pkulyn
---

# Bilibili字幕提取Skill

从Bilibili视频提取字幕，保存为Markdown到Obsidian知识库。英文字幕由智能体自动翻译为双语对照。

## 路由表

| 用户意图 | 命令 | 说明 |
|---------|------|------|
| 提取单个视频字幕 | `extract` | 给URL或BV号 |
| 批量提取收藏夹 | `batch` | 给收藏夹URL或ID |
| 批量提取付费课程 | `course` | 给课程URL或SS号 |
| 查看/初始化配置 | `config` | 首次使用需配置 |

## 工作流程

### 步骤1：提取字幕

```bash
# 单视频
cd D:\cc_projects\Agent-Skills\skills\bili2obsidian && python bili2obsidian.py extract "<URL>"

# 收藏夹批量
cd D:\cc_projects\Agent-Skills\skills\bili2obsidian && python bili2obsidian.py batch "<收藏夹URL>"

# 付费课程批量
cd D:\cc_projects\Agent-Skills\skills\bili2obsidian && python bili2obsidian.py course "<课程URL>"
```

**字幕类型偏好**：默认`best`（自动选最佳），可选 `ai`（AI生成）/ `upload`（UP主上传）/ `cc`（CC字幕）：
```bash
python bili2obsidian.py extract "<URL>" --type ai
```

### 步骤2：翻译英文字幕（智能体后处理）

字幕提取完成后，检查输出中是否标记了 `⚠️ 英文字幕，需要翻译`。如果有：

1. 读取该Markdown文件
2. 找到 `## 字幕` 部分的内容
3. 将英文原文逐条翻译为中文，保持时间戳格式 `[MM:SS]` 不变
4. 在每条原文下方插入翻译行，格式为：`         **翻译**: <中文翻译>`
5. 在原文行前加 `**原文**:` 标记，形成双语对照
6. 保存文件

**翻译规则**：
- 保持技术术语的准确性（如API、CLI等可保留原文）
- 翻译要自然流畅，符合中文表达习惯
- 时间戳 `[MM:SS]` 格式严格保持不变

## 配置

输出位置由 `config/config.local.json` 控制：

```json
{
  "bili2obsidian": {
    "obsidian_vault_path": "D:/pkulyn_vault",
    "output_folder": "Bilibili"
  }
}
```

首次使用时运行 `python bili2obsidian.py config --init` 初始化。

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError` | 依赖未安装 | `pip install -r requirements.txt` |
| 字幕为空 | 视频无字幕 | 提示用户该视频没有可用字幕 |
| 编码乱码 | Windows控制台编码 | 脚本已内置UTF-8修复，如仍有问题尝试 `chcp 65001` |
| 收藏夹提取部分失败 | 部分视频无字幕 | 正常现象，检查输出日志中的跳过记录 |

## 依赖

- bilibili-api-python >= 16.0.0
