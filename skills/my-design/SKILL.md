---
name: my-design
description: |
  打字，回车，一份能交付的设计。支持PPT幻灯片、交互原型、动画Demo、网页/信息图。
  触发词：做PPT、做设计、画原型、做动画、做网页、做信息图、design、slide、prototype、animation、infographic、
  画一页、做一张、生成幻灯片、生成原型、生成动画、landing page、海报、banner、dashboard、
  UI设计、视觉设计、品牌设计、排版设计
model: inherit
license: MIT
metadata:
  version: "1.0.0"
  category: design
  type: code-generator
  author: pkulyn
---

# my-design — 打字，回车，交付。

## 核心哲学（优先级从高到低）

### #0 事实验证先于假设
**为什么**：AI最擅长编造看似合理的细节——产品名、配色、logo位置，错一个就全废。涉及具体品牌/产品/技术时，必须先WebSearch验证，再动手画。凭空假设 = 技术债。

### #1 从 existing context 出发，不凭空画
**为什么**：品牌有规范、产品有历史、用户有预期。从零画出来的东西要么违反品牌约束，要么跟现有体系割裂。先找已有的，再补缺的。

**§1.a 核心资产协议（5步硬流程，涉及品牌时必走）：**
1. **问** — 问用户有无品牌指南/设计稿/参考链接
2. **搜** — 在飞书文档/Wiki/云空间搜索品牌资产（关键词：品牌、VI、设计规范、color、logo）
3. **下载** — 下载找到的规范文档/图片到本地
4. **验证+提取** — 读取内容，提取色彩/字型/间距/圆角/阴影/动效参数
5. **固化** — 写入 `brand-spec.md`，后续所有设计以此为准

### #2 Junior Designer 模式：先展示假设 + placeholder，再执行
**为什么**：设计最怕"黑箱出图"——你花20分钟填完所有细节，用户一看方向全错。先展示你的假设和placeholder，让用户校准方向，再投入细节。10秒对齐 > 20分钟返工。

### #3 给 variations，不给"最终答案"
**为什么**：设计是探索，不是填空。3个跨维度变体（如：极简vs丰富vs大胆）比1个"完美"方案更有价值。用户从对比中知道自己要什么，比直接给答案高效10倍。

### #4 Placeholder > 烂实现
**为什么**：一个清晰的灰色方块写着"[数据图表]"，比一个比例失调、配色诡异的假图表强100倍。前者是诚实的占位，后者是误导性的垃圾。宁可空着，不要糊弄。

### #5 系统优先，不要填充
**为什么**：用Design System约束（间距8px倍数、色彩从palette取、字型3种以内）代替逐像素调整。系统化设计一致性高、修改成本低、扩展性强。手工填充=维护噩梦。

### #6 反 AI slop
**为什么**：AI生成的设计有6个致命通病，每个都在摧毁可信度。识别并消灭它们。

**要规避的核心清单：**
- ❌ 渐变滥用（到处purple→blue gradient）
- ❌ **文字渐变**（`background-clip:text` + `text-fill-color:transparent`）—— 后半段可读性极差，绝对禁止
- ❌ emoji当图标（📊📈🎯不是设计）
- ❌ 通用slogan（"赋能未来""智领创新"）
- ❌ 假数据不留痕（硬编码数字不带[placeholder]标记）
- ❌ 过度装饰（阴影套阴影、圆角套圆角）
- ❌ 对称强迫症（所有卡片等宽等高，像Excel）
- ❌ **深色背景作为默认** —— 用户已明确否定，浅色主题优先

**正向做什么：**
- ✅ 用oklch()精确控制色彩感知均匀性
- ✅ 图标用SVG或图标库（Lucide/Phosphor），不用emoji
- ✅ 文案用真实内容或明确标记的placeholder
- ✅ 留白是有意的设计决策，不是"没做完"
- ✅ 不对称布局创造视觉节奏

---

## 记忆系统（每次调用必读）

**在执行任何步骤之前，必须先读取以下文件：**
1. `MEMORY.md` — 偏好汇总、坑点摘要、迭代历史
2. `memory/style-preferences.md` — 用户确认的风格偏好及 Design Token
3. `memory/pitfalls.md` — 绝对禁止的用法和需谨慎的陷阱
4. `memory/iterations.md` — 历次迭代记录和教训
5. `memory/design-tokens.md` — 03/04 风格的完整 CSS 变量集（可直接复制使用）

**为什么**：这些记录来自真实使用中的反馈，优先级高于默认规范。比如用户已两次否定渐变文字，如果忽略记忆再次使用，就是重复犯错。

**更新规则**：每次设计交付后，将新的偏好/坑点/错误/教训追加到对应文件中。

---

## 4大场景路由表

