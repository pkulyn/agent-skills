#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模板管理器 - 支持多级模板查找和自定义模板覆盖
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


class TemplateManager:
    """模板管理器 - 多级模板查找和自定义覆盖"""

    def __init__(self,
                 custom_templates_dir: Optional[str] = None,
                 domain_templates_dir: str = "domain_templates",
                 default_templates_dir: str = "templates"):
        """
        初始化模板管理器

        Args:
            custom_templates_dir: 用户自定义模板目录（最高优先级）
            domain_templates_dir: 领域特定模板目录
            default_templates_dir: 默认模板目录（最低优先级）
        """
        self.custom_templates_dir = Path(custom_templates_dir) if custom_templates_dir else None
        self.domain_templates_dir = Path(domain_templates_dir)
        self.default_templates_dir = Path(default_templates_dir)

        # 确保目录存在
        self.domain_templates_dir.mkdir(exist_ok=True)
        if self.custom_templates_dir:
            self.custom_templates_dir.mkdir(exist_ok=True)

        # 模板缓存
        self._template_cache: Dict[str, str] = {}

    def _get_template_search_paths(self, template_name: str, domain: Optional[str] = None) -> List[Path]:
        """
        获取模板查找路径列表（按优先级排序）

        Args:
            template_name: 模板文件名
            domain: 专业领域（用于领域特定模板）

        Returns:
            模板查找路径列表
        """
        paths = []

        # 1. 用户自定义模板（最高优先级）
        if self.custom_templates_dir:
            paths.append(self.custom_templates_dir / template_name)

        # 2. 领域特定模板
        if domain:
            domain_dir = self.domain_templates_dir / domain
            paths.append(domain_dir / template_name)

        # 3. 默认模板（最低优先级）
        paths.append(self.default_templates_dir / template_name)

        return paths

    def get_template(self, template_name: str, domain: Optional[str] = None,
                    use_cache: bool = True) -> Optional[str]:
        """
        获取模板内容

        Args:
            template_name: 模板文件名
            domain: 专业领域（用于领域特定模板查找）
            use_cache: 是否使用缓存

        Returns:
            模板内容，找不到则返回None
        """
        cache_key = f"{domain or 'default'}:{template_name}"

        # 检查缓存
        if use_cache and cache_key in self._template_cache:
            return self._template_cache[cache_key]

        # 按优先级查找模板
        search_paths = self._get_template_search_paths(template_name, domain)

        for path in search_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 缓存结果
                    if use_cache:
                        self._template_cache[cache_key] = content

                    return content
                except Exception as e:
                    print(f"警告：读取模板文件 {path} 失败: {e}")
                    continue

        return None

    def render_template(self, template_name: str, variables: Dict[str, Any],
                       domain: Optional[str] = None) -> Optional[str]:
        """
        渲染模板（替换变量）

        Args:
            template_name: 模板文件名
            variables: 变量字典
            domain: 专业领域

        Returns:
            渲染后的内容，失败则返回None
        """
        template_content = self.get_template(template_name, domain)
        if template_content is None:
            return None

        # 替换变量 {{variable_name}} 或 {{variable_name:default_value}}
        def replace_variable(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) else ""

            if var_name in variables:
                value = variables[var_name]
                # 处理列表类型
                if isinstance(value, list):
                    return '\n'.join(str(item) for item in value)
                return str(value)
            else:
                return default_value

        # 使用正则表达式替换变量
        rendered = re.sub(r'\{\{(\w+)(?::([^}]+))?\}\}', replace_variable, template_content)

        return rendered

    def save_custom_template(self, template_name: str, content: str) -> bool:
        """
        保存自定义模板

        Args:
            template_name: 模板文件名
            content: 模板内容

        Returns:
            bool: 是否保存成功
        """
        if not self.custom_templates_dir:
            print("错误：未设置自定义模板目录")
            return False

        try:
            template_path = self.custom_templates_dir / template_name
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # 清除缓存
            for key in list(self._template_cache.keys()):
                if key.endswith(f":{template_name}"):
                    del self._template_cache[key]

            return True

        except Exception as e:
            print(f"保存自定义模板失败: {e}")
            return False

    def delete_custom_template(self, template_name: str) -> bool:
        """
        删除自定义模板

        Args:
            template_name: 模板文件名

        Returns:
            bool: 是否删除成功
        """
        if not self.custom_templates_dir:
            return False

        template_path = self.custom_templates_dir / template_name

        if not template_path.exists():
            print(f"自定义模板 {template_name} 不存在")
            return False

        try:
            template_path.unlink()

            # 清除缓存
            for key in list(self._template_cache.keys()):
                if key.endswith(f":{template_name}"):
                    del self._template_cache[key]

            return True

        except Exception as e:
            print(f"删除自定义模板失败: {e}")
            return False

    def list_templates(self, domain: Optional[str] = None) -> Dict[str, List[str]]:
        """
        列出所有可用模板

        Args:
            domain: 专业领域

        Returns:
            按来源分类的模板列表字典
        """
        result = {
            'custom': [],
            'domain': [],
            'default': []
        }

        # 自定义模板
        if self.custom_templates_dir and self.custom_templates_dir.exists():
            result['custom'] = [f.name for f in self.custom_templates_dir.iterdir()
                              if f.is_file()]

        # 领域特定模板
        if domain:
            domain_dir = self.domain_templates_dir / domain
            if domain_dir.exists():
                result['domain'] = [f.name for f in domain_dir.iterdir()
                                   if f.is_file()]

        # 默认模板
        if self.default_templates_dir.exists():
            result['default'] = [f.name for f in self.default_templates_dir.iterdir()
                              if f.is_file()]

        return result

    def clear_cache(self) -> None:
        """清除模板缓存"""
        self._template_cache.clear()


# 便捷函数接口

def get_template_manager(custom_templates_dir: Optional[str] = None) -> TemplateManager:
    """获取模板管理器实例的便捷函数"""
    return TemplateManager(custom_templates_dir=custom_templates_dir)


def render_template_string(template_content: str, variables: Dict[str, Any]) -> str:
    """
    渲染模板字符串（替换变量）

    Args:
        template_content: 模板内容
        variables: 变量字典

    Returns:
        渲染后的内容
    """
    def replace_variable(match):
        var_name = match.group(1)
        default_value = match.group(2) if match.group(2) else ""

        if var_name in variables:
            value = variables[var_name]
            if isinstance(value, list):
                return '\n'.join(str(item) for item in value)
            return str(value)
        else:
            return default_value

    import re
    return re.sub(r'\{\{(\w+)(?::([^}]+))?\}\}', replace_variable, template_content)
