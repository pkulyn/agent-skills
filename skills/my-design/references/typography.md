# 字体与排印参考

> my-design skill 专用参考文档。面向 Agent 使用，中文为主，技术术语保留英文。

---

## 1. 字体配对方案（8 组推荐）

每组包含：display 字体 + body 字体 + 适用场景 + CDN 链接 + CSS 写法。

### 1.1 金融权威

| 项目 | 值 |
|------|-----|
| Display | Source Serif 4（衬线标题） |
| Body | Noto Sans SC（无衬线正文） |
| 场景 | 金融报告、年报、权威声明、银行/基金 PPT |
| CDN | `<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,700&family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">` |

```css
font-family: 'Source Serif 4', 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
```

### 1.2 科技极简

| 项目 | 值 |
|------|-----|
| Display | Space Grotesk（几何感） |
| Body | Inter（高可读） |
| 场景 | SaaS 产品页、技术文档、数据面板、开发者工具 |
| CDN | `<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">` |

```css
font-family: 'Space Grotesk', 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
```

### 1.3 人文温润

| 项目 | 值 |
|------|-----|
| Display | EB Garamond（经典衬线） |
| Body | Source Han Serif / Noto Serif SC（宋体） |
| 场景 | 文化机构、书院、人文杂志、读书会、非遗项目 |
| CDN | `<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,700;1,400&family=Noto+Serif+SC:wght@400;600;700&display=swap" rel="stylesheet">` |

```css
font-family: 'EB Garamond', 'Noto Serif SC', 'Source Han Serif SC', 'STSong', 'SimSun', serif;
```

### 1.4 现代商务

| 项目 | 值 |
|------|-----|
| Display | Plus Jakarta Sans（圆润） |
| Body | PingFang SC（系统字体，无需加载） |
| 场景 | 企业官网、商务汇报、ToB 产品、会议 PPT |
| CDN | `<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">` |

```css
font-family: 'Plus Jakarta Sans', 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif;
```

> PingFang SC 为 macOS/iOS 系统字体，Windows 回退到微软雅黑。

### 1.5 数据驱动

| 项目 | 值 |
|------|-----|
| Display | JetBrains Mono（等宽数据） |
| Body | SF Pro / system-ui（系统 UI 字体） |
| 场景 | 数据大屏、终端风格页面、代码展示、量化报告 |
| CDN | `<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">` |

```css
font-family: 'JetBrains Mono', 'SF Pro Text', -apple-system, 'Segoe UI', 'Microsoft YaHei', monospace;
```

> SF Pro 无法通过 web font 加载，仅限 Apple 生态回退。其他平台走 system-ui 链。

### 1.6 创意设计

| 项目 | 值 |
|------|-----|
| Display | Playfair Display（高对比衬线） |
| Body | Lora（正文衬线） |
| 场景 | 设计工作室、艺术展、时尚品牌、婚礼/活动邀请 |
| CDN | `<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Lora:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">` |

```css
font-family: 'Playfair Display', 'Lora', 'Noto Serif SC', 'STSong', serif;
```

### 1.7 东方极简

| 项目 | 值 |
|------|-----|
| Display | Noto Serif SC（思源宋） |
| Body | Noto Sans SC（思源黑） |
| 场景 | 日式/中式极简、禅意设计、茶道/花道、极简品牌 |
| CDN | `<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">` |

```css
font-family: 'Noto Serif SC', 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
```

> ⚠️ Noto Serif SC / Noto Sans SC web font 文件较大（子集化后仍可达 2-5MB/weight），建议配合系统回退链，仅加载标题所需 weight。

### 1.8 党建政务

| 项目 | 值 |
|------|-----|
| Display | STHeiti（华文黑体） |
| Body | SimSun（宋体） |
| 场景 | 党建 PPT、政府文件、红色主题、政务汇报、公文体 |
| CDN | 无需 CDN（均为系统字体） |

```css
font-family: 'STHeiti', 'SimHei', 'Microsoft YaHei', sans-serif;   /* 标题 */
font-family: 'SimSun', 'STSong', 'FangSong', serif;                /* 正文 */
```

