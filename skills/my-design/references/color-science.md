# 色彩科学参考文档

> 面向 Agent 使用的可执行色彩指南。中文为主，技术术语保留英文。

---

## 1. oklch 色彩系统

### 1.1 oklch vs hsl vs rgb

| 维度 | RGB | HSL | oklch |
|------|-----|-----|-------|
| 模型 | 设备相关，加色混合 | 极坐标但感知不均匀 | 感知均匀的极坐标 |
| 亮度 | 无亮度轴 | L 是相对明度，非线性 | L 是感知亮度（CIE 基础） |
| 饱和度 | 无 | S 是相对饱和度，与亮度耦合 | C 是绝对色度（chroma），独立于亮度 |
| 色相 | 无 | H 环均匀但感知不均（蓝区窄，黄区宽） | H 环感知均匀 |
| 关键优势 | 浏览器原生，兼容性最好 | 直觉好，CSS 支持广泛 | **色阶均匀、和谐色推导精确** |
| 关键劣势 | 无法直觉调色 | 蓝色区过窄，同 L 值实际亮度差异大 | 旧浏览器不支持，需 fallback |

**结论：设计推导用 oklch，最终输出同时提供 HEX + oklch 值，CSS 优先 oklch() 并带 HEX fallback。**

### 1.2 oklch() CSS 函数

```css
/* 语法 */
color: oklch(L C H / alpha);

/* L: 0~1 感知亮度 (0=纯黑, 1=纯白) */
/* C: 0~0.4+ 色度/饱和度 (0=灰色, 值越大越鲜艳) */
/* H: 0~360 色相角度 */
/* alpha: 0~1 透明度 (可省略) */

/* 示例 */
--brand: oklch(0.55 0.15 250);        /* 深蓝品牌色 */
--brand-light: oklch(0.75 0.10 250);   /* 浅一级 */
--brand-dark: oklch(0.35 0.18 250);    /* 深一级 */
```

**浏览器支持（2026 年）：**
- Chrome 111+ / Edge 111+ / Safari 15.4+ / Firefox 113+ ✅
- 覆盖率 > 95%，可直接使用，但需为旧浏览器提供 fallback

**Fallback 策略：**

```css
/* 方案 A：CSS 层叠（推荐） */
--brand: #1E3A5F;                        /* fallback HEX */
--brand: oklch(0.35 0.10 250);           /* 现代浏览器覆盖 */

/* 方案 B：@supports（更精确） */
--brand: #1E3A5F;
@supports (color: oklch(0 0 0)) {
  --brand: oklch(0.35 0.10 250);
}
```

### 1.3 用 oklch 派生和谐色

**核心原则：不凭空发明新色相，所有新色从品牌色或 oklch 和谐推导。**

给定品牌色 `oklch(L₀ C₀ H₀)`：

#### 同色相变亮度/饱和度（最常用）

```
浅一级：oklch(L₀+0.15  C₀×0.7  H₀)    -- 亮度提升，饱和度略降
深一级：oklch(L₀-0.15  C₀×1.1  H₀)    -- 亮度降低，饱和度略升
极浅：  oklch(L₀+0.30  C₀×0.4  H₀)    -- 背景用
极深：  oklch(L₀-0.25  C₀×1.2  H₀)    -- 文字用
```

#### 互补色（Complementary）

```
互补色：oklch(L₀  C₀  (H₀ + 180) % 360)
```

#### 三角色（Triadic）

```
色相1：oklch(L₀  C₀  H₀)
色相2：oklch(L₀  C₀  (H₀ + 120) % 360)
色相3：oklch(L₀  C₀  (H₀ + 240) % 360)
```

#### 类似色（Analogous）

```
色相1：oklch(L₀  C₀  H₀)
色相2：oklch(L₀  C₀  (H₀ + 30) % 360)
色相3：oklch(L₀  C₀  (H₀ - 30) % 360)
```

#### 分裂互补（Split-Complementary）

