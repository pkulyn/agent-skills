#!/usr/bin/env python3
"""
render.py — Playwright 截图/验证脚本

功能：
  screenshot(url, output_path)  — 全页或指定元素截图
  validate(url)                 — 检查 console error 数量、布局溢出
  verify_clicks(url, selectors) — 点击测试

用法：
  python render.py screenshot --url https://example.com --output screenshot.png
  python render.py screenshot --url file:///path/to/slide.html --output slide.png --selector ".slide-1"
  python render.py validate --url file:///path/to/slide.html
  python render.py verify-clicks --url file:///path/to/slide.html --selectors ".btn1,.btn2"

依赖：
  pip install playwright
  playwright install chromium
"""

import argparse
import sys
import json
import os
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout
except ImportError:
    print("[ERROR] 缺少依赖 playwright，请运行：")
    print("  pip install playwright")
    print("  playwright install chromium")
    sys.exit(1)


# ── 常量 ──────────────────────────────────────────────────
DEFAULT_VIEWPORT = {"width": 1920, "height": 1080}
DEFAULT_TIMEOUT = 30000  # 30s


# ── screenshot ────────────────────────────────────────────

def screenshot(url: str, output_path: str, selector: str = None,
               full_page: bool = False, wait_ready: bool = True,
               timeout: int = DEFAULT_TIMEOUT, scale: float = 2.0):
    """
    全页或指定元素截图。

    Args:
        url: 页面 URL（支持 file://）
        output_path: 输出图片路径
        selector: CSS 选择器（指定元素截图），None 则全页
        full_page: 是否全页截图（含滚动区域）
        wait_ready: 是否等待 window.__ready === true
        timeout: 超时毫秒数
        scale: 设备像素比（清晰度）
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport=DEFAULT_VIEWPORT,
            device_scale_factor=scale,
        )
        page = context.new_page()

        print(f"[INFO] 打开: {url}")
        page.goto(url, wait_until="domcontentloaded")

        if wait_ready:
            try:
                page.wait_for_function("window.__ready === true", timeout=timeout)
                print("[INFO] 页面就绪信号已收到 (__ready=true)")
            except PwTimeout:
                print("[WARN] 等待 __ready 超时，继续截图...")

        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        if selector:
            el = page.locator(selector)
            if el.count() == 0:
                print(f"[ERROR] 未找到元素: {selector}")
                browser.close()
                return False
            el.screenshot(path=output_path)
            print(f"[OK] 元素截图已保存: {output_path}")
        else:
            page.screenshot(path=output_path, full_page=full_page)
            print(f"[OK] 截图已保存: {output_path}")

        browser.close()
        return True


# ── validate ──────────────────────────────────────────────

def validate(url: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """
    检查页面质量：
      - console error 数量
      - 布局溢出（水平/垂直滚动条出现）

    Returns:
        dict: { "console_errors": int, "overflow_x": bool, "overflow_y": bool, "errors": [...] }
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport=DEFAULT_VIEWPORT)
        page = context.new_page()

        # 收集 console 错误
        console_errors = []

        def on_console(msg):
            if msg.type == "error":
                console_errors.append(msg.text)

        page.on("console", on_console)

        print(f"[INFO] 验证: {url}")
        page.goto(url, wait_until="domcontentloaded")

        try:
            page.wait_for_function("window.__ready === true", timeout=timeout)
        except PwTimeout:
            print("[WARN] 等待 __ready 超时")

        # 额外等待确保所有渲染完成
        page.wait_for_timeout(1000)

        # 检测布局溢出
        overflow = page.evaluate("""() => {
            const html = document.documentElement;
            return {
                overflowX: html.scrollWidth > html.clientWidth,
                overflowY: html.scrollHeight > html.clientHeight,
                scrollWidth: html.scrollWidth,
                clientWidth: html.clientWidth,
                scrollHeight: html.scrollHeight,
                clientHeight: html.clientHeight,
            };
        }""")

        browser.close()

    result = {
        "console_errors": len(console_errors),
        "errors": console_errors[:20],  # 最多 20 条
        "overflow_x": overflow["overflowX"],
        "overflow_y": overflow["overflowY"],
        "details": overflow,
    }

    # 输出摘要
    print(f"\n{'='*50}")
    print(f"  验证结果: {url}")
    print(f"{'='*50}")
    print(f"  Console Errors: {result['console_errors']}")
    if result['console_errors'] > 0:
        for err in result['errors'][:5]:
            print(f"    - {err[:120]}")
    print(f"  水平溢出: {'⚠️ 是' if result['overflow_x'] else '✅ 否'}")
    print(f"  垂直溢出: {'⚠️ 是' if result['overflow_y'] else '✅ 否'}")
    if result['overflow_x'] or result['overflow_y']:
        print(f"    scrollW={overflow['scrollWidth']} clientW={overflow['clientWidth']}")
        print(f"    scrollH={overflow['scrollHeight']} clientH={overflow['clientHeight']}")
    print(f"{'='*50}\n")

    return result


