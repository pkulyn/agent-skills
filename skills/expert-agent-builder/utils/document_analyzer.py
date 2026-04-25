#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文档分析器模块
用于分析用户提供的文档资料，提取用户个人信息和Agent画像信息
支持多种格式：.txt, .md, .json, .docx (待扩展)
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# 尝试导入chardet，如果不可用则使用回退方案
try:
    import chardet
    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False


class DocumentAnalyzer:
    """文档分析器类"""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.extractors = {
            '.txt': self._analyze_text_file,
            '.md': self._analyze_text_file,
            '.json': self._analyze_json_file,
            '.docx': self._analyze_docx_file,
        }

    def analyze_documents(self, documents_path: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        分析文档资料，提取用户个人信息和Agent画像信息

        Args:
            documents_path: 文档路径（可以是文件或目录）

        Returns:
            Tuple[user_profile, agent_profile]: 提取的用户信息和Agent信息
        """
        path = Path(documents_path)

        if not path.exists():
            raise FileNotFoundError(f"文档路径不存在: {documents_path}")

        if path.is_file():
            return self._analyze_single_file(path)
        else:
            return self._analyze_directory(path)

    def _analyze_single_file(self, file_path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """分析单个文件"""
        ext = file_path.suffix.lower()

        if ext not in self.extractors:
            raise ValueError(f"不支持的文件格式: {ext}")

        if self.debug:
            print(f"分析文件: {file_path}")

        return self.extractors[ext](file_path)

    def _analyze_directory(self, dir_path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """分析目录中的所有文档"""
        user_profiles = []
        agent_profiles = []

        # 遍历目录中的所有文件
        for file_path in dir_path.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in self.extractors:
                    try:
                        user_profile, agent_profile = self._analyze_single_file(file_path)
                        user_profiles.append(user_profile)
                        agent_profiles.append(agent_profile)
                    except Exception as e:
                        if self.debug:
                            print(f"分析文件 {file_path} 时出错: {e}")

        # 合并所有提取的信息
        merged_user_profile = self._merge_profiles(user_profiles, 'user')
        merged_agent_profile = self._merge_profiles(agent_profiles, 'agent')

        return merged_user_profile, merged_agent_profile

    def _analyze_text_file(self, file_path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """分析文本文件（.txt, .md）"""
        # 检测文件编码
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding'] or 'utf-8'

        # 读取文件内容
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            content = f.read()

        # 提取信息
        user_profile = self._extract_user_info_from_text(content)
        agent_profile = self._extract_agent_info_from_text(content)

        return user_profile, agent_profile

    def _analyze_json_file(self, file_path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """分析JSON文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 根据JSON结构提取信息
        user_profile = self._extract_from_json(data, 'user')
        agent_profile = self._extract_from_json(data, 'agent')

        return user_profile, agent_profile

    def _analyze_docx_file(self, file_path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """分析Word文档（.docx）"""
        # 暂时使用文本提取，后续可以集成python-docx
        # 先尝试作为文本文件处理
        return self._analyze_text_file(file_path)

    def _extract_user_info_from_text(self, text: str) -> Dict[str, Any]:
        """从文本中提取用户信息"""
        user_info = {
            "basic_info": {},
            "background": {},
            "communication_preferences": {},
            "emotional_preferences": {},
            "project_context": {}
        }

        # 提取姓名
        name_patterns = [
            r'姓名[：:]\s*([^\n]+)',
            r'名字[：:]\s*([^\n]+)',
            r'Name[：:]\s*([^\n]+)',
            r'name[：:]\s*([^\n]+)',
        ]

        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                user_info["basic_info"]["name"] = {"value": match.group(1).strip(), "_说明": "用户的真实姓名或常用称呼"}
                break

        # 提取职业头衔
        title_patterns = [
            r'职业[：:]\s*([^\n]+)',
            r'职位[：:]\s*([^\n]+)',
            r'头衔[：:]\s*([^\n]+)',
            r'Title[：:]\s*([^\n]+)',
            r'Position[：:]\s*([^\n]+)',
        ]

        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                user_info["basic_info"]["professional_title"] = {"value": match.group(1).strip(), "_说明": "用户的职业头衔"}
                break

        # 提取组织/公司
        org_patterns = [
            r'组织[：:]\s*([^\n]+)',
            r'公司[：:]\s*([^\n]+)',
            r'Organization[：:]\s*([^\n]+)',
            r'Company[：:]\s*([^\n]+)',
        ]

        for pattern in org_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                user_info["basic_info"]["organization"] = {"value": match.group(1).strip(), "_说明": "用户所在的组织或公司"}
                break

        # 提取行业
        industry_patterns = [
            r'行业[：:]\s*([^\n]+)',
            r'Industry[：:]\s*([^\n]+)',
        ]

        for pattern in industry_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                user_info["basic_info"]["industry"] = {"value": match.group(1).strip(), "_说明": "用户所在的行业"}
                break

        # 提取教育背景
        education_pattern = r'教育背景[：:]\s*([^\n]+)'
        match = re.search(education_pattern, text)
        if match:
            user_info["background"]["education"] = {"value": [match.group(1).strip()], "_说明": "用户的教育背景"}

        # 提取工作经历
        work_pattern = r'工作经历[：:]\s*([^\n]+)'
        match = re.search(work_pattern, text)
        if match:
            user_info["background"]["work_experience"] = {"value": [match.group(1).strip()], "_说明": "用户的工作经历"}

        # 提取专业领域专长
        expertise_pattern = r'专业领域[：:]\s*([^\n]+)'
        match = re.search(expertise_pattern, text)
        if match:
            user_info["background"]["areas_of_expertise"] = {"value": [match.group(1).strip()], "_说明": "用户的专业领域专长"}

        return user_info

    def _extract_agent_info_from_text(self, text: str) -> Dict[str, Any]:
        """从文本中提取Agent信息"""
        agent_info = {
            "professional_identity": {},
            "core_personality": {},
            "work_behavior": {},
            "environment_understanding": {},
            "specialization_parameters": {},
            "domain_specific_settings": {},
            "learning_and_development": {},
            "other_requirements": {}
        }

        # 提取Agent角色
        role_patterns = [
            r'Agent角色[：:]\s*([^\n]+)',
            r'Agent角色定义[：:]\s*([^\n]+)',
            r'Agent Role[：:]\s*([^\n]+)',
        ]

        for pattern in role_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                agent_info["professional_identity"]["role_definition"] = {"value": match.group(1).strip(), "_说明": "Agent的角色定义"}
                break

        # 提取专业领域
        domain_patterns = [
            r'专业领域[：:]\s*([^\n]+)',
            r'Domain[：:]\s*([^\n]+)',
            r'Expertise[：:]\s*([^\n]+)',
        ]

        for pattern in domain_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                agent_info["professional_identity"]["domain_expertise"] = {"value": match.group(1).strip(), "_说明": "Agent的专业领域"}
                break

        # 提取经验水平
        experience_patterns = [
            r'经验水平[：:]\s*([^\n]+)',
            r'Experience Level[：:]\s*([^\n]+)',
        ]

        for pattern in experience_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                agent_info["professional_identity"]["experience_level"] = {"value": match.group(1).strip(), "_说明": "Agent的经验水平"}
                break

        # 提取核心能力
        competencies_pattern = r'核心能力[：:]\s*([^\n]+)'
        match = re.search(competencies_pattern, text)
        if match:
            competencies = [c.strip() for c in match.group(1).split('、') if c.strip()]
            agent_info["professional_identity"]["key_competencies"] = {"value": competencies, "_说明": "Agent的核心能力"}

        # 提取情感智能水平
        ei_pattern = r'情感智能[：:]\s*(\d+)'
        match = re.search(ei_pattern, text)
        if match:
            agent_info["specialization_parameters"]["emotional_intelligence_level"] = {"value": int(match.group(1)), "_说明": "Agent的情感智能水平"}

        # 提取技术深度
        tech_pattern = r'技术深度[：:]\s*(\d+)'
        match = re.search(tech_pattern, text)
        if match:
            agent_info["specialization_parameters"]["technical_depth"] = {"value": int(match.group(1)), "_说明": "Agent的专业技术深度"}

        # 提取协作强度
        collab_pattern = r'协作强度[：:]\s*(\d+)'
        match = re.search(collab_pattern, text)
        if match:
            agent_info["specialization_parameters"]["collaboration_intensity"] = {"value": int(match.group(1)), "_说明": "Agent的协作强度"}

        return agent_info

    def _extract_from_json(self, data: Dict[str, Any], profile_type: str) -> Dict[str, Any]:
        """从JSON数据中提取信息"""
        if profile_type == 'user':
            # 尝试从常见键名中提取用户信息
            user_keys = ['user_profile', 'user', 'basic_info', '个人信息']
            for key in user_keys:
                if key in data:
                    return self._normalize_profile(data[key], 'user')

        elif profile_type == 'agent':
            # 尝试从常见键名中提取Agent信息
            agent_keys = ['agent_profile', 'agent', 'agent_info', 'Agent信息']
            for key in agent_keys:
                if key in data:
                    return self._normalize_profile(data[key], 'agent')

        # 如果找不到特定键，返回空结构
        if profile_type == 'user':
            return {
                "basic_info": {},
                "background": {},
                "communication_preferences": {},
                "emotional_preferences": {},
                "project_context": {}
            }
        else:
            return {
                "professional_identity": {},
                "core_personality": {},
                "work_behavior": {},
                "environment_understanding": {},
                "specialization_parameters": {},
                "domain_specific_settings": {},
                "learning_and_development": {},
                "other_requirements": {}
            }

    def _normalize_profile(self, profile_data: Dict[str, Any], profile_type: str) -> Dict[str, Any]:
        """规范化配置文件结构"""
        if profile_type == 'user':
            normalized = {
                "basic_info": profile_data.get("basic_info", {}),
                "background": profile_data.get("background", {}),
                "communication_preferences": profile_data.get("communication_preferences", {}),
                "emotional_preferences": profile_data.get("emotional_preferences", {}),
                "project_context": profile_data.get("project_context", {})
            }
        else:  # agent
            normalized = {
                "professional_identity": profile_data.get("professional_identity", {}),
                "core_personality": profile_data.get("core_personality", {}),
                "work_behavior": profile_data.get("work_behavior", {}),
                "environment_understanding": profile_data.get("environment_understanding", {}),
                "specialization_parameters": profile_data.get("specialization_parameters", {}),
                "domain_specific_settings": profile_data.get("domain_specific_settings", {}),
                "learning_and_development": profile_data.get("learning_and_development", {}),
                "other_requirements": profile_data.get("other_requirements", {})
            }

        return normalized

    def _merge_profiles(self, profiles: List[Dict[str, Any]], profile_type: str) -> Dict[str, Any]:
        """合并多个配置文件"""
        if not profiles:
            return self._create_empty_profile(profile_type)

        # 深度合并所有配置文件
        merged = profiles[0].copy()

        for profile in profiles[1:]:
            merged = self._deep_merge(merged, profile)

        return merged

    def _deep_merge(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并两个字典"""
        result = dict1.copy()

        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _create_empty_profile(self, profile_type: str) -> Dict[str, Any]:
        """创建空的配置文件结构"""
        if profile_type == 'user':
            return {
                "basic_info": {},
                "background": {},
                "communication_preferences": {},
                "emotional_preferences": {},
                "project_context": {}
            }
        else:
            return {
                "professional_identity": {},
                "core_personality": {},
                "work_behavior": {},
                "environment_understanding": {},
                "specialization_parameters": {},
                "domain_specific_settings": {},
                "learning_and_development": {},
                "other_requirements": {}
            }


def test_document_analyzer():
    """测试文档分析器"""
    analyzer = DocumentAnalyzer(debug=True)

    # 测试文本文件
    test_text = """姓名：张三
职业：技术总监
组织：云创科技
行业：互联网科技
教育背景：计算机科学硕士
工作经历：10年软件开发经验
专业领域：云计算、大数据
Agent角色：技术架构顾问
专业领域：技术架构
经验水平：高级（7-15年经验）
核心能力：系统架构设计、性能优化、技术债务管理
情感智能：8
技术深度：9
协作强度：8"""

    # 创建测试文件
    test_file = Path("test_document.txt")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_text)

    try:
        user_profile, agent_profile = analyzer.analyze_documents(str(test_file))
        print("用户信息提取结果:")
        print(json.dumps(user_profile, ensure_ascii=False, indent=2))
        print("\nAgent信息提取结果:")
        print(json.dumps(agent_profile, ensure_ascii=False, indent=2))
    finally:
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()


if __name__ == "__main__":
    test_document_analyzer()