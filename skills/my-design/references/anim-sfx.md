# anim-sfx.md — 动画Demo专项参考文档

> my-design skill 专用 | 动画设计 + 视频导出 + 音效设计 | 面向Agent使用

---

## 1. 动画架构（4层递进，从轻到重）

| 层级 | 方案 | 适用场景 | 复杂度 |
|------|------|----------|--------|
| L1 | CSS transitions/animations | 80%微交互：hover、fade、slide、pulse | ★☆☆☆ |
| L2 | React state + setTimeout/rAF | 简单帧动画、事件驱动、逐步揭示 | ★★☆☆ |
| L3 | 自定义 useTime + Easing + interpolate | 时间轴驱动的完整动画场景、多段编排 | ★★★☆ |
| L4 | Popmotion CDN（Fallback） | 前三层确实不够时：弹性物理、拖拽、复杂编排 | ★★★★ |

### 🚫 禁止使用

- **Framer Motion** — bundle 大（~30KB gzip），React inline Babel 不支持 JSX runtime
- **GSAP** — 商业许可风险，全局污染，与 React 生命周期冲突
- **Lottie** — 依赖 lottie-web（~250KB），JSON 资源体积大，渲染不一致

### L1: CSS transitions/animations 示例

```css
/* 微交互：hover 淡入 */
.card { transition: opacity 0.3s ease, transform 0.3s ease; }
.card:hover { opacity: 1; transform: translateY(-4px); }

/* 循环脉冲 */
@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
.pulse { animation: pulse 2s ease-in-out infinite; }
```

### L2: React state + setTimeout/rAF 示例

```jsx
function StepReveal({ steps }) {
  const [visible, setVisible] = React.useState(0);
  React.useEffect(() => {
    if (visible < steps.length) {
      const t = setTimeout(() => setVisible(v => v + 1), 800);
      return () => clearTimeout(t);
    }
  }, [visible, steps.length]);
  return steps.slice(0, visible).map((s, i) => <div key={i}>{s}</div>);
}
```

### L3 & L4: 见下方 Stage + Sprite 时间轴模型

---

## 2. Stage + Sprite 时间轴模型

### 概念

| 概念 | 职责 |
|------|------|
| **Stage** | 全局时间轴控制器：play/pause/scrubber/loop，管理总时长 |
| **Sprite** | 时间片段：start/duration/easing/内容，在时间轴上占一段 |
| **useTime** | React Hook：获取当前时间，驱动动画重渲染 |
| **interpolate** | 关键帧插值函数：`interpolate(t, keyframes, easing)` |
| **Easing** | 缓动函数库：easeInOutCubic / easeOutExpo / easeInOutQuart 等 |

### 完整 JS 实现骨架（可直接复制）