```
色相1：oklch(L₀  C₀  H₀)
色相2：oklch(L₀  C₀  (H₀ + 150) % 360)
色相3：oklch(L₀  C₀  (H₀ + 210) % 360)
```

> **实操建议**：派生后检查 C 值，若 > 0.37 可能超出 sRGB 色域，需 clamp 到 0.37 以内。

---

## 2. 5 种经典配色方案模板

### 2.1 金融权威 — 深蓝+金+白

**适用场景**：投研报告、风控演示、年度报告、机构品牌

| 角色 | HEX | oklch | 用途 |
|------|-----|-------|------|
| Primary | `#1A3A5C` | `oklch(0.30 0.08 245)` | 标题、主色块 |
| Primary Light | `#3D6B8E` | `oklch(0.50 0.08 245)` | 副标题、图标 |
| Accent Gold | `#C8A951` | `oklch(0.73 0.12 85)` | 数据高亮、CTA、关键指标 |
| Background | `#F5F6F8` | `oklch(0.97 0.005 250)` | 页面背景 |
| Text | `#1C2533` | `oklch(0.22 0.02 250)` | 正文文字 |
| White | `#FFFFFF` | `oklch(1 0 0)` | 卡片背景、留白 |

```css
:root {
  --color-primary: #1A3A5C;
  --color-primary-light: #3D6B8E;
  --color-accent: #C8A951;
  --color-bg: #F5F6F8;
  --color-text: #1C2533;
  --color-white: #FFFFFF;
}
@supports (color: oklch(0 0 0)) {
  :root {
    --color-primary: oklch(0.30 0.08 245);
    --color-primary-light: oklch(0.50 0.08 245);
    --color-accent: oklch(0.73 0.12 85);
    --color-bg: oklch(0.97 0.005 250);
    --color-text: oklch(0.22 0.02 250);
    --color-white: oklch(1 0 0);
  }
}
```

### 2.2 科技极简 — 深灰+翠绿+白

**适用场景**：产品发布、技术分享、API 文档、DevOps

| 角色 | HEX | oklch | 用途 |
|------|-----|-------|------|
| Primary | `#2D2D2D` | `oklch(0.30 0.005 150)` | 标题、深色区块 |
| Accent Green | `#00B37E` | `oklch(0.65 0.18 160)` | CTA、状态、代码高亮 |
| Accent Light | `#66D9B0` | `oklch(0.80 0.12 160)` | 次要高亮 |
| Background | `#FAFAFA` | `oklch(0.98 0.002 150)` | 页面背景 |
| Text | `#1A1A1A` | `oklch(0.20 0.005 150)` | 正文 |
| Muted | `#8C8C8C` | `oklch(0.60 0.005 150)` | 说明文字 |

```css
:root {
  --color-primary: #2D2D2D;
  --color-accent: #00B37E;
  --color-accent-light: #66D9B0;
  --color-bg: #FAFAFA;
  --color-text: #1A1A1A;
  --color-muted: #8C8C8C;
}
@supports (color: oklch(0 0 0)) {
  :root {
    --color-primary: oklch(0.30 0.005 150);
    --color-accent: oklch(0.65 0.18 160);
    --color-accent-light: oklch(0.80 0.12 160);
    --color-bg: oklch(0.98 0.002 150);
    --color-text: oklch(0.20 0.005 150);
    --color-muted: oklch(0.60 0.005 150);
  }
}
```

### 2.3 党建政务 — 红+金+白

**适用场景**：党建汇报、政务报告、红色主题、组织生活

| 角色 | HEX | oklch | 用途 |
|------|-----|-------|------|
| Primary Red | `#C41E24` | `oklch(0.50 0.20 25)` | 标题、主色块、旗帜 |
| Dark Red | `#8B1A1A` | `oklch(0.35 0.16 25)` | 深色区块、页头 |
| Accent Gold | `#D4A843` | `oklch(0.72 0.13 80)` | 徽章、装饰、高亮 |
| Background | `#FFF8F0` | `oklch(0.98 0.01 80)` | 页面背景（暖白） |
| Text | `#2B1A0E` | `oklch(0.22 0.02 60)` | 正文（暖黑） |
| White | `#FFFFFF` | `oklch(1 0 0)` | 卡片、留白 |

