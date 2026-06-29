# 网页/信息图专项参考

面向 Agent 使用。my-design skill 生成网页、信息图、Dashboard、落地页时的设计规范与架构选型指南。

---

## 1. 网页类型与架构选型

| 类型 | 架构 | 说明 |
|------|------|------|
| 落地页/Landing | 单文件HTML | 独立交付，无框架依赖 |
| Dashboard | 单文件React | Chart.js/D3 可视化，状态管理 |
| 信息图 | 单文件HTML | 长图/固定画布，纯CSS布局 |
| 营销页 | 单文件React | 动效+交互，组件化 |
| 设计系统文档 | 多文件 | 组件库+Token，按模块拆分 |

**拆文件条件**（同 prototypes）：代码 >1000 行，或需多 agent 并行开发。

---

## 2. 响应式策略

| 页面类型 | 策略 | 说明 |
|----------|------|------|
| 落地页/营销页 | Mobile-first，3断点 | 375 / 768 / 1280 |
| Dashboard | Desktop-only（1920×1080） | 移动端做简化版 |
| 信息图 | 固定宽度 1200px | 视口自动缩放 |
| 设计系统 | 全响应式展示 | 组件在不同断点下均可预览 |

### CSS 断点

```css
@media (max-width: 767px) { /* mobile */ }
@media (min-width: 768px) and (max-width: 1279px) { /* tablet */ }
@media (min-width: 1280px) { /* desktop */ }
```

### Mobile-first 写法模板

```css
/* 默认 mobile 样式 */
.container { padding: 16px; }

@media (min-width: 768px) {
  .container { padding: 24px; }
}

@media (min-width: 1280px) {
  .container { padding: 32px; max-width: 1200px; margin: 0 auto; }
}
```

---

## 3. 信息图设计规范

### 布局

- **固定宽度** 1200px，高度随内容自然延伸
- **纵向叙事流**：标题 → 数据 → 洞察 → 结论
- 内容区左右留白 40-60px

### 色彩

- 1 个主色 + 1 个 accent + 中性色（灰阶 5 级）
- 数据系列色：主色同色系 3-5 个明度梯度，避免彩虹色

### 字号

| 元素 | 字号 | 字重 |
|------|------|------|
| 主标题 | 36-48px | 700 |
| 章节标题 | 28-32px | 600 |
| 数据标注 | 24-32px | 700 |
| 正文 | 16-18px | 400 |
| 注释 | 14px | 400 |

### 间距节奏

- Section 间距：48-64px
- 组内元素间距：16-24px
- 数据卡片内边距：24-32px

### 导出

- HTML → PNG：使用 Playwright 全页截图
- 截图命令参考：
  ```js
  await page.goto('file:///path/to/infographic.html');
  await page.screenshot({ path: 'infographic.png', fullPage: true });
  ```

---

## 4. Dashboard 设计规范

### 主题

- **深色/浅色双模式**，CSS 变量切换
- 推荐变量命名：
  ```css
  :root { --bg-primary; --bg-card; --text-primary; --text-secondary; --border; --accent; }
  [data-theme="dark"] { --bg-primary: #0f172a; ... }
  ```

### 图表

- **Chart.js 标配**：折线 / 柱状 / 饼图 / 雷达图
- **D3.js**：自定义复杂场景（桑基图、力导向图、地理热力图）
- 图表容器使用 `ResizeObserver` 实现响应式
  ```js
  const ro = new ResizeObserver(() => chart.resize());
  ro.observe(container);
  ```

### 卡片布局

- Shadow 层级 2-3 级（`box-shadow: 0 2px 8px rgba(0,0,0,0.08)`)
- 圆角 8-12px
- 卡片间距 16-24px
- CSS Grid 或 Flexbox 排列

### 数据展示原则

- **数据墨水比最大化**：删除 gridlines / 3D 效果 / 多余阴影
- 模拟数据 + 刷新动画（骨架屏 / 数字滚动）
- 关键指标突出：大字号 + accent 色