```jsx
// ===== Easing 库 =====
const Easing = {
  linear: t => t,
  easeInQuad: t => t * t,
  easeOutQuad: t => t * (2 - t),
  easeInOutQuad: t => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t,
  easeInCubic: t => t * t * t,
  easeOutCubic: t => (--t) * t * t + 1,
  easeInOutCubic: t => t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1,
  easeOutExpo: t => t === 1 ? 1 : 1 - Math.pow(2, -10 * t),
  easeInOutQuart: t => t < 0.5 ? 8 * t * t * t * t : 1 - 8 * (--t) * t * t * t,
  easeOutBack: t => { const c1 = 1.70158; const c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
};

// ===== interpolate 关键帧插值 =====
// keyframes: [{ time: 0, value: 0 }, { time: 0.5, value: 100 }, { time: 1, value: 80 }]
function interpolate(progress, keyframes, easing = Easing.linear) {
  if (!keyframes || keyframes.length === 0) return 0;
  if (keyframes.length === 1) return keyframes[0].value;

  const p = Math.max(0, Math.min(1, easing(progress)));

  // 找到当前所在区间
  let i = 0;
  for (i = 0; i < keyframes.length - 1; i++) {
    if (p <= keyframes[i + 1].time) break;
  }

  const from = keyframes[i];
  const to = keyframes[Math.min(i + 1, keyframes.length - 1)];
  const segLen = to.time - from.time;
  const segProgress = segLen > 0 ? (p - from.time) / segLen : 1;

  // 线性插值（value 可以是数字或对象 {x, y, ...}）
  if (typeof from.value === 'number') {
    return from.value + (to.value - from.value) * segProgress;
  }
  // 对象插值
  const result = {};
  for (const k of Object.keys(from.value)) {
    result[k] = from.value[k] + (to.value[k] - from.value[k]) * segProgress;
  }
  return result;
}

// ===== Sprite 时间片段 =====
class Sprite {
  constructor({ start, duration, easing = Easing.linear, render }) {
    this.start = start;       // 开始时间（秒）
    this.duration = duration; // 持续时间（秒）
    this.easing = easing;     // 缓动函数
    this.render = render;     // (localProgress, globalTime) => ReactNode
  }

  // 当前帧的本地进度 [0, 1]，未开始返回 -1，已结束返回 2
  progress(globalTime) {
    const end = this.start + this.duration;
    if (globalTime < this.start) return -1;
    if (globalTime > end) return 2;
    return (globalTime - this.start) / this.duration;
  }

  // 归一化进度 [0, 1]，含 easing
  easedProgress(globalTime) {
    const p = this.progress(globalTime);
    if (p < 0 || p > 1) return p;
    return this.easing(p);
  }
}

// ===== Stage 全局时间轴 =====
class Stage {
  constructor({ duration, loop = true, sprites = [] }) {
    this.duration = duration;
    this.loop = loop;
    this.sprites = sprites;
    this.time = 0;
    this.playing = false;
    this._rafId = null;
    this._lastTs = null;
    this._listeners = new Set();
  }

  // 播放控制
  play() {
    if (this.playing) return;
    this.playing = true;
    // 录制模式下不循环
    if (typeof window !== 'undefined' && window.__recording === true) {
      this.loop = false;
    }
    this._lastTs = performance.now();
    this._tick();
  }

  pause() {
    this.playing = false;
    if (this._rafId) cancelAnimationFrame(this._rafId);
  }

  seek(time) {
    this.time = Math.max(0, Math.min(time, this.duration));
    this._emit();
  }

  // 订阅时间更新
  subscribe(fn) {
    this._listeners.add(fn);
    return () => this._listeners.delete(fn);
  }

  _emit() {
    for (const fn of this._listeners) fn(this.time);
  }

  _tick = () => {
    if (!this.playing) return;
    const now = performance.now();
    const dt = (now - this._lastTs) / 1000;
    this._lastTs = now;
    this.time += dt;

    if (this.time >= this.duration) {
      if (this.loop) {
        this.time = this.time % this.duration;
      } else {
        this.time = this.duration;
        this.playing = false;
        this._emit();
        return;
      }
    }

    this._emit();
    this._rafId = requestAnimationFrame(this._tick);
  };
}

// ===== useTime Hook =====
function useTime(stage) {
  const [time, setTime] = React.useState(stage.time);
  React.useEffect(() => {
    setTime(stage.time);
    return stage.subscribe(t => setTime(t));
  }, [stage]);
  return time;
}

// ===== 使用示例 =====
// const stage = new Stage({
//   duration: 10,
//   loop: true,
//   sprites: [
//     new Sprite({ start: 0, duration: 2, easing: Easing.easeOutExpo,
//       render: (p) => <div style={{ opacity: p, transform: `translateY(${(1-p)*40}px)` }}>Hello</div>
//     }),
//     new Sprite({ start: 2, duration: 3, easing: Easing.easeInOutCubic,
//       render: (p) => <div style={{ transform: `scale(${interpolate(p, [{time:0,value:0.8},{time:1,value:1}])})` }}>World</div>
//     }),
//   ],
// });
//
// function AnimationPlayer() {
//   const time = useTime(stage);
//   return (
//     <div>
//       {stage.sprites.map((sprite, i) => {
//         const p = sprite.easedProgress(time);
//         if (p < 0 || p > 1) return null;
//         return <React.Fragment key={i}>{sprite.render(p, time)}</React.Fragment>;
//       })}
//     </div>
//   );
// }
```

