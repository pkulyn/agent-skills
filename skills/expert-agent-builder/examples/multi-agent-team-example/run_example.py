#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多Agent团队示例运行脚本
演示如何使用Expert Agent Builder创建多Agent协作系统
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def run_example():
    """运行多Agent示例"""

    print("=" * 60)
    print("Expert Agent Builder - 多Agent团队示例")
    print("=" * 60)

    # 检查当前目录
    current_dir = Path(__file__).parent
    print(f"示例目录: {current_dir}")

    # 检查必要文件是否存在
    required_files = [
        "user-profile.json",
        "team-info.json",
        "collaboration-rules.json",
        "agent-profile-project-manager.json",
        "agent-profile-technical-architect.json",
        "agent-profile-developer-expert.json",
        "agent-profile-tester-expert.json"
    ]

    missing_files = []
    for file in required_files:
        if not (current_dir / file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        print("请确保所有必要文件存在后再运行示例。")
        return 1

    print("✓ 所有必要文件存在")

    # 1. 收集文件内容，验证示例数据
    print("\n1. 验证示例数据完整性...")

    try:
        with open(current_dir / "user-profile.json", 'r', encoding='utf-8') as f:
            user_profile = json.load(f)

        with open(current_dir / "team-info.json", 'r', encoding='utf-8') as f:
            team_info = json.load(f)

        with open(current_dir / "collaboration-rules.json", 'r', encoding='utf-8') as f:
            collaboration_rules = json.load(f)

        print("✓ 示例数据格式正确")

        # 显示基本信息
        user_name = user_profile.get("basic_info", {}).get("name", {}).get("value", "未填写")
        team_name = team_info.get("basic_info", {}).get("team_name", {}).get("value", "智能协作工作台")
        team_size = team_info.get("basic_info", {}).get("team_size", {}).get("value", 4)

        print(f"  用户: {user_name}")
        print(f"  团队: {team_name} ({team_size} 个Agent)")

    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误: {e}")
        return 1
    except Exception as e:
        print(f"❌ 数据验证失败: {e}")
        return 1

    # 2. 运行智能模式创建多Agent配置
    print("\n2. 运行Expert Agent Builder智能模式...")

    # 找到主脚本路径
    main_script = current_dir.parent.parent / "openclaw-config-generator.py"

    if not main_script.exists():
        print(f"❌ 找不到主脚本: {main_script}")
        return 1

    print(f"主脚本: {main_script}")

    # 准备命令
    command = [
        sys.executable,
        str(main_script),
        "--mode", "smart"
    ]

    print(f"命令: {' '.join(command)}")
    print("\n" + "-" * 40)
    print("接下来将启动智能模式交互流程。")
    print("请按照提示选择：")
    print("  1. 平台: openclaw 或 claudecode")
    print("  2. 模式: multi-agent (多Agent)")
    print("  3. 信息获取方式: document (资料整理模式)")
    print("  4. 提供文档路径: . (当前目录)")
    print("-" * 40)

    # 询问用户是否继续
    response = input("\n是否继续运行示例？[Y/N]: ").strip().upper()

    if response != 'Y':
        print("示例运行已取消。")
        return 0

    print("\n正在启动Expert Agent Builder智能模式...")
    print("=" * 60)

    try:
        # 运行主脚本
        print(f"执行命令: {' '.join(command)}")
        print("-" * 60 + "\n")

        # 直接执行，捕获输出

        result = subprocess.run(command, capture_output=False, text=True)

        print("-" * 60 + "\n")

        if result.returncode == 0:
            print("✅ 示例运行成功！")

            # 显示生成的配置信息
            config_dir = current_dir / "generated-config"
            if config_dir.exists():
                print(f"\n生成的配置位于: {config_dir}")

                # 列出生成的文件
                print("生成的文件结构：")
                for root, dirs, files in os.walk(config_dir):
                    level = root.replace(str(config_dir), '').count(os.sep)
                    indent = ' ' * 2 * level
                    print(f'{indent}{os.path.basename(root)}/')
                    subindent = ' ' * 2 * (level + 1)
                    for file in files[:5]:  # 只显示前5个文件
                        print(f'{subindent}{file}')
                    if len(files) > 5:
                        print(f'{subindent}... 还有 {len(files) - 5} 个文件')

            print("\n📖 使用说明：")
            print("  1. 查看生成的配置文件: `generated-config/`")
            print("  2. 查看验证报告: `generated-config/validation_report.md`")
            print("  3. 查看团队配置: `generated-config/agent-config/team-config/`")
            print("  4. 详细文档请查看: `README.md`")

            return 0

        else:
            print(f"❌ 示例运行失败，返回码: {result.returncode}")
            if result.stderr:
                print(f"错误输出:\n{result.stderr}")
            return result.returncode

    except KeyboardInterrupt:
        print("\n\n示例运行被用户中断。")
        return 130
    except Exception as e:
        print(f"❌ 运行过程中出现异常: {e}")
        return 1

def show_manual_mode():
    """显示手动运行说明"""

    print("\n" + "=" * 60)
    print("手动运行说明")
    print("=" * 60)

    print("\n如果您想手动运行，请执行以下步骤：")

    print("\n1. 确保当前在示例目录中：")
    print(f"   cd {Path(__file__).parent}")

    print("\n2. 运行Expert Agent Builder智能模式：")
    print("   python ../../openclaw-config-generator.py --mode smart")

    print("\n3. 在交互流程中选择：")
    print("   - 平台: openclaw 或 claudecode")
    print("   - 模式: multi-agent (多Agent)")
    print("   - 信息获取方式: document (资料整理模式)")
    print("   - 文档路径: . (当前目录)")

    print("\n4. 确认信息后生成配置")

    print("\n5. 查看生成的配置：")
    print("   - OpenClaw格式: generated-config/agent-config/")
    print("   - Claude Code格式: generated-config/claudecode-config/")
    print("   - 验证报告: generated-config/validation_report.md")

if __name__ == "__main__":

    print("\nExpert Agent Builder 多Agent示例")
    print("-" * 60)

    print("\n本示例演示如何创建多Agent协作系统。")
    print("它将使用智能模式引导您创建包含4个专业Agent的团队配置。")

    print("\n请选择运行方式：")
    print("  1. 自动运行示例 (推荐)")
    print("  2. 显示手动运行说明")
    print("  3. 退出")

    choice = input("\n您的选择 [1-3]: ").strip()

    if choice == '1':
        sys.exit(run_example())
    elif choice == '2':
        show_manual_mode()
    else:
        print("示例运行已取消。")