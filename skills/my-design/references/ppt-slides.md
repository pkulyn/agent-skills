# PPT 幻灯片专项参考

> 面向 Agent 使用，具体可执行。中文为主，技术术语保留英文。

---

## 1. HTML优先架构 + 交付格式决策树

HTML deck 是所有 PPT 任务路径的**默认基础产物**。先产出 HTML，再按需转换。

```
用户需求是什么？
│
├─ 只要PPT ──────────→ HTML预览 + PPTX导出
├─ 要演讲 ───────────→ HTML预览 + PDF备选
├─ 要品牌套壳 ───────→ HTML预览 + PPTX + 自定义品牌模板后处理
└─ 只要预览 ─────────→ HTML即可（无需导出）
```

**执行规则：**
- 所有 PPT 任务第一步都是生成 HTML deck
- 预览通过 Canvas present 验证
- PPTX/PDF 是可选的第二步导出
- 品牌套壳是第三步后处理

---

## 2. 幻灯片架构选型

### 决策树

```
页数 ≥ 10？ ──→ 多文件架构
│
├─ 是 → 多文件架构
│       ├─ 学术课件 ✓
│       ├─ 多agent并行生成 ✓
│       └─ 页面独立修改 ✓
│
└─ 否 → 单文件架构
        ├─ ≤10页 ✓
        ├─ pitch deck ✓
        └─ 需跨页共享状态（进度条/导航） ✓
```

### 多文件架构（默认推荐）

**结构：**
```
deck/
├── deck_index.html        ← 拼接器，加载所有slide
├── slide_01_cover.html
├── slide_02_toc.html
├── slide_03_section.html
├── ...
└── deck_style.css         ← 共享样式（可选）
```