### L4 Fallback: Popmotion CDN

```html
<!-- 仅在 L1-L3 不够时引入 -->
<script src="https://cdn.jsdelivr.net/npm/popmotion@11/dist/popmotion.min.js"></script>
<script>
  const { spring, animate } = popmotion;
  // 弹性物理动画
  spring({ from: 0, to: 100, stiffness: 200, damping: 20 })
    .start(v => { /* 更新状态 */ });
</script>
```

---

## 3. 动画设计避坑（14条）

| # | 规则 | 为什么 |
|---|------|--------|
| 1 | **不要在画面内画底部进度条/时间码** | Stage 自带 scrubber 控件，画面内的进度条与控件撞车，且导出视频后进度条成为画面永久内容无法去除 |
| 2 | **第一帧必须设 `window.__ready=true`** | Playwright 录制脚本等待此信号才开始录制，否则会录到空白/加载中的画面 |
| 3 | **检测 `window.__recording===true` 时强制 `loop=false`** | 录制需要动画播放一次后自然停止；循环播放会导致录制永远不结束或截断 |
| 4 | **固定尺寸内容必须自实现 JS 缩放 + letterbox** | CSS `transform: scale()` 在不同视口下无法正确 letterbox；自实现缩放可保证画面比例不变形 |
| 5 | **不要用 `scrollIntoView`** | 录制环境中滚动行为不可控，可能导致画面跳动或超出录制区域 |
| 6 | **避免在动画元素上用 `will-change`** | 浏览器为 `will-change` 元素分配独立 GPU 图层，动画结束后不释放，长时间运行导致 GPU 内存泄露，尤其录制场景 |
| 7 | **canvas 动画用 `requestAnimationFrame` 不用 `setInterval`** | `setInterval` 无法与屏幕刷新率同步，导致丢帧和卡顿；rAF 自动适配刷新率且标签页不可见时自动暂停 |
| 8 | **图片预加载：`Image()` 对象 + `onload` 回调后再开始动画** | 图片未加载完成时动画已经开始，会出现闪烁/占位符；预加载确保第一帧就是完整画面 |
| 9 | **渐变色动画用 `@keyframes` + `background-position` 而非 JS 逐帧更新** | JS 逐帧修改 `background` 属性触发样式重计算（style recalc）；CSS 动画走合成线程，性能高 10x+ |
| 10 | **文字动画优先 `transform`/`opacity`（合成层），不触发布局 reflow** | `transform` 和 `opacity` 只触发 composite 不触发 layout+paint；修改 `width`/`height`/`top`/`left` 会 reflow 整个渲染树 |
| 11 | **多段动画用 Sprite 偏移量而非嵌套 `setTimeout`** | 嵌套 `setTimeout` 时间漂移累积，且不可 scrub/seek；Sprite 模型时间绝对定位，可任意跳转 |
| 12 | **3D 变换加 `perspective` 到父容器** | `perspective` 设在变换元素自身会导致每个元素独立消失点；设在父容器保证统一透视，3D 场景才协调 |
| 13 | **导出前测试：所有动画元素 `overflow:hidden` 防截断** | 动画元素在运动中可能溢出容器边界，录制区域固定导致截断；`overflow:hidden` 确保画面干净 |
| 14 | **音频和画面分离录制，后期合成** | 浏览器录制视频不含音频；且音频播放时机受网络/缓冲影响，音画同步不可靠；后期用 ffmpeg 精确合成 |

---

## 4. 视频导出管线

### 流程总览

```
HTML → Playwright录制25fps MP4（中间产物）
    → convert-formats.sh 派生60fps MP4 + palette优化GIF
    → add-music.sh 加BGM + SFX
    → 最终成品MP4
```

### render-video.js 核心逻辑