```css
:root {
  --color-primary: #C41E24;
  --color-primary-dark: #8B1A1A;
  --color-accent: #D4A843;
  --color-bg: #FFF8F0;
  --color-text: #2B1A0E;
  --color-white: #FFFFFF;
}
@supports (color: oklch(0 0 0)) {
  :root {
    --color-primary: oklch(0.50 0.20 25);
    --color-primary-dark: oklch(0.35 0.16 25);
    --color-accent: oklch(0.72 0.13 80);
    --color-bg: oklch(0.98 0.01 80);
    --color-text: oklch(0.22 0.02 60);
    --color-white: oklch(1 0 0);
  }
}
```

### 2.4 人文温润 — 赭石+米白+墨

**适用场景**：文化机构、教育品牌、人文专题、书刊风格

| 角色 | HEX | oklch | 用途 |
|------|-----|-------|------|
| Primary | `#8B4513` | `oklch(0.40 0.10 45)` | 标题、品牌色 |
| Warm Beige | `#F5ECD7` | `oklch(0.94 0.02 80)` | 页面背景 |
| Ink Black | `#2C1810` | `oklch(0.20 0.03 40)` | 正文文字 |
| Accent Clay | `#C67B4E` | `oklch(0.60 0.12 50)` | 高亮、按钮 |
| Muted Sage | `#8A9A7B` | `oklch(0.60 0.06 130)` | 辅助、标签 |
| Cream | `#FFF8EE` | `oklch(0.98 0.01 80)` | 卡片背景 |

```css
:root {
  --color-primary: #8B4513;
  --color-bg: #F5ECD7;
  --color-text: #2C1810;
  --color-accent: #C67B4E;
  --color-muted: #8A9A7B;
  --color-cream: #FFF8EE;
}
@supports (color: oklch(0 0 0)) {
  :root {
    --color-primary: oklch(0.40 0.10 45);
    --color-bg: oklch(0.94 0.02 80);
    --color-text: oklch(0.20 0.03 40);
    --color-accent: oklch(0.60 0.12 50);
    --color-muted: oklch(0.60 0.06 130);
    --color-cream: oklch(0.98 0.01 80);
  }
}
```

### 2.5 数据驱动 — 深底+多色 Accent

**适用场景**：Dashboard、数据可视化、监控大屏、BI 报告

| 角色 | HEX | oklch | 用途 |
|------|-----|-------|------|
| Background | `#0F1419` | `oklch(0.18 0.01 250)` | 深色底 |
| Surface | `#1C2630` | `oklch(0.25 0.015 245)` | 卡片/面板 |
| Text | `#E8ECF0` | `oklch(0.92 0.01 240)` | 正文文字 |
| Accent Blue | `#4EA8DE` | `oklch(0.65 0.12 230)` | 数据系列1/主accent |
| Accent Green | `#5CC98A` | `oklch(0.70 0.14 150)` | 数据系列2/正面指标 |
| Accent Amber | `#F0B429` | `oklch(0.78 0.14 80)` | 数据系列3/警告 |
| Accent Red | `#E5534B` | `oklch(0.58 0.18 20)` | 数据系列4/负面指标 |
| Accent Purple | `#A371F7` | `oklch(0.60 0.16 290)` | 数据系列5 |

```css
:root {
  --color-bg: #0F1419;
  --color-surface: #1C2630;
  --color-text: #E8ECF0;
  --color-accent-blue: #4EA8DE;
  --color-accent-green: #5CC98A;
  --color-accent-amber: #F0B429;
  --color-accent-red: #E5534B;
  --color-accent-purple: #A371F7;
}
@supports (color: oklch(0 0 0)) {
  :root {
    --color-bg: oklch(0.18 0.01 250);
    --color-surface: oklch(0.25 0.015 245);
    --color-text: oklch(0.92 0.01 240);
    --color-accent-blue: oklch(0.65 0.12 230);
    --color-accent-green: oklch(0.70 0.14 150);
    --color-accent-amber: oklch(0.78 0.14 80);
    --color-accent-red: oklch(0.58 0.18 20);
    --color-accent-purple: oklch(0.60 0.16 290);
  }
}
```

