#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能领域检测器 - 根据Agent描述自动推荐最合适的专业领域
"""

import re
from difflib import SequenceMatcher
from typing import Dict, Any, List, Optional, Tuple

from .domain_adapter import DomainAdapter


class DomainDetector:
    """智能领域检测器 - 基于关键词匹配和文本相似度"""

    # 领域关键词映射（权重从1-5，越高表示越重要）
    DOMAIN_KEYWORDS = {
        "技术架构": {
            "keywords": {
                "架构": 5, "系统": 4, "技术": 4, "云原生": 5, "分布式": 5,
                "微服务": 5, "架构师": 5, "技术选型": 4, "性能优化": 4,
                "高可用": 4, "容器": 3, "Kubernetes": 5, "Docker": 4,
                "DevOps": 4, "CI/CD": 4, "基础设施": 4, "中间件": 4
            },
            "patterns": [
                r"架构.*设计", r"技术.*架构", r"系统.*架构",
                r"云原生.*架构", r"分布式.*系统"
            ]
        },

        "法律咨询": {
            "keywords": {
                "法律": 5, "法务": 5, "律师": 5, "合同": 4, "合规": 4,
                "法规": 4, "条款": 4, "诉讼": 4, "仲裁": 4, "知识产权": 4,
                "劳动法": 4, "公司法": 4, "商业法": 4, "法律风险": 4,
                "法律咨询": 5, "法律顾问": 5, "法务咨询": 5
            },
            "patterns": [
                r"法律.*咨询", r"法务.*顾问", r"合同.*审查",
                r"合规.*检查", r"法律.*意见"
            ]
        },

        "商业战略": {
            "keywords": {
                "战略": 5, "商业": 4, "业务": 3, "市场": 4, "竞争": 4,
                "分析": 3, "规划": 4, "咨询": 3, "顾问": 4, "战略师": 5,
                "商业模式": 5, "市场分析": 4, "竞争分析": 4, "财务分析": 4,
                "战略规划": 5, "业务战略": 4, "增长战略": 4, "数字化转型": 4
            },
            "patterns": [
                r"战略.*规划", r"商业.*战略", r"市场.*分析",
                r"竞争.*分析", r"业务.*咨询"
            ]
        },

        "创意设计": {
            "keywords": {
                "设计": 5, "创意": 5, "视觉": 4, "用户体验": 4, "UI": 4,
                "UX": 4, "品牌": 4, "艺术": 4, "美学": 4, "设计师": 5,
                "创意总监": 5, "视觉设计": 4, "产品设计": 4, "平面设计": 4,
                "交互设计": 4, "服务设计": 4, "设计思维": 4, "创意思维": 4
            },
            "patterns": [
                r"创意.*设计", r"视觉.*设计", r"用户体验.*设计",
                r"品牌.*设计", r"UI.*UX"
            ]
        },

        "医学研究": {
            "keywords": {
                "医学": 5, "医疗": 4, "临床": 5, "研究": 4, "医生": 4,
                "医院": 3, "药物": 4, "治疗": 4, "诊断": 4, "医师": 4,
                "临床研究": 5, "医学研究": 5, "临床试验": 5, "循证医学": 4,
                "医学文献": 4, "病理分析": 4, "医学统计": 4, "医学伦理": 4
            },
            "patterns": [
                r"临床.*研究", r"医学.*研究", r"临床.*试验",
                r"医学.*文献", r"循证.*医学"
            ]
        },

        "党政公文写作": {
            "keywords": {
                "党务": 5, "党建": 5, "公文": 5, "文稿": 4, "材料": 4,
                "党委": 4, "支部": 4, "党员": 4, "组织": 3, "纪检": 4,
                "党务工作": 5, "党建工作": 5, "党政公文": 5, "公文写作": 5,
                "发言稿": 4, "工作总结": 4, "调研报告": 4, "党建材料": 5
            },
            "patterns": [
                r"党务.*工作", r"党建.*工作", r"公文.*写作",
                r"党政.*公文", r"党建.*材料"
            ]
        },

        "科幻小说创作": {
            "keywords": {
                "科幻": 5, "小说": 4, "创作": 4, "写作": 4, "文学": 4,
                "故事": 4, "情节": 4, "角色": 4, "世界观": 5, "设定": 4,
                "科幻小说": 5, "小说创作": 5, "科幻创作": 5, "故事创作": 4,
                "人物设定": 4, "情节设计": 4, "世界观构建": 5, "科幻设定": 4
            },
            "patterns": [
                r"科幻.*小说", r"小说.*创作", r"科幻.*创作",
                r"故事.*创作", r"世界观.*构建"
            ]
        }
    }

    def __init__(self):
        """初始化领域检测器"""
        self.domain_adapter = DomainAdapter()

    def detect_domain(self, description: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        检测文本描述最匹配的专业领域

        Args:
            description: Agent描述文本
            top_k: 返回前k个最匹配的领域

        Returns:
            列表，每项为(领域名称, 匹配分数)的元组
        """
        if not description or not description.strip():
            return [("技术架构", 0.0)]

        scores = {}

        # 1. 关键词匹配评分
        for domain, data in self.DOMAIN_KEYWORDS.items():
            score = self._calculate_keyword_score(description, data)
            scores[domain] = score

        # 2. 正则模式匹配（额外加分）
        for domain, data in self.DOMAIN_KEYWORDS.items():
            if 'patterns' in data:
                pattern_matches = 0
                for pattern in data['patterns']:
                    if re.search(pattern, description, re.IGNORECASE):
                        pattern_matches += 1
                # 每个匹配的模式额外加5分
                scores[domain] += pattern_matches * 5

        # 3. 文本相似度计算（针对描述较长的情况）
        if len(description) > 20:
            for domain in scores:
                similarity = self._calculate_similarity(description, domain)
                # 将相似度（0-1）转换为0-20的分数
                scores[domain] += similarity * 20

        # 4. 获取top_k个最匹配的
        sorted_domains = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # 归一化分数（转换为0-100的范围）
        max_score = sorted_domains[0][1] if sorted_domains else 1
        if max_score == 0:
            max_score = 1

        normalized_results = [
            (domain, min(100, round((score / max_score) * 100, 1)))
            for domain, score in sorted_domains[:top_k]
        ]

        return normalized_results

    def _calculate_keyword_score(self, description: str, domain_data: Dict) -> float:
        """
        计算关键词匹配分数

        Args:
            description: 描述文本
            domain_data: 领域数据（包含关键词和权重）

        Returns:
            匹配分数
        """
        score = 0.0
        description_lower = description.lower()

        keywords = domain_data.get('keywords', {})
        for keyword, weight in keywords.items():
            # 检查关键词是否出现在描述中
            if keyword.lower() in description_lower:
                # 计算出现次数
                count = description_lower.count(keyword.lower())
                # 前3次出现计分，之后权重递减
                for i in range(min(count, 3)):
                    multiplier = 1.0 if i == 0 else (0.5 if i == 1 else 0.25)
                    score += weight * multiplier

        return score

    def _calculate_similarity(self, description: str, domain: str) -> float:
        """
        计算描述与领域的文本相似度

        Args:
            description: 描述文本
            domain: 领域名称

        Returns:
            相似度分数（0-1）
        """
        # 使用SequenceMatcher计算相似度
        domain_data = self.DOMAIN_KEYWORDS.get(domain, {})

        # 构建领域参考文本（关键词加权）
        reference_parts = []

        # 添加领域名称
        reference_parts.append(domain * 3)  # 重复3次增加权重

        # 添加关键词
        keywords = domain_data.get('keywords', {})
        for keyword, weight in sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]:
            repeat_count = max(1, weight // 2)
            reference_parts.append(keyword * repeat_count)

        reference_text = ' '.join(reference_parts)

        # 计算相似度
        matcher = SequenceMatcher(None, description.lower(), reference_text.lower())
        return matcher.ratio()

    def get_domain_confidence(self, description: str, domain: str) -> float:
        """
        获取描述与特定领域的匹配置信度

        Args:
            description: 描述文本
            domain: 领域名称

        Returns:
            置信度分数（0-100）
        """
        results = self.detect_domain(description, top_k=10)

        for dom, score in results:
            if dom == domain:
                return score

        return 0.0

    def suggest_domain(self, description: str, threshold: float = 60.0) -> Optional[str]:
        """
        根据描述建议最合适的领域

        Args:
            description: 描述文本
            threshold: 置信度阈值，低于此值返回None

        Returns:
            建议的领域名称，置信度不足则返回None
        """
        results = self.detect_domain(description, top_k=1)

        if not results:
            return None

        domain, score = results[0]

        if score >= threshold:
            return domain

        return None


# 便捷函数接口

def detect_domain(description: str, top_k: int = 3) -> List[Tuple[str, float]]:
    """检测领域的便捷函数"""
    detector = DomainDetector()
    return detector.detect_domain(description, top_k)


def suggest_domain(description: str, threshold: float = 60.0) -> Optional[str]:
    """建议领域的便捷函数"""
    detector = DomainDetector()
    return detector.suggest_domain(description, threshold)
