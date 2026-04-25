"""
命令行接口模块
提供CLI命令处理
"""
import argparse
import asyncio
import sys
from pathlib import Path

from config import get_config, Bili2ObsidianConfig
from main import Bili2Obsidian


def create_parser() -> argparse.ArgumentParser:
    """创建参数解析器"""
    parser = argparse.ArgumentParser(
        prog='bili2obsidian',
        description='提取Bilibili视频字幕并保存到Obsidian知识库',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 提取单个视频字幕
  %(prog)s extract "https://www.bilibili.com/video/BV1xx411c7mD"

  # 批量提取收藏夹
  %(prog)s batch "https://space.bilibili.com/123456/favlist?fid=123456"

  # 批量提取付费课程
  %(prog)s course "https://www.bilibili.com/cheese/play/ss1234"
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # extract 命令
    extract_parser = subparsers.add_parser('extract', help='提取视频字幕', aliases=['e'])
    extract_parser.add_argument('url', help='B站视频URL或BV号')
    extract_parser.add_argument('-o', '--output', help='指定输出文件名（不含扩展名）')
    extract_parser.add_argument('--type', choices=['ai', 'upload', 'cc', 'best'], default='best', help='字幕类型偏好（默认: best）')

    # config 命令
    config_parser = subparsers.add_parser('config', help='配置管理', aliases=['c'])
    config_parser.add_argument('--init', action='store_true', help='初始化配置文件')
    config_parser.add_argument('--show', action='store_true', help='显示当前配置')
    config_parser.add_argument('--path', help='指定配置文件路径')

    # batch 命令
    batch_parser = subparsers.add_parser('batch', help='批量提取收藏夹字幕', aliases=['b'])
    batch_parser.add_argument('favorite', help='B站收藏夹URL或ID')
    batch_parser.add_argument('--type', choices=['ai', 'upload', 'cc', 'best'], default='best', help='字幕类型偏好（默认: best）')
    batch_parser.add_argument('-f', '--force', action='store_true', help='强制覆盖已存在的文件')

    # course 命令
    course_parser = subparsers.add_parser('course', help='批量提取付费课程字幕', aliases=['cs', 'cheese'])
    course_parser.add_argument('course', help='B站课程URL或SS号')
    course_parser.add_argument('--type', choices=['ai', 'upload', 'cc', 'best'], default='best', help='字幕类型偏好（默认: best）')
    course_parser.add_argument('-f', '--force', action='store_true', help='强制覆盖已存在的文件')

    # 全局选项
    parser.add_argument('--config', help='指定配置文件路径')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细输出')
    parser.add_argument('--version', action='version', version='%(prog)s 1.1.0')

    return parser


async def handle_extract(args) -> int:
    """处理extract命令"""
    try:
        config = get_config()
        bili2obs = Bili2Obsidian(config)
        sub_type = args.type if args.type != 'best' else config.default_subtitle_type

        print(f"正在处理: {args.url}")
        print(f"字幕类型: {sub_type}")

        result = await bili2obs.process_video(
            url=args.url,
            subtitle_type=sub_type,
            output_name=args.output
        )

        print(f"\n✓ 完成!")
        print(f"  文件: {result['file_path']}")
        print(f"  标题: {result['title']}")
        print(f"  字幕条目: {result['subtitle_count']}")
        if result.get('needs_translation'):
            print(f"  ⚠️ 英文字幕，需要翻译")

        return 0

    except Exception as e:
        print(f"\n✗ 错误: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


async def handle_config(args) -> int:
    """处理config命令"""
    config_path = args.path or "config.json"

    if args.init:
        config = Bili2ObsidianConfig()
        config.to_file(config_path)
        print(f"配置文件已创建: {config_path}")
        return 0

    if args.show:
        if not Path(config_path).exists():
            print(f"配置文件不存在: {config_path}")
            return 1
        config = Bili2ObsidianConfig.from_file(config_path)
        print("当前配置:")
        print(f"  Vault路径: {config.obsidian_vault_path}")
        print(f"  输出文件夹: {config.output_folder}")
        print(f"  默认字幕类型: {config.default_subtitle_type}")
        return 0

    print("请使用 --init 创建配置或 --show 查看配置")
    return 1


async def handle_batch(args) -> int:
    """处理batch命令"""
    try:
        config = get_config()
        bili2obs = Bili2Obsidian(config)
        sub_type = args.type if args.type != 'best' else config.default_subtitle_type

        print(f"开始批量处理收藏夹: {args.favorite}")
        print(f"字幕类型: {sub_type}")
        print(f"强制覆盖: {'是' if args.force else '否'}")
        print("=" * 50)

        result = await bili2obs.process_favorite(
            favorite_url_or_id=args.favorite,
            subtitle_type=sub_type,
            force=args.force
        )

        if not result['success']:
            print(f"\n✗ 错误: {result['message']}", file=sys.stderr)
            return 1

        print("\n" + "=" * 50)
        print("✅ 处理完成!")
        print(f"  总计视频: {result['total']} 个")
        print(f"  成功处理: {result['processed']} 个")
        print(f"  跳过: {result['skipped']} 个")
        print(f"  失败: {result['failed']} 个")

        if result['needs_translation']:
            print(f"\n  ⚠️ 以下{len(result['needs_translation'])}个文件含英文字幕，需要翻译：")
            for fp in result['needs_translation']:
                print(f"    - {fp}")

        return 0

    except Exception as e:
        print(f"\n✗ 错误: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


async def handle_course(args) -> int:
    """处理course命令"""
    try:
        config = get_config()
        bili2obs = Bili2Obsidian(config)
        sub_type = args.type if args.type != 'best' else config.default_subtitle_type

        print(f"开始批量处理课程: {args.course}")
        print(f"字幕类型: {sub_type}")
        print(f"强制覆盖: {'是' if args.force else '否'}")
        print("=" * 50)

        result = await bili2obs.process_course(
            course_url_or_id=args.course,
            subtitle_type=sub_type,
            force=args.force
        )

        if not result['success']:
            print(f"\n✗ 错误: {result['message']}", file=sys.stderr)
            return 1

        print("\n" + "=" * 50)
        print("✅ 处理完成!")
        print(f"  总计视频: {result['total']} 个")
        print(f"  成功处理: {result['processed']} 个")
        print(f"  跳过: {result['skipped']} 个")
        print(f"  失败: {result['failed']} 个")

        if result['needs_translation']:
            print(f"\n  ⚠️ 以下{len(result['needs_translation'])}个文件含英文字幕，需要翻译：")
            for fp in result['needs_translation']:
                print(f"    - {fp}")

        return 0

    except Exception as e:
        print(f"\n✗ 错误: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


async def main_async():
    """异步主函数"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    if args.command in ['extract', 'e']:
        return await handle_extract(args)
    elif args.command in ['config', 'c']:
        return await handle_config(args)
    elif args.command in ['batch', 'b']:
        return await handle_batch(args)
    elif args.command in ['course', 'cs', 'cheese']:
        return await handle_course(args)
    else:
        print(f"未知命令: {args.command}")
        return 1


def main():
    """主入口"""
    return asyncio.run(main_async())


if __name__ == '__main__':
    sys.exit(main())