| 场景 | 判断信号 | 参考文档 | Starter组件 |
|------|----------|----------|-------------|
| PPT幻灯片 | "PPT""幻灯片""slide""deck""汇报" | `references/ppt-slides.md` | `assets/deck_stage.js` |
| 交互原型 | "原型""prototype""app""iOS""Android""交互" | `references/prototypes.md` | `assets/ios_frame.jsx` |
| 动画Demo | "动画""animation""过渡""动效""motion" | `references/anim-sfx.md` | `assets/animations.jsx` |
| 网页/信息图 | "网页""landing""海报""dashboard""信息图""banner" | `references/web-pages.md` | `assets/design_canvas.jsx` |

**共享参考**：`references/design-styles.md` · `references/color-science.md` · `references/typography.md`

---

## 标准工作流（8步）

### Step 1: 理解需求 + 风格顾问
- 解析用户意图：场景？受众？调性？关键约束？
- **需求模糊时走Fallback**（见§设计方向顾问）
- **读取 `memory/style-preferences.md`**：优先使用用户已确认的风格（当前：03 数据叙事派 + 04 Rams 功能主义）
- 输出：一句话设计brief + 风格方向（1-3个关键词）

### Step 2: 抽核心资产
- 涉及品牌 → 走§1.a核心资产协议
- 不涉及品牌 → 从用户描述中提取视觉关键词，记录到 `design-brief.md`
- 有参考图/链接 → 下载分析，提取Design Token

### Step 3: 声明 Design System
**必须声明，用户确认后再写代码。** 声明内容：
- 色彩：主色/辅色/中性色（用oklch值）
- 字型：标题/正文/辅助（族名+字重+字号范围）
- 间距：基数（通常8px）+ 间距梯度
- 圆角：小/中/大三档
- 阴影：层级定义
- 动效：时长/缓动函数

输出格式：Design System卡片，用户确认 ✅ 后继续。

### Step 4: 构建文件夹结构
```
{project}/
├── index.html          # 入口
├── brand-spec.md       # 品牌规范（如有）
├── design-brief.md     # 设计brief
└── assets/             # 静态资源
```

### Step 5: Junior pass
- 展示assumptions清单
- 用placeholder填充不确定区域，标注`[待确认]`
- 展示reasoning：为什么选这个布局/配色
- **尽早show** — 第一个可预览版本 < 2分钟

### Step 6: Full pass
- 填充placeholder（Step 2/5确认后）
- 生成3+ variations（跨维度：色彩/布局/信息密度）
- 加Tweaks：微调参数暴露为CSS变量，方便用户"再蓝一点""间距大一点"

### Step 7: 验证
- Playwright截图检查：布局/配色/文字可读性
- 控制台检查：无报错、无警告
- 响应式检查（至少1920×1080和375×812）

### Step 8: 交付

HTML 预览确认后，**必须导出 PPTX 交付**（"一份能交付的设计"= 必须能交付）。

**使用 `scripts/html2pptx.py` 导出：**

| 模式 | 命令 | 何时用 |
|------|------|--------|
| 保真（默认） | `export(html, pptx, mode="fidelity")` | 绝大多数场景，像素级还原 |
| 可编辑 | `export(html, pptx, mode="editable", style_id="03")` | 需要在 PowerPoint 中修改文字时 |

```python
from html2pptx import export
export("slides.html", "output.pptx", mode="fidelity")   # 保真
export("slides.html", "output.pptx", mode="editable")   # 可编辑
```

- 保真模式：截图→图片嵌入，视觉 100% 还原（图表/动画/特殊排版无忧）
- 可编辑模式：解析 HTML→原生 PPTX 元素，文字可编辑（图表页需保真补图）
- 涉及品牌套壳 → 先 html2pptx 保真导出，再可选品牌模板套壳（用户提供自定义 brand-template）
- 可选 PDF 导出（Playwright PDF）

---

## 设计方向顾问（Fallback模式）

用户需求模糊时，从5大流派中推荐3个差异化方向：

| 流派 | 代表哲学 | 关键词 |
|------|----------|--------|
| 瑞士国际 | 网格、无衬线、理性 | 精确、秩序、信息密度 |
| 日式极简 | 留白、质感、侘寂 | 透气、自然、细节 |
| 荷兰风格派 | 几何、原色、非对称 | 大胆、对比、结构 |
| 苹果Human Interface | 圆角、层次、动效 | 温暖、直觉、流畅 |
| 新粗野主义 | 大字、高对比、无装饰 | 直接、冲击、反装饰 |

**操作**：选3个跨流派方向，并行生成3个迷你Demo（同内容，不同视觉语言），让用户选方向。

---

## 技术规范

### 工具脚本（`scripts/`）

| 脚本 | 用途 |
|------|------|
| `shot2send.py` | 截图+发送飞书一步到位 |
| `srv.py` | HTTP 静态服务器（自动端口、自动清理） |
| `batch_shot.py` | 批量截图（断点续传+重试） |
| `charts.py` | 风格化图表生成（柱状/折线/sparkline） |
| `html2pptx.py` | HTML→PPTX 双模导出（保真/可编辑+品牌套壳） |
| `doc2md.py` | PDF/DOCX/URL → Markdown 内容解析 |

用法：`sys.path.insert(0, 'skills/my-design/scripts'); from shot2send import shot_and_send`

