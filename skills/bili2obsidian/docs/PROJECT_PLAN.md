# Bilibili字幕提取Skill项目规划

## 一、项目概述

**目标**：开发一个Claude Code Skill，实现从Bilibili视频提取字幕并整理保存到Obsidian知识库。

**核心功能**：
1. 解析B站视频URL/ID
2. 提取视频信息（标题、UP主、简介、标签）
3. 获取CC字幕（自动生成或上传字幕）
4. 格式化输出为Markdown
5. 保存到指定Obsidian知识库路径

---

## 二、技术方案

### 2.1 Bilibili字幕获取方案

**推荐方案**：使用 `bilibili-api-python` 库

```bash
pip install bilibili-api-python
```

**关键API**：
- `video.get_info()` - 获取视频基本信息
- `video.get_subtitle()` - 获取字幕信息
- `video.get_cid()` - 获取视频CID
- `subtitle.get_subtitle_content()` - 获取字幕内容

**字幕类型**：
1. **ai_subtitle** - 自动生成字幕（AI识别）
2. **subtitle** - UP主上传字幕
3. **cc字幕** - 多语言支持

### 2.2 Obsidian集成方案

**推荐方案**：直接文件系统写入

**理由**：
- Obsidian本质是基于Markdown文件的本地知识库
- 直接写入文件即可被Obsidian识别
- 无需依赖第三方API或插件

**文件结构**：
```
D:/pkulyn_vault/
├── Bilibili/
│   ├── {video_id}_{title}.md
│   └── index.md
```

### 2.3 Skill架构

```
SKILL: bili2obsidian
├── index.ts          # Skill入口/命令定义
├── lib/
│   ├── bilibili.ts   # Bilibili API封装
│   ├── subtitle.ts   # 字幕解析/格式化
│   ├── markdown.ts   # Markdown生成
│   └── obsidian.ts   # Obsidian文件操作
└── types/
    └── index.ts      # TypeScript类型定义
```

---

## 三、功能设计

### 3.1 核心命令

| 命令 | 描述 |
|------|------|
| `/bili extract <url>` | 提取指定视频的字幕 |
| `/bili batch <playlist>` | 批量提取播放列表 |
| `/bili search <keyword>` | 搜索视频并提取 |

### 3.2 输出格式（Markdown）

```markdown
---
title: "视频标题"
url: "https://www.bilibili.com/video/BVxxx"
up: "UP主名称"
upload_date: "2024-01-15"
tags: [标签1, 标签2]
duration: "10:23"
subtitle_type: "ai"  # ai | upload | cc
---

# 视频标题

## 视频信息

- **UP主**: [UP主名称](https://space.bilibili.com/xxx)
- **发布时间**: 2024-01-15
- **时长**: 10:23
- **视频链接**: [点击观看](https://www.bilibili.com/video/BVxxx)

## 字幕内容

[00:00] 开场白内容...

[00:15] 第一段内容...

...
```

### 3.3 配置选项

```json
{
  "bili2obsidian": {
    "obsidian_vault_path": "D:/pkulyn_vault",
    "output_folder": "Bilibili",
    "default_subtitle_type": "ai",
    "include_timestamp": true,
    "include_metadata": true,
    "video_info_fetch": true,
    "translation": {
      "enabled": true,
      "target_lang": "zh-CN",
      "source_lang": "auto",
      "translate_english_only": true
    }
  }
}
```

**翻译功能说明**：
- `enabled`: 是否启用自动翻译
- `target_lang`: 目标语言，固定为 `zh-CN`（中文）
- `source_lang`: 源语言，`auto` 自动检测
- `translate_english_only`: 仅翻译英文字幕（推荐，避免重复翻译）

---

## 四、开发计划

### 阶段一：基础功能（2-3天）

- [ ] 搭建Skill项目结构
- [ ] 实现Bilibili API封装
- [ ] 实现基础字幕提取
- [ ] 实现Markdown生成
- [ ] 实现Obsidian文件写入

### 阶段二：功能完善（2-3天）

- [ ] 支持多种字幕类型
- [ ] 添加视频信息获取
- [ ] 实现配置管理
- [ ] 添加错误处理
- [ ] 完善日志记录

### 阶段三：增强功能（可选）

- [ ] 批量处理功能
- [ ] 搜索集成
- [ ] 字幕翻译
- [ ] 自动更新检查

---

## 五、依赖清单

### Python依赖
```
bilibili-api-python>=16.0.0
aiohttp>=3.8.0
```

### Node.js/Skill依赖
```
# 根据Skill SDK要求
```

---

## 六、注意事项

### 合规性
1. **版权**：仅提取允许访问的字幕，遵守B站用户协议
2. **隐私**：不存储用户登录凭证
3. **频率限制**：添加合理的请求间隔，避免对B站服务器造成压力

### 错误处理
- 视频不存在或已删除
- 字幕不存在或关闭
- 网络请求失败
- 文件写入权限问题

### 配置建议
- Obsidian Vault路径通过环境变量或配置指定
- 支持相对路径和绝对路径
- 可配置输出子文件夹

---

## 七、参考资源

### 开源库
- [bilibili-api](https://github.com/Nemo2011/bilibili-api) - Python Bilibili API

### 文档
- [Bilibili API 文档](https://nemo2011.github.io/bilibili-api/)
- Obsidian Help 文档

---

## 项目验收标准

1. [ ] 成功提取B站视频字幕并保存为Markdown
2. [ ] 生成的Markdown格式正确，包含完整的元数据
3. [ ] 文件正确保存到指定的Obsidian Vault路径
4. [ ] 配置选项可正常工作
5. [ ] 错误处理完善，对用户友好

---

**预计开发周期**: 5-7天  
**复杂度**: 中等  
**技术风险**: 低（依赖成熟开源库）