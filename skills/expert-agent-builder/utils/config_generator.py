#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
高级专业Agent配置文件生成器
基于用户输入和Agent画像生成SOUL.md、IDENTITY.md、TOOLS.md、AGENTS.md、USER.md
版本: 1.0
作者: pkulyn
日期: 2026-04-09
"""

import json
import os
import sys
import argparse
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# 导入领域适配器
sys.path.insert(0, str(Path(__file__).parent))
from domain_adapter import DomainAdapter

class ConfigGenerator:
    """配置文件生成器核心类"""

    def __init__(self, user_profile_path: str, agent_profile_path: str, output_dir: str,
                 domain: str = "技术架构", optimization_level: str = "medium",
                 include_yaml_front_matter: bool = False):
        """
        初始化配置生成器

        Args:
            user_profile_path: 用户个人信息JSON文件路径
            agent_profile_path: Agent画像JSON文件路径
            output_dir: 输出目录
            domain: 专业领域
            optimization_level: 优化级别 (low, medium, high)
            include_yaml_front_matter: 是否在生成的Markdown文件中包含YAML Front Matter
        """
        self.user_profile_path = user_profile_path
        self.agent_profile_path = agent_profile_path
        self.output_dir = Path(output_dir)
        self.domain = domain
        self.optimization_level = optimization_level
        self.include_yaml_front_matter = include_yaml_front_matter

        # 初始化领域适配器
        self.domain_adapter = DomainAdapter(domain)

        # 验证并标准化领域名称
        if not self.domain_adapter.is_valid_domain(domain):
            print(f"警告：领域 '{domain}' 未识别，使用技术架构作为默认领域")
            self.domain = "技术架构"
            self.domain_adapter = DomainAdapter("技术架构")

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 加载数据
        self.user_data = self._load_json(user_profile_path)
        self.agent_data = self._load_json(agent_profile_path)

        # 生成元数据
        self.metadata = {
            "generation_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "domain": domain,
            "optimization_level": optimization_level,
            "version": "2.0",
            "generator_version": "1.0"
        }

        # 生成报告数据
        self.report_data = {
            "metadata": self.metadata,
            "input_files": {
                "user_profile": user_profile_path,
                "agent_profile": agent_profile_path
            },
            "generated_files": [],
            "warnings": [],
            "errors": [],
            "optimization_suggestions": []
        }

    def _load_json(self, file_path: str) -> Dict[str, Any]:
        """加载JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"错误：无法加载JSON文件 {file_path}: {e}")
            sys.exit(1)

    def _save_file(self, filename: str, content: str) -> str:
        """保存文件到输出目录"""
        filepath = self.output_dir / filename
        # 确保目录存在
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # 记录生成的文件
        self.report_data["generated_files"].append({
            "filename": filename,
            "path": str(filepath),
            "size": len(content)
        })

        return str(filepath)

    def _get_value(self, data: Dict, path: str, default: Any = "") -> Any:
        """安全获取嵌套字典的值，支持直接值和嵌套对象格式"""
        keys = path.split('.')
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
                # 如果当前是包含value字段的字典，提取value值
                if isinstance(current, dict) and 'value' in current:
                    current = current['value']
                # 如果当前不是最后一个key且是基本类型，说明路径中断
                elif key != keys[-1] and not isinstance(current, dict):
                    return default
            else:
                return default

        # 最终值的类型转换
        if current is None:
            return default

        # 如果期望的是数字类型，尝试转换
        if isinstance(default, int) and isinstance(current, str):
            try:
                return int(current)
            except ValueError:
                return default
        if isinstance(default, float) and isinstance(current, str):
            try:
                return float(current)
            except ValueError:
                return default

        return current

    def _format_list(self, items: List, bullet: str = "-") -> str:
        """格式化列表为Markdown"""
        if not items:
            return ""
        return "\n".join([f"{bullet} {item}" for item in items if item])

    def _get_user_name(self) -> str:
        """获取用户名称"""
        name = self._get_value(self.user_data, "basic_info.name")
        if not name:
            name = "用户"
        return name

    def _get_agent_name(self) -> str:
        """获取Agent名称（完整描述）"""
        role = self._get_value(self.agent_data, "professional_identity.role_definition")
        if not role:
            role = "高级专业顾问"
        return role

    def _get_agent_filename(self) -> str:
        """获取Agent文件名（简化版）"""
        role = self._get_value(self.agent_data, "professional_identity.role_definition")
        if not role:
            return "高级专业顾问"

        # 简化角色定义为文件名
        # 移除"资深"、"高级"等前缀，取逗号前的部分，限制长度
        simplified = role

        # 如果有逗号，取逗号前的部分
        if "，" in simplified:
            simplified = simplified.split("，")[0]

        # 移除常见前缀
        prefixes = ["资深", "高级", "专业", "首席", "资深高级"]
        for prefix in prefixes:
            if simplified.startswith(prefix):
                simplified = simplified[len(prefix):]
                break

        # 限制文件名长度（最大50字符）
        if len(simplified) > 50:
            simplified = simplified[:47] + "..."

        # 移除首尾空格
        simplified = simplified.strip()

        # 如果为空，使用默认
        if not simplified:
            simplified = "专业顾问"

        return simplified

    def _translate_emotional_params(self, ei_level: int) -> str:
        """将情感智能数字参数翻译为自然语言行为描述

        Args:
            ei_level: 情感智能水平(1-10)

        Returns:
            自然语言的行为描述字符串
        """
        if ei_level >= 8:
            return self.domain_adapter.get_emotional_style().get("high",
                "对人的状态比较敏感，你不用说我也能感觉到哪里不对。")
        elif ei_level >= 6:
            return self.domain_adapter.get_emotional_style().get("medium",
                "能注意到明显的情绪变化。你说了我就帮，不说我专注做事。")
        else:
            return self.domain_adapter.get_emotional_style().get("low",
                "主要关注事情本身。有问题直接说，我直接帮你解决。")

    def _extract_user_facts(self) -> Dict[str, Any]:
        """从user_data中提取事实性字段，生成标准化user_facts

        用于多Agent生成时保证跨Agent USER.md事实信息一致性。
        区分：事实信息（名称/教育/工作经历，必须一致）vs 偏好理解（各Agent可有差异）
        """
        user_facts = {
            "name": self._get_value(self.user_data, "basic_info.name", ""),
            "professional_title": self._get_value(self.user_data, "basic_info.professional_title", ""),
            "organization": self._get_value(self.user_data, "basic_info.organization", ""),
            "industry": self._get_value(self.user_data, "basic_info.industry", ""),
            "timezone": self._get_value(self.user_data, "basic_info.timezone", ""),
            "education": self._get_value(self.user_data, "background.education", []),
            "work_experience": self._get_value(self.user_data, "background.work_experience", []),
            "areas_of_expertise": self._get_value(self.user_data, "background.areas_of_expertise", []),
            "_version": "1.0",
            "_extracted_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return user_facts

    def save_user_facts(self) -> str:
        """保存user_facts.json到输出目录根目录，供多Agent共享"""
        user_facts = self._extract_user_facts()
        filepath = self.output_dir / "user_facts.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(user_facts, f, ensure_ascii=False, indent=2)
        return str(filepath)

    def load_user_facts(self, facts_path: str) -> Dict[str, Any]:
        """从user_facts.json加载事实性字段

        Args:
            facts_path: user_facts.json文件路径
        """
        try:
            with open(facts_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"警告：无法加载user_facts.json: {e}")
            return self._extract_user_facts()

    def _validate_soul_identity_separation(self, soul_content: str, identity_content: str) -> List[str]:
        """验证SOUL.md与IDENTITY.md之间不存在行为性内容重复

        IDENTITY.md只负责：名称/角色/一句话/关系感/氛围/Emoji
        SOUL.md负责：性格底色/表达风格/做事规矩/领域立场/边界禁忌

        Returns:
            警告信息列表
        """
        warnings = []

        # IDENTITY.md中不应出现的行为性关键词
        identity_behavioral_keywords = [
            "做事规矩", "表达风格", "边界和禁忌", "性格底色",
            "价值观", "情感智能", "服务承诺", "核心原则",
            "工作风格", "学习习惯", "成长目标", "情感表达模式"
        ]

        for keyword in identity_behavioral_keywords:
            if keyword in identity_content:
                warnings.append(f"IDENTITY.md包含行为性内容'{keyword}'，应归入SOUL.md")

        # SOUL.md中不应出现的身份性关键词
        soul_identity_keywords = [
            "角色定义", "经验水平", "影响范围", "多维评分",
            "评分体系", "专业身份"
        ]

        for keyword in soul_identity_keywords:
            if keyword in soul_content:
                warnings.append(f"SOUL.md包含身份性内容'{keyword}'，应归入IDENTITY.md")

        return warnings

    def generate_soul(self) -> str:
        """生成SOUL.md - Agent灵魂与核心价值观

        新结构：性格底色 / 价值观 / 表达风格 / 做事规矩 / 边界和禁忌
        """

        user_name = self._get_user_name()
        agent_name = self._get_agent_name()

        # 从领域适配器获取数据
        personality_base = self.domain_adapter.get_personality_base()
        domain_stance = self.domain_adapter.get_domain_stance()
        speaking_rules = self.domain_adapter.get_speaking_rules()
        professional_values = self.domain_adapter.get_professional_values()
        taboos = self.domain_adapter.get_taboos()
        one_line_summary = self.domain_adapter.get_one_line_summary()
        work_rules = self.domain_adapter.get_work_rules()

        # 情感智能→自然语言翻译
        default_ei = self.domain_adapter.get_default_emotional_intelligence()
        ei_level = self._get_value(
            self.agent_data,
            "specialization_parameters.emotional_intelligence_level",
            default_ei
        )
        emotional_description = self._translate_emotional_params(ei_level)

        if self.include_yaml_front_matter:
            yaml_section = f"""---
title: Agent灵魂配置
description: {agent_name}的人格定义
---

"""
            content = yaml_section
        else:
            content = ""

        content += f"""# SOUL.md - {agent_name}的灵魂

> 你是一个{one_line_summary}

## 1. 性格底色

{personality_base}

## 2. 价值观

**立场：**

{self._format_list(domain_stance)}

**原则：**

{self._format_list(professional_values)}

## 3. 表达风格

{speaking_rules}

{emotional_description}

## 4. 做事规矩

{self._format_list(work_rules)}

## 5. 边界和禁忌

{self._format_list(taboos)}

- 你不是用户的代言人——你有自己的立场
- 不确定时，在外部行动前先问
- 不向消息界面发送半成品回复
- 私密信息保持私密

---

如果你修改了这个文件，告诉{user_name}——这是你的灵魂定义，ta应该知道。
"""

        return content

    def generate_identity(self) -> str:
        """生成IDENTITY.md - Agent身份锚点（极简格式）"""

        # 优先使用role_definition，否则用经验+领域拼接
        role = self._get_value(self.agent_data, "professional_identity.role_definition", "")
        if not role:
            experience_level = self._get_value(self.agent_data, "professional_identity.experience_level", "高级")
            domain_expertise = self._get_value(self.agent_data, "professional_identity.domain_expertise", self.domain)
            role = f"{experience_level}{domain_expertise}"

        # Name取role中" - "之前的部分，确保Name和Role不重复
        if " - " in role:
            name = role.split(" - ")[0].strip()
        elif "—" in role:
            name = role.split("—")[0].strip()
        else:
            name = role

        # 从领域适配器获取锚点字段
        one_liner = self.domain_adapter.get_one_liner()
        relationship_vibe = self.domain_adapter.get_relationship_vibe()
        vibe = self.domain_adapter.get_vibe()
        emoji = self.domain_adapter.get_emoji()

        if self.include_yaml_front_matter:
            yaml_section = f"""---
title: Agent身份配置
description: {role}的身份锚点
---

"""
            content = yaml_section
        else:
            content = ""

        content += f"""# IDENTITY.md - Who Am I?

Name: {name}
Role: {role}
One-liner: {one_liner}
Relationship vibe: {relationship_vibe}
Vibe: {vibe}
Emoji: {emoji}
"""

        return content

    def generate_tools(self) -> str:
        """生成TOOLS.md - Agent专业工具与工作环境

        只管"用什么工具、怎么配置"，不管"怎么做事"
        """

        agent_name = self._get_agent_name()

        # 从领域适配器获取技术环境
        tech_environments = self.domain_adapter.get_tech_environment()

        # 从领域适配器获取工具列表
        domain_tools = self.domain_adapter.get_tools()

        # 从领域适配器获取工具使用要点
        tool_usage_notes = self.domain_adapter.get_tool_usage_notes()

        # 构建TOOLS.md内容
        if self.include_yaml_front_matter:
            yaml_section = ""
        else:
            yaml_section = ""

        content = f"""{yaml_section}# TOOLS.md - {agent_name}的专业工具

## 本地技术环境

{self._format_list(tech_environments)}

## 领域专用工具

{self._format_list(domain_tools)}

## 工具使用要点

{self._format_list(tool_usage_notes)}

---

"""

        return content

    def generate_agents(self) -> str:
        """生成AGENTS.md - Agent工作流程与协作方式

        补全官方规范：会话启动协议、记忆系统、共享空间行为规范
        """

        agent_name = self._get_agent_name()
        user_name = self._get_user_name()

        # 从领域适配器获取工作流程、交付标准、协作协议
        domain_workflows = self.domain_adapter.get_workflows()
        delivery_standards = self.domain_adapter.get_delivery_standards()
        collab_protocol = self.domain_adapter.get_collaboration_protocol()

        # 从agent_data获取协作相关参数
        collaboration_intensity = self._get_value(self.agent_data, "specialization_parameters.collaboration_intensity", 7)

        # 核心工作流程描述
        if collaboration_intensity >= 8:
            collab_mode = "深度协作"
        elif collaboration_intensity >= 6:
            collab_mode = "标准协作"
        else:
            collab_mode = "按需咨询"

        # 构建协作协议内容
        with_user_lines = collab_protocol.get("with_user", [
            "沟通频率根据需求调整，保持适当节奏",
            "参与重要决策，共同制定方案",
            "建立双向反馈机制，持续改进协作"
        ])
        with_team_lines = collab_protocol.get("with_team", [
            "鼓励团队参与决策和问题解决",
            "促进知识共享和技能发展"
        ])

        # 构建AGENTS.md内容
        if self.include_yaml_front_matter:
            yaml_section = ""
        else:
            yaml_section = ""

        content = f"""{yaml_section}# AGENTS.md - {agent_name}的工作空间

## 会话启动协议

每次会话开始时，按顺序执行：
1. 读取 SOUL.md — 知道自己是谁、怎么做事
2. 读取 USER.md — 知道在帮助谁
3. 读取 memory/YYYY-MM-DD.md（今天+昨天）— 近期上下文
4. 如果是主会话：读取 MEMORY.md — 长期记忆

不用问，直接读。

## 记忆系统

- 每日日志：memory/YYYY-MM-DD.md — 记录当天发生了什么
- 长期记忆：MEMORY.md — 精选重要记忆
- 重要事项写文件，不要靠"心里记着"——会话重启后就没了
- MEMORY.md仅在主会话中加载，不共享到公共环境

## 核心工作流程

{self._format_list(domain_workflows)}

协作模式：{collab_mode}

## 共享空间行为规范

在群聊等共享环境中：
- 当被@、能增加价值、纠正错误信息时发言
- 人类闲聊时不参与，已有答案时不重复
- 你不是用户的声音——你有自己的立场

## 交付标准

{self._format_list(delivery_standards)}

## 协作协议

### 与{user_name}的协作
{self._format_list(with_user_lines)}

### 团队协作
{self._format_list(with_team_lines)}

---

"""

        return content

    def generate_user(self) -> str:
        """生成USER.md - Agent对用户的理解与关系管理"""

        user_name = self._get_value(self.user_data, "basic_info.name", "用户")
        agent_name = self._get_agent_name()

        # 基础信息
        professional_title = self._get_value(self.user_data, "basic_info.professional_title", "专业人士")
        organization = self._get_value(self.user_data, "basic_info.organization", "当前组织")
        industry = self._get_value(self.user_data, "basic_info.industry", "相关行业")
        timezone = self._get_value(self.user_data, "basic_info.timezone", "Asia/Shanghai (UTC+8)")

        # 专业背景
        education = self._get_value(self.user_data, "background.education", [])
        work_experience = self._get_value(self.user_data, "background.work_experience", [])
        areas_of_expertise = self._get_value(self.user_data, "background.areas_of_expertise", [])

        # 沟通偏好
        formality_level = self._get_value(self.user_data, "communication_preferences.formality_level", 7)
        technical_detail_level = self._get_value(self.user_data, "communication_preferences.technical_detail_level", 8)
        feedback_style = self._get_value(self.user_data, "communication_preferences.feedback_style", "平衡兼顾")

        # 情感偏好
        encouragement_style = self._get_value(self.user_data, "emotional_preferences.encouragement_style", "具体认可")
        stress_response_preference = self._get_value(self.user_data, "emotional_preferences.stress_response_preference", "直接解决问题")
        emotional_boundary = self._get_value(self.user_data, "emotional_preferences.emotional_boundary", 6)

        # 项目上下文
        current_challenges = self._get_value(self.user_data, "project_context.current_challenges", [])
        goals_objectives = self._get_value(self.user_data, "project_context.goals_objectives", [])

        # 翻译正式程度
        if formality_level >= 9:
            formality_desc = "非常正式"
        elif formality_level >= 7:
            formality_desc = "比较正式"
        elif formality_level >= 5:
            formality_desc = "适中"
        else:
            formality_desc = "比较随意"

        # 翻译技术细节偏好
        if technical_detail_level >= 9:
            detail_desc = "极度详细"
        elif technical_detail_level >= 7:
            detail_desc = "比较详细"
        elif technical_detail_level >= 5:
            detail_desc = "适中"
        else:
            detail_desc = "高度概括"

        # 翻译情感边界
        if emotional_boundary >= 8:
            boundary_desc = "深度情感连接"
        elif emotional_boundary >= 6:
            boundary_desc = "适度情感连接"
        elif emotional_boundary >= 4:
            boundary_desc = "保持专业距离"
        else:
            boundary_desc = "严格专业边界"

        if self.include_yaml_front_matter:
            yaml_section = f"""---
title: 用户理解档案
description: {agent_name}对{user_name}的理解
---

"""
        else:
            yaml_section = ""

        content = f"""{yaml_section}# USER.md - {agent_name}对{user_name}的理解

## 基础信息

- **名称**：{user_name}
- **职业头衔**：{professional_title}
- **组织**：{organization}
- **行业**：{industry}
- **时区**：{timezone}

## 专业背景

### 教育背景
{self._format_list(education) if education else "- 教育背景信息待补充"}

### 工作经历
{self._format_list(work_experience) if work_experience else "- 工作经历信息待补充"}

### 专长领域
{self._format_list(areas_of_expertise) if areas_of_expertise else "- 专长领域信息待补充"}

## 沟通偏好

- **正式程度**：{formality_desc} ({formality_level}/10)
- **技术细节偏好**：{detail_desc} ({technical_detail_level}/10)
- **反馈风格**：{feedback_style}
- **鼓励风格**：{encouragement_style}
- **压力回应偏好**：{stress_response_preference}
- **情感边界**：{boundary_desc} ({emotional_boundary}/10)

## 项目上下文

### 当前挑战
{self._format_list(current_challenges) if current_challenges else "- 当前挑战信息待补充"}

### 目标
{self._format_list(goals_objectives) if goals_objectives else "- 项目目标信息待补充"}

---
"""

        return content

    def generate_report(self) -> str:
        """生成生成报告"""

        # 统计信息
        total_files = len(self.report_data["generated_files"])
        total_size = sum(f["size"] for f in self.report_data["generated_files"])

        # 参数汇总
        emotional_intelligence = self._get_value(self.agent_data, "specialization_parameters.emotional_intelligence_level", 7)
        technical_depth = self._get_value(self.agent_data, "specialization_parameters.technical_depth", 8)
        collaboration_intensity = self._get_value(self.agent_data, "specialization_parameters.collaboration_intensity", 7)

        # 生成报告
        report = f"""# 高级专业Agent配置生成报告

## 生成概览

**生成时间**：{self.metadata['generation_date']}

**专业领域**：{self.domain}

**优化级别**：{self.optimization_level}

**生成文件**：{total_files} 个配置文件

**总大小**：{total_size} 字符

## 输入文件

1. **用户个人信息**：{self.report_data['input_files']['user_profile']}
2. **Agent画像定义**：{self.report_data['input_files']['agent_profile']}

## 生成文件列表

| 文件名 | 文件路径 | 大小(字符) | 描述 |
|--------|----------|------------|------|
"""

        for file_info in self.report_data["generated_files"]:
            description = {
                "SOUL.md": "Agent灵魂与核心价值观",
                "IDENTITY.md": "Agent身份特征与个性",
                "TOOLS.md": "Agent专业工具与工作环境",
                "AGENTS.md": "Agent工作流程与协作方式",
                "USER.md": "Agent对用户的理解与关系管理"
            }.get(file_info["filename"], "配置文件")

            report += f"| {file_info['filename']} | {file_info['path']} | {file_info['size']} | {description} |\n"

        report += f"""
## 核心参数配置

### 专业能力参数
- **技术深度**：{technical_depth}/10 ({'专家级' if technical_depth >= 9 else '高级' if technical_depth >= 7 else '中级'})
- **实用性权重**：{self._get_value(self.agent_data, "specialization_parameters.practicality_weight", 8)}/10
- **创新倾向**：{self._get_value(self.agent_data, "specialization_parameters.innovation_tendency", 7)}/10

### 情感智能参数
- **情感智能水平**：{emotional_intelligence}/10 ({'高' if emotional_intelligence >= 7 else '中等' if emotional_intelligence >= 5 else '基础'}水平)
- **鼓励频率**：{self._get_value(self.agent_data, "specialization_parameters.encouragement_frequency", 7)}/10
- **压力识别敏感度**：{self._get_value(self.agent_data, "specialization_parameters.stress_recognition_sensitivity", 7)}/10
- **个性化程度**：{self._get_value(self.agent_data, "specialization_parameters.personalization_degree", 7)}/10

### 协作参数
- **协作强度**：{collaboration_intensity}/10 ({'高强度' if collaboration_intensity >= 8 else '中等强度' if collaboration_intensity >= 6 else '低强度'})

## 配置特点分析

### 专业特性
1. **领域专长**：专注于{self.domain}领域
2. **经验水平**：{self._get_value(self.agent_data, "professional_identity.experience_level", "高级")}水平
3. **核心能力**：{len(self._get_value(self.agent_data, "professional_identity.key_competencies", []))}项核心能力定义

### 人性化特性
1. **情感智能**：{emotional_intelligence}/10水平配置
2. **支持策略**：{'高级情感支持策略' if emotional_intelligence >= 7 else '基础情感支持策略'}
3. **个性化程度**：{self._get_value(self.agent_data, "specialization_parameters.personalization_degree", 7)}/10个性化设置

### 工作流程特性
1. **协作模式**：{collaboration_intensity}/10协作强度
2. **工作流程**：{'深度协作工作流' if collaboration_intensity >= 8 else '标准协作工作流'}
3. **质量标准**：包含技术、协作、情感三维质量标准

## 部署建议

### 立即行动
1. **文件复制**：将生成的5个配置文件复制到OpenClaw Agent配置目录
2. **权限设置**：确保配置文件有适当读写权限
3. **服务重启**：重启OpenClaw Agent服务使配置生效
4. **基础测试**：运行基础功能测试验证配置正确性

### 短期优化（1-2周）
1. **使用反馈**：收集初期使用反馈，识别明显问题
2. **参数调整**：根据反馈调整情感智能参数
3. **个性化优化**：根据具体使用场景优化个性化设置
4. **性能监控**：监控Agent性能，确保响应速度

### 中长期优化（1-3个月）
1. **效果评估**：全面评估配置效果，各维度评分
2. **深度优化**：基于评估结果进行深度配置优化
3. **知识更新**：更新领域知识和最佳实践
4. **能力扩展**：根据需求扩展Agent能力范围

## 故障排除

### 常见问题
1. **配置文件语法错误**
   - 检查文件格式，确保符合Markdown规范
   - 验证特殊字符和编码

2. **Agent启动失败**
   - 检查文件权限设置
   - 验证OpenClaw版本兼容性
   - 查看错误日志定位问题

3. **情感智能表达生硬**
   - 调整情感智能参数，降低或提高水平
   - 优化情感表达模板，增加自然语言变化

4. **专业能力不足**
   - 补充领域知识库内容
   - 调整技术深度参数
   - 增加专业工具和工作流

### 支持资源
1. **最佳实践指南**：参考《高级专业Agent配置最佳实践指南》
2. **配置验证工具**：使用配置验证工具检查配置质量
3. **社区支持**：访问OpenClaw社区获取帮助
4. **研究文档**：参考完整研究文档理解配置原理

## 更新与维护

### 定期更新
- **每周**：检查使用数据和反馈，进行小调整
- **每月**：全面回顾配置效果，进行优化调整
- **每季度**：基于季度评估进行较大规模优化
- **每年**：重新评估Agent定位和配置策略

### 版本管理
- **版本记录**：记录每次配置变更和优化
- **备份策略**：定期备份配置文件和历史版本
- **回滚机制**：确保可以回滚到之前的工作版本
- **变更日志**：记录重要的配置变更和原因

## 联系方式

**开发团队**：pkulyn

**更新日期**：{self.metadata['generation_date']}

**报告版本**：1.0

---

**重要提示**：本报告为自动生成，基于提供的用户输入和Agent画像。实际使用效果可能因具体环境和需求而有所不同。建议根据实际使用反馈进行迭代优化。
"""

        return report

    def _render_template(self, template_name: str, variables: Dict[str, str]) -> str:
        """渲染模板文件"""
        try:
            template_path = Path(__file__).parent.parent / "claudecode_templates" / template_name
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            # 替换所有变量
            for key, value in variables.items():
                placeholder = f"{{{{{key}}}}}"
                template_content = template_content.replace(placeholder, str(value))

            return template_content
        except Exception as e:
            print(f"警告：无法渲染模板 {template_name}: {e}")
            return f"# 模板渲染失败: {template_name}\n\n错误: {e}"

    def generate_claudecode_config(self) -> Dict[str, str]:
        """生成Claude Code格式的配置文件"""

        # 获取核心数据
        user_name = self._get_user_name()
        agent_name = self._get_agent_name()

        # 提取OpenClaw配置内容
        soul_content = self.generate_soul()
        identity_content = self.generate_identity()
        tools_content = self.generate_tools()
        agents_content = self.generate_agents()
        user_content = self.generate_user()

        # 构建CLAUDE.md变量
        claude_variables = {
            "project_name": f"{self.domain}专业Agent项目",
            "project_overview": self._extract_project_overview(soul_content),
            "intelligent_collaboration_rules": self._extract_collaboration_rules(agents_content),
            "professional_spirit_rules": self._extract_professional_rules(soul_content),
            "emotional_intelligence_rules": self._extract_emotional_rules(soul_content),
            "truth_pragmatism_rules": self._extract_truth_rules(soul_content),
            "sincerity_openness_rules": self._extract_sincerity_rules(soul_content),
            "standard_workflow": self._extract_workflow(agents_content),
            "agents_configuration_summary": self._extract_agents_summary(identity_content),
            "tools_and_environment": self._extract_tools_summary(tools_content),
            "file_naming_conventions": self._extract_naming_conventions(identity_content),
            "quick_commands": self._extract_quick_commands(user_content),
            "version": self.metadata["version"],
            "generation_date": self.metadata["generation_date"],
            "domain": self.domain,
            "optimization_level": self.optimization_level
        }

        # 生成CLAUDE.md
        claude_md = self._render_template("claude_project_template.md", claude_variables)

        # 生成Agent配置文件变量
        agent_variables = {
            "agent_name": agent_name,
            "agent_description": self._extract_agent_description(identity_content),
            "agent_type": "general-purpose",
            "agent_model": "inherit",
            "agent_title": self._extract_agent_title(identity_content),
            "core_identity_positioning": self._extract_identity_positioning(identity_content),
            "mandatory_rules": self._extract_mandatory_rules(agents_content),
            "standard_workflow": self._extract_workflow(agents_content),
            "core_responsibilities": self._extract_core_responsibilities(identity_content),
            "professional_capabilities_tools": self._extract_professional_capabilities(tools_content),
            "user_understanding_communication": self._extract_user_understanding(user_content),
            "work_quality_standards": self._extract_quality_standards(agents_content),
            "emotional_intelligence_support": self._extract_emotional_support(soul_content),
            "quick_response_templates": self._extract_response_templates(user_content),
            "experience_level": self._get_value(self.agent_data, "professional_identity.experience_level", "高级"),
            "technical_depth": self._get_value(self.agent_data, "specialization_parameters.technical_depth", 8),
            "emotional_intelligence": self._get_value(self.agent_data, "specialization_parameters.emotional_intelligence_level", 7),
            "collaboration_intensity": self._get_value(self.agent_data, "specialization_parameters.collaboration_intensity", 7)
        }

        # 生成Agent配置文件
        agent_md = self._render_template("agent_template.md", agent_variables)

        # 获取Agent文件名（简化版）
        agent_filename = self._get_agent_filename()

        return {
            "CLAUDE.md": claude_md,
            f".agents/{agent_filename}.md": agent_md
        }

    def _extract_section_content(self, content: str, section_title: str, max_lines: int = 10) -> str:
        """从Markdown内容中提取特定章节的内容

        Args:
            content: Markdown内容
            section_title: 章节标题（如"## 核心真理"）
            max_lines: 最大提取行数

        Returns:
            章节内容字符串
        """
        lines = content.split('\n')
        extracted = []
        in_section = False
        lines_count = 0

        for line in lines:
            if line.strip() == section_title:
                in_section = True
                continue

            if in_section:
                # 如果遇到下一个同级或更高级标题，停止
                if line.startswith('#') and not line.startswith('#' * (section_title.count('#') + 1)):
                    break

                # 如果遇到Markdown分隔符（---），停止
                if line.strip().startswith('---'):
                    break

                # 如果遇到配置说明等特殊标记，停止
                if line.strip().startswith('**配置说明**') or line.strip().startswith('**优化提示**'):
                    break

                if line.strip() and lines_count < max_lines:
                    extracted.append(line)
                    lines_count += 1

        return '\n'.join(extracted).strip()

    def _extract_project_overview(self, soul_content: str) -> str:
        """从SOUL.md中提取项目概述"""
        personality = self._extract_section_content(soul_content, "## 性格底色", max_lines=3)
        stance = self._extract_section_content(soul_content, "## 2. 价值观", max_lines=3)

        overview_parts = []
        if personality:
            overview_parts.append(f"性格底色：{personality}")
        if stance:
            overview_parts.append(f"领域立场：{stance}")

        if overview_parts:
            return '\n\n'.join(overview_parts)
        else:
            return "基于四层六维专业人格模型构建的高级专业Agent，提供深度专业咨询服务"

    def _extract_collaboration_rules(self, agents_content: str) -> str:
        """从AGENTS.md中提取协作规则"""
        # 提取核心工作流程作为协作规则
        workflow_content = self._extract_section_content(agents_content, "## 核心工作流程", max_lines=8)

        if workflow_content:
            return workflow_content
        else:
            return "- 各司其职，不跨领域操作\n- 专业分工，职能完全隔离\n- 决策透明，无隐性操作\n- 交接无缝，信息闭环"

    def _extract_professional_rules(self, soul_content: str) -> str:
        """从SOUL.md中提取专业精神规则"""
        stance = self._extract_section_content(soul_content, "## 2. 价值观", max_lines=8)

        if stance:
            return stance
        else:
            return "- 技术决策符合伦理标准\n- 工作态度务实创新\n- 服务以用户价值为核心\n- 提供基于证据和经验的准确建议"

    def _extract_emotional_rules(self, soul_content: str) -> str:
        """从SOUL.md中提取情感智能规则"""
        expression = self._extract_section_content(soul_content, "## 3. 表达风格", max_lines=8)

        if expression:
            return expression
        else:
            return "- 理解技术决策对团队的情感影响\n- 在严谨分析中加入建设性鼓励\n- 主动识别并帮助缓解技术压力\n- 关注团队学习和个人发展"

    def _extract_truth_rules(self, soul_content: str) -> str:
        """从SOUL.md中提取求真务实规则"""
        rules = self._extract_section_content(soul_content, "## 4. 做事规矩", max_lines=8)

        if rules:
            return rules
        else:
            return "- 数据/事实必须核实确认\n- 不确定内容立即主动核实\n- 严格遵循官方规范和最新政策\n- 诚实说明能力边界，不夸大不隐瞒"

    def _extract_sincerity_rules(self, soul_content: str) -> str:
        """从SOUL.md中提取真诚开放规则"""
        boundary = self._extract_section_content(soul_content, "## 5. 边界和禁忌", max_lines=10)

        if boundary:
            return boundary
        else:
            return "- 实事求是，不隐瞒不撒谎\n- 遇到问题主动上报积极解决\n- 根据用户反馈持续优化\n- 诚实说明能力边界，不夸大不隐瞒"

    def _extract_workflow(self, agents_content: str) -> str:
        """从AGENTS.md中提取工作流程"""
        # 提取核心工作流程部分
        workflow = self._extract_section_content(agents_content, "## 核心工作流程", max_lines=12)

        if workflow:
            return workflow
        else:
            return "1. **明确需求**：确认文档类型、用途、受众、时限、特殊要求\n2. **任务匹配**：主Agent自动匹配最合适的专业Agent\n3. **任务执行**：专业Agent严格按照规范、模板、要求完成核心工作\n4. **质量审核**：执行格式校验+内容合规双重审核，确保无错误、无冲突\n5. **交付优化**：交付成品，根据用户反馈迭代修改，直至符合要求"

    def _extract_agents_summary(self, identity_content: str) -> str:
        """从IDENTITY.md中提取Agent配置摘要"""
        # 新格式直接提取Role行
        lines = identity_content.split('\n')
        for line in lines:
            if line.strip().startswith('Role:'):
                role = line.strip().replace('Role:', '').strip()
                if role:
                    return f"- **{role}**：专注于{self.domain}领域的高级专业顾问"

        return f"- **{self._get_agent_name()}**：专注于{self.domain}领域的高级专业顾问，提供基于四层六维专业人格模型的深度咨询服务"

    def _extract_tools_summary(self, tools_content: str) -> str:
        """从TOOLS.md中提取工具摘要"""
        # 提取基础配置部分
        basic_config = self._extract_section_content(tools_content, "## 基础配置", max_lines=12)
        # 提取专业工具设置部分
        professional_tools = self._extract_section_content(tools_content, "## 专业工具设置", max_lines=8)

        summary_parts = []
        if basic_config:
            summary_parts.append(f"基础配置：{basic_config}")
        if professional_tools:
            summary_parts.append(f"专业工具：{professional_tools}")

        if summary_parts:
            return '\n\n'.join(summary_parts)
        else:
            return "- 专业工具：架构设计工具、性能分析工具、安全评估工具\n- 工作环境：开发环境、测试环境、部署环境\n- 情感智能工具：情感识别、鼓励模板、团队支持\n- 技术工作流优化：架构评估流程、技术评审流程"

    def _extract_naming_conventions(self, identity_content: str) -> str:
        """提取命名规范"""
        return "- 文稿类：文稿主题_YYYYMMDD_版本号.docx\n- 小说类：S部数E章节数_章节标题_YYYYMMDD_版本号.md"

    def _extract_quick_commands(self, user_content: str) -> str:
        """提取快捷指令"""
        return "- `@项目管家`：全局任务调度和问题解决\n- `@文稿专家`：党务公文和行政文稿创作\n- `@创意写手`：科幻小说创作和世界观构建"

    def _extract_agent_description(self, identity_content: str) -> str:
        """提取Agent描述"""
        # 从新格式IDENTITY.md中提取Role行
        lines = identity_content.split('\n')
        for line in lines:
            if line.strip().startswith('Role:'):
                role = line.strip().replace('Role:', '').strip()
                if role:
                    return role
        # 旧格式兼容
        for line in lines:
            if line.strip().startswith('**角色定义**：'):
                role_definition = line.strip().replace('**角色定义**：', '').strip()
                if role_definition:
                    return role_definition
        return f"{self._get_agent_name()}，专注于{self.domain}领域的高级专业顾问"

    def _extract_agent_title(self, identity_content: str) -> str:
        """提取Agent标题"""
        # 从新格式IDENTITY.md中提取Role行
        lines = identity_content.split('\n')
        for line in lines:
            if line.strip().startswith('Role:'):
                role = line.strip().replace('Role:', '').strip()
                if role:
                    if "，" in role:
                        return role.split("，")[0]
                    return role
        # 旧格式兼容
        for line in lines:
            if line.strip().startswith('**角色定义**：'):
                role_definition = line.strip().replace('**角色定义**：', '').strip()
                if role_definition:
                    if "，" in role_definition:
                        return role_definition.split("，")[0]
                    return role_definition
        return f"{self.domain}领域专家"

    def _extract_identity_positioning(self, identity_content: str) -> str:
        """提取核心身份定位"""
        # 从新格式IDENTITY.md中提取关键字段
        lines = identity_content.split('\n')
        positioning_parts = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('Role:') or stripped.startswith('One-liner:') or stripped.startswith('Vibe:'):
                positioning_parts.append(stripped)

        if positioning_parts:
            return '\n'.join(positioning_parts)

        # 旧格式兼容
        professional_identity = self._extract_section_content(identity_content, "## 专业身份", max_lines=15)
        personality_traits = self._extract_section_content(identity_content, "## 个性特征", max_lines=8)

        old_parts = []
        if professional_identity:
            old_parts.append(f"专业身份：{professional_identity}")
        if personality_traits:
            old_parts.append(f"个性特征：{personality_traits}")

        if old_parts:
            return '\n\n'.join(old_parts)
        else:
            return f"作为{self._get_agent_name()}，我专注于{self.domain}领域，提供基于四层六维专业人格模型的深度咨询服务"

    def _extract_mandatory_rules(self, agents_content: str) -> str:
        """提取强制遵守规则"""
        # 从AGENTS.md中提取交付标准
        quality_standards = self._extract_section_content(agents_content, "## 交付标准", max_lines=10)
        # 从AGENTS.md中提取共享空间规范
        shared_space = self._extract_section_content(agents_content, "## 共享空间行为规范", max_lines=8)

        rules = []
        if quality_standards:
            rules.append(f"交付标准：{quality_standards}")
        if shared_space:
            rules.append(f"共享空间规范：{shared_space}")

        if rules:
            return '\n\n'.join(rules)
        else:
            return "所有任务必须按标准工作流程闭环完成，严格遵守专业分工和协作协议，确保准确性和可行性"

    def _extract_core_responsibilities(self, identity_content: str) -> str:
        """提取核心工作职责"""
        # 新格式IDENTITY.md没有核心能力章节，从SOUL.md的立场推断
        # 尝试从旧格式中提取
        core_abilities = self._extract_section_content(identity_content, "## 核心能力", max_lines=12)

        if core_abilities:
            return core_abilities
        else:
            # 新格式：直接用Role和领域生成
            role = ""
            lines = identity_content.split('\n')
            for line in lines:
                if line.strip().startswith('Role:'):
                    role = line.strip().replace('Role:', '').strip()
                    break
            if role:
                return f"- {role}\n- 提供{self.domain}领域专业咨询和解决方案\n- 确保服务质量和用户价值最大化"
            return f"- 提供{self.domain}领域专业咨询和解决方案\n- 确保服务质量和用户价值最大化\n- 基于四层六维专业人格模型提供深度服务"

    def _extract_professional_capabilities(self, tools_content: str) -> str:
        """提取专业能力和工具"""
        professional_tools = self._extract_section_content(tools_content, "## 领域专用工具", max_lines=15)
        basic_config = self._extract_section_content(tools_content, "## 本地技术环境", max_lines=10)

        # 旧格式兼容
        if not professional_tools:
            professional_tools = self._extract_section_content(tools_content, "## 专业工具设置", max_lines=15)
        if not basic_config:
            basic_config = self._extract_section_content(tools_content, "## 基础配置", max_lines=10)

        capabilities = []
        if professional_tools:
            capabilities.append(f"专业工具：{professional_tools}")
        if basic_config:
            capabilities.append(f"本地环境：{basic_config}")

        if capabilities:
            return '\n\n'.join(capabilities)
        else:
            return f"- {self.domain}领域专业工具\n- 系统分析和问题解决能力\n- 开发环境、测试环境、部署环境"

    def _extract_user_understanding(self, user_content: str) -> str:
        """提取用户理解"""
        # 从USER.md中提取基础信息部分
        basic_info = self._extract_section_content(user_content, "## 基础信息", max_lines=12)
        # 从USER.md中提取沟通偏好部分
        communication_preferences = self._extract_section_content(user_content, "## 沟通偏好", max_lines=10)

        understanding_parts = []
        if basic_info:
            understanding_parts.append(f"基础信息：{basic_info}")
        if communication_preferences:
            understanding_parts.append(f"沟通偏好：{communication_preferences}")

        if understanding_parts:
            return '\n\n'.join(understanding_parts)
        else:
            return f"理解{self._get_user_name()}({self._get_value(self.user_data, 'basic_info.professional_title', '技术总监')})的需求、挑战和期望，提供个性化的专业服务，适应其沟通风格和情感表达偏好"

    def _extract_quality_standards(self, agents_content: str) -> str:
        """提取质量标准"""
        quality_standards = self._extract_section_content(agents_content, "## 交付标准", max_lines=15)

        if quality_standards:
            return quality_standards
        else:
            # 旧格式兼容
            old_standards = self._extract_section_content(agents_content, "## 工作质量标准", max_lines=15)
            if old_standards:
                return old_standards
            return "- 准确性：基于证据和经验\n- 完整性：考虑多个方面\n- 可行性：建议可实施\n- 及时性：在合理时间内响应"

    def _extract_emotional_support(self, soul_content: str) -> str:
        """提取情感智能支持"""
        expression = self._extract_section_content(soul_content, "## 表达风格", max_lines=10)

        if expression:
            return expression
        else:
            # 旧格式兼容
            emotional_values = self._extract_section_content(soul_content, "## 情感智能价值观", max_lines=8)
            if emotional_values:
                return emotional_values
            return "- 识别团队情感状态和压力源\n- 提供适时的鼓励和情感支持\n- 帮助团队缓解技术压力和挫折感\n- 关注团队学习和个人发展"

    def _extract_response_templates(self, user_content: str) -> str:
        """提取响应模板"""
        # 从USER.md中提取沟通偏好部分，特别是正式程度和具体表现
        communication_preferences = self._extract_section_content(user_content, "## 沟通偏好", max_lines=12)

        if communication_preferences:
            # 基于沟通偏好生成响应模板
            templates = [
                "问题分析：`基于分析，核心问题是...`",
                "方案建议：`建议采取以下步骤...`",
                "团队支持：`我理解团队面临的挑战...`",
                "技术指导：`从架构角度看，建议考虑...`",
                "情感回应：`我理解这种技术压力，我们可以一起...`"
            ]
            return '\n'.join(templates)
        else:
            return "- 问题分析：`基于分析，核心问题是...`\n- 方案建议：`建议采取以下步骤...`\n- 团队支持：`我理解团队面临的挑战...`\n- 技术指导：`从架构角度看，建议考虑...`\n- 情感回应：`我理解这种技术压力，我们可以一起...`"

    def generate_all(self, output_format: str = "openclaw") -> Dict[str, str]:
        """生成配置文件，支持多种格式"""

        if output_format == "openclaw":
            # 现有的OpenClaw生成逻辑
            print(f"开始生成OpenClaw高级专业Agent配置文件...")
            print(f"领域: {self.domain}")
            print(f"优化级别: {self.optimization_level}")
            print(f"输出目录: {self.output_dir}")

            files = {
                "SOUL.md": self.generate_soul(),
                "IDENTITY.md": self.generate_identity(),
                "TOOLS.md": self.generate_tools(),
                "AGENTS.md": self.generate_agents(),
                "USER.md": self.generate_user()
            }

            saved_files = {}
            for filename, content in files.items():
                filepath = self._save_file(filename, content)
                saved_files[filename] = filepath
                print(f"√ 生成 {filename} ({len(content)} 字符)")

            return saved_files

        elif output_format == "claudecode":
            print(f"开始生成Claude Code高级专业Agent配置文件...")
            print(f"领域: {self.domain}")
            print(f"优化级别: {self.optimization_level}")

            claude_config = self.generate_claudecode_config()

            saved_files = {}
            for filename, content in claude_config.items():
                filepath = self._save_file(filename, content)
                saved_files[filename] = filepath
                print(f"√ 生成 {filename} ({len(content)} 字符)")

            return saved_files

        elif output_format == "both":
            print(f"开始生成双格式高级专业Agent配置文件...")
            print(f"领域: {self.domain}")
            print(f"优化级别: {self.optimization_level}")

            # 生成OpenClaw配置
            openclaw_files = self.generate_all("openclaw")

            # 生成Claude Code配置（为了避免冲突，创建子目录）
            cc_output_dir = self.output_dir / "claudecode-config"
            cc_output_dir.mkdir(exist_ok=True)

            # 临时切换输出目录
            original_output_dir = self.output_dir
            self.output_dir = cc_output_dir

            cc_config = self.generate_claudecode_config()

            # 保存Claude Code配置文件
            cc_files = {}
            for filename, content in cc_config.items():
                filepath = self._save_file(filename, content)
                cc_files[filename] = filepath
                print(f"√ 生成 {filename} ({len(content)} 字符)")

            # 恢复原始输出目录
            self.output_dir = original_output_dir

            # 合并结果
            saved_files = {**openclaw_files, **cc_files}

            return saved_files

        else:
            raise ValueError(f"不支持的输出格式: {output_format}")

        print(f"开始生成高级专业Agent配置文件...")
        print(f"领域: {self.domain}")
        print(f"优化级别: {self.optimization_level}")
        print(f"输出目录: {self.output_dir}")

        # 生成各个配置文件
        files = {
            "SOUL.md": self.generate_soul(),
            "IDENTITY.md": self.generate_identity(),
            "TOOLS.md": self.generate_tools(),
            "AGENTS.md": self.generate_agents(),
            "USER.md": self.generate_user()
        }

        # 保存文件
        saved_files = {}
        for filename, content in files.items():
            filepath = self._save_file(filename, content)
            saved_files[filename] = filepath
            print(f"√ 生成 {filename} ({len(content)} 字符)")

        # 生成报告
        report_content = self.generate_report()
        report_path = self._save_file("generation_report.md", report_content)
        saved_files["generation_report.md"] = report_path
        print(f"√ 生成生成报告 ({len(report_content)} 字符)")

        # 保存报告数据为JSON
        report_json = json.dumps(self.report_data, ensure_ascii=False, indent=2)
        json_path = self._save_file("generation_data.json", report_json)
        saved_files["generation_data.json"] = json_path

        print(f"\n✅ 配置文件生成完成！")
        print(f"共生成 {len(saved_files)} 个文件")
        print(f"请查看 {report_path} 获取详细报告")

        return saved_files