---

## 3. 1 色 → 5 级色阶算法

从 1 个主色推导 5 级色阶：**极浅 / 浅 / 中（原色）/ 深 / 极深**

用于：背景渐变、hover/focus 状态、层级区分、图表系列。

### 3.1 算法说明

输入主色 `oklch(L₀ C₀ H₀)`，输出 5 级：

| 级别 | 亮度 | 色度 | 色相 | 用途 |
|------|------|------|------|------|
| 50 极浅 | L₀ + 0.35 (clamp ≤0.97) | C₀ × 0.35 | H₀ | 极浅背景、tag 背景 |
| 100 浅 | L₀ + 0.18 (clamp ≤0.92) | C₀ × 0.6 | H₀ | 浅背景、hover 态 |
| 500 中 | L₀ | C₀ | H₀ | 原色、主按钮 |
| 700 深 | L₀ - 0.15 (clamp ≥0.18) | C₀ × 1.1 | H₀ | 深色区块、active 态 |
| 900 极深 | L₀ - 0.28 (clamp ≥0.12) | C₀ × 1.2 | H₀ | 文字色、最深背景 |

### 3.2 Python 实现

```python
import math

def hex_to_oklch(hex_str: str) -> tuple:
    """HEX → oklch (近似转换，使用 sRGB → Linear → OKLab → oklch)"""
    hex_str = hex_str.lstrip('#')
    r, g, b = int(hex_str[0:2], 16) / 255, int(hex_str[2:4], 16) / 255, int(hex_str[4:6], 16) / 255

    # sRGB → Linear RGB
    def linearize(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r_l, g_l, b_l = linearize(r), linearize(g), linearize(b)

    # Linear RGB → OKLab (simplified matrix)
    l_ = 0.4122214708 * r_l + 0.5363325363 * g_l + 0.0514459929 * b_l
    m_ = 0.2119034982 * r_l + 0.6806995451 * g_l + 0.1073969566 * b_l
    s_ = 0.0883024619 * r_l + 0.2817188376 * g_l + 0.6299787005 * b_l

    l_c = l_ ** (1/3) if l_ >= 0 else 0
    m_c = m_ ** (1/3) if m_ >= 0 else 0
    s_c = s_ ** (1/3) if s_ >= 0 else 0

    L = 0.2104542553 * l_c + 0.7936177850 * m_c - 0.0040720468 * s_c
    a = 1.9779984951 * l_c - 2.4285922050 * m_c + 0.4505937099 * s_c
    b_ok = 0.0259040371 * l_c + 0.7827717662 * m_c - 0.8086757660 * s_c

    C = (a ** 2 + b_ok ** 2) ** 0.5
    H = math.degrees(math.atan2(b_ok, a)) % 360
    return (L, C, H)


def oklch_to_hex(L: float, C: float, H: float) -> str:
    """oklch → HEX (近似转换)"""
    H_rad = math.radians(H)
    a = C * math.cos(H_rad)
    b_ok = C * math.sin(H_rad)

    l_c = L + 0.3963377774 * a + 0.2158037573 * b_ok
    m_c = L - 0.1055613458 * a - 0.0638541728 * b_ok
    s_c = L - 0.0894841775 * a - 1.2914855480 * b_ok

    l_ = l_c ** 3
    m_ = m_c ** 3
    s_ = s_c ** 3

    r_l = +4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_
    g_l = -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_
    b_l = -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_

    def delinearize(c):
        c = max(0, min(1, c))
        return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055

    r, g, b = delinearize(r_l), delinearize(g_l), delinearize(b_l)
    return '#{:02x}{:02x}{:02x}'.format(
        int(round(r * 255)), int(round(g * 255)), int(round(b * 255))
    )


def generate_scale(hex_color: str) -> dict:
    """
    从1个主色生成5级色阶。

    参数:
        hex_color: 主色 HEX 值，如 '#1A3A5C'

    返回:
        dict: {50: {'hex': ..., 'oklch': ...}, 100: ..., 500: ..., 700: ..., 900: ...}
    """
    L, C, H = hex_to_oklch(hex_color)

    steps = [
        (50,  min(L + 0.35, 0.97), C * 0.35, H),
        (100, min(L + 0.18, 0.92), C * 0.6,  H),
        (500, L,                   C,         H),
        (700, max(L - 0.15, 0.18), C * 1.1,  H),
        (900, max(L - 0.28, 0.12), C * 1.2,  H),
    ]

    result = {}
    for level, l, c, h in steps:
        c = min(c, 0.37)  # clamp to sRGB gamut
        result[level] = {
            'hex': oklch_to_hex(l, c, h),
            'oklch': f'oklch({l:.3f} {c:.3f} {h:.1f})',
        }
    return result


# 使用示例
if __name__ == '__main__':
    scale = generate_scale('#1A3A5C')
    for level, vals in scale.items():
        print(f"  {level}: {vals['hex']}  {vals['oklch']}")
```

