#!/usr/bin/env python3
"""batch_shot: 批量截图，支持断点续传+重试。

用法:
  from batch_shot import batch_screenshot

  tasks = [
    {"id": "01", "url": "http://localhost:8770/style_01.html", "pages": [
      {"name": "cover", "js": "...slide switch js..."},
      {"name": "chart", "js": "..."},
    ]},
  ]
  batch_screenshot(tasks, out_dir="/tmp/shots")
"""
import json, base64, os, time
import urllib.request

CDP = "http://127.0.0.1:18800"
_ws = None

def _get_ws():
    global _ws
    if _ws is not None:
        try:
            _ws.ping()
            return _ws
        except:
            _ws = None
    import websocket
    targets = json.loads(urllib.request.urlopen(f"{CDP}/json").read())
    page = next(t for t in targets if t.get('type') == 'page')
    _ws = websocket.create_connection(page['webSocketDebuggerUrl'], suppress_origin=True)
    return _ws

def _cdp(method, params=None, retry=2):
    ws = _get_ws()
    for attempt in range(retry):
        try:
            ws.send(json.dumps({"id": 1, "method": method, "params": params or {}}))
            return json.loads(ws.recv())
        except Exception as e:
            if attempt < retry - 1:
                _ws = None
                ws = _get_ws()
            else:
                raise

def batch_screenshot(tasks, out_dir, width=1920, height=1080, skip_existing=True):
    """批量截图。skip_existing=True 时跳过已存在的文件（断点续传）。"""
    os.makedirs(out_dir, exist_ok=True)
    done = 0
    skipped = 0
    failed = 0

    for task in tasks:
        tid = task["id"]
        # Navigate
        try:
            _cdp("Page.navigate", {"url": task["url"]})
            time.sleep(1.0)
        except Exception as e:
            print(f"  [{tid}] navigate failed: {e}")
            failed += len(task["pages"])
            continue

        for page in task["pages"]:
            out_path = os.path.join(out_dir, f"{tid}_{page['name']}.png")

            # 断点续传：跳过已存在的
            if skip_existing and os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
                skipped += 1
                continue

            # 切换页面
            if "js" in page:
                try:
                    _cdp("Runtime.evaluate", {"expression": page["js"]})
                    time.sleep(0.3)
                except:
                    pass

            # 截图
            try:
                result = _cdp("Page.captureScreenshot", {
                    "format": "png",
                    "clip": {"x": 0, "y": 0, "width": width, "height": height, "scale": 1}
                })
                if 'result' in result and 'data' in result['result']:
                    img = base64.b64decode(result['result']['data'])
                    with open(out_path, 'wb') as f:
                        f.write(img)
                    done += 1
                    print(f"  [{tid}] {page['name']}: {len(img)//1024}KB ✅")
                else:
                    failed += 1
                    print(f"  [{tid}] {page['name']}: no data ❌")
            except Exception as e:
                failed += 1
                print(f"  [{tid}] {page['name']}: {e} ❌")

    print(f"\nDone: {done} done, {skipped} skipped, {failed} failed")
    return done, skipped, failed