**deck_index.html 拼接器模板：**
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=1920">
  <title>{{DECK_TITLE}}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #1a1a2e; display: flex; flex-direction: column; align-items: center; gap: 20px; padding: 20px; }
    .slide-frame { width: 1920px; height: 1080px; border: 1px solid #333; border-radius: 8px; overflow: hidden; }
    iframe { width: 1920px; height: 1080px; border: none; transform-origin: top left; }
  </style>
</head>
<body>
  <!-- 每个slide用iframe加载，或用fetch注入 -->
  <div class="slide-frame"><iframe src="slide_01_cover.html"></iframe></div>
  <div class="slide-frame"><iframe src="slide_02_toc.html"></iframe></div>
  <!-- ... -->
</body>
</html>
```

**单页 slide 模板：**
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=1920">
  <title>{{SLIDE_TITLE}}</title>
  <style>
    :root {
      --primary: #2D5AF0;
      --accent: #FF6B35;
      --bg: #FFFFFF;
      --text: #1A1A2E;
      --text-secondary: #666666;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      width: 1920px;
      height: 1080px;
      font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
      background: var(--bg);
      color: var(--text);
      overflow: hidden;
    }
  </style>
</head>
<body>
  <!-- 页面内容 -->
</body>
</html>
```

### 单文件架构

**适用：** ≤10页、pitch deck、需跨页共享状态

**核心：** 使用 `deck_stage.js` web component 管理页面切换和共享状态。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=1920">
  <title>{{DECK_TITLE}}</title>
  <style>
    :root {
      --primary: #2D5AF0;
      --accent: #FF6B35;
      --bg: #FFFFFF;
      --text: #1A1A2E;
      --text-secondary: #666666;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      width: 1920px; height: 1080px;
      font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
      background: var(--bg); color: var(--text); overflow: hidden;
    }
    deck-stage { display: block; width: 100%; height: 100%; }
    deck-slide { display: none; width: 1920px; height: 1080px; position: absolute; top: 0; left: 0; }
    deck-slide[active] { display: flex; }
    /* 共享导航条 */
    .nav-bar { position: absolute; bottom: 20px; right: 40px; font-size: 14px; color: #999; z-index: 100; }
  </style>
</head>
<body>
<deck-stage>
  <deck-slide active>
    <!-- Slide 1: cover -->
  </deck-slide>
  <deck-slide>
    <!-- Slide 2: toc -->
  </deck-slide>
  <!-- ... -->
</deck-stage>
<div class="nav-bar"><span id="pageNum">1</span> / <span id="totalPages">10</span></div>
<script>
  class DeckStage extends HTMLElement {
    connectedCallback() {
      this.slides = this.querySelectorAll('deck-slide');
      this.current = 0;
      this.total = this.slides.length;
      document.getElementById('totalPages').textContent = this.total;
      this.show(0);
      document.addEventListener('keydown', e => {
        if (e.key === 'ArrowRight' || e.key === ' ') this.next();
        if (e.key === 'ArrowLeft') this.prev();
      });
    }
    show(n) {
      this.slides.forEach((s, i) => s.toggleAttribute('active', i === n));
      this.current = n;
      const pn = document.getElementById('pageNum');
      if (pn) pn.textContent = n + 1;
    }
    next() { if (this.current < this.total - 1) this.show(this.current + 1); }
    prev() { if (this.current > 0) this.show(this.current - 1); }
  }
  customElements.define('deck-stage', DeckStage);
</script>
</body>
</html>
```

---

## 3. 12种PPT页面类型模板

### 3.1 封面页 (cover)

**视觉特征：** 大标题居中/偏左，副标题小字，底部日期+品牌标识，大面积留白或背景图

**布局参数：**
- 标题：56-72px，font-weight: 700，居中或偏左
- 副标题：24-28px，font-weight: 400，color: var(--text-secondary)
- 日期：16-18px，底部40px处
- 品牌logo：右上角或底部左对齐

**HTML骨架：**
```html
<div style="display:flex; flex-direction:column; justify-content:center; align-items:center; height:100%; padding:80px 120px;">
  <div style="font-size:64px; font-weight:700; line-height:1.2; text-align:center;">{{主标题}}</div>
  <div style="font-size:26px; font-weight:400; color:var(--text-secondary); margin-top:24px;">{{副标题}}</div>
  <div style="position:absolute; bottom:40px; left:120px; font-size:16px; color:#999;">{{日期}}</div>
  <div style="position:absolute; bottom:40px; right:120px;"><!-- logo --></div>
</div>
```

**常见踩坑：**
- 标题过长不换行 → 设 `max-width: 80%` + `word-break: keep-all`
- 移动端标题溢出 → 画布固定1920px，无需响应式
- 忘记设 brand 标识 → 每个封面必须有

---

### 3.2 目录页 (toc)

**视觉特征：** 章节编号+标题纵向排列，可选编号圆/图标，右侧可配装饰线条

**布局参数：**
- 编号圆：40px直径，var(--primary)背景，白色数字
- 章节标题：28-32px
- 间距：每项60-80px
- 左侧缩进：120-160px

**HTML骨架：**
```html
<div style="display:flex; flex-direction:column; justify-content:center; padding:80px 160px;">
  <div style="font-size:36px; font-weight:700; margin-bottom:48px;">目录</div>
  <div style="display:flex; align-items:center; margin-bottom:48px;">
    <div style="width:40px; height:40px; border-radius:50%; background:var(--primary); color:#fff; display:flex; align-items:center; justify-content:center; font-size:18px; font-weight:700; flex-shrink:0;">01</div>
    <div style="margin-left:24px; font-size:28px;">{{章节标题1}}</div>
  </div>
  <!-- 重复每项 -->
</div>
```

**常见踩坑：**
- 章节超过6个 → 分两栏或缩小字号
- 编号圆和文字不对齐 → 用 `align-items: center`
- 无视觉层次 → 当前章节高亮（如加深色块）

---

### 3.3 章节分隔页 (section)

**视觉特征：** 大号章节序号+标题，极简，视觉节奏切换，可用对比色背景

**布局参数：**
- 序号：120-180px，极细font-weight:100-200，opacity: 0.15-0.2
- 标题：48-56px，font-weight: 700
- 可选：背景色切换为 var(--primary) + 白色文字
- 内边距：大，营造呼吸感

**HTML骨架：**
```html
<div style="display:flex; flex-direction:column; justify-content:center; align-items:flex-start; height:100%; padding:80px 160px; background:var(--primary);">
  <div style="font-size:160px; font-weight:100; opacity:0.15; line-height:1; color:#fff;">01</div>
  <div style="font-size:52px; font-weight:700; color:#fff; margin-top:-20px;">{{章节标题}}</div>
</div>
```

**常见踩坑：**
- 序号太大被裁切 → 确保父容器 `overflow: hidden`
- 白字在浅色背景不可见 → 确保背景色足够深
- 与封面页混淆 → section页更极简，无副标题无日期

---

### 3.4 要点列表页 (bullets)

**视觉特征：** 3-5个要点，图标/编号/卡片式排列，每项一行

**布局参数：**
- 要点数：3-5个（超过5个分页）
- 字号：24-28px
- 图标：32-40px
- 行间距：56-64px
- 可选样式：图标式 / 编号式 / 卡片式

**HTML骨架（图标式）：**
```html
<div style="padding:80px 160px;">
  <div style="font-size:36px; font-weight:700; margin-bottom:48px;">{{页面标题}}</div>
  <div style="display:flex; align-items:flex-start; margin-bottom:48px;">
    <div style="width:36px; height:36px; flex-shrink:0; margin-right:20px; color:var(--primary);">●</div>
    <div>
      <div style="font-size:26px; font-weight:600;">{{要点标题}}</div>
      <div style="font-size:20px; color:var(--text-secondary); margin-top:8px;">{{补充说明}}</div>
    </div>
  </div>
  <!-- 重复每项 -->
</div>
```

**HTML骨架（卡片式）：**
```html
<div style="display:flex; gap:32px; padding:80px 120px;">
  <div style="flex:1; background:#F7F8FC; border-radius:12px; padding:40px;">
    <div style="font-size:36px; color:var(--primary); margin-bottom:16px;">01</div>
    <div style="font-size:24px; font-weight:600;">{{卡片标题}}</div>
    <div style="font-size:18px; color:var(--text-secondary); margin-top:12px;">{{卡片内容}}</div>
  </div>
  <!-- 重复卡片 -->
</div>
```

**常见踩坑：**
- 要点超过5个 → 拆分为两页
- 图标大小不一致 → 固定width/height + flex-shrink:0
- 卡片宽度不均 → 用 `flex:1` 等分

---

### 3.5 数据展示页 (data)

**视觉特征：** 大数字+说明文字，可选可视化图表（柱状/环形/趋势线）

**布局参数：**
- 大数字：72-96px，font-weight: 700，var(--primary) 或 var(--accent)
- 说明文字：20-24px，color: var(--text-secondary)
- 图表区：占页面50-60%宽度
- 数据标签：紧贴数字，14-16px

**HTML骨架：**
```html
<div style="display:flex; padding:80px 120px; gap:80px;">
  <div style="flex:1; display:flex; flex-direction:column; justify-content:center;">
    <div style="font-size:88px; font-weight:700; color:var(--primary);">89%</div>
    <div style="font-size:22px; color:var(--text-secondary); margin-top:16px;">{{指标说明}}</div>
  </div>
  <div style="flex:1.2; display:flex; align-items:center; justify-content:center;">
    <!-- 图表区域：用SVG或内联chart -->
  </div>
</div>
```

**常见踩坑：**
- 数字太大溢出 → 测试最宽数字（如888,888,888）
- 图表无标注 → 每个数据点必须有标签
- 颜色含义不清 → 图例必不可少

---

### 3.6 对比页 (comparison)

**视觉特征：** 双栏/多栏对比，支持表格/卡片，中间分隔线或VS标记

**布局参数：**
- 栏数：2-3栏
- 栏间距：40-60px，中间分隔线1px #E0E0E0
- 标题栏：背景色区分（如 var(--primary) vs var(--accent)）
- 内容行：等高对齐

**HTML骨架：**
```html
<div style="padding:80px 120px;">
  <div style="font-size:36px; font-weight:700; margin-bottom:48px;">{{对比标题}}</div>
  <div style="display:flex; gap:0;">
    <!-- 左栏 -->
    <div style="flex:1; background:#F7F8FC; border-radius:12px 0 0 12px; padding:40px;">
      <div style="font-size:24px; font-weight:700; color:var(--primary); margin-bottom:24px;">方案A</div>
      <div style="font-size:20px; margin-bottom:16px;">{{对比项1}}</div>
      <!-- ... -->
    </div>
    <!-- 右栏 -->
    <div style="flex:1; background:#E8F0FE; border-radius:0 12px 12px 0; padding:40px;">
      <div style="font-size:24px; font-weight:700; color:var(--accent); margin-bottom:24px;">方案B</div>
      <div style="font-size:20px; margin-bottom:16px;">{{对比项1}}</div>
      <!-- ... -->
    </div>
  </div>
</div>
```

**常见踩坑：**
- 两栏内容不等高 → 用 `align-items: stretch` 或固定min-height
- 表格线太密 → 用背景色区分而非边框线
- 对比维度不对应 → 确保左右行一一对应

---

### 3.7 时间线页 (timeline)

**视觉特征：** 横向/纵向流程，里程碑标记，连线+节点

**布局参数：**
- 横向时间线：适合4-6个节点
- 纵向时间线：适合5-8个节点
- 节点圆：16-20px，var(--primary)填充
- 连线：2px，#E0E0E0
- 年份/标签：16-18px，bold
- 描述：16-20px

**HTML骨架（横向）：**
```html
<div style="padding:80px 120px;">
  <div style="font-size:36px; font-weight:700; margin-bottom:64px;">{{时间线标题}}</div>
  <div style="position:relative; display:flex; justify-content:space-between; align-items:flex-start; padding-top:40px;">
    <!-- 中轴线 -->
    <div style="position:absolute; top:40px; left:0; right:0; height:2px; background:#E0E0E0;"></div>
    <!-- 节点 -->
    <div style="display:flex; flex-direction:column; align-items:center; width:200px;">
      <div style="width:16px; height:16px; border-radius:50%; background:var(--primary); margin-bottom:24px;"></div>
      <div style="font-size:18px; font-weight:700;">{{年份}}</div>
      <div style="font-size:16px; color:var(--text-secondary); margin-top:8px; text-align:center;">{{描述}}</div>
    </div>
    <!-- 重复节点 -->
  </div>
</div>
```

**常见踩坑：**
- 节点超过6个横向放不下 → 改纵向或分页
- 连线与节点不对齐 → 用绝对定位确保一致
- 文字与节点重叠 → 节点下方留够 margin

---

### 3.8 引语页 (quote)

**视觉特征：** 大字引语+出处，留白为主，装饰性引号

**布局参数：**
- 引号装饰：120-160px，opacity: 0.1，绝对定位
- 引语文字：36-44px，font-weight: 400，line-height: 1.5
- 出处：18-20px，color: var(--text-secondary)
- 上下左右：大留白（至少120px）

**HTML骨架：**
```html
<div style="display:flex; flex-direction:column; justify-content:center; align-items:center; height:100%; padding:120px 200px; position:relative;">
  <div style="position:absolute; top:80px; left:120px; font-size:140px; opacity:0.1; font-family:Georgia,serif;">"</div>
  <div style="font-size:40px; font-weight:400; line-height:1.5; text-align:center; max-width:80%;">{{引语内容}}</div>
  <div style="font-size:18px; color:var(--text-secondary); margin-top:40px;">—— {{出处}}</div>
</div>
```

**常见踩坑：**
- 引语过长 → 截断或换页，不要缩小字号到28以下
- 装饰引号遮挡文字 → 调低opacity或偏移位置
- 留白不够 → 这是最需要呼吸感的页面类型

---

### 3.9 图片页 (image)

**视觉特征：** 全出血图 或 分栏图文混排

**布局参数：**
- 全出血：图片100%宽高，文字覆盖（加半透明遮罩）
- 左图右文：图60% + 文40%
- 上图下文：图60%高 + 文40%高
- 图片文字间距：40-60px

**HTML骨架（左图右文）：**
```html
<div style="display:flex; height:100%;">
  <div style="flex:1.5; overflow:hidden;">
    <img src="{{IMAGE_URL}}" style="width:100%; height:100%; object-fit:cover;" />
  </div>
  <div style="flex:1; display:flex; flex-direction:column; justify-content:center; padding:60px 80px;">
    <div style="font-size:32px; font-weight:700; margin-bottom:24px;">{{标题}}</div>
    <div style="font-size:20px; color:var(--text-secondary); line-height:1.6;">{{描述文字}}</div>
  </div>
</div>
```

**常见踩坑：**
- 图片加载失败 → 设 `background-color` 兜底
- 图片比例不对 → 用 `object-fit: cover`
- 全出血图文字不可读 → 加半透明深色遮罩层

---

### 3.10 团队页 (team)

**视觉特征：** 头像网格+姓名+职位，2-4列排列

**布局参数：**
- 头像：120-140px圆形
- 姓名：20-22px，font-weight: 600
- 职位：16-18px，color: var(--text-secondary)
- 卡片间距：32-40px
- 列数：3-4列（6-8人），2列（4人以内）

**HTML骨架：**
```html
<div style="padding:80px 120px;">
  <div style="font-size:36px; font-weight:700; margin-bottom:48px;">{{团队标题}}</div>
  <div style="display:flex; flex-wrap:wrap; gap:40px; justify-content:center;">
    <div style="display:flex; flex-direction:column; align-items:center; width:200px;">
      <div style="width:120px; height:120px; border-radius:50%; background:#E0E0E0; margin-bottom:16px; overflow:hidden;">
        <img src="{{AVATAR_URL}}" style="width:100%; height:100%; object-fit:cover;" />
      </div>
      <div style="font-size:20px; font-weight:600;">{{姓名}}</div>
      <div style="font-size:16px; color:var(--text-secondary); margin-top:4px;">{{职位}}</div>
    </div>
    <!-- 重复每人 -->
  </div>
</div>
```

**常见踩坑：**
- 头像非正方形变形 → 必须 `border-radius:50%` + `object-fit:cover`
- 人数太多一页放不下 → 分页或缩小字号
- 头像占位空白 → 设默认背景色兜底

---

### 3.11 总结页 (summary)

**视觉特征：** 核心结论提炼，3-5条，简洁有力，视觉权重一致

**布局参数：**
- 结论数：3-5条
- 编号：24px，var(--primary)
- 结论文字：24-28px，font-weight: 500
- 行间距：48-56px
- 可选：左侧竖线装饰

**HTML骨架：**
```html
<div style="display:flex; flex-direction:column; justify-content:center; padding:80px 160px;">
  <div style="font-size:36px; font-weight:700; margin-bottom:48px;">核心总结</div>
  <div style="display:flex; align-items:flex-start; margin-bottom:40px;">
    <div style="width:4px; height:32px; background:var(--primary); border-radius:2px; margin-right:20px; flex-shrink:0; margin-top:4px;"></div>
    <div style="font-size:26px; font-weight:500; line-height:1.4;">{{结论1}}</div>
  </div>
  <!-- 重复每条 -->
</div>
```

**常见踩坑：**
- 结论超过5条 → 强制精简，这不是列表页
- 结论太长 → 每条不超过20字（中文）
- 无视觉重点 → 可用编号圆或竖线标记

---

### 3.12 结束页 (ending)

**视觉特征：** 感谢+联系方式，风格呼应封面，极简

**布局参数：**
- "谢谢" / "Thank You"：56-72px，font-weight: 700
- 联系方式：18-20px，color: var(--text-secondary)
- 品牌标识：与封面一致（位置、大小）
- 背景：与封面呼应（色块/图片/纯色）

**HTML骨架：**
```html
<div style="display:flex; flex-direction:column; justify-content:center; align-items:center; height:100%; background:var(--primary);">
  <div style="font-size:64px; font-weight:700; color:#fff;">谢谢</div>
  <div style="font-size:20px; color:rgba(255,255,255,0.7); margin-top:32px;">{{联系方式}}</div>
  <div style="position:absolute; bottom:40px; right:120px;"><!-- logo，同封面 --></div>
</div>
```

**常见踩坑：**
- 与封面风格割裂 → 复用封面配色/背景/字体
- 联系方式堆太多 → 最多3行（邮箱+电话+网站）
- 忘记品牌标识 → 结束页也必须有

---

## 4. html2pptx 4条硬约束

PPTX导出时（通过 pptxgenjs），HTML 必须满足以下约束。**违反任何一条都会导致导出失败或排版错乱。**

| # | 约束 | 正确 | 错误 |
|---|------|------|------|
| 1 | 不用CSS Grid | `display: flex` / `position: absolute` | `display: grid` / `grid-template-columns` |
| 2 | 字体大小用px | `font-size: 24px` | `font-size: 1.5rem` / `font-size: 1.2em` |
| 3 | 文本块独立div | `<div>标题</div><div>内容</div>` | `<p><span>标题</span><span>内容</span></p>` |
| 4 | 颜色用#hex | `color: #FF6B35` / `background: #1A1A2E` | `color: rgb(255,107,53)` / `color: hsl(18,100%,60%)` |

**额外注意：**
- 转换比例：**1px = 1pt**（在pptxgenjs中）
- 避免使用CSS变量作为颜色值传给pptxgenjs → 解析成#hex再传入
- 避免使用伪元素 `::before` / `::after` 做关键内容 → pptxgenjs无法渲染伪元素
- SVG图表无法直接转PPTX → 改用pptxgenjs原生图表API，或导出为图片后插入

---

## 5. ≥5页Deck的Showcase流程

**核心原则：** 先做2页showcase定grammar，确认后再批量推全部页面。避免推完全部才发现风格不一致。

### 步骤

```
1. 分析内容 → 确定页面类型清单
2. 选showcase页面
   ├─ 封面页（必选，定基调）
   └─ 1个最有代表性的内容页（bullets/data/comparison等）
3. 生成showcase HTML
4. Canvas present 预览 → 展示给用户确认
5. 确认grammar要素：
   ├─ 字号层级（标题/副标题/正文/辅助）
   ├─ 色板（primary/accent/中性色）
   ├─ 间距节奏（padding/margin/gap）
   └─ 组件风格（圆角/阴影/边框）
6. 用户确认 → 批量生成全部页面
7. 逐页present → 最终确认
```

### Grammar确认清单

生成showcase后，向用户确认以下要素（可一次问完）：

- **字号层级**：标题 ≈ 36-40px / 副标题 ≈ 24-28px / 正文 ≈ 20-24px / 辅助 ≈ 16-18px
- **色板**：primary / accent / bg / text / text-secondary
- **间距**：页面内边距 / 元素间距 / 段落间距
- **组件风格**：圆角(0/8/12px) / 阴影(none/subtle) / 边框(none/1px)

### 如果用户不满意

- 调整grammar → 重新生成showcase → 再次确认
- **不要**在grammar未确认时批量生成

---

## 6. 品牌套壳后处理

### 工作方式

```
输入：标准PPTX文件（任何风格）
  ↓
处理：套用自定义品牌母版（用户提供 brand-template/template.pptx）
  ├─ 背景 → 替换为品牌背景
  ├─ Logo → 插入品牌 logo（右上角或页脚）
  └─ 页脚 → 添加品牌页脚文字/页码
  ↓
输出：带品牌皮肤的PPTX
```

### 触发条件

用户说出以下任一关键词时触发后处理：
- "品牌版"
- "正式版"
- "套壳"

### 执行流程

```
1. 先生成标准PPTX（正常流程）
2. html2pptx.py 通过 brand-template/ 下的自定义模板套壳
3. 展示品牌版给用户
```

### 注意事项

- 套壳只处理母版层，**不修改内容**（文字/图表/布局保持原样）
- 套壳后内容可能被母版元素遮挡 → 检查边距是否够大
- 如果用户要求完全自定义品牌风格 → 应在HTML阶段就使用品牌色板，不要依赖后处理

---

## 7. PPT设计速查

| 规则 | 数值 |
|------|------|
| 画布比例 | 16:9 固定 |
| 画布像素 | 1920 × 1080 px |
| 最小正文字号 | 24px（投影场景建议 28px+） |
| 标题字号 | 36-72px（按页面类型） |
| 每页字数上限 | 40字（中文）/ 60词（英文） |
| 色彩规则 | 1主色 + 1accent + 中性色，有彩色不超过3种 |
| 行距 | 1.3-1.5 倍字号 |
| 页面内边距 | 最少 60-80px，推荐 80-120px |
| 元素间距 | 32-64px |
| 圆角 | 8-12px（卡片/按钮），0px（全出血图） |
| 字体 | "PingFang SC", "Microsoft YaHei", sans-serif |

### 字号层级速查

| 用途 | 字号 | font-weight |
|------|------|-------------|
| 封面大标题 | 56-72px | 700 |
| 页面标题 | 36-40px | 700 |
| 章节分隔标题 | 48-56px | 700 |
| 副标题 | 24-28px | 400-600 |
| 正文/要点 | 20-24px | 400-500 |
| 辅助文字 | 16-18px | 400 |
| 大数字 | 72-96px | 700 |
| 页脚/标注 | 14-16px | 400 |

### 色板模板

**商务蓝（默认）：**
```css
--primary: #2D5AF0;
--accent: #FF6B35;
--bg: #FFFFFF;
--bg-alt: #F7F8FC;
--text: #1A1A2E;
--text-secondary: #666666;
--border: #E0E0E0;
```

**科技深色：**
```css
--primary: #00D4FF;
--accent: #7B61FF;
--bg: #0F0F1A;
--bg-alt: #1A1A2E;
--text: #FFFFFF;
--text-secondary: #999999;
--border: #333355;
```

**暖色学术：**
```css
--primary: #C8553D;
--accent: #F28F3B;
--bg: #FFF8F0;
--bg-alt: #F5EDE4;
--text: #2D2424;
--text-secondary: #7A6B6B;
--border: #E0D5CC;
```