> 党建政务场景禁止使用花哨西文字体。严格遵循：标题黑体 + 正文宋体。红色主色 #DE2910，金色辅色 #FFDE00。

---

## 2. 字号层级系统

### 2.1 PPT 场景（1920×1080）

| 层级 | 字号 | 字重 | 用途 |
|------|------|------|------|
| 封面标题 | 72–120px | 700 / Bold | 封面主标题 |
| 章节标题 | 48–64px | 600–700 | 分隔页、章节开头 |
| 页面标题 | 36–48px | 600 | 单页标题 |
| 正文 | 24–32px | 400–500 | 段落正文、列表项 |
| 注释/图注 | 18–20px | 300–400 | 脚注、数据来源、图片说明 |

**关键规则：**
- 同一页面字号层级不超过 3 级
- 标题与正文字号比 ≥ 1.5:1
- 最小字号不低于 16px（投影可读性底线）

### 2.2 网页场景

| 层级 | 字号 | 字重 | 行高 |
|------|------|------|------|
| h1 | 48–72px | 700 | 1.1–1.2 |
| h2 | 32–48px | 600–700 | 1.2–1.3 |
| h3 | 24–32px | 600 | 1.3 |
| body | 16–18px | 400 | 1.5–1.7 |
| small | 12–14px | 400 | 1.4–1.5 |

**响应式缩放（clamp 写法）：**
```css
h1 { font-size: clamp(32px, 5vw, 72px); }
h2 { font-size: clamp(24px, 3.5vw, 48px); }
body { font-size: clamp(15px, 1.1vw, 18px); }
```

### 2.3 原型场景（iPhone 15 Pro，逻辑像素）

| 层级 | 字号 | 字重 | 用途 |
|------|------|------|------|
| 大标题（Large Title） | 34px | 700 | 导航栏大标题 |
| 导航标题 | 17–20px | 600 | 常规导航栏标题 |
| 正文 | 15–17px | 400–500 | 列表项、段落 |
| 辅助文字 | 12–13px | 400 | 时间戳、标签、说明 |
| 极小文字 | 10–11px | 500 | 角标、badge |

---

## 3. 中文排印规范

### 3.1 行距

- 中文行距宜**大于英文**（汉字无升部/降部，行间需额外呼吸空间）
- 正文：`line-height: 1.7–2.0`（倍数字号）
- 标题：`line-height: 1.2–1.4`
- PPT 正文：行距 1.3–1.5 倍

### 3.2 字距

- 正文：`letter-spacing: 0`（默认即可）
- 标题可微调：`letter-spacing: 0.02–0.05em`
- 大标题有时需要负字距：`letter-spacing: -0.02em`（字越大越紧凑）

### 3.3 段间距

- 段间距 = 0.8–1.2 倍行高
- CSS 写法：`margin-bottom: 0.8em` ~ `1.2em`（基于 body 的 em）

### 3.4 中英文混排

- **盘古之白**：英文/数字与中文之间加半角空格
  - ✅ `使用 React 框架` / ❌ `使用React框架`
  - ✅ `版本 2.0 发布` / ❌ `版本2.0发布`
- 专有名词使用英文原文时可不加：`iPhone`、`macOS`

### 3.5 标点挤压

```css
text-spacing: trim-start allow-end ideograph-alpha ideograph-numeric;
```

- `trim-start`：行首标点挤压
- `allow-end`：行尾标点半宽
- `ideograph-alpha`：中英文间距调整
- 浏览器支持有限，Chrome 113+ 可用

### 3.6 禁则处理

- 避头点号：`。` `，` `、` `）` `」` 不出现在行首
- 避尾点号：`（` `「` 不出现在行尾
- CSS：`line-break: strict;` 或 `line-break: anywhere;`（按需选择）

### 3.7 中文引号

- 推荐用直角引号「」『』
- 横排用「」，竖排用竖排用﹁﹂
- ❌ 避免：""（西文引号在中文排版中不协调）

