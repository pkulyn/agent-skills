#!/usr/bin/env node
/**
 * export_deck_pdf.mjs — HTML→PDF 导出脚本
 *
 * 使用 Playwright 打开 HTML 文件，等待 window.__ready === true（最多 30s），
 * 然后导出为 PDF。
 *
 * 对于 deck（幻灯片组）：检测 .slide / [data-slide] 元素，
 * 每页单独截图，合并为多页 PDF。
 *
 * 用法：
 *   node export_deck_pdf.mjs -i slide.html -o output.pdf
 *   node export_deck_pdf.mjs --input deck.html --output deck.pdf [--timeout 30000]
 *
 * 依赖：
 *   npm install playwright
 *   npx playwright install chromium
 */

import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';

// ── 常量 ──────────────────────────────────────────────────
const DEFAULT_TIMEOUT = 30000; // 30s
const VIEWPORT_WIDTH = 1920;
const VIEWPORT_HEIGHT = 1080;

// ── 工具函数 ──────────────────────────────────────────────

function parseArgs(argv) {
  const args = argv.slice(2);
  const opts = {
    input: '',
    output: 'output.pdf',
    timeout: DEFAULT_TIMEOUT,
    selector: '.slide, [data-slide], [data-page]',
    fullPage: false,
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '-i': case '--input':    opts.input = args[++i]; break;
      case '-o': case '--output':   opts.output = args[++i]; break;
      case '-t': case '--timeout':  opts.timeout = parseInt(args[++i]) || DEFAULT_TIMEOUT; break;
      case '-s': case '--selector': opts.selector = args[++i]; break;
      case '-f': case '--fullpage': opts.fullPage = true; break;
      case '-h': case '--help':
        console.log(`
export_deck_pdf.mjs — HTML→PDF 导出脚本

用法:
  node export_deck_pdf.mjs -i <input.html> -o <output.pdf> [选项]

选项:
  -i, --input      输入 HTML 文件路径 (必填)
  -o, --output     输出 PDF 文件路径 (默认: output.pdf)
  -t, --timeout    等待 __ready 超时毫秒数 (默认: 30000)
  -s, --selector   幻灯片选择器 (默认: ".slide, [data-slide], [data-page]")
  -f, --fullpage   全页截图模式 (不分页)
  -h, --help       显示帮助信息

依赖:
  npm install playwright && npx playwright install chromium
`);
        process.exit(0);
    }
  }
  return opts;
}

/**
 * 等待页面就绪信号 window.__ready === true
 */
async function waitForReady(page, timeout) {
  try {
    await page.waitForFunction('window.__ready === true', { timeout });
    console.log('[INFO] 页面就绪信号已收到 (__ready=true)');
  } catch (err) {
    console.warn('[WARN] 等待 __ready 超时，继续处理...');
  }
}

/**
 * 全页 PDF 导出
 */
async function exportFullPagePDF(page, outputPath) {
  await page.pdf({
    path: outputPath,
    format: 'A4',
    printBackground: true,
    margin: { top: 0, right: 0, bottom: 0, left: 0 },
  });
  console.log(`[OK] 全页 PDF 已生成: ${outputPath}`);
}

/**
 * Deck 模式：每张幻灯片单独截图 → 合并为多页 PDF
 */
