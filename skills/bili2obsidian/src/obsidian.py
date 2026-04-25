"""
Obsidian知识库文件操作模块
处理Markdown文件的保存、更新和索引
"""
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


class ObsidianManager:
    """Obsidian知识库管理器"""

    def __init__(self, vault_path: str, output_folder: str = "Bilibili"):
        """
        初始化管理器

        Args:
            vault_path: Obsidian Vault根路径
            output_folder: 输出子文件夹名称
        """
        self.vault_path = Path(vault_path)
        self.output_folder = output_folder
        self.output_path = self.vault_path / output_folder

        # 确保输出目录存在
        self.output_path.mkdir(parents=True, exist_ok=True)

    def save_markdown(
        self,
        content: str,
        filename: str,
        bvid: str = ""
    ) -> str:
        """
        保存Markdown文件

        Args:
            content: Markdown内容
            filename: 文件名（不含扩展名）
            bvid: 视频BV号（用于元数据）

        Returns:
            保存的文件完整路径
        """
        # 清理文件名中的非法字符
        safe_filename = self._sanitize_filename(filename)
        file_path = self.output_path / f"{safe_filename}.md"

        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(file_path)

    def update_index(self, video_entries: List[Dict[str, Any]]) -> str:
        """
        更新索引文件

        Args:
            video_entries: 视频条目列表，每项包含title, bvid, up, date等信息

        Returns:
            索引文件路径
        """
        index_path = self.output_path / "index.md"

        lines = []
        lines.append("---")
        lines.append(f"title: \"Bilibili字幕索引\"")
        lines.append(f"date: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append("category: \"索引\"")
        lines.append("---")
        lines.append("")
        lines.append("# Bilibili字幕索引")
        lines.append("")
        lines.append(f"*最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        lines.append("")
        lines.append(f"**共计 {len(video_entries)} 个视频字幕**")
        lines.append("")

        # 按日期分组
        entries_by_date: Dict[str, List[Dict]] = {}
        for entry in video_entries:
            date = entry.get('date', '未知日期')
            if date not in entries_by_date:
                entries_by_date[date] = []
            entries_by_date[date].append(entry)

        # 生成表格
        lines.append("## 视频列表")
        lines.append("")
        lines.append("| 日期 | 标题 | UP主 | 链接 |")
        lines.append("|------|------|------|------|")

        for date in sorted(entries_by_date.keys(), reverse=True):
            for entry in entries_by_date[date]:
                title = entry.get('title', '未知标题')
                up = entry.get('up', '未知UP')
                bvid = entry.get('bvid', '')
                filename = entry.get('filename', '')

                # 链接到本地文件
                if filename:
                    link = f"[{bvid}](./{filename}.md)"
                else:
                    link = f"[{bvid}](https://www.bilibili.com/video/{bvid})"

                lines.append(f"| {date} | {title} | {up} | {link} |")

        lines.append("")

        # 添加标签统计
        lines.append("## 标签统计")
        lines.append("")

        all_tags: Dict[str, int] = {}
        for entry in video_entries:
            for tag in entry.get('tags', []):
                all_tags[tag] = all_tags.get(tag, 0) + 1

        if all_tags:
            # 按出现次数排序
            sorted_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)
            for tag, count in sorted_tags[:20]:  # 只显示前20个
                lines.append(f"- #{tag} ({count})")
        else:
            lines.append("*暂无标签统计*")

        lines.append("")

        # 写入文件
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        return str(index_path)

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        清理文件名中的非法字符

        Args:
            filename: 原始文件名

        Returns:
            安全的文件名
        """
        # Windows非法字符: < > : " / \ | ? *
        # 替换为下划线或空格
        invalid_chars = '<>:"/\\|?*'

        result = filename
        for char in invalid_chars:
            result = result.replace(char, '_')

        # 移除前后空格和点
        result = result.strip('. ')

        # 限制长度（Windows路径最大260字符）
        max_len = 100  # 给扩展名和其他部分留空间
        if len(result) > max_len:
            result = result[:max_len]

        return result if result else "untitled"

    def get_output_path(self) -> Path:
        """获取输出路径"""
        return self.output_path

    def get_vault_path(self) -> Path:
        """获取Vault根路径"""
        return self.vault_path

    def get_extracted_bvids(self) -> set:
        """
        获取所有已提取的视频BV号集合

        Returns:
            已提取的BV号集合
        """
        extracted_bvids = set()

        # 遍历所有.md文件
        for md_file in self.output_path.glob("*.md"):
            if md_file.name == "index.md":
                continue  # 跳过索引文件

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                # 查找YAML Front Matter
                in_front_matter = False
                for line in lines:
                    stripped_line = line.strip()
                    if stripped_line == "---":
                        if not in_front_matter:
                            in_front_matter = True
                        else:
                            break  # YAML结束
                    elif in_front_matter:
                        # 匹配bvid字段
                        if stripped_line.startswith("bvid:"):
                            # 提取bvid值，格式为 bvid: "BV1xx411c7mZ" 或 bvid: BV1xx411c7mZ
                            bvid_match = re.search(r'bvid:\s*["\']?([A-Za-z0-9]+)["\']?', line)
                            if bvid_match:
                                bvid = bvid_match.group(1)
                                if bvid.startswith("BV"):
                                    extracted_bvids.add(bvid)
                            break  # 找到bvid就不用继续看了

            except Exception as e:
                print(f"读取文件{md_file}时出错: {e}")
                continue

        return extracted_bvids