```javascript
const { chromium } = require('playwright');

async function renderVideo(htmlPath, outputPath) {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // 1. 设置视口（与 HTML 设计尺寸一致）
  await page.setViewportSize({ width: 1920, height: 1080 });

  // 2. 打开 HTML
  await page.goto(`file://${htmlPath}`);

  // 3. 等待 window.__ready === true
  await page.waitForFunction('window.__ready === true', { timeout: 30000 });

  // 4. 读取时长
  const duration = await page.evaluate(() => {
    const el = document.documentElement;
    return parseFloat(el.getAttribute('data-duration')) || 10;
  });

  // 5. 进入录制模式
  await page.evaluate(() => { window.__recording = true; });

  // 6. 开始录制
  await page.video.startRecording({ path: outputPath });

  // 7. 等待动画播放完毕
  await page.waitForTimeout(duration * 1000 + 200); // +200ms 余量

  // 8. 停止录制
  const videoPath = await page.video.stopRecording();

  await browser.close();
  return videoPath;
}

// CLI 入口
const htmlPath = process.argv[2];
const outputPath = process.argv[3] || 'output/raw.mp4';
renderVideo(htmlPath, outputPath).then(p => console.log('Done:', p));
```

### HTML 模板约定

```html
<!DOCTYPE html>
<html data-duration="10">
<head>
  <meta charset="UTF-8">
  <style>
    /* 1920x1080 设计稿 */
    body { margin: 0; width: 1920px; height: 1080px; overflow: hidden; }
  </style>
</head>
<body>
  <div id="root"></div>
  <script>
    // 动画初始化...
    // 所有资源加载完成后：
    window.__ready = true;
  </script>
</body>
</html>
```

### convert-formats.sh — 格式转换

```bash
#!/bin/bash
set -e
INPUT="$1"  # raw.mp4 (25fps)
BASENAME="${INPUT%.*}"

# 60fps 插帧 MP4
ffmpeg -y -i "$INPUT" \
  -vf "minterpolate='mi_mode=mci:mc_mode=aobmc:vsbmc=1:fps=60'" \
  -c:v libx264 -preset medium -crf 18 \
  "${BASENAME}_60fps.mp4"

# Palette 优化 GIF
ffmpeg -y -i "$INPUT" \
  -vf "fps=15,scale=960:-1:flags=lanczos,palettegen" \
  /tmp/palette.png

ffmpeg -y -i "$INPUT" -i /tmp/palette.png \
  -filter_complex "fps=15,scale=960:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3" \
  "${BASENAME}.gif"

echo "✅ Converted: ${BASENAME}_60fps.mp4, ${BASENAME}.gif"
```

### add-music.sh — 音轨合成

```bash
#!/bin/bash
set -e
VIDEO="$1"     # 60fps.mp4
BGM="$2"       # 背景音乐
SFX_DIR="$3"   # SFX 目录（可选）
OUTPUT="${VIDEO%.*}_final.mp4"

# 基础：加 BGM（-shortest 以视频时长为准）
if [ -z "$SFX_DIR" ] || [ -z "$(ls -A "$SFX_DIR" 2>/dev/null)" ]; then
  ffmpeg -y -i "$VIDEO" -i "$BGM" \
    -c:v copy -c:a aac -b:a 192k \
    -shortest \
    "$OUTPUT"
else
  # 有 SFX：先混音再合成
  # 生成 SFX 混音轨道（叠加到 BGM）
  SFX_FILTER=$(find "$SFX_DIR" -name '*.mp3' -o -name '*.wav' | \
    while read f; do echo -n "-i '$f' "; done)

  # 简单双轨合成：BGM + 一个 SFX mix
  ffmpeg -y -i "$VIDEO" -i "$BGM" \
    -filter_complex "[1:a]volume=0.3[bgm];[bgm]amix=inputs=1:duration=first[aout]" \
    -map 0:v -map "[aout]" \
    -c:v copy -c:a aac -b:a 192k \
    -shortest \
    "$OUTPUT"
fi

