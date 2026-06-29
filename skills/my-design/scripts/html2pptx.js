#!/usr/bin/env node
/**
 * html2pptx.js — HTML→PPTX 元素级翻译器
 *
 * 将 HTML 文件中的 DOM 元素翻译为 PPTX 对象（文本→TextBox、图片→Picture、矩形→Shape），
 * 保留字号/颜色/粗体/斜体/对齐等文本格式，以及背景色/边框/圆角等视觉属性。
 *
 * 画布映射：16:9  HTML 1920×1080  →  PPTX 10″×5.625″
 * 坐标转换：1 px ≈ 9525 EMU（1920px → 10inch）
 *
 * 用法：
 *   node html2pptx.js -i input.html -o output.pptx
 *   node html2pptx.js --input slide.html --output slide.pptx [--width 1920] [--height 1080]
 *
 * 依赖：pptxgenjs
 *   若未安装，脚本会给出安装提示：npm install pptxgenjs
 */

'use strict';

const fs = require('fs');
const path = require('path');

// ── 依赖检查 ──────────────────────────────────────────────
let PptxGenJS;
try {
  PptxGenJS = require('pptxgenjs');
} catch (e) {
  console.error('[ERROR] 缺少依赖 pptxgenjs，请运行：');
  console.error('  npm install pptxgenjs');
  process.exit(1);
}

// ── 常量 ──────────────────────────────────────────────────
const HTML_WIDTH = 1920;
const HTML_HEIGHT = 1080;
const PPTX_WIDTH = 10;      // inches
const PPTX_HEIGHT = 5.625;  // inches
const PX_TO_EMU = 9525;     // 1px ≈ 9525 EMU (1920px → 10inch)
const INCH_PER_PX = PPTX_WIDTH / HTML_WIDTH;  // px → inch

// ── 工具函数 ──────────────────────────────────────────────

/**
 * 解析颜色字符串为 #RRGGBB 格式
 */
