# 安装和使用指南

## 快速安装

```bash
# 1. 进入项目目录
cd D:/cc_projects/skill-bilibili-obsidian

# 2. 安装依赖
pip install -r requirements.txt
```

## 配置步骤

### 方式一：使用默认配置
编辑 `config/default.json`，修改 `obsidian_vault_path` 为你的Obsidian库路径。

### 方式二：使用自定义配置文件
创建 `~/.bili2obsidian.json`，内容如下：

```json
{
  "obsidian_vault_path": "D:/pkulyn_vault",
  "output_folder": "Bilibili",
  "translation": {
    "enabled": true
  }
}
```

### 配置B站登录（推荐）
大部分视频的字幕需要登录才能获取，建议配置登录凭证：

1. 在浏览器中打开B站并登录
2. 按F12打开开发者工具
3. 进入Application/存储 -> Cookies -> https://www.bilibili.com
4. 复制以下三个Cookie的值：
   - SESSDATA
   - bili_jct
   - buvid3
5. 填入配置文件的 `bilibili_credential` 部分

## 使用方法

### 提取单个视频字幕
```bash
python -m src extract "https://www.bilibili.com/video/BVxxx"

# 提取并翻译
python -m src extract "https://www.bilibili.com/video/BVxxx" --translate

# 指定字幕类型（ai/upload/cc）
python -m src extract "BVxxx" --type upload
```

### 查看配置
```bash
python -m src config --show
```

## 输出位置
字幕文件会保存在：
`你的Obsidian库路径/Bilibili/BVxxx_视频标题.md`

## 常见问题

### Q: 提示"获取字幕列表失败: Credential 类未提供 sessdata 或者为空"
A: 需要配置B站登录凭证，参考上面的配置步骤。

### Q: 字幕为空或获取失败
A: 1. 确认视频是否有字幕（打开视频页面检查）
   2. 确认登录凭证是否有效
   3. 尝试切换字幕类型：`--type upload` 或 `--type cc`

### Q: 生成的Markdown文件乱码
A: 确保Obsidian的文件编码设置为UTF-8。

## 测试示例
```bash
# 测试视频
python -m src extract "https://www.bilibili.com/video/BV1YxckzbEaT/" --translate
```
