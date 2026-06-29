#!/usr/bin/env python3
"""shot2send: 截图 + 发送一步到位。

用法（被其他脚本 import）:
  from shot2send import shot, send_file, shot_and_send

  # 截取当前浏览器页面，保存到指定路径
  shot("/tmp/out.png")

  # 发送本地文件到飞书
  send_file("/tmp/out.png", "说明文字")

  # 截图+发送一步到位
  shot_and_send("/tmp/out.png", "P8 结尾页")
"""
import json, base64, os, time
import urllib.request

CDP = "http://127.0.0.1:18800"
_ws = None

def _get_ws():
    global _ws
    if _ws is not None:
        return _ws
    import websocket
    targets = json.loads(urllib.request.urlopen(f"{CDP}/json").read())
    page = next(t for t in targets if t.get('type') == 'page')
    _ws = websocket.create_connection(page['webSocketDebuggerUrl'], suppress_origin=True)
    return _ws

def navigate(url, wait=1.0):
    ws = _get_ws()
    ws.send(json.dumps({"id": 1, "method": "Page.navigate", "params": {"url": url}}))
    ws.recv()
    time.sleep(wait)

def run_js(code, wait=0.3):
    ws = _get_ws()
    ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code}}))
    ws.recv()
    time.sleep(wait)

def shot(out_path, width=1920, height=1080):
    """截取当前浏览器页面，保存到 out_path。"""
    ws = _get_ws()
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    ws.send(json.dumps({
        "id": 1, "method": "Page.captureScreenshot",
        "params": {"format": "png", "clip": {"x": 0, "y": 0, "width": width, "height": height, "scale": 1}}
    }))
    result = json.loads(ws.recv())
    if 'result' in result and 'data' in result['result']:
        img = base64.b64decode(result['result']['data'])
        with open(out_path, 'wb') as f:
            f.write(img)
        return len(img)
    return 0

def send_file(file_path, caption="", channel="feishu"):
    """通过 openclaw CLI 发送文件到飞书。"""
    import subprocess
    cmd = ["openclaw", "message", "send", "--channel", channel, "--media", file_path]
    if caption:
        cmd += ["--message", caption]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return r.returncode == 0

def shot_and_send(out_path, caption="", **kw):
    """截图 + 发送一步到位。返回 (截图字节数, 发送是否成功)。"""
    size = shot(out_path, **kw)
    ok = send_file(out_path, caption) if size > 0 else False
    return size, ok

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: shot2send.py <out_path> [caption]")
        sys.exit(1)
    out = sys.argv[1]
    cap = sys.argv[2] if len(sys.argv) > 2 else ""
    size, ok = shot_and_send(out, cap)
    print(f"截图: {size//1024}KB, 发送: {'✅' if ok else '❌'}")