function parseColor(raw) {
  if (!raw || raw === 'transparent' || raw === 'none' || raw === 'initial') return null;
  const s = raw.trim().toLowerCase();

  // #hex
  if (/^#[0-9a-f]{6}$/i.test(s)) return s;
  if (/^#[0-9a-f]{3}$/i.test(s)) {
    return '#' + s[1] + s[1] + s[2] + s[2] + s[3] + s[3];
  }

  // rgb(r, g, b)
  const rgbMatch = s.match(/rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/);
  if (rgbMatch) {
    const r = parseInt(rgbMatch[1]).toString(16).padStart(2, '0');
    const g = parseInt(rgbMatch[2]).toString(16).padStart(2, '0');
    const b = parseInt(rgbMatch[3]).toString(16).padStart(2, '0');
    return `#${r}${g}${b}`;
  }

  // 命名颜色（常用子集）
  const NAMED = {
    white: '#ffffff', black: '#000000', red: '#ff0000', green: '#008000',
    blue: '#0000ff', yellow: '#ffff00', gray: '#808080', grey: '#808080',
    orange: '#ffa500', purple: '#800080', pink: '#ffc0cb',
  };
  if (NAMED[s]) return NAMED[s];

  return null;
}

/**
 * 解析像素值 → 数字（去掉 px 后缀）
 */
function parsePx(val) {
  if (!val || val === 'auto') return 0;
  return parseFloat(val) || 0;
}

/**
 * px → pt 直接映射（1px ≈ 1pt，PPTX 常见做法）
 */
function pxToPt(px) {
  return px; // 直接映射
}

/**
 * px → inch
 */
function pxToInch(px) {
  return px * INCH_PER_PX;
}

/**
 * 解析 CSS border-radius → PPTX roundRect 参数
 */
function parseBorderRadius(val) {
  if (!val || val === '0px' || val === '0') return 0;
  return parsePx(val);
}

/**
 * 解析 text-align → PptxGenJS align
 */
function parseAlign(val) {
  if (!val) return 'left';
  const map = { left: 'left', center: 'center', right: 'right', justify: 'justify' };
  return map[val.toLowerCase()] || 'left';
}

/**
 * 解析 font-weight → bold
 */
function isBold(weight) {
  if (!weight) return false;
  if (weight === 'bold' || weight === 'bolder') return true;
  return parseInt(weight) >= 600;
}

/**
 * 检测是否为 CSS Grid 布局
 */
function isGridLayout(style) {
  return style.display === 'grid' || style.display === 'inline-grid';
}

// ── 简易 HTML 解析（无 DOM 依赖，使用正则 + 递归） ──────────

/**
 * 极简 HTML 解析：提取 <body> 内的元素信息
 * 返回元素列表 [{tag, style, rect, text, children, src, ...}]
 */
function parseHTML(htmlStr) {
  // 使用 linkedom 或 jsdom 如果可用，否则用正则
  let document;
  try {
    const { parseHTML } = require('linkedom');
    const { document: doc } = parseHTML(htmlStr);
    document = doc;
  } catch (_) {
    // linkedom 不可用，尝试 jsdom
    try {
      const { JSDOM } = require('jsdom');
      document = new JSDOM(htmlStr).window.document;
    } catch (__) {
      console.error('[ERROR] 需要 linkedom 或 jsdom 来解析 HTML。请运行：');
      console.error('  npm install linkedom   (推荐，轻量)');
      console.error('  或 npm install jsdom');
      process.exit(1);
    }
  }
  return document;
}

// ── 元素遍历 & 翻译 ──────────────────────────────────────

/**
 * 递归遍历 DOM，收集可翻译的元素
 */
function collectElements(node, elements = [], parentOffset = { x: 0, y: 0 }) {
  if (node.nodeType !== 1) return elements; // 只处理 Element 节点

  const tag = node.tagName.toLowerCase();
  const style = node.style || {};
  const computedStyle = node.ownerDocument.defaultView
    ? node.ownerDocument.defaultView.getComputedStyle(node)
    : style;

  // 跳过 Grid 布局元素
  if (isGridLayout(computedStyle)) {
    console.warn(`[WARN] 跳过 CSS Grid 布局元素: <${tag}> (${node.id || node.className || ''})`);
    return elements;
  }

  // 跳过不可见元素
  if (computedStyle.display === 'none' || computedStyle.visibility === 'hidden' || computedStyle.opacity === '0') {
    return elements;
  }

  // 获取位置信息
  const rect = node.getBoundingClientRect ? node.getBoundingClientRect() : null;
  if (!rect) return elements;

  const x = rect.left + parentOffset.x;
  const y = rect.top + parentOffset.y;
  const w = rect.width;
  const h = rect.height;

  // 零尺寸元素跳过
  if (w <= 0 || h <= 0) return elements;

  const el = {
    tag,
    x, y, w, h,
    style: computedStyle,
    text: '',
    src: '',
    children: [],
  };

  // 图片
  if (tag === 'img') {
    el.src = node.getAttribute('src') || '';
    el.alt = node.getAttribute('alt') || '';
    elements.push(el);
    return elements;
  }

  // SVG（当作图片处理）
  if (tag === 'svg') {
    el.type = 'svg';
    elements.push(el);
    return elements;
  }

  // 提取直接文本（不含子元素文本）
  let directText = '';
  for (const child of node.childNodes) {
    if (child.nodeType === 3) { // TEXT_NODE
      directText += child.textContent;
    }
  }
  el.text = directText.trim();

  // 有背景/边框/文本的 div → 矩形/TextBox
  const hasBg = !!parseColor(computedStyle.backgroundColor);
  const hasBorder = parsePx(computedStyle.borderWidth) > 0;
  const hasText = el.text.length > 0;

  if (hasBg || hasBorder || hasText) {
    elements.push(el);
  }

  // 递归子元素
  for (const child of node.children || []) {
    collectElements(child, elements, parentOffset);
  }

  return elements;
}

// ── PPTX 生成 ────────────────────────────────────────────

/**
 * 将收集到的元素列表翻译为 PPTX
 */
function buildPPTX(elements, outputPath) {
  const pptx = new PptxGenJS();
  pptx.defineLayout({ name: 'CUSTOM_16x9', width: PPTX_WIDTH, height: PPTX_HEIGHT });
  pptx.layout = 'CUSTOM_16x9';

  const slide = pptx.addSlide();

  for (const el of elements) {
    const left = pxToInch(el.x);
    const top = pxToInch(el.y);
    const width = pxToInch(el.w);
    const height = pxToInch(el.h);
    const style = el.style;

    // ── 图片 ──
    if (el.tag === 'img' && el.src) {
      try {
        // 支持 data: URI 和文件路径
        const imgPath = el.src.startsWith('data:') ? el.src : el.src;
        slide.addImage({
          path: imgPath,
          x: left, y: top, w: width, h: height,
          rounding: parseBorderRadius(style.borderRadius) > 0,
        });
      } catch (err) {
        console.warn(`[WARN] 图片添加失败: ${el.src} — ${err.message}`);
      }
      continue;
    }

    // ── SVG → 图片 ──
    if (el.type === 'svg') {
      // SVG 需要预转换为 PNG，此处跳过并警告
      console.warn(`[WARN] SVG 元素需要预转换为 PNG，已跳过 (位置: ${Math.round(el.x)},${Math.round(el.y)})`);
      continue;
    }

    const bgColor = parseColor(style.backgroundColor);
    const borderColor = parseColor(style.borderColor);
    const borderWidth = parsePx(style.borderWidth);
    const borderRadius = parseBorderRadius(style.borderRadius);
    const hasText = el.text.length > 0;

    // ── 纯文本 + 背景/边框 → TextBox（带形状背景） ──
    if (hasText) {
      const fontSize = pxToPt(parsePx(style.fontSize) || 16);
      const fontColor = parseColor(style.color) || '#000000';
      const bold = isBold(style.fontWeight);
      const italic = (style.fontStyle === 'italic');
      const align = parseAlign(style.textAlign);
      const fontFamily = style.fontFamily ? style.fontFamily.replace(/['"]/g, '').split(',')[0].trim() : 'Arial';

      const textOptions = {
        x: left, y: top, w: width, h: height,
        fontSize,
        color: fontColor.replace('#', ''),
        bold,
        italic,
        align,
        fontFace: fontFamily,
        valign: style.verticalAlign === 'middle' ? 'mid' : (style.verticalAlign === 'bottom' ? 'bot' : 'top'),
        wrap: true,
      };

      // 背景填充
      if (bgColor) {
        textOptions.fill = { color: bgColor.replace('#', '') };
      }

      // 边框
      if (borderWidth > 0 && borderColor) {
        textOptions.line = { color: borderColor.replace('#', ''), width: borderWidth * INCH_PER_PX };
      }

      // 圆角
      if (borderRadius > 0) {
        textOptions.rectRadius = borderRadius * INCH_PER_PX;
      }

      slide.addText(el.text, textOptions);
      continue;
    }

    // ── 纯矩形/形状（无文本，有背景或边框） ──
    if (bgColor || (borderWidth > 0 && borderColor)) {
      const shapeOpts = {
        x: left, y: top, w: width, h: height,
        shape: borderRadius > 0 ? 'roundRect' : 'rect',
      };

      if (bgColor) {
        shapeOpts.fill = { color: bgColor.replace('#', '') };
      }
      if (borderWidth > 0 && borderColor) {
        shapeOpts.line = { color: borderColor.replace('#', ''), width: borderWidth * INCH_PER_PX };
      }
      if (borderRadius > 0) {
        shapeOpts.rectRadius = borderRadius * INCH_PER_PX;
      }

      slide.addShape(shapeOpts.shape === 'roundRect' ? 'roundRect' : 'rect', shapeOpts);
      continue;
    }
  }

  pptx.writeFile({ fileName: outputPath })
    .then(() => console.log(`[OK] PPTX 已生成: ${outputPath}`))
    .catch(err => {
      console.error(`[ERROR] 写入 PPTX 失败: ${err.message}`);
      process.exit(1);
    });
}

// ── CLI ───────────────────────────────────────────────────

function main() {
  const args = process.argv.slice(2);
  let inputPath = '';
  let outputPath = 'output.pptx';
  let htmlWidth = HTML_WIDTH;
  let htmlHeight = HTML_HEIGHT;

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '-i': case '--input':  inputPath = args[++i]; break;
      case '-o': case '--output': outputPath = args[++i]; break;
      case '-W': case '--width':  htmlWidth = parseInt(args[++i]) || HTML_WIDTH; break;
      case '-H': case '--height': htmlHeight = parseInt(args[++i]) || HTML_HEIGHT; break;
      case '-h': case '--help':
        console.log(`
html2pptx.js — HTML→PPTX 元素级翻译器

用法:
  node html2pptx.js -i <input.html> -o <output.pptx> [选项]

选项:
  -i, --input   输入 HTML 文件路径 (必填)
  -o, --output  输出 PPTX 文件路径 (默认: output.pptx)
  -W, --width   HTML 画布宽度 (默认: 1920)
  -H, --height  HTML 画布高度 (默认: 1080)
  -h, --help    显示帮助信息

依赖:
  npm install pptxgenjs linkedom
`);
        process.exit(0);
    }
  }

  if (!inputPath) {
    console.error('[ERROR] 必须指定输入文件: -i <input.html>');
    process.exit(1);
  }

  const absInput = path.resolve(inputPath);
  if (!fs.existsSync(absInput)) {
    console.error(`[ERROR] 输入文件不存在: ${absInput}`);
    process.exit(1);
  }

  console.log(`[INFO] 读取 HTML: ${absInput}`);
  const htmlStr = fs.readFileSync(absInput, 'utf-8');

  // 解析 HTML
  const document = parseHTML(htmlStr);
  const body = document.body || document.querySelector('body') || document.documentElement;

  // 收集元素
  const elements = collectElements(body);
  console.log(`[INFO] 收集到 ${elements.length} 个元素`);

  // 生成 PPTX
  const absOutput = path.resolve(outputPath);
  buildPPTX(elements, absOutput);
}

main();
