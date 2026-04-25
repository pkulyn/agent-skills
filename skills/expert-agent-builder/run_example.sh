#!/bin/bash

echo "🚀 OpenClaw高级专业Agent配置生成器 - 示例模式"
echo "=============================================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到Python3，请安装Python 3.8或更高版本"
    exit 1
fi

# 创建输出目录
mkdir -p "example-output"

# 运行示例模式
python3 openclaw-config-generator.py \
  --mode example \
  --output-dir "example-output" \
  --validation-level strict

echo ""
echo "✅ 示例运行完成！"
echo "📁 生成的文件保存在: example-output/"
echo ""
echo "📋 快速查看生成的文件："
ls -la example-output/