### 3.3 JavaScript 实现

```javascript
/**
 * HEX → oklch 近似转换
 */
function hexToOklch(hex) {
  const r = parseInt(hex.slice(1, 3), 16) / 255;
  const g = parseInt(hex.slice(3, 5), 16) / 255;
  const b = parseInt(hex.slice(5, 7), 16) / 255;

  const linearize = (c) => c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  const rL = linearize(r), gL = linearize(g), bL = linearize(b);

  const l_ = 0.4122214708 * rL + 0.5363325363 * gL + 0.0514459929 * bL;
  const m_ = 0.2119034982 * rL + 0.6806995451 * gL + 0.1073969566 * bL;
  const s_ = 0.0883024619 * rL + 0.2817188376 * gL + 0.6299787005 * bL;

  const lc = l_ >= 0 ? l_ ** (1/3) : 0;
  const mc = m_ >= 0 ? m_ ** (1/3) : 0;
  const sc = s_ >= 0 ? s_ ** (1/3) : 0;

  const L = 0.2104542553 * lc + 0.7936177850 * mc - 0.0040720468 * sc;
  const a = 1.9779984951 * lc - 2.4285922050 * mc + 0.4505937099 * sc;
  const bok = 0.0259040371 * lc + 0.7827717662 * mc - 0.8086757660 * sc;

  const C = Math.sqrt(a * a + bok * bok);
  const H = (Math.atan2(bok, a) * 180 / Math.PI + 360) % 360;
  return [L, C, H];
}

/**
 * oklch → HEX 近似转换
 */
function oklchToHex(L, C, H) {
  const Hrad = H * Math.PI / 180;
  const a = C * Math.cos(Hrad);
  const bok = C * Math.sin(Hrad);

  const lc = L + 0.3963377774 * a + 0.2158037573 * bok;
  const mc = L - 0.1055613458 * a - 0.0638541728 * bok;
  const sc = L - 0.0894841775 * a - 1.2914855480 * bok;

  const l_ = lc ** 3, m_ = mc ** 3, s_ = sc ** 3;

  const rL = +4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_;
  const gL = -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_;
  const bL = -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_;

  const delinearize = (c) => {
    c = Math.max(0, Math.min(1, c));
    return c <= 0.0031308 ? 12.92 * c : 1.055 * (c ** (1/2.4)) - 0.055;
  };

  const toHex = (v) => Math.round(delinearize(v) * 255).toString(16).padStart(2, '0');
  return `#${toHex(rL)}${toHex(gL)}${toHex(bL)}`;
}