async function exportDeckPDF(page, outputPath, selector) {
  // 查找所有 slide 元素
  const slideCount = await page.locator(selector).count();

  if (slideCount === 0) {
    console.warn('[WARN] 未找到幻灯片元素，回退到全页模式');
    await exportFullPagePDF(page, outputPath);
    return;
  }

  console.log(`[INFO] 检测到 ${slideCount} 张幻灯片`);

  // 使用 PDF 打印方式，逐页生成
  // Playwright 的 pdf() 不直接支持多页自定义区域，
  // 所以采用策略：逐个 slide 截图，然后用 PDFKit 合并

  const screenshots = [];
  const tmpDir = path.join(path.dirname(outputPath), '.tmp_pdf_frames');

  if (!fs.existsSync(tmpDir)) {
    fs.mkdirSync(tmpDir, { recursive: true });
  }

  for (let i = 0; i < slideCount; i++) {
    const slideEl = page.locator(selector).nth(i);
    const screenshotPath = path.join(tmpDir, `slide_${String(i).padStart(3, '0')}.png`);

    await slideEl.screenshot({
      path: screenshotPath,
      type: 'png',
    });
    screenshots.push(screenshotPath);
    console.log(`[INFO] 截图 ${i + 1}/${slideCount}`);
  }

  // 使用 Playwright 生成多页 PDF
  // 创建新页面，每页插入一张截图
  const browser = page.context().browser();
  const context = await browser.newContext();
  const pdfPage = await context.newPage();

  // 计算页面尺寸（16:9 比例）
  const pdfWidth = 1920;
  const pdfHeight = 1080;

  await pdfPage.setViewportSize({ width: pdfWidth, height: pdfHeight });

  // 构建多页 HTML
  const imgTags = screenshots.map((sp, idx) => {
    const dataUri = fs.readFileSync(sp).toString('base64');
    return `<div style="page-break-after: always; width: ${pdfWidth}px; height: ${pdfHeight}px; overflow: hidden;">
      <img src="data:image/png;base64,${dataUri}" style="width: 100%; height: 100%; object-fit: contain;" />
    </div>`;
  }).join('\n');

  await pdfPage.setContent(`<!DOCTYPE html><html><head><style>
    @page { size: ${pdfWidth}px ${pdfHeight}px; margin: 0; }
    body { margin: 0; padding: 0; }
    div { page-break-after: always; }
    div:last-child { page-break-after: auto; }
  </style></head><body>${imgTags}</body></html>`, { waitUntil: 'networkidle' });

  await pdfPage.pdf({
    path: outputPath,
    width: `${pdfWidth}px`,
    height: `${pdfHeight}px`,
    printBackground: true,
    margin: { top: 0, right: 0, bottom: 0, left: 0 },
  });

  console.log(`[OK] Deck PDF 已生成 (${slideCount} 页): ${outputPath}`);

  // 清理临时文件
  for (const sp of screenshots) {
    try { fs.unlinkSync(sp); } catch (_) {}
  }
  try { fs.rmdirSync(tmpDir); } catch (_) {}

  await context.close();
}

// ── 主流程 ────────────────────────────────────────────────

async function main() {
  const opts = parseArgs(process.argv);

  if (!opts.input) {
    console.error('[ERROR] 必须指定输入文件: -i <input.html>');
    process.exit(1);
  }

  const absInput = path.resolve(opts.input);
  if (!fs.existsSync(absInput)) {
    console.error(`[ERROR] 输入文件不存在: ${absInput}`);
    process.exit(1);
  }

  const absOutput = path.resolve(opts.output);
  const fileUrl = `file://${absInput}`;

  console.log(`[INFO] 打开 HTML: ${absInput}`);
  console.log(`[INFO] 输出 PDF: ${absOutput}`);

  let browser;
  try {
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      viewport: { width: VIEWPORT_WIDTH, height: VIEWPORT_HEIGHT },
      deviceScaleFactor: 2, // 2x 清晰度
    });

    const page = await context.newPage();
    await page.goto(fileUrl, { waitUntil: 'domcontentloaded' });

    // 等待页面就绪
    await waitForReady(page, opts.timeout);

    // 导出
    if (opts.fullPage) {
      await exportFullPagePDF(page, absOutput);
    } else {
      await exportDeckPDF(page, absOutput, opts.selector);
    }

    await context.close();
  } catch (err) {
    console.error(`[ERROR] 导出失败: ${err.message}`);
    process.exit(1);
  } finally {
    if (browser) await browser.close();
  }
}

main();
