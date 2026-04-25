"""
Markdown文件生成模块
将视频信息和字幕转换为Obsidian兼容的Markdown格式
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

from bilibili import VideoInfo, SubtitleInfo, SubtitleItem


@dataclass
class MarkdownGenerator:
    """Markdown生成器"""
    include_timestamp: bool = True
    include_metadata: bool = True
    include_bilingual: bool = True
    original_label: str = "原文"
    translated_label: str = "翻译"

    def generate(
        self,
        video_info: VideoInfo,
        subtitle_info: Optional[SubtitleInfo] = None,
        translated_items: Optional[List[Dict]] = None
    ) -> str:
        """
        生成完整的Markdown内容

        Args:
            video_info: 视频信息
            subtitle_info: 字幕信息
            translated_items: 翻译后的字幕条目（可选）

        Returns:
            Markdown内容字符串
        """
        lines = []

        # 1. YAML Front Matter
        if self.include_metadata:
            lines.extend(self._generate_front_matter(video_info, subtitle_info))
            lines.append("---")
            lines.append("")

        # ✅ 新增：视频封面
        if video_info.cover_url:
            lines.append(f"![{video_info.title}]({video_info.cover_url})")
            lines.append("")

        # 2. 标题
        lines.append(f"# {video_info.title}")
        lines.append("")

        # 3. 简洁视频信息（避免和YAML重复）
        lines.append(f"👤 UP主：[{video_info.up_name}](https://space.bilibili.com/{video_info.up_id})")
        lines.append(f"🔗 视频链接：[点击观看](https://www.bilibili.com/video/{video_info.bvid})")
        if video_info.description:
            lines.append(f"📝 简介：{video_info.description[:200]}{'...' if len(video_info.description) > 200 else ''}")
        lines.append("")

        # 4. 字幕内容
        if subtitle_info and subtitle_info.items:
            lines.append("## 字幕")
            lines.append("")

            if translated_items and self.include_bilingual:
                lines.extend(self._generate_bilingual_subtitles(translated_items))
            else:
                lines.extend(self._generate_single_subtitles(subtitle_info.items))
        else:
            lines.append("⚠️ 该视频没有可用字幕")
            lines.append("")

        # 5. 页脚
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

        return "\n".join(lines)

    def _generate_front_matter(
        self,
        video_info: VideoInfo,
        subtitle_info: Optional[SubtitleInfo] = None
    ) -> List[str]:
        """
        生成YAML Front Matter

        Args:
            video_info: 视频信息
            subtitle_info: 字幕信息

        Returns:
            YAML行列表
        """
        lines = ["---"]

        # 基础信息
        lines.append(f'title: "{self._escape_yaml(video_info.title)}"')
        lines.append(f'bvid: "{video_info.bvid}"')
        lines.append(f'avid: {video_info.avid}')
        lines.append(f'up: "{self._escape_yaml(video_info.up_name)}"')
        lines.append(f'up_id: {video_info.up_id}')

        # 日期处理
        if video_info.upload_time:
            try:
                upload_date = datetime.fromtimestamp(int(video_info.upload_time))
                lines.append(f'date: "{upload_date.strftime("%Y-%m-%d")}"')
            except:
                lines.append(f'date: "{video_info.upload_time}"')

        lines.append(f'duration: {video_info.duration}')

        # 统计信息
        lines.append(f'views: {video_info.view_count}')
        lines.append(f'likes: {video_info.like_count}')
        lines.append(f'coins: {video_info.coin_count}')

        # 标签
        if video_info.tags:
            tags_str = ', '.join([f'"{self._escape_yaml(tag)}"' for tag in video_info.tags])
            lines.append(f'tags: [{tags_str}]')

        # 链接
        lines.append(f'url: "https://www.bilibili.com/video/{video_info.bvid}"')
        lines.append(f'cover: "{video_info.cover_url}"')

        # 字幕信息
        if subtitle_info:
            lines.append(f'subtitle_lang: "{subtitle_info.lang}"')
            lines.append(f'subtitle_lang_name: "{subtitle_info.lang_name}"')
            lines.append(f'subtitle_type: "{subtitle_info.subtitle_type}"')
            lines.append(f'subtitle_count: {len(subtitle_info.items)}')

        # Obsidian分类
        lines.append(f'category: "Bilibili字幕"')

        return lines

    def _generate_video_info(self, video_info: VideoInfo) -> List[str]:
        """
        生成视频信息部分

        Args:
            video_info: 视频信息

        Returns:
            行列表
        """
        lines = []

        # 封面图
        if video_info.cover_url:
            lines.append(f"![封面]({video_info.cover_url})")
            lines.append("")

        # 基本信息表格
        lines.append("| 项目 | 信息 |")
        lines.append("|------|------|")
        lines.append(f"| 标题 | {video_info.title} |")
        lines.append(f"| UP主 | [{video_info.up_name}](https://space.bilibili.com/{video_info.up_id}) |")

        if video_info.upload_time:
            try:
                upload_date = datetime.fromtimestamp(int(video_info.upload_time))
                lines.append(f"| 发布时间 | {upload_date.strftime('%Y-%m-%d %H:%M')} |")
            except:
                lines.append(f"| 发布时间 | {video_info.upload_time} |")

        # 时长格式化
        duration = video_info.duration
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        seconds = duration % 60
        if hours > 0:
            duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            duration_str = f"{minutes}:{seconds:02d}"
        lines.append(f"| 时长 | {duration_str} |")

        lines.append(f"| 播放量 | {video_info.view_count:,} |")
        lines.append(f"| 点赞 | {video_info.like_count:,} |")
        lines.append(f"| 投币 | {video_info.coin_count:,} |")

        lines.append(f"| 视频链接 | [点击观看](https://www.bilibili.com/video/{video_info.bvid}) |")

        # 简介
        if video_info.description:
            lines.append("")
            lines.append("### 简介")
            lines.append("")
            lines.append(video_info.description)

        return lines

    def _generate_single_subtitles(self, items: List[SubtitleItem]) -> List[str]:
        """
        生成单语言字幕

        Args:
            items: 字幕条目列表

        Returns:
            行列表
        """
        lines = []

        for item in items:
            if self.include_timestamp:
                time_str = self._format_time(item.from_time)
                lines.append(f"[{time_str}] {item.content}")
            else:
                lines.append(item.content)
            lines.append("")

        return lines

    def _generate_bilingual_subtitles(self, translated_items: List[Dict]) -> List[str]:
        """
        生成双语字幕

        Args:
            translated_items: 翻译后的条目列表

        Returns:
            行列表
        """
        lines = []

        for item in translated_items:
            from_time = item.get('from_time', 0)
            original = item.get('content', '')
            translated = item.get('translated', '')

            if not original:
                continue

            if self.include_timestamp:
                time_str = self._format_time(from_time)
                lines.append(f"[{time_str}] **{self.original_label}**: {original}")
                if translated and translated != original:
                    lines.append(f"         **{self.translated_label}**: {translated}")
            else:
                lines.append(f"**{self.original_label}**: {original}")
                if translated and translated != original:
                    lines.append(f"**{self.translated_label}**: {translated}")

            lines.append("")

        return lines

    @staticmethod
    def _format_time(seconds: float) -> str:
        """
        格式化时间戳

        Args:
            seconds: 秒数

        Returns:
            格式化的时间字符串（HH:MM:SS 或 MM:SS）
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def _escape_yaml(text: str) -> str:
        """
        转义YAML特殊字符

        Args:
            text: 原始文本

        Returns:
            转义后的文本
        """
        if not text:
            return ""

        # 转义双引号和反斜杠
        return text.replace('\\', '\\\\').replace('"', '\\"')