echo "✅ Final: $OUTPUT"
```

---

## 5. 音效设计规范

### BGM + SFX 双轨制

| 轨道 | 职责 | 频段 | 音量 |
|------|------|------|------|
| **BGM** | 低频铺底，营造氛围 | 中低频（200Hz-2kHz 为主） | -15dB ~ -10dB（安静背景） |
| **SFX** | 高频点睛，强化关键瞬间 | 中高频（2kHz-8kHz 为主） | -6dB ~ 0dB（清晰突出） |

### 6 首场景化 BGM

| 编号 | 名称 | 场景 | 特征 |
|------|------|------|------|
| bgm-tech | 科技感 | 产品发布、技术 Demo | 电子音色，稳定节拍，120-140 BPM |
| bgm-tech-alt | 科技感变体 | 同上，更轻快 | 减少低频，更空灵 |
| bgm-ad | 广告感 | 营销推广、品牌宣传 | 鼓点明确，情绪递进，结尾上扬 |
| bgm-ad-alt | 广告感变体 | 同上，更柔和 | 钢琴/弦乐为主 |
| bgm-educational | 教学感 | 功能讲解、教程 | 极简，无明确节拍，不干扰旁白 |
| bgm-tutorial | 工具演示 | 操作录屏、步骤演示 | 环境音/Lo-fi，几乎感知不到 |

### 37 个预制 SFX（按类别）

| 类别 | 数量 | 命名规则 | 典型用途 |
|------|------|----------|----------|
| **whoosh** | 8 | whoosh-soft / whoosh-hard / whoosh-fast / whoosh-slow / whoosh-digital / whoosh-air / whoosh-slide / whoosh-spin | 画面转场、元素飞入飞出 |
| **click** | 6 | click-soft / click-hard / click-digital / click-tap / click-toggle / click-select | 按钮点击、选项切换 |
| **pop** | 5 | pop-small / pop-medium / pop-large / pop-bubble / pop-appear | 元素出现、气泡弹出 |
| **ding** | 5 | ding-single / ding-double / ding-bell / ding-notification / ding-success | 提示、完成、通知 |
| **rise** | 7 | rise-up / rise-sweep / rise-digital / rise-glide / rise-escalate / rise-shine / rise-power | 数值增长、进度上升、情绪走高 |
| **fall** | 6 | fall-down / fall-sweep / fall-digital / fall-glide / fall-descend / fall-fade | 数值下降、淡出、收尾 |

### 黄金配比

| 场景类型 | SFX 密度 | BGM 音量 | 示例 |
|----------|----------|----------|------|
| 发布 hero | ≈ 6 个 SFX / 10s | -12dB | 每个转场 whoosh + 每个数据点 pop + 结尾 ding |
| 功能介绍 | ≈ 3 个 SFX / 10s | -15dB | 关键操作 click + 元素出现 pop + 完成 ding |
| 工具演示 | ≈ 0-2 个 SFX / 10s | -18dB 或关闭 | 仅点击操作时 click，其余静音 |
| 教学讲解 | 0 个 SFX | 关闭 | 纯视觉 + 可能的旁白 |

### ffmpeg 双轨合成模板

```bash
# 完整版：BGM + 多个 SFX + 视频
# 假设 SFX 时间轴已确定

ffmpeg -y \
  -i video_60fps.mp4 \
  -i bgm-tech.mp3 \
  -i sfx-whoosh-soft.mp3 \
  -i sfx-pop-medium.mp3 \
  -i sfx-ding-success.mp3 \
  -filter_complex "\
    [1:a]volume=0.25,afade=t=in:d=0.5,afade=t=out:st=9.5:d=0.5[bgm]; \
    [2:a]adelay=1500|1500,volume=0.8[sfx1]; \
    [3:a]adelay=3200|3200,volume=0.7[sfx2]; \
    [4:a]adelay=8500|8500,volume=0.6[sfx3]; \
    [bgm][sfx1][sfx2][sfx3]amix=inputs=4:duration=first:normalize=0[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -b:a 192k \
  -shortest \
  output_final.mp4

