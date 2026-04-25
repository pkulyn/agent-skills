#!/usr/bin/env python3
"""
入口脚本
"""
import sys
import os
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == "win32":
    # 设置控制台输出编码为UTF-8
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    # 尝试修改控制台代码页为UTF-8
    try:
        os.system('chcp 65001 >nul')
    except:
        pass

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cli import main

if __name__ == "__main__":
    sys.exit(main())
