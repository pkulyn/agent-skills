#!/usr/bin/env python3
"""
程序入口点
"""
import sys
import asyncio

from cli import main

if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
