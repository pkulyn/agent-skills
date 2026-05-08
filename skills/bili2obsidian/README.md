# Bilibili字幕提取工具 (bili2obsidian)

将Bilibili视频字幕提取并保存到Obsidian知识库的自动化工具，支持收藏夹/付费课程批量提取、英文字幕智能体翻译、元数据管理和Obsidian友好的Markdown格式。

## ✨ 功能特点

- 🎥 **多类型字幕提取**：支持AI自动生成字幕、UP主上传字幕、CC字幕三种类型，中文优先，自动选择最优
- 📦 **批量提取**：支持收藏夹和付费课程批量提取，自动去重已提取视频
- 🌐 **智能体翻译**：英文字幕自动标记，由AI智能体后处理翻译，无需配置翻译API，翻译质量更高
- 📝 **Obsidian兼容**：生成带有完整YAML Front Matter的Markdown文档，含视频封面，完美融入知识库
- 📊 **智能标签**：从视频标题提取实体标签 + API标签去重合并，标签更精准
- 🔤 **自动标点**：AI字幕原始数据无标点，自动添加中文逗号和句号，智能分段，阅读更流畅
- 🔒 **安全配置**：支持本地配置文件存储B站凭证，不会泄露隐私
- 📂 **规范命名**：自动使用`UP主：视频标题`格式命名文件，便于知识库管理

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/pkulyn/bili2obsidian.git
cd bili2obsidian

# 安装依赖
pip install -r requirements.txt
```

### 配置

#### 1. 基础配置
编辑 `config/default.json` 或创建 `~/.bili2obsidian.json` 配置文件：

```json
{
  "obsidian_vault_path": "D:/pkulyn_vault",
  "output_folder": "Bilibili",
  "default_subtitle_type": "ai"
}
```

#### 2. B站登录配置（可选但推荐）
部分视频的字幕需要登录才能获取，配置B站凭证可以获得更好的使用体验：

1. 打开B站网站并登录
2. 按F12打开开发者工具，切换到Application/存储标签
3. 在Cookie中找到三个字段：
   - `SESSDATA`
   - `bili_jct`
   - `buvid3`
4. 填入配置文件：

```json
{
  "bilibili_credential": {
    "sessdata": "你的SESSDATA",
    "bili_jct": "你的bili_jct",
    "buvid3": "你的buvid3"
  }
}
```

> 💡 提示：你也可以创建`config/config.local.json`文件存储个人配置，该文件会被`.gitignore`自动忽略，不会提交到仓库。

### 使用方法

#### 单视频提取

```bash
# 提取视频字幕（支持URL或BV号）
python bili2obsidian.py extract "https://www.bilibili.com/video/BV1YxckzbEaT"

# 提取并指定字幕类型
python bili2obsidian.py extract "BV1YxckzbEaT" --type ai

# 显示帮助信息
python bili2obsidian.py --help
```

#### 批量提取收藏夹

```bash
# 批量提取收藏夹中所有视频字幕（自动跳过已提取的视频）
python bili2obsidian.py batch "https://space.bilibili.com/443558422/favlist?fid=3868639722"

# 强制覆盖已存在的文件
python bili2obsidian.py batch "https://space.bilibili.com/443558422/favlist?fid=3868639722" --force
```

#### 批量提取付费课程

```bash
# 批量提取已购买课程的所有视频字幕
python bili2obsidian.py course "https://www.bilibili.com/cheese/play/ss6838"

# 通过SS号提取
python bili2obsidian.py course "ss6838"
```

### 输出示例

生成的Markdown文件会保存在你的Obsidian Vault的`Bilibili/`目录下，文件名为：
`姜Dora在此：性格扭扭捏捏的人都有一个特质，社恐不会聊天接话必看.md`

文件内容结构：
```markdown
---
title: "ChatGPT/Codex接码最新教程分享，3分钟解决！"
source: "https://www.bilibili.com/video/BV1Us9fBUEjR"
bvid: "BV1Us9fBUEjR"
avid: 116510517431474
up: "AI_小波"
up_id: 14836418
date: "2026-05-03"
duration: 153
views: 14122
likes: 246
coins: 131
subtitle_type: "中文（AI自动生成）"
subtitle_count: 83
tags:
  - ChatGPT
  - Codex
  - 知识分享官
  - 教程
---