# 参数说明：
# adelay=1500|1500  — SFX 延迟 1500ms（左右声道）
# volume=0.8        — SFX 音量 80%
# normalize=0       — 不自动归一化（保持各轨音量比例）
# afade             — BGM 淡入淡出
```

---

## 6. 交付前验证

### ✅ 验证清单

```bash
# 1. 确认有 audio stream
ffprobe -v error -select_streams a -show_entries stream=codec_name,channels,sample_rate -of csv=p=0 output_final.mp4
# 预期输出: aac,2,44100  (编码格式, 声道数, 采样率)

# 2. 确认视频帧率达标
ffprobe -v error -select_streams v -show_entries stream=r_frame_rate,width,height -of csv=p=0 output_final.mp4
# 预期输出: 60/1,1920,1080  或  25/1,1920,1080

# 3. 确认总时长
ffprobe -v error -show_entries format=duration -of csv=p=0 output_final.mp4
# 预期输出: 10.04  (秒)

# 4. 文件大小合理
ls -lh output_final.mp4
# 10s 1080p60 通常 5-15MB

# 5. 快速抽帧检查
ffmpeg -y -i output_final.mp4 -vf "select=eq(n\,0)" -frames:v 1 frame_first.png
ffmpeg -y -i output_final.mp4 -vf "select=eq(n\,149)" -frames:v 1 frame_mid.png
ffmpeg -y -i output_final.mp4 -sseof -0.1 -frames:v 1 frame_last.png
```

### 🖥️ 浏览器预览

1. 用 Playwright 之外的方式打开 HTML（双击或本地服务器）
2. **完整播放一遍**，不跳过
3. 检查项：
   - [ ] 无闪烁/空白帧
   - [ ] 所有元素在动画结束后位置正确
   - [ ] 文字无截断（`overflow:hidden` 生效）
   - [ ] 缩放后 letterbox 正确（非全屏拉伸）
   - [ ] `window.__ready` 在首帧内容渲染后设为 true

### 📊 帧率要求

| 用途 | 最低帧率 | 推荐帧率 | 说明 |
|------|----------|----------|------|
| 内部评审 | 25fps | 25fps | Playwright 原始录制 |
| 外部交付 | 25fps | 60fps | `minterpolate` 插帧 |
| GIF 预览 | 10fps | 15fps | 文件体积优先 |
| 实时交互 | 30fps | 60fps | 用户可操作的 Demo |

---

## 附录：快速模板

### 最小可录制 HTML

```html
<!DOCTYPE html>
<html data-duration="5">
<head>
  <meta charset="UTF-8">
  <style>
    * { margin: 0; box-sizing: border-box; }
    body { width: 1920px; height: 1080px; overflow: hidden; background: #0a0a0a; }
    .fade-in { opacity: 0; animation: fadeIn 1s ease forwards; }
    @keyframes fadeIn { to { opacity: 1; } }
  </style>
</head>
<body>
  <div class="fade-in" style="color:#fff;font-size:64px;padding:40px;">Hello, Animation!</div>
  <script>
    // 图片预加载示例
    const imgs = [];
    function preload(src) {
      return new Promise(resolve => {
        const img = new Image();
        img.onload = resolve;
        img.onerror = resolve; // 即使失败也继续
        img.src = src;
        imgs.push(img);
      });
    }

    async function init() {
      // await preload('hero.png');
      // 动画初始化...
      window.__ready = true;
    }
    init();
  </script>
</body>
</html>
```

### JS 缩放 + Letterbox

```javascript
function fitScreen(designW, designH) {
  const scale = Math.min(
    window.innerWidth / designW,
    window.innerHeight / designH
  );
  const el = document.getElementById('root');
  el.style.transform = `scale(${scale})`;
  el.style.transformOrigin = 'top left';
  el.style.position = 'absolute';
  el.style.left = ((window.innerWidth - designW * scale) / 2) + 'px';
  el.style.top = ((window.innerHeight - designH * scale) / 2) + 'px';
}

window.addEventListener('resize', () => fitScreen(1920, 1080));
fitScreen(1920, 1080);
```