/**
 * 从1个主色生成5级色阶
 * @param {string} hexColor - 主色 HEX，如 '#1A3A5C'
 * @returns {Object} {50: {hex, oklch}, 100: ..., 500: ..., 700: ..., 900: ...}
 */
function generateScale(hexColor) {
  const [L0, C0, H0] = hexToOklch(hexColor);

  const steps = [
    [50,  Math.min(L0 + 0.35, 0.97), C0 * 0.35, H0],
    [100, Math.min(L0 + 0.18, 0.92), C0 * 0.6,  H0],
    [500, L0,                         C0,         H0],
    [700, Math.max(L0 - 0.15, 0.18),  C0 * 1.1,  H0],
    [900, Math.max(L0 - 0.28, 0.12),  C0 * 1.2,  H0],
  ];

  const result = {};
  for (const [level, l, c, h] of steps) {
    const cClamped = Math.min(c, 0.37);
    result[level] = {
      hex: oklchToHex(l, cClamped, h),
      oklch: `oklch(${l.toFixed(3)} ${cClamped.toFixed(3)} ${h.toFixed(1)})`,
    };
  }
  return result;
}

// 使用示例
// const scale = generateScale('#1A3A5C');
// console.log(scale);
```

---

## 4. 色彩无障碍

### 4.1 WCAG 2.1 对比度标准

| 等级 | 普通文本（<18px / <14px bold） | 大文本（≥18px / ≥14px bold） | UI 组件 & 图形 |
|------|-------------------------------|------------------------------|---------------|
| AA | **4.5:1** | **3:1** | 3:1 |
| AAA | **7:1** | **4.5:1** | — |

### 4.2 对比度计算（简化版）

```
相对亮度 L = 0.2126 * R_lin + 0.7152 * G_lin + 0.0722 * B_lin
对比度 ratio = (L_light + 0.05) / (L_dark + 0.05)
```

**实操规则：**
- 正文文字 vs 背景：对比度 ≥ 4.5:1（AA）
- 大标题 vs 背景：对比度 ≥ 3:1（AA）
- 追求高质量：正文对比度 ≥ 7:1（AAA）

### 4.3 深色模式/浅色模式调整

**浅色模式 → 深色模式转换规则：**

| 浅色模式 | 深色模式 | 说明 |
|---------|---------|------|
| 白底 `#FFFFFF` | 深底 `#121212` ~ `#1E1E1E` | 不要用纯黑 `#000000`，纯黑造成过高对比度致眼疲劳 |
| 深色文字 `#1A1A1A` | 浅色文字 `#E0E0E0` ~ `#F0F0F0` | 不要用纯白文字，降低对比度至 7:1~10:1 |
| 高饱和 accent | 降低饱和度 10%~20% | 深色底上高饱和色过亮刺眼 |
| 低对比辅助文字 | 适当提亮 | 深色底上对比度进一步降低，需补偿 |

**深色模式关键对比度：**
- 正文文字 vs 深底：**≥ 7:1**（深色模式更易眼疲劳，推荐 AAA）
- 次要文字 vs 深底：**≥ 4.5:1**
- accent 色 vs 深底：**≥ 3:1**

### 4.4 色盲友好设计

**原则：不只用颜色区分信息。**

| 做法 | 示例 |
|------|------|
| 颜色 + 形状 | 🔴 错误圆点 / 🟢 成功方点 / 🟡 警告三角 |
| 颜色 + 图案 | 图表中不同系列用不同填充纹理 |
| 颜色 + 文字标签 | 状态标签写明文字：「通过」「失败」而非只有色块 |
| 颜色 + 位置 | 不同类别用空间位置区分（左右、上下） |

**常见色盲类型与配色规避：**
- 红绿色盲（最常见，约8%男性）：避免红/绿作为唯一区分
- 蓝黄色盲：避免蓝/黄作为唯一区分
- 全色盲：必须加形状/文字/位置

