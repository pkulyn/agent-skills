"""
Markdown文件生成模块
将视频信息和字幕转换为Obsidian兼容的Markdown格式
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

from bilibili import VideoInfo, SubtitleInfo, SubtitleItem


# 字幕类型中文标签映射
SUBTITLE_TYPE_LABELS = {
    'ai': '中文（AI自动生成）',
    'upload': '中文（人工上传）',
    'cc': '中文（字幕组）',
    'en': '英文（需翻译）',
}


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
        """生成完整的Markdown内容"""
        lines = []

        # 1. YAML Front Matter
        if self.include_metadata:
            lines.extend(self._generate_front_matter(video_info, subtitle_info))
            lines.append("---")
            lines.append("")

        # 2. 封面图
        if video_info.cover_url:
            lines.append(f"![视频封面]({video_info.cover_url})")
            lines.append("")

        # 3. 标题
        lines.append(f"# {video_info.title}")
        lines.append("")

        # 4. 视频信息（引用块格式）
        date_str = ''
        if video_info.upload_time:
            try:
                upload_date = datetime.fromtimestamp(int(video_info.upload_time))
                date_str = upload_date.strftime('%Y-%m-%d')
            except:
                date_str = str(video_info.upload_time)

        type_label = '中文'
        if subtitle_info:
            type_label = SUBTITLE_TYPE_LABELS.get(
                subtitle_info.subtitle_type,
                subtitle_info.subtitle_type
            )

        info_parts = [
            f"**来源**: [B站视频](https://www.bilibili.com/video/{video_info.bvid})",
            f"**UP主**: {video_info.up_name}",
            f"**字幕类型**: {type_label}",
        ]
        if date_str:
            info_parts.append(f"**提取日期**: {date_str}")
        lines.append(f"> {' | '.join(info_parts)}")
        lines.append("")

        # 5. 简介
        if video_info.description:
            desc = video_info.description[:200]
            if len(video_info.description) > 200:
                desc += '...'
            lines.append(f"📝 简介：{desc}")
            lines.append("")

        # 6. 分隔线
        lines.append("---")
        lines.append("")

        # 7. 字幕内容
        if subtitle_info and subtitle_info.items:
            if translated_items and self.include_bilingual:
                lines.extend(self._generate_bilingual_subtitles(translated_items))
            else:
                lines.extend(self._generate_merged_subtitles(subtitle_info.items))
        else:
            lines.append("⚠️ 该视频没有可用字幕")
            lines.append("")

        # 8. 页脚
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
        """生成YAML Front Matter"""
        lines = ["---"]

        # 基础信息
        lines.append(f'title: "{self._escape_yaml(video_info.title)}"')
        lines.append(f'source: "https://www.bilibili.com/video/{video_info.bvid}"')
        lines.append(f'bvid: "{video_info.bvid}"')
        lines.append(f'avid: {video_info.avid}')
        lines.append(f'up: "{self._escape_yaml(video_info.up_name)}"')
        lines.append(f'up_id: {video_info.up_id}')

        # 视频发布日期
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

        # 字幕类型（中文标签）
        if subtitle_info:
            type_label = SUBTITLE_TYPE_LABELS.get(
                subtitle_info.subtitle_type,
                subtitle_info.subtitle_type
            )
            lines.append(f'subtitle_type: "{type_label}"')
            lines.append(f'subtitle_count: {len(subtitle_info.items)}')

        # 标签
        if video_info.tags:
            lines.append('tags:')
            for tag in video_info.tags:
                lines.append(f'  - {self._escape_yaml(tag)}')

        return lines

    def _generate_single_subtitles(self, items: List[SubtitleItem]) -> List[str]:
        """生成单语言字幕（逐条带时间戳）"""
        lines = []

        for item in items:
            if self.include_timestamp:
                time_str = self._format_time(item.from_time)
                lines.append(f"[{time_str}] {item.content}")
            else:
                lines.append(item.content)
            lines.append("")

        return lines

    def _generate_merged_subtitles(self, items: List[SubtitleItem], max_gap: float = 1.5, max_chars: int = 120) -> List[str]:
        """生成合并字幕（无时间戳，添加中文标点，智能分段）

        分段规则：
        1. 相邻条目时间间隔超过max_gap秒时换段
        2. 当前段落累计字符数超过max_chars时换段
        """
        lines = []
        paragraph = []
        para_chars = 0

        for i, item in enumerate(items):
            # 检查是否需要换段
            should_break = False
            if paragraph and i > 0:
                prev = items[i - 1]
                gap = item.from_time - prev.to_time
                if gap > max_gap:
                    should_break = True
                elif para_chars + len(item.content) > max_chars:
                    should_break = True

            if should_break:
                lines.append(self._add_punctuation(paragraph))
                lines.append("")
                paragraph = []
                para_chars = 0

            paragraph.append(item.content)
            para_chars += len(item.content)

        if paragraph:
            lines.append(self._add_punctuation(paragraph))
            lines.append("")

        return lines

    @staticmethod
    def _add_punctuation(segments: List[str]) -> str:
        """为拼接的字幕片段添加中文标点

        AI字幕原始数据没有标点，条目间用逗号连接，段落末用句号。
        已有标点的字幕（人工上传）不会被重复添加。
        """
        if not segments:
            return ""

        result = []
        for i, seg in enumerate(segments):
            seg = seg.strip()
            if not seg:
                continue

            # 已有尾部标点则保留，否则根据位置添加
            if seg and seg[-1] in '，。、；：！？,…—':
                result.append(seg)
            elif i < len(segments) - 1:
                result.append(seg + '，')
            else:
                result.append(seg + '。')

        return ''.join(result)

    def _generate_bilingual_subtitles(self, translated_items: List[Dict]) -> List[str]:
        """生成双语字幕"""
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
        """格式化时间戳"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def _escape_yaml(text: str) -> str:
        """转义YAML特殊字符"""
        if not text:
            return ""
        return text.replace('\\', '\\\\').replace('"', '\\"')
