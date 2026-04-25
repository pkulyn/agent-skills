"""
配置管理模块
"""
import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


@dataclass
class TranslationConfig:
    """翻译配置"""
    enabled: bool = True
    target_lang: str = "zh-CN"
    source_lang: str = "auto"
    translate_english_only: bool = True


@dataclass
class BilibiliCredential:
    """B站登录凭证"""
    sessdata: str = ""
    bili_jct: str = ""
    buvid3: str = ""

@dataclass
class Bili2ObsidianConfig:
    """主配置类"""
    obsidian_vault_path: str = "D:/pkulyn_vault"
    output_folder: str = "Bilibili"
    default_subtitle_type: str = "ai"  # ai | upload | cc
    include_timestamp: bool = True
    include_metadata: bool = True
    video_info_fetch: bool = True
    translation: TranslationConfig = None
    bilibili_credential: BilibiliCredential = None

    def __post_init__(self):
        if self.translation is None:
            self.translation = TranslationConfig()
        if self.bilibili_credential is None:
            self.bilibili_credential = BilibiliCredential()

    @classmethod
    def from_file(cls, config_path: str) -> "Bili2ObsidianConfig":
        """从配置文件加载"""
        path = Path(config_path)
        if not path.exists():
            return cls()

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 处理嵌套的翻译配置
        translation_data = data.pop('translation', {})
        credential_data = data.pop('bilibili_credential', {})

        config = cls(**data)
        config.translation = TranslationConfig(**translation_data)
        config.bilibili_credential = BilibiliCredential(**credential_data)

        return config

    def to_file(self, config_path: str):
        """保存到配置文件"""
        data = asdict(self)
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_output_path(self) -> Path:
        """获取完整的输出路径"""
        vault_path = Path(self.obsidian_vault_path)
        output_path = vault_path / self.output_folder
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path


# 全局配置实例
_config: Optional[Bili2ObsidianConfig] = None


def get_config() -> Bili2ObsidianConfig:
    """获取全局配置"""
    global _config
    if _config is None:
        # 尝试从配置文件加载
        config_paths = [
            os.path.expanduser("~/.config/bili2obsidian/config.json"),
            os.path.expanduser("~/.bili2obsidian.json"),
            "config.json",
            "config/default.json",  # 项目默认配置
        ]

        for path in config_paths:
            if os.path.exists(path):
                _config = Bili2ObsidianConfig.from_file(path)
                break
        else:
            _config = Bili2ObsidianConfig()

    return _config


def set_config(config: Bili2ObsidianConfig):
    """设置全局配置"""
    global _config
    _config = config