### 3.8 优雅换行

```css
text-wrap: pretty;    /* 优先使用，避免孤字/寡行 */
text-wrap: balance;   /* 标题场景，平衡行宽 */
overflow-wrap: break-word;  /* 兜底 */
```

---

## 4. 反 AI Slop 字体清单

### 4.1 Display 字体黑名单

以下字体作为 display/标题字体时**禁止默认选用**（太常见 = 没风格）：

| 字体 | 原因 |
|------|------|
| Inter | 全网默认，毫无辨识度 |
| Roboto | Android 系统字体，太普及 |
| Arial | 时代遗留，避免使用 |
| system-ui | 等于没选字体 |
| Fraunces | AI 生成设计的高频选择，已成刻板印象 |

### 4.2 例外情况

- 品牌 spec（品牌手册）明确要求使用上述字体时，遵从品牌规范
- body/正文字体可用 Inter/Roboto（可读性优先）

### 4.3 中文禁忌

- **禁止全页宋体**（论文、书刊、政务公文体除外）
- 宋体仅用于：标题点缀、衬线配对、传统/人文风格
- 正文首选黑体/无衬线

---

## 5. 字体加载优化

### 5.1 font-display 策略

```css
@font-face {
  font-family: 'MyFont';
  src: url('/fonts/myfont.woff2') format('woff2');
  font-display: swap;  /* FOIT → FOUT：先显示回退字体，加载后替换 */
}
```

- `swap`：推荐默认值，避免不可见文字闪烁（FOIT）
- `optional`：弱网环境友好，可能直接用回退字体
- `block`：不推荐，最长 3s 白屏

### 5.2 Google Fonts 按需加载

只加载实际使用的 weight 和 subset：

```
✅ https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap
❌ https://fonts.googleapis.com/css2?family=Space+Grotesk  (全部 weight)
```

常用 weight 速查：
- 300：Light（辅助/注释）
- 400：Regular（正文）
- 500：Medium（强调正文）
- 600：SemiBold（小标题）
- 700：Bold（标题）

### 5.3 中文 Web Font 策略

中文 web font 单个 weight 可达 5–15MB，**禁止直接全量加载**：

**方案 A：系统字体回退链（推荐）**
```css
font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', 'Hiragino Sans GB', sans-serif;
```
- macOS → PingFang SC
- Windows → Microsoft YaHei
- Android → Noto Sans CJK

**方案 B：子集化 web font**
- 使用 Google Fonts 的中文子集（按需加载常用字）
- 或用 `pyftsubset` / `fonttools` 自行子集化

**方案 C：动态加载**
- 页面加载后异步加载中文字体
- 搭配 `document.fonts.ready` 回调

### 5.4 Preload 关键字体

```html
<link rel="preload" href="/fonts/display-font.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/body-font.woff2" as="font" type="font/woff2" crossorigin>
```

- 只 preload 首屏必需的字体（通常 1–2 个）
- 中文 web font **不 preload**（文件太大，拖慢首屏）

### 5.5 格式优先级

1. **WOFF2**：最小体积，现代浏览器全支持
2. WOFF：兼容旧浏览器
3. TTF/OTF：不推荐 web 使用

```css
@font-face {
  src: url('font.woff2') format('woff2'),
       url('font.woff') format('woff');  /* fallback */
}
```

---

## 附录：快速选择决策树

```
需要中文吗？
├── 是 → 场景类型？
│   ├── 金融/权威 → 1.1 金融权威
│   ├── 党政/政务 → 1.8 党建政务
│   ├── 文化/人文 → 1.3 人文温润 或 1.7 东方极简
│   ├── 科技/数据 → 1.2 科技极简 或 1.5 数据驱动
│   └── 商务/通用 → 1.4 现代商务
└── 否 → 风格偏好？
    ├── 极简/几何 → 1.2 科技极简
    ├── 经典/衬线 → 1.6 创意设计
    └── 现代/圆润 → 1.4 现代商务
```
