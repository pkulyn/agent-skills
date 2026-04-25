#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自定义领域管理器 - 支持通过JSON文件定义新的专业领域
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class CustomDomainManager:
    """自定义领域管理器 - 支持CRUD操作"""

    def __init__(self, custom_domains_dir: str = "custom_domains"):
        """
        初始化自定义领域管理器

        Args:
            custom_domains_dir: 自定义领域JSON文件存放目录
        """
        self.custom_domains_dir = Path(custom_domains_dir)
        self.custom_domains_dir.mkdir(exist_ok=True)
        self._domains_cache: Dict[str, Dict[str, Any]] = {}
        self._load_all_domains()

    def _load_all_domains(self) -> None:
        """加载所有自定义领域配置"""
        for json_file in self.custom_domains_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    domain_config = json.load(f)
                    domain_name = domain_config.get('name', json_file.stem)
                    self._domains_cache[domain_name] = domain_config
            except Exception as e:
                print(f"警告：加载自定义领域文件 {json_file} 失败: {e}")

    def create_domain(self, name: str, config: Dict[str, Any]) -> bool:
        """
        创建新的自定义领域

        Args:
            name: 领域名称
            config: 领域配置字典

        Returns:
            bool: 是否创建成功
        """
        try:
            # 验证必要字段
            required_fields = ['description', 'soul_core_truths', 'professional_values',
                             'tools', 'workflows']
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"缺少必要字段: {field}")

            # 验证推荐字段（v2.0新增）
            recommended_fields = ['personality_base', 'domain_stance', 'speaking_rules',
                                'taboos', 'emotional_style', 'one_liner',
                                'relationship_vibe', 'vibe']
            missing_recommended = [f for f in recommended_fields if f not in config]
            if missing_recommended:
                print(f"警告：自定义领域 '{name}' 缺少推荐字段: {', '.join(missing_recommended)}")
                print("  推荐字段能显著提升生成配置的质量和人格深度")

            # 设置默认值
            config.setdefault('name', name)
            config.setdefault('code', self._generate_code(name))
            config.setdefault('formality_level', 7)
            config.setdefault('technical_depth', 8)
            config.setdefault('emotional_intelligence', 7)
            config.setdefault('color_scheme', 'blue')
            config.setdefault('personality_base', '专业、务实、有主见。')
            config.setdefault('domain_stance', config.get('soul_core_truths', []))
            config.setdefault('speaking_rules', '短句为主，该直说直说。不确定的时候说"不确定"。')
            config.setdefault('taboos', ['不堆砌术语显得高深'])
            config.setdefault('emotional_style', {
                "high": "对人的状态比较敏感，你不用说我也能感觉到哪里不对。",
                "medium": "能注意到明显的情绪变化。你说了我就帮，不说我专注做事。",
                "low": "主要关注事情本身。有问题直接说，我直接帮你解决。"
            })
            config.setdefault('one_liner', '专业、务实、有主见')
            config.setdefault('relationship_vibe', '可信赖的专业伙伴')
            config.setdefault('vibe', '沉稳可靠')
            config.setdefault('emoji', '✦')

            # 保存到文件
            file_path = self.custom_domains_dir / f"{self._generate_code(name)}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            # 更新缓存
            self._domains_cache[name] = config

            return True

        except Exception as e:
            print(f"创建自定义领域失败: {e}")
            return False

    def get_domain(self, name: str) -> Optional[Dict[str, Any]]:
        """
        获取自定义领域配置

        Args:
            name: 领域名称

        Returns:
            领域配置字典，不存在则返回None
        """
        return self._domains_cache.get(name)

    def update_domain(self, name: str, updates: Dict[str, Any]) -> bool:
        """
        更新自定义领域配置

        Args:
            name: 领域名称
            updates: 要更新的字段

        Returns:
            bool: 是否更新成功
        """
        try:
            if name not in self._domains_cache:
                raise ValueError(f"领域 '{name}' 不存在")

            # 更新配置
            self._domains_cache[name].update(updates)

            # 保存到文件
            code = self._domains_cache[name].get('code', self._generate_code(name))
            file_path = self.custom_domains_dir / f"{code}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._domains_cache[name], f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            print(f"更新自定义领域失败: {e}")
            return False

    def delete_domain(self, name: str) -> bool:
        """
        删除自定义领域

        Args:
            name: 领域名称

        Returns:
            bool: 是否删除成功
        """
        try:
            if name not in self._domains_cache:
                raise ValueError(f"领域 '{name}' 不存在")

            # 获取文件名
            code = self._domains_cache[name].get('code', self._generate_code(name))
            file_path = self.custom_domains_dir / f"{code}.json"

            # 删除文件
            if file_path.exists():
                file_path.unlink()

            # 从缓存中移除
            del self._domains_cache[name]

            return True

        except Exception as e:
            print(f"删除自定义领域失败: {e}")
            return False

    def list_domains(self) -> List[str]:
        """
        列出所有自定义领域名称

        Returns:
            领域名称列表
        """
        return list(self._domains_cache.keys())

    def get_all_domains(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有自定义领域配置

        Returns:
            领域名称到配置的映射字典
        """
        return self._domains_cache.copy()

    def _generate_code(self, name: str) -> str:
        """生成领域代码"""
        import re
        # 转换为拼音或英文，这里简化处理
        code = re.sub(r'[^\w\s]', '', name.lower())
        code = code.replace(' ', '_')
        return code[:50]  # 限制长度


# 便捷函数接口

def create_custom_domain(name: str, config: Dict[str, Any],
                        custom_domains_dir: str = "custom_domains") -> bool:
    """创建自定义领域的便捷函数"""
    manager = CustomDomainManager(custom_domains_dir)
    return manager.create_domain(name, config)


def get_custom_domain(name: str, custom_domains_dir: str = "custom_domains") -> Optional[Dict[str, Any]]:
    """获取自定义领域的便捷函数"""
    manager = CustomDomainManager(custom_domains_dir)
    return manager.get_domain(name)


def list_custom_domains(custom_domains_dir: str = "custom_domains") -> List[str]:
    """列出所有自定义领域的便捷函数"""
    manager = CustomDomainManager(custom_domains_dir)
    return manager.list_domains()