---

## 5. 落地页设计规范

### Hero Section

- 大标题（48-64px）+ 副标题 + CTA 按钮 + 视觉锚点（插图/产品截图）
- CTA 按钮：accent 色，圆角 8px，padding 12px 32px
- 首屏高度 ≥ 80vh

### 社会证明

- **真实数据 > 假 logo 墙**
- 数字指标：用户数 / 成功率 / 节省时间，配合计数动画
- 用户评价：头像 + 姓名 + 职位 + 短引言

### 交互三态

```css
.btn-cta {
  background: var(--accent);
  transition: all 0.2s ease;
}
.btn-cta:hover { filter: brightness(1.1); transform: translateY(-1px); }
.btn-cta:focus { outline: 2px solid var(--accent); outline-offset: 2px; }
.btn-cta:active { transform: translateY(0); filter: brightness(0.95); }
```

### 动效

- **入场动画**：元素淡入 + 上移（`@keyframes fadeInUp`）
- **滚动触发**：`IntersectionObserver`
  ```js
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
  }, { threshold: 0.15 });
  ```

### 表单

- 实时 validation（`:invalid` / `:valid` 伪类）
- Error state：红色边框 + 错误文案
- 成功反馈：绿色勾 + 短文案 + 可选 confetti 动效

---

## 6. Tweaks 面板规范

每个网页交付物**默认附带** Tweaks 面板，即使未明确要求。

### 位置与样式

- 右下角浮动，`position: fixed; bottom: 20px; right: 20px;`
- 标题固定 "Tweaks"
- 关闭时**完全隐藏**（`display: none`），非缩小
- 半透明背景 + backdrop-blur

### 暴露参数

| 参数 | 类型 | 默认 |
|------|------|------|
| 主题色 / accent | color picker | 按设计稿 |
| 字号基准 | slider | 16px |
| 暗色模式 | toggle | off |
| 间距密度 | select（compact/normal/relaxed）| normal |
| 变体 | select | default |

### Creative Tweaks

即使没要求，也默认加 1-2 个 creative tweak，例如：
- 渐变方向切换
- 圆角大小（sharp / medium / round）
- 动效开关
- 字体风格（modern / classic / playful）

### 实现模板

```html
<div id="tweaks-panel" style="position:fixed;bottom:20px;right:20px;z-index:9999;
  background:rgba(255,255,255,0.9);backdrop-filter:blur(12px);border-radius:12px;
  padding:16px;box-shadow:0 4px 20px rgba(0,0,0,0.15);width:260px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
    <strong>Tweaks</strong>
    <button onclick="document.getElementById('tweaks-panel').style.display='none'">✕</button>
  </div>
  <!-- tweak controls here -->
</div>
```

---

## 7. 搜索引擎友好（如页面需 SEO）

> 不适用于：内部原型 / 演示 / 信息图

### 语义 HTML

```html
<main>
  <article>
    <header>...</header>
    <section>...</section>
    <footer>...</footer>
  </article>
</main>
<nav>...</nav>
```

### Open Graph Meta Tags

```html
<meta property="og:title" content="页面标题">
<meta property="og:description" content="页面描述">
<meta property="og:image" content="https://example.com/og-image.png">
<meta property="og:type" content="website">
```

### 结构化数据（JSON-LD）

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "页面标题",
  "description": "页面描述"
}
</script>
```

---

## 8. 交付前验证清单

- [ ] 控制台 **0 error 0 warning**
- [ ] 目标断点逐一检查（375 / 768 / 1280 或 1920）
- [ ] 交互组件 3 态覆盖（hover / focus / active）
- [ ] Chart.js 图表 `ResizeObserver` 响应正常
- [ ] 无文字溢出 / 截断（`overflow: hidden` 不应是默认方案）
- [ ] Tweaks 面板可打开、可调整、可关闭
- [ ] 深色/浅色模式切换正常（Dashboard）
- [ ] 图片/图标加载失败有 fallback
