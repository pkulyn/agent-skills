#!/usr/bin/env python3
"""srv: 自动端口分配的 HTTP 静态服务器。

用法（被其他脚本 import）:
  from srv import serve_dir
  url = serve_dir("/path/to/html/files")
  # url = "http://localhost:8770"
  # 用完自动清理（atexit），也可手动 stop(url)
"""
import os, subprocess, atexit, time, socket

_active = {}  # port -> proc

def _find_free_port(start=8770, end=8790):
    for p in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', p))
                return p
            except OSError:
                continue
    return None

def _cleanup():
    for port, proc in _active.items():
        try:
            proc.terminate()
        except:
            pass

atexit.register(_cleanup)

def serve_dir(directory, port=None):
    """启动 HTTP 服务器，返回 base URL。"""
    if port is None:
        port = _find_free_port()
    if port is None:
        raise RuntimeError("无可用端口 (8770-8790)")

    # 如果该端口已有服务，先检查是否存活
    if port in _active:
        try:
            _active[port].poll()
            if _active[port].returncode is None:
                return f"http://localhost:{port}"
        except:
            pass

    proc = subprocess.Popen(
        ["python3", "-m", "http.server", str(port), "--directory", directory],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    _active[port] = proc
    time.sleep(0.5)

    # 验证
    import urllib.request
    try:
        urllib.request.urlopen(f"http://localhost:{port}/", timeout=2)
    except:
        time.sleep(1)

    return f"http://localhost:{port}"

def stop(url_or_port):
    """停止指定服务器。"""
    port = int(url_or_port.split(":")[-1].rstrip("/")) if isinstance(url_or_port, str) else url_or_port
    if port in _active:
        _active[port].terminate()
        del _active[port]

def stop_all():
    """停止所有服务器。"""
    _cleanup()
    _active.clear()