![视频封面](https://i2.hdslb.com/bfs/archive/xxx.jpg)

# ChatGPT/Codex接码最新教程分享，3分钟解决！

> **来源**: [B站视频](https://www.bilibili.com/video/BV1Us9fBUEjR) | **UP主**: AI_小波 | **字幕类型**: 中文（AI自动生成） | **提取日期**: 2026-05-03

📝 简介：简单的教程分享，文档在置顶评论。

---

最近OpenAI的风控又升级了，现在登录codex都需要解码了，而且国内号码呢也是用不了的，所以说今天小布来，来分享一个极其简单的解码教程，让你3分钟就能搞定，有几点需要注意，第一个就是解码，它是不支持虚拟号码的，第二个，如果你是在近期新注册的GPT账号。

再去登录go test，这边是必定会触发这个解码认证的，那么接下来小波就以codex解码为例子...

---

*生成时间: 2026-05-08 16:07:14*
```

### 英文字幕翻译（智能体后处理）

当提取的字幕被检测为英文时，程序会输出标记 `⚠️ 英文字幕，需要翻译`。此时可由AI智能体自动完成翻译：

1. 智能体读取含英文字幕的Markdown文件
2. 找到 `## 字幕` 部分的内容
3. 将英文原文逐条翻译为中文，保持时间戳格式不变
4. 在每条原文下方插入翻译行，形成双语对照：

```
[00:05] **原文**: Hello everyone, welcome to my channel
         **翻译**: 大家好，欢迎来到我的频道
```

**优势**：
- 零API配置，无需Google Translate或其他翻译服务
- 翻译质量更高，技术术语处理更准确
- 无网络连接问题，不会因翻译服务不可用导致整体失败

## 🔄 去重机制

程序通过扫描输出目录下已有Markdown文件的YAML Front Matter中的 `bvid` 字段实现去重：
- 批量处理时自动跳过已提取的视频
- 使用 `--force` 参数可强制覆盖

## 📁 项目结构

```
bili2obsidian/
├── src/                          # 源代码目录
│   ├── __init__.py
│   ├── __main__.py              # 模块入口
│   ├── main.py                  # 核心逻辑（含英文检测）
│   ├── cli.py                   # 命令行接口
│   ├── config.py                # 配置管理
│   ├── bilibili.py              # Bilibili API封装
│   ├── markdown_generator.py    # Markdown文档生成
│   └── obsidian.py              # Obsidian文件操作
├── config/                       # 配置文件目录
│   ├── default.json             # 默认配置
│   └── config.local.json        # 本地个人配置（不会被提交）
├── docs/                         # 文档目录
├── bili2obsidian.py             # 便捷启动脚本
├── requirements.txt              # 依赖包列表
├── INSTALL.md                    # 详细安装说明
├── README.md                     # 本文件
├── SKILL.md                      # Claude Skill定义文件
└── .gitignore                    # Git忽略配置
```

## 🛠️ 技术栈

- **Python >= 3.8**
- [bilibili-api-python](https://github.com/Nemo2011/bilibili-api) >= 16.0.0 - B站API封装
- [aiohttp](https://docs.aiohttp.org/) >= 3.8.0 - 异步HTTP请求

## 📄 许可证

MIT License - 详见LICENSE文件

## 🤝 贡献

欢迎提交Issue和Pull Request！如果有功能建议或问题反馈，请随时提出。

## 📅 更新日志

### v1.2.0 (2026-05-08)
- ✅ AI字幕自动添加中文标点（逗号连接片段，句号结束段落），阅读更自然流畅
- ✅ 智能分段：基于时间间隔 + 字符数双重规则，AI字幕不再合并为一大段
- ✅ 智能标签：从视频标题提取英文实体标签（如ChatGPT、Codex），与API标签去重合并，不区分大小写
- ✅ 字幕选择优化：中文优先级最高（zh > ai-zh > en），综合语言+类型评分选择最佳字幕
- ✅ 封面URL修复：B站API返回http协议，自动替换为https
- ✅ 文件名双重后缀修复：避免生成`.md.md`文件
- ✅ 未配置Vault路径时给出明确错误提示
- ✅ Markdown格式重构：视频信息改为引用块格式，去除冗余字段，字幕不再使用`## 字幕`标题

### v1.1.0 (2026-04-22)
- ✅ 翻译方案重构：移除deep-translator依赖，改为AI智能体后处理翻译
- ✅ 新增收藏夹批量提取功能（自动去重）
- ✅ 新增付费课程批量提取功能（支持已购买课程）
- ✅ 英文字幕智能检测（采样多条判断，避免中英混合误判）
- ✅ 输出中增加视频封面图片
- ✅ 文件命名格式调整为`UP主：视频标题`
- ✅ 修复翻译模块await同步方法导致的崩溃问题
- ✅ 翻译失败时降级保存原文字幕，不再中断整个流程
- ✅ 移除--translate参数，翻译由智能体自动处理

### v1.0.0 (2026-04-21)
- ✅ 初始版本正式发布
- ✅ 支持三种类型字幕自动提取
- ✅ 完整的Obsidian Markdown生成
- ✅ YAML Front Matter元数据支持
- ✅ 配置文件管理系统
- ✅ 命令行接口