### React + Babel Inline
```html
<script src="https://unpkg.com/react@18.2.0/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18.2.0/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/@babel/standalone@7.24.0/babel.min.js"></script>
<script type="text/babel">
  // 代码写这里
</script>
```

### 3条铁律
1. **不用 `styles` 变量名** — 与Babel编译冲突，用 `sx` / `css` / `token` 代替
2. **跨文件用 `Object.assign(window, {Component})`** — Babel inline无模块系统
3. **不用 `scrollIntoView`** — 在Canvas/iframe中行为不可控，用 `scrollTop` 手动控制

### CSS 最佳实践
- 布局：Grid做骨架，Flexbox做对齐，不用float
- 色彩：`oklch()` 优先（感知均匀），fallback用hex
- 文字：`text-wrap: pretty`（浏览器优化断行），`clamp()` 做响应式字号
- 间距：8px基数梯度（8/16/24/32/48/64）
- 缩放：固定尺寸内容（如幻灯片960×540）用JS实现等比缩放，不依赖CSS transform（避免模糊）

```js
// 固定尺寸缩放模板
function useScale(designW = 960, designH = 540) {
  const [s, setS] = React.useState(1);
  React.useEffect(() => {
    const fn = () => {
      const sx = window.innerWidth / designW;
      const sy = window.innerHeight / designH;
      setS(Math.min(sx, sy, 1.5));
    };
    fn(); window.addEventListener('resize', fn);
    return () => window.removeEventListener('resize', fn);
  }, []);
  return s;
}
```

---

## Starter Components 路由表

| 组件 | 文件 | 用途 |
|------|------|------|
| 幻灯片舞台 | `assets/deck_stage.js` | PPT场景的960×540画布+翻页+缩放 |
| 幻灯片入口 | `assets/deck_index.html` | PPT场景的HTML壳 |
| 设计画布 | `assets/design_canvas.jsx` | 网页/信息图的通用画布 |
| iOS框架 | `assets/ios_frame.jsx` | 交互原型的设备框架 |
| 动画引擎 | `assets/animations.jsx` | 动画Demo的缓动+关键帧工具 |

（文件不存在时，从零构建对应能力，不报错中断。）

---

## 反 AI slop 速查表

| 检查项 | 触发词/信号 | 修正 |
|--------|------------|------|
| 渐变滥用 | 同一页面3+渐变 | 最多1个主角渐变，其余用纯色 |
| **文字渐变** | background-clip:text | **绝对禁止**，用纯色 |
| **深色背景默认** | bg:#1B2838/#000 | **默认浅色**，深色仅按需 |
| emoji当图标 | 📊📈🎯💡 | 换SVG图标或Lucide |
| 通用slogan | "赋能""引领""创新" | 用具体内容或[placeholder] |
| 假数据不留痕 | 硬编码数字无标记 | 加`[示例数据]`标注 |
| 过度装饰 | 双层阴影+双层圆角 | 减一层 |
| 对称强迫 | N个卡片全等宽 | 至少1个突破网格 |
| 紫色默认 | #6366f1 / purple-500 | 从Design System取色 |
| 字体堆砌 | 3+字族 | 最多2个字族（标题+正文） |

---

## 交付前 Checklist

- [ ] Design System已声明且用户已确认
- [ ] 无AI slop（逐项检查上表）
- [ ] **已导出 PPTX**：保真模式导出并通过 message 发送给用户
- [ ] 如用户需要可编辑版本，额外导出 editable 模式
- [ ] **无文字渐变、默认浅色背景**（检查 `memory/pitfalls.md` 禁则）
- [ ] 品牌色彩/字型与brand-spec.md一致（如有）
- [ ] Placeholder已全部替换或标注[待确认]
- [ ] 浏览器控制台0 error
- [ ] 至少1个variation供用户选择
- [ ] Tweaks参数暴露为CSS变量
- [ ] 1920×1080截图正常
- [ ] 响应式（375px宽）不崩溃
- [ ] **更新记忆**：将本次发现的偏好/坑点/错误追加到 `memory/` 对应文件

---

## 异常处理表

| 场景 | 处理 |
|------|------|
| **需求模糊** | 走Fallback模式，推荐3个差异化方向，并行生成迷你Demo |
| **用户拒绝回答风格问题** | 默认"苹果HIG"方向，标注[风格待确认]，继续Junior pass |
| **Design context矛盾**（如用户要"极简"又嫌"太空"） | 指出矛盾，给2个折中方案，不要自作主张 |
| **时间紧迫** | 跳过Step 6 variations，只做1个但标注[可迭代方向] |
| **品牌规范缺失** | 执行§1.a协议1-2步后仍无结果，用行业通用规范+标注[品牌规范待补充] |
| **技术实现不确定** | 先用placeholder+文字说明意图，不要赌一个可能失败的实现 |
| **用户要"像某产品"** | WebSearch该产品真实UI，截图分析，不凭记忆画 |
| **内容量超出画布** | 优先级排序，砍低优先级内容，标注[内容超量，已裁剪]，不压缩字号硬塞 |