**推荐数据可视化调色板（色盲友好）：**
```
#4EA8DE (蓝)
#F0B429 (琥珀)
#5CC98A (绿)
#E5534B (红)
#A371F7 (紫)
#2DD4BF (青)
```

---

## 5. 反 AI Slop 色彩清单

### 5.1 禁止清单 🚫

| 反模式 | 说明 |
|--------|------|
| 紫色渐变（非品牌） | AI 默认偏好紫蓝渐变，若无品牌 spec 明确要求则禁止使用 |
| `#0D1117` 深蓝底 | GitHub 风格深底，仅限开发者工具场景，非技术场景禁止 |
| 凭空发明的 accent 色 | 任何 accent 必须从品牌色或 oklch 和谐推导，不能"觉得好看"就加 |
| `#6366F1` Indigo 滥用 | Tailwind indigo 是 AI 最爱的默认色，除非品牌 spec 含此色否则不用 |
| 蓝紫双色搭配 | 非品牌场景禁止蓝+紫组合，这是 AI slop 的标志 |
| 纯黑 `#000000` 背景 | 深色模式用 `#121212`~`#1E1E1E`，纯黑对比过高 |
| `#F3F4F6` 冷灰背景 | 此灰色偏冷偏死，用有温度的灰替代 |

### 5.2 推荐清单 ✅

| 做法 | 说明 |
|------|------|
| 从品牌 spec 取色 | 优先使用品牌规范中的色彩，不自行发明 |
| oklch 和谐推导 | 所有新色从品牌主色通过 oklch 变亮度/色相推导 |
| 有温度的灰色 | 暖色系品牌用暖灰（H≈60-80）、冷色系用冷灰（H≈240-260） |
| 中性色带品牌色相 | 灰色/白色加入微量品牌色相的 C 值（0.005~0.02），让中性色与品牌一体 |
| 检查色阶均匀性 | 5 级色阶的相邻级亮度差 ≈ 0.15~0.18，不均则调整 |
| 对比度验证 | 每个文字/背景组合都要过 WCAG AA 标准 |

---

## 6. 行业配色速查表

### 金融

```
#1A3A5C  深蓝（权威/信任）
#3D6B8E  中蓝（专业/稳健）
#C8A951  金（价值/卓越）
#F5F6F8  浅灰蓝背景
#1C2533  深色文字
```

### 科技

```
#2D2D2D  深灰（沉稳/专业）
#00B37E  翠绿（活力/创新）
#4EA8DE  天蓝（技术/智能）
#FAFAFA  极浅灰背景
#1A1A1A  近黑文字
```

### 医疗

```
#0E6EB8  医疗蓝（专业/安全）
#2A9D8F  薄荷绿（健康/生机）
#E8F4FD  浅蓝背景（洁净/安心）
#F4F1DE  暖米白（人文关怀）
#1A2332  深色文字
```

### 教育

```
#2B4C7E  学院蓝（知识/严谨）
#D4A843  暖金（学术/荣誉）
#5AAE7E  成长绿（发展/希望）
#FFF8EE  暖白背景
#2C1810  暖黑文字
```

### 政务

```
#C41E24  政务红（权威/庄重）
#D4A843  金（荣誉/正式）
#8B1A1A  深红（历史/传承）
#FFF8F0  暖白背景
#2B1A0E  暖黑文字
```

### 消费品

```
#E8524A  活力红（热情/购买）
#F0B429  琥珀黄（温暖/信赖）
#2D2D2D  深灰（高端/质感）
#F7F3ED  米白背景（亲近/舒适）
#5A4A3A  棕色文字（温润/品质）
```

### 文化

```
#8B4513  赭石（传统/底蕴）
#C67B4E  陶土（人文/温度）
#8A9A7B  苔绿（自然/宁静）
#F5ECD7  米白背景
#2C1810  墨色文字
```

### 能源

```
#0A5E2C  能源绿（可持续/环保）
#1A3A5C  深蓝（稳定/工业）
#F0B429  琥珀（能源/光照）
#F7F7F7  浅灰背景
#1A2332  深色文字
```
