"""
主程序模块
整合Bilibili API、Markdown生成和Obsidian保存
"""
import re
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List

from bilibili import BilibiliClient, VideoInfo, SubtitleInfo
from markdown_generator import MarkdownGenerator
from obsidian import ObsidianManager
from config import Bili2ObsidianConfig


def _is_english_subtitle(items) -> bool:
    """检测字幕是否为英文（采样多条判断，避免单条误判）"""
    if not items:
        return False

    # 采样前5条（跳过可能的问候语）
    sample_items = items[1:6] if len(items) > 2 else items[:3]
    english_count = 0

    for item in sample_items:
        text = item.content if hasattr(item, 'content') else str(item)
        if not text or not text.strip():
            continue
        import re as _re
        cleaned = _re.sub(r'[^\w\s]', '', text)
        cleaned = _re.sub(r'\d+', '', cleaned).strip()
        if not cleaned:
            continue
        english_chars = len(_re.findall(r'[a-zA-Z]', cleaned))
        total_chars = len(cleaned.replace(' ', ''))
        if total_chars > 0 and english_chars / total_chars > 0.7:
            english_count += 1

    # 超过半数采样为英文才判定为英文字幕
    return english_count > len(sample_items) / 2


class Bili2Obsidian:
    """Bilibili到Obsidian主类"""

    def __init__(self, config: Bili2ObsidianConfig):
        self.config = config

        # 创建B站凭证（如果配置了）
        credential = None
        cred_config = config.bilibili_credential
        if cred_config and cred_config.sessdata:
            from bilibili_api import Credential
            credential = Credential(
                sessdata=cred_config.sessdata,
                bili_jct=cred_config.bili_jct,
                buvid3=cred_config.buvid3
            )

        self.bili_client = BilibiliClient(credential=credential)
        self.obs_manager = ObsidianManager(
            vault_path=config.obsidian_vault_path,
            output_folder=config.output_folder
        )
        self.md_generator = MarkdownGenerator(
            include_timestamp=config.include_timestamp,
            include_metadata=config.include_metadata,
            include_bilingual=True
        )

    async def process_video(
        self,
        url: str,
        subtitle_type: str = "ai",
        output_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        处理单个视频

        Args:
            url: B站视频URL或BV号
            subtitle_type: 字幕类型偏好
            output_name: 指定输出文件名

        Returns:
            处理结果字典，包含 needs_translation 标记
        """
        # 1. 提取BV号
        bvid = self._extract_bvid(url)
        if not bvid:
            raise ValueError(f"无法从URL中提取BV号: {url}")

        # 2. 获取视频信息
        print(f"正在获取视频信息: {bvid}")
        video_info = await self.bili_client.get_video_info(bvid)

        # 3. 获取字幕
        print(f"正在获取字幕: {bvid}")
        subtitle_info = await self.bili_client.get_best_subtitle(bvid, subtitle_type)

        # 4. 检测是否为英文字幕
        is_english = False
        if subtitle_info and subtitle_info.items:
            sample_text = subtitle_info.items[0].content
            is_english = _is_english_subtitle(subtitle_info.items)
            if is_english:
                print(f"检测到英文字幕（需要后续翻译）")

        # 5. 生成Markdown
        print(f"正在生成Markdown文档...")
        markdown_content = self.md_generator.generate(
            video_info=video_info,
            subtitle_info=subtitle_info
        )

        # 6. 确定输出文件名：格式为 UP主：视频标题
        if output_name:
            safe_filename = output_name
        else:
            up_part = video_info.up_name if video_info.up_name else "unknown_up"
            title_part = video_info.title[:50] if video_info.title else "untitled"
            up_part = self._sanitize_filename(up_part)
            title_part = self._sanitize_filename(title_part)
            safe_filename = f"{up_part}：{title_part}"

        # 7. 保存文件
        print(f"正在保存文件...")
        file_path = self.obs_manager.save_markdown(
            content=markdown_content,
            filename=safe_filename
        )

        # 8. 返回结果
        return {
            "bvid": bvid,
            "title": video_info.title,
            "up": video_info.up_name,
            "file_path": file_path,
            "filename": safe_filename,
            "subtitle_count": len(subtitle_info.items) if subtitle_info else 0,
            "needs_translation": is_english,
            "subtitle_type": subtitle_info.subtitle_type if subtitle_info else None
        }

    @staticmethod
    def _extract_bvid(url: str) -> Optional[str]:
        """从URL或字符串中提取BV号"""
        if re.match(r'^BV[a-zA-Z0-9]{10}$', url):
            return url
        match = re.search(r'BV[a-zA-Z0-9]{10}', url)
        if match:
            return match.group(0)
        return None

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """清理文件名中的非法字符"""
        invalid_chars = '<>:"/\\|?*'
        result = filename
        for char in invalid_chars:
            result = result.replace(char, '_')
        result = result.strip('. ')
        if len(result) > 50:
            result = result[:50]
        return result if result else "untitled"

    async def process_favorite(
        self,
        favorite_url_or_id: str,
        subtitle_type: str = "ai",
        force: bool = False
    ) -> Dict[str, Any]:
        """
        批量处理收藏夹中的所有视频

        Args:
            favorite_url_or_id: 收藏夹URL或ID
            subtitle_type: 字幕类型偏好
            force: 是否强制覆盖已存在的文件

        Returns:
            处理结果统计，包含需要翻译的文件列表
        """
        # 1. 提取收藏夹ID
        media_id = self.bili_client.extract_favorite_id(favorite_url_or_id)
        if not media_id:
            raise ValueError(f"无法从输入中提取收藏夹ID: {favorite_url_or_id}")

        print(f"开始处理收藏夹，ID: {media_id}")

        # 2. 获取收藏夹所有视频
        videos = await self.bili_client.get_favorite_videos(media_id)
        if not videos:
            return {
                "success": False,
                "message": "收藏夹中没有视频或获取失败",
                "total": 0, "processed": 0, "skipped": 0, "failed": 0,
                "results": [], "needs_translation": []
            }

        # 3. 获取已提取的BV号
        extracted_bvids = self.obs_manager.get_extracted_bvids()
        print(f"本地已提取{len(extracted_bvids)}个视频")

        # 4. 逐个处理视频
        total_videos = len(videos)
        processed = skipped = failed = 0
        results = []
        needs_translation = []

        print(f"收藏夹共{total_videos}个视频，开始处理...")

        for i, video in enumerate(videos, 1):
            bvid = video.get('bvid')
            title = video.get('title', '未知标题')

            print(f"\n[{i}/{total_videos}] 处理视频: {title} ({bvid})")

            if not force and bvid in extracted_bvids:
                print(f"✅ 视频已提取，跳过")
                skipped += 1
                continue

            try:
                result = await self.process_video(
                    url=bvid,
                    subtitle_type=subtitle_type
                )
                results.append(result)
                processed += 1
                if result.get('needs_translation'):
                    needs_translation.append(result['file_path'])
                print(f"✅ 处理完成: {result['file_path']}")

                await asyncio.sleep(1)

            except Exception as e:
                failed += 1
                print(f"❌ 处理失败: {e}")
                continue

        # 5. 输出结果
        print(f"\n🎉 收藏夹处理完成！")
        print(f"总计: {total_videos} | 成功: {processed} | 跳过: {skipped} | 失败: {failed}")
        if needs_translation:
            print(f"\n⚠️ 以下{len(needs_translation)}个文件含英文字幕，需要翻译：")
            for fp in needs_translation:
                print(f"  - {fp}")

        return {
            "success": True,
            "total": total_videos,
            "processed": processed,
            "skipped": skipped,
            "failed": failed,
            "results": results,
            "needs_translation": needs_translation
        }

    async def process_course(
        self,
        course_url_or_id: str,
        subtitle_type: str = "ai",
        force: bool = False
    ) -> Dict[str, Any]:
        """
        批量处理付费课程中的所有视频

        Args:
            course_url_or_id: 课程URL或SS号
            subtitle_type: 字幕类型偏好
            force: 是否强制覆盖已存在的文件

        Returns:
            处理结果统计，包含需要翻译的文件列表
        """
        # 1. 提取课程ID
        ss_id = self.bili_client.extract_course_id(course_url_or_id)
        if not ss_id:
            raise ValueError(f"无法从输入中提取课程ID: {course_url_or_id}")

        print(f"开始处理课程，SS号: {ss_id}")

        # 2. 获取课程所有视频
        videos = await self.bili_client.get_course_videos(ss_id)
        if not videos:
            return {
                "success": False,
                "message": "课程中没有视频或获取失败（请确认已购买该课程）",
                "total": 0, "processed": 0, "skipped": 0, "failed": 0,
                "results": [], "needs_translation": []
            }

        # 3. 获取已提取的BV号
        extracted_bvids = self.obs_manager.get_extracted_bvids()
        print(f"本地已提取{len(extracted_bvids)}个视频")

        # 4. 逐个处理视频
        total_videos = len(videos)
        processed = skipped = failed = 0
        results = []
        needs_translation = []

        print(f"课程共{total_videos}个视频，开始处理...")

        for i, video in enumerate(videos, 1):
            epid = video.get('epid')
            bvid = video.get('bvid')
            title = video.get('title', '未知标题')
            index = video.get('index', '')
            up_name = video.get('up_name', '')

            print(f"\n[{i}/{total_videos}] 处理视频: {index} {title} (EP{epid})")

            if not force and bvid in extracted_bvids:
                print(f"✅ 视频已提取，跳过")
                skipped += 1
                continue

            try:
                # 1. 获取视频信息
                print(f"正在获取视频信息: EP{epid}")
                video_info = await self.bili_client.get_course_video_info(epid)
                video_info.up_name = up_name
                video_info.up_id = video.get('up_id', 0)

                # 2. 获取字幕
                print(f"正在获取字幕: EP{epid}")
                subtitle_list = await self.bili_client.get_course_subtitle_list(epid)
                subtitle_info = None

                if subtitle_list:
                    priority_map = {'upload': 0, 'ai': 1, 'cc': 2}

                    best_subtitle = None
                    best_priority = float('inf')

                    for sub in subtitle_list:
                        sub_type_code = 'cc'
                        if sub.get('is_ai', False):
                            sub_type_code = 'ai'
                        elif sub.get('is_user_upload', False):
                            sub_type_code = 'upload'

                        priority = priority_map.get(sub_type_code, 3)
                        if sub_type_code == subtitle_type:
                            priority = -1

                        if priority < best_priority:
                            best_priority = priority
                            best_subtitle = sub

                    if best_subtitle:
                        subtitle_url = best_subtitle.get('subtitle_url', '')
                        if subtitle_url:
                            if not subtitle_url.startswith('http'):
                                subtitle_url = f"https:{subtitle_url}"

                            items = await self.bili_client.get_subtitle_content(subtitle_url)

                            if items:
                                sub_type = 'cc'
                                if best_subtitle.get('is_ai', False):
                                    sub_type = 'ai'
                                elif best_subtitle.get('is_user_upload', False):
                                    sub_type = 'upload'

                                subtitle_info = SubtitleInfo(
                                    lang=best_subtitle.get('lan', ''),
                                    lang_name=best_subtitle.get('lan_doc', ''),
                                    subtitle_type=sub_type,
                                    items=items
                                )

                # 3. 检测英文字幕
                is_english = False
                if subtitle_info and subtitle_info.items:
                    is_english = _is_english_subtitle(subtitle_info.items)
                    if is_english:
                        print(f"检测到英文字幕（需要后续翻译）")

                # 4. 生成Markdown
                print(f"正在生成Markdown文档...")
                markdown_content = self.md_generator.generate(
                    video_info=video_info,
                    subtitle_info=subtitle_info
                )

                # 5. 确定输出文件名
                up_part = video_info.up_name if video_info.up_name else 'unknown_up'
                title_part = video_info.title[:50] if video_info.title else 'untitled'
                up_part = self._sanitize_filename(up_part)
                title_part = self._sanitize_filename(title_part)
                safe_filename = f"{up_part}：{title_part}"

                # 6. 保存文件
                print(f"正在保存文件...")
                file_path = self.obs_manager.save_markdown(
                    content=markdown_content,
                    filename=safe_filename
                )

                # 7. 记录结果
                result = {
                    'bvid': video_info.bvid,
                    'title': video_info.title,
                    'up': video_info.up_name,
                    'file_path': file_path,
                    'filename': safe_filename,
                    'subtitle_count': len(subtitle_info.items) if subtitle_info else 0,
                    'needs_translation': is_english,
                    'subtitle_type': subtitle_info.subtitle_type if subtitle_info else None
                }
                results.append(result)
                processed += 1
                if is_english:
                    needs_translation.append(file_path)
                print(f"✅ 处理完成: {result['file_path']}")

                await asyncio.sleep(1)

            except Exception as e:
                failed += 1
                print(f"❌ 处理失败: {e}")
                import traceback
                traceback.print_exc()
                continue

        # 5. 输出结果
        print(f"\n🎉 课程处理完成！")
        print(f"总计: {total_videos} | 成功: {processed} | 跳过: {skipped} | 失败: {failed}")
        if needs_translation:
            print(f"\n⚠️ 以下{len(needs_translation)}个文件含英文字幕，需要翻译：")
            for fp in needs_translation:
                print(f"  - {fp}")

        return {
            "success": True,
            "total": total_videos,
            "processed": processed,
            "skipped": skipped,
            "failed": failed,
            "results": results,
            "needs_translation": needs_translation
        }