# ── verify_clicks ─────────────────────────────────────────

def verify_clicks(url: str, selectors: list, timeout: int = DEFAULT_TIMEOUT) -> list:
    """
    逐个点击指定元素，检测是否有 JS 错误。

    Args:
        url: 页面 URL
        selectors: CSS 选择器列表
        timeout: 超时毫秒数

    Returns:
        list: [{ selector, success, error? }]
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport=DEFAULT_VIEWPORT)
        page = context.new_page()

        # 收集点击后的错误
        click_errors = []

        def on_console(msg):
            if msg.type == "error":
                click_errors.append(msg.text)

        page.on("console", on_console)

        print(f"[INFO] 点击测试: {url}")
        page.goto(url, wait_until="domcontentloaded")

        try:
            page.wait_for_function("window.__ready === true", timeout=timeout)
        except PwTimeout:
            print("[WARN] 等待 __ready 超时")

        results = []

        for sel in selectors:
            click_errors.clear()
            el = page.locator(sel)

            try:
                count = el.count()
                if count == 0:
                    results.append({"selector": sel, "success": False, "error": "元素未找到"})
                    print(f"  ❌ {sel} — 元素未找到")
                    continue

                el.click(timeout=5000)
                page.wait_for_timeout(500)  # 等待反应

                if click_errors:
                    results.append({
                        "selector": sel,
                        "success": False,
                        "error": click_errors[0][:200],
                    })
                    print(f"  ❌ {sel} — 点击后出错: {click_errors[0][:80]}")
                else:
                    results.append({"selector": sel, "success": True})
                    print(f"  ✅ {sel} — 点击成功")

            except Exception as e:
                results.append({"selector": sel, "success": False, "error": str(e)[:200]})
                print(f"  ❌ {sel} — 异常: {e}")

        browser.close()

    print(f"\n[结果] {sum(1 for r in results if r['success'])}/{len(results)} 通过")
    return results


# ── CLI ───────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="render.py — Playwright 截图/验证脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 全页截图
  python render.py screenshot --url file:///path/to/slide.html --output slide.png

  # 指定元素截图
  python render.py screenshot --url file:///path/to/slide.html --selector ".slide-1" --output s1.png

  # 验证页面质量
  python render.py validate --url file:///path/to/slide.html

  # 点击测试
  python render.py verify-clicks --url file:///path/to/slide.html --selectors ".btn1,.btn2"
""",
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # screenshot
    p_ss = subparsers.add_parser("screenshot", help="截图")
    p_ss.add_argument("--url", required=True, help="页面 URL（支持 file://）")
    p_ss.add_argument("--output", required=True, help="输出图片路径")
    p_ss.add_argument("--selector", default=None, help="CSS 选择器（指定元素截图）")
    p_ss.add_argument("--full-page", action="store_true", help="全页截图（含滚动区域）")
    p_ss.add_argument("--no-wait", action="store_true", help="不等待 __ready 信号")
    p_ss.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="超时毫秒数")
    p_ss.add_argument("--scale", type=float, default=2.0, help="设备像素比（默认 2.0）")

    # validate
    p_val = subparsers.add_parser("validate", help="验证页面质量")
    p_val.add_argument("--url", required=True, help="页面 URL")
    p_val.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="超时毫秒数")
    p_val.add_argument("--json", action="store_true", help="输出 JSON 格式结果")

    # verify-clicks
    p_click = subparsers.add_parser("verify-clicks", help="点击测试")
    p_click.add_argument("--url", required=True, help="页面 URL")
    p_click.add_argument("--selectors", required=True, help="CSS 选择器列表，逗号分隔")
    p_click.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="超时毫秒数")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "screenshot":
        screenshot(
            url=args.url,
            output_path=args.output,
            selector=args.selector,
            full_page=args.full_page,
            wait_ready=not args.no_wait,
            timeout=args.timeout,
            scale=args.scale,
        )
    elif args.command == "validate":
        result = validate(url=args.url, timeout=args.timeout)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "verify-clicks":
        selectors = [s.strip() for s in args.selectors.split(",") if s.strip()]
        verify_clicks(url=args.url, selectors=selectors, timeout=args.timeout)


if __name__ == "__main__":
    main()
