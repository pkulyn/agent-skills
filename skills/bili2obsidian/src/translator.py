"""
字幕翻译模块
使用 deep-translator 进行字幕翻译
"""
from dataclasses import dataclass
from typing import List, Optional
import re


@dataclass
class TranslatedSubtitle:
    """翻译后的字幕条目"""
    from_time: float
    to_time: float
    original: str
    translated: str


class SubtitleTranslator:
    """字幕翻译器"""

    def __init__(self, target_lang: str = "zh-CN", source_lang: str = "auto"):
        """
        初始化翻译器

        Args:
            target_lang: 目标语言代码
            source_lang: 源语言代码（auto为自动检测）
        """
        self.target_lang = target_lang
        self.source_lang = source_lang
        self._translator = None

    def _get_translator(self):
        """获取翻译器实例（延迟加载）"""
        if self._translator is None:
            try:
                from deep_translator import GoogleTranslator
                self._translator = GoogleTranslator(
                    source=self.source_lang,
                    target=self.target_lang
                )
            except ImportError:
                raise ImportError(
                    "deep-translator未安装，请运行: pip install deep-translator"
                )
        return self._translator

    def _is_english(self, text: str) -> bool:
        """
        检测文本是否为英文

        Args:
            text: 待检测文本

        Returns:
            是否为英文内容
        """
        if not text or not text.strip():
            return False

        # 移除标点、数字、空格
        cleaned = re.sub(r'[^\w\s]', '', text)
        cleaned = re.sub(r'\d+', '', cleaned)
        cleaned = cleaned.strip()

        if not cleaned:
            return False

        # 统计英文字符比例
        english_chars = len(re.findall(r'[a-zA-Z]', cleaned))
        total_chars = len(cleaned.replace(' ', ''))

        if total_chars == 0:
            return False

        # 英文字符占比超过70%认为是英文
        return english_chars / total_chars > 0.7

    def translate_text(self, text: str, force_translate: bool = False) -> str:
        """
        翻译单个文本

        Args:
            text: 待翻译文本
            force_translate: 是否强制翻译（忽略语言检测）

        Returns:
            翻译后的文本
        """
        if not text or not text.strip():
            return text

        # 检测是否需要翻译
        if not force_translate and not self._is_english(text):
            # 非英文内容，原样返回
            return text

        try:
            translator = self._get_translator()
            result = translator.translate(text)
            return result if result else text
        except Exception as e:
            print(f"翻译失败: {e}")
            return text

    def translate_subtitles(
        self,
        subtitles: List[dict],
        translate_english_only: bool = True
    ) -> List[TranslatedSubtitle]:
        """
        批量翻译字幕

        Args:
            subtitles: 字幕条目列表，每项包含from_time, to_time, content
            translate_english_only: 是否只翻译英文字幕

        Returns:
            翻译后的字幕列表
        """
        result = []

        # 批量处理，每10条翻译一次（避免请求过快）
        batch_size = 10
        for i in range(0, len(subtitles), batch_size):
            batch = subtitles[i:i + batch_size]

            for item in batch:
                from_time = item.get('from_time', 0)
                to_time = item.get('to_time', 0)
                content = item.get('content', '')

                if not content:
                    continue

                # 判断是否需要翻译
                need_translate = True
                if translate_english_only and not self._is_english(content):
                    need_translate = False

                if need_translate:
                    translated = self.translate_text(content, force_translate=True)
                else:
                    translated = content

                result.append(TranslatedSubtitle(
                    from_time=from_time,
                    to_time=to_time,
                    original=content,
                    translated=translated
                ))

        return result

    def format_bilingual(
        self,
        translated_subtitles: List[TranslatedSubtitle],
        show_original: bool = True
    ) -> str:
        """
        格式化双语字幕

        Args:
            translated_subtitles: 翻译后的字幕列表
            show_original: 是否显示原文

        Returns:
            格式化后的字幕文本
        """
        lines = []

        for item in translated_subtitles:
            # 时间戳
            from_str = self._format_time(item.from_time)
            to_str = self._format_time(item.to_time)

            if show_original and item.original != item.translated:
                # 双语显示
                lines.append(f"[{from_str}] {item.original}")
                lines.append(f"         {item.translated}")
            else:
                # 仅显示翻译
                lines.append(f"[{from_str}] {item.translated}")

            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _format_time(seconds: float) -> str:
        """格式化时间为 HH:MM:SS 或 MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"


# 便捷函数
def translate_subtitle_text(
    text: str,
    target_lang: str = "zh-CN",
    translate_english_only: bool = True
) -> str:
    """
    快速翻译单条字幕

    Args:
        text: 字幕文本
        target_lang: 目标语言
        translate_english_only: 是否只翻译英文

    Returns:
        翻译后的文本
    """
    translator = SubtitleTranslator(target_lang=target_lang)

    if translate_english_only and not translator._is_english(text):
        return text

    return translator.translate_text(text, force_translate=True)
