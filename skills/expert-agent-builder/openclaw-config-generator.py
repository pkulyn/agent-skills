#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenClaw高级专业Agent配置生成器
基于第四阶段研究成果，帮助用户快速创建专业级Agent配置文件
版本: 2.0.0
作者: pkulyn
日期: 2026-04-11
"""

import os
import sys
import json
import argparse
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# 添加utils目录到路径
sys.path.insert(0, str(Path(__file__).parent / "utils"))

# 导入全局配置
try:
    from config import VERSION, VERSION_SHORT, PROJECT_NAME, AUTHOR, RELEASE_DATE
except ImportError:
    # 如果配置文件不存在，使用默认值
    VERSION = "2.0.0"
    VERSION_SHORT = "2.0"
    PROJECT_NAME = "Expert Agent Builder"
    AUTHOR = "pkulyn"
    RELEASE_DATE = "2026-04-11"

try:
    from config_generator import ConfigGenerator
    from validator import ConfigValidator, ValidationLevel, generate_markdown_report
    from document_analyzer import DocumentAnalyzer
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保utils目录中存在config_generator.py、validator.py和document_analyzer.py文件")
    sys.exit(1)

class InteractiveTemplateFiller:
    """交互式模板填充器"""

    def __init__(self, output_dir: str = "generated-config"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _print_header(self, title: str):
        """打印标题"""
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)

    def _get_input(self, prompt: str, default: str = "", required: bool = True) -> str:
        """获取用户输入"""
        while True:
            if default:
                full_prompt = f"{prompt} [{default}]: "
            else:
                full_prompt = f"{prompt}: "

            value = input(full_prompt).strip()

            if not value and default:
                return default
            elif not value and required:
                print("  此项为必填项，请重新输入")
            else:
                return value

    def _get_list_input(self, prompt: str, example: List[str] = None) -> List[str]:
        """获取列表输入"""
        print(f"\n{prompt}")
        if example:
            print(f"  示例: {', '.join(example)}")
        print("  输入完成后留空回车继续")

        items = []
        while True:
            item = input(f"  - 第{len(items)+1}项: ").strip()
            if not item:
                if len(items) == 0:
                    print("  至少需要输入一项")
                    continue
                else:
                    break
            items.append(item)

        return items

    def fill_user_profile(self) -> Dict[str, Any]:
        """填充用户个人信息模板"""
        self._print_header("用户个人信息填写")

        print("请提供以下信息，这将帮助Agent更好地理解和服务您")

        profile = {
            "basic_info": {
                "name": {
                    "value": self._get_input("姓名"),
                    "_说明": "用户的真实姓名或常用称呼"
                },
                "professional_title": {
                    "value": self._get_input("职业头衔", "技术总监"),
                    "_说明": "用户的职业头衔"
                },
                "organization": {
                    "value": self._get_input("组织/公司", "当前组织"),
                    "_说明": "用户所在的组织或公司"
                },
                "industry": {
                    "value": self._get_input("行业", "互联网科技"),
                    "_说明": "用户所在的行业"
                },
                "timezone": {
                    "value": self._get_input("时区", "Asia/Shanghai (UTC+8)"),
                    "_说明": "用户所在时区"
                }
            },
            "background": {
                "education": {
                    "value": self._get_list_input("教育背景", ["计算机科学学士", "软件工程硕士"]),
                    "_说明": "用户的教育背景"
                },
                "work_experience": {
                    "value": self._get_list_input("工作经历", ["5年软件开发经验", "3年架构设计经验"]),
                    "_说明": "用户的工作经历"
                },
                "areas_of_expertise": {
                    "value": self._get_list_input("专长领域", ["云原生架构", "分布式系统", "微服务设计"]),
                    "_说明": "用户的专业领域专长"
                }
            },
            "communication_preferences": {
                "formality_level": {
                    "value": int(self._get_input("沟通正式程度 (1-10)", "7")),
                    "_说明": "1=非常随意, 10=非常正式"
                },
                "technical_detail_level": {
                    "value": int(self._get_input("技术细节程度 (1-10)", "8")),
                    "_说明": "1=高度概括, 10=极度详细"
                },
                "feedback_style": {
                    "value": self._get_input("反馈风格", "平衡兼顾", required=False),
                    "_说明": "直接坦诚/温和建设性/平衡兼顾"
                }
            },
            "emotional_preferences": {
                "encouragement_style": {
                    "value": self._get_input("鼓励风格", "具体认可", required=False),
                    "_说明": "具体认可/过程表扬/成就庆祝/持续支持"
                },
                "stress_response_preference": {
                    "value": self._get_input("压力回应偏好", "直接解决问题", required=False),
                    "_说明": "情感支持先行/直接解决问题/提供多种选择/给予思考空间"
                },
                "emotional_boundary": {
                    "value": int(self._get_input("情感边界 (1-10)", "6")),
                    "_说明": "1=严格专业边界, 10=深度情感连接"
                }
            },
            "project_context": {
                "current_challenges": {
                    "value": self._get_list_input("当前挑战", ["系统性能瓶颈", "技术债务累积", "团队技能分布不均"]),
                    "_说明": "用户当前面临的主要挑战"
                },
                "goals_objectives": {
                    "value": self._get_list_input("项目目标", ["提升系统性能30%", "减少技术债务50%", "提升团队整体技能水平"]),
                    "_说明": "用户的项目目标"
                },
                "constraints_limitations": {
                    "value": self._get_list_input("约束限制", ["预算有限", "时间紧张", "团队规模较小"]),
                    "_说明": "项目的约束和限制条件"
                },
                "success_metrics": {
                    "value": self._get_list_input("成功指标", ["用户满意度提升20%", "系统响应时间降低40%", "团队交付速度提升30%"]),
                    "_说明": "衡量项目成功的指标"
                }
            }
        }

        return profile

    def fill_agent_profile(self) -> Dict[str, Any]:
        """填充Agent画像模板"""
        self._print_header("高级专业Agent画像填写")

        print("请为您的Agent定义以下专业特征")

        profile = {
            "professional_identity": {
                "domain_expertise": {
                    "value": self._get_input("专业领域", "技术架构"),
                    "_说明": "Agent的专业领域"
                },
                "experience_level": {
                    "value": self._get_input("经验水平", "高级（7-15年经验）"),
                    "_说明": "Agent的经验水平"
                },
                "role_definition": {
                    "value": self._get_input("角色定义", "资深技术架构顾问，专注于云原生和分布式系统设计"),
                    "_说明": "Agent的角色定义"
                },
                "influence_scope": {
                    "value": self._get_input("影响范围", "部门影响"),
                    "_说明": "Agent的影响范围"
                },
                "professional_background": {
                    "value": self._get_input("专业背景", "拥有12年大型互联网公司架构设计经验，曾主导多个千万级用户系统的架构演进"),
                    "_说明": "Agent的专业背景"
                },
                "key_competencies": {
                    "value": self._get_list_input("核心能力", [
                        "系统架构设计",
                        "技术选型评估",
                        "性能优化",
                        "技术债务管理",
                        "团队技术指导"
                    ]),
                    "_说明": "Agent的核心能力"
                }
            },
            "core_personality": {
                "worldview": {
                    "value": self._get_input("世界观", "技术是解决问题的工具，但人文关怀同样重要；优秀的架构应该既高效又可维护"),
                    "_说明": "Agent的世界观"
                },
                "core_values": {
                    "value": self._get_list_input("核心价值观", [
                        "技术伦理至上",
                        "用户价值导向",
                        "团队协作优先",
                        "持续学习成长",
                        "务实创新平衡"
                    ]),
                    "_说明": "Agent的核心价值观"
                },
                "personality_traits": {
                    "value": self._get_list_input("个性特征", [
                        "技术敏锐",
                        "耐心指导",
                        "鼓励风格",
                        "同理理解",
                        "建设性批评"
                    ]),
                    "_说明": "Agent的个性特征"
                },
                "emotional_style": {
                    "value": self._get_input("情感风格", "平衡适中"),
                    "_说明": "Agent的情感表达风格"
                },
                "communication_style": {
                    "value": self._get_input("沟通风格", "直接清晰"),
                    "_说明": "Agent的沟通风格"
                },
                "decision_making_style": {
                    "value": self._get_input("决策风格", "数据驱动"),
                    "_说明": "Agent的决策风格"
                }
            },
            "work_behavior": {
                "problem_solving_approach": {
                    "value": self._get_input("问题解决方法", "采用系统化分析方法：问题定义→根本原因分析→方案设计→实施规划→效果评估→团队学习"),
                    "_说明": "Agent的问题解决方法"
                },
                "team_collaboration_style": {
                    "value": self._get_input("团队协作风格", "教练型（培养能力）"),
                    "_说明": "Agent的团队协作风格"
                },
                "thinking_patterns": {
                    "value": self._get_list_input("思维模式", [
                        "系统思维",
                        "批判性思维",
                        "战略思维",
                        "成长思维"
                    ]),
                    "_说明": "Agent的思维模式"
                },
                "learning_habits": {
                    "value": self._get_list_input("学习习惯", [
                        "持续跟踪技术趋势",
                        "定期复盘项目经验",
                        "积极参与技术社区",
                        "系统学习理论知识"
                    ]),
                    "_说明": "Agent的学习习惯"
                },
                "quality_standards": {
                    "value": self._get_list_input("质量标准", [
                        "代码可维护性",
                        "系统可靠性99.9%",
                        "文档完整性",
                        "团队满意度",
                        "用户价值实现"
                    ]),
                    "_说明": "Agent的质量标准"
                },
                "work_rhythm": {
                    "value": self._get_input("工作节奏", "平衡节奏"),
                    "_说明": "Agent的工作节奏"
                }
            },
            "environment_understanding": {
                "user_insight_depth": {
                    "value": self._get_input("用户洞察深度", "全方位理解"),
                    "_说明": "Agent对用户的理解深度"
                },
                "situational_awareness": {
                    "value": self._get_input("情境意识", "能够识别项目阶段、团队状态、技术挑战、业务压力、个人成长需求等多维度情境"),
                    "_说明": "Agent的情境意识能力"
                },
                "relationship_management": {
                    "value": self._get_input("关系管理", "信任建立"),
                    "_说明": "Agent的关系管理能力"
                },
                "communication_adaptation": {
                    "value": self._get_input("沟通适应", "能够根据用户背景、情绪状态、沟通偏好、学习风格调整表达方式"),
                    "_说明": "Agent的沟通适应能力"
                },
                "context_integration": {
                    "value": self._get_input("情境整合", "优秀整合"),
                    "_说明": "Agent的情境整合能力"
                }
            },
            "specialization_parameters": {
                "emotional_intelligence_level": {
                    "value": int(self._get_input("情感智能水平 (1-10)", "8")),
                    "_说明": "Agent的情感智能水平，影响情感识别和支持能力"
                },
                "encouragement_frequency": {
                    "value": int(self._get_input("鼓励频率 (1-10)", "7")),
                    "_说明": "Agent提供鼓励和认可的频率"
                },
                "stress_recognition_sensitivity": {
                    "value": int(self._get_input("压力识别敏感度 (1-10)", "8")),
                    "_说明": "Agent识别用户压力状态的敏感度"
                },
                "personalization_degree": {
                    "value": int(self._get_input("个性化程度 (1-10)", "7")),
                    "_说明": "Agent提供个性化服务的程度"
                },
                "technical_depth": {
                    "value": int(self._get_input("技术深度 (1-10)", "9")),
                    "_说明": "Agent的专业技术深度"
                },
                "practicality_weight": {
                    "value": int(self._get_input("实用性权重 (1-10)", "9")),
                    "_说明": "Agent建议的实用性和可行性权重"
                },
                "innovation_tendency": {
                    "value": int(self._get_input("创新倾向 (1-10)", "7")),
                    "_说明": "Agent提供创新解决方案的倾向"
                },
                "collaboration_intensity": {
                    "value": int(self._get_input("协作强度 (1-10)", "8")),
                    "_说明": "Agent的协作强度和工作参与度"
                }
            },
            "domain_specific_settings": {
                "technology_architecture": {
                    "preferred_methodologies": {
                        "value": self._get_list_input("偏好的方法论", [
                            "领域驱动设计",
                            "事件驱动架构",
                            "微服务架构",
                            "云原生设计",
                            "可扩展架构"
                        ]),
                        "_说明": "偏好的技术架构方法论"
                    },
                    "technology_stack_preferences": {
                        "value": self._get_list_input("技术栈偏好", [
                            "云平台：AWS/Azure",
                            "容器：Docker/Kubernetes",
                            "数据库：PostgreSQL/Redis/MongoDB",
                            "消息队列：Kafka/RabbitMQ"
                        ]),
                        "_说明": "偏好的技术栈"
                    },
                    "design_principles": {
                        "value": self._get_list_input("设计原则", [
                            "可扩展性优先",
                            "可靠性至上",
                            "可维护性考虑",
                            "成本效益平衡",
                            "团队友好性"
                        ]),
                        "_说明": "遵循的设计原则"
                    }
                }
            },
            "output_style": {
                "formality_level": {
                    "value": int(self._get_input("输出正式程度 (1-10)", "7")),
                    "_说明": "1=非常随意，10=非常正式"
                },
                "detail_level": {
                    "value": int(self._get_input("输出详细程度 (1-10)", "8")),
                    "_说明": "1=高度概括，10=极度详细"
                },
                "visual_support_preference": {
                    "value": self._get_input("视觉支持偏好", "简单图表"),
                    "_说明": "文本为主/简单图表/详细图表"
                },
                "language_style": {
                    "value": self._get_input("语言风格", "技术精确"),
                    "_说明": "技术精确/通俗易懂/平衡兼顾"
                },
                "structure_preference": {
                    "value": self._get_input("结构偏好", "线性逻辑"),
                    "_说明": "线性逻辑/主题分明/混合结构"
                }
            },
            "integration_requirements": {
                "tool_integrations": {
                    "value": self._get_list_input("工具集成需求", [
                        "GitHub",
                        "JIRA",
                        "Confluence",
                        "Slack",
                        "Draw.io"
                    ]),
                    "_说明": "需要集成的工具"
                },
                "platform_requirements": {
                    "value": self._get_list_input("平台需求", [
                        "OpenClaw环境",
                        "Docker容器",
                        "云平台访问"
                    ]),
                    "_说明": "平台环境需求"
                },
                "data_sources": {
                    "value": self._get_list_input("数据源", [
                        "内部知识库",
                        "技术文档库",
                        "性能监控数据",
                        "项目管理系统"
                    ]),
                    "_说明": "需要访问的数据源"
                },
                "api_integrations": {
                    "value": self._get_list_input("API集成", [
                        "GitHub API",
                        "JIRA API",
                        "监控系统API",
                        "文档系统API"
                    ]),
                    "_说明": "需要集成的API"
                }
            },
            "additional_configuration": {
                "custom_templates": {
                    "value": self._get_list_input("自定义模板", [
                        "架构设计文档模板",
                        "技术评审记录模板",
                        "技术债务跟踪模板",
                        "团队技能评估模板"
                    ]),
                    "_说明": "需要的自定义模板"
                },
                "branding_elements": {
                    "value": self._get_list_input("品牌元素", [
                        "组织标志",
                        "品牌颜色（蓝色系）",
                        "专业字体",
                        "技术顾问标识"
                    ]),
                    "_说明": "品牌元素需求"
                },
                "compliance_requirements": {
                    "value": self._get_list_input("合规性要求", [
                        "数据保留政策",
                        "访问控制要求",
                        "审计日志需求",
                        "安全标准符合"
                    ]),
                    "_说明": "合规性要求"
                },
                "other_requirements": {
                    "value": self._get_input("其他需求", "需要支持中英文技术术语，能够根据用户技术水平调整解释深度", required=False),
                    "_说明": "其他特殊需求"
                }
            }
        }

        return profile

    def fill_team_info(self) -> Dict[str, Any]:
        """填充团队信息模板"""
        self._print_header("多Agent团队信息填写")

        print("请提供多Agent协作团队的以下信息")

        team_info = {
            "basic_info": {
                "team_name": {
                    "value": self._get_input("团队名称", "智能协作工作台"),
                    "_说明": "多Agent团队的名称"
                },
                "team_description": {
                    "value": self._get_input("团队描述", "基于四层六维专业人格模型构建的智能协作系统，支持复杂业务流程"),
                    "_说明": "团队的简要描述"
                },
                "team_size": {
                    "value": int(self._get_input("团队规模 (Agent数量)", "3")),
                    "_说明": "团队中Agent的数量"
                },
                "primary_domain": {
                    "value": self._get_input("主要领域", "智能协作与项目管理"),
                    "_说明": "团队专注的主要专业领域"
                }
            },
            "collaboration_model": {
                "coordination_style": {
                    "value": self._get_input("协调风格", "领导协调型"),
                    "_说明": "团队协调方式：领导协调/平等协作/混合模式"
                },
                "decision_making_process": {
                    "value": self._get_input("决策流程", "主Agent集中决策+专业Agent建议"),
                    "_说明": "团队的决策流程描述"
                },
                "communication_protocol": {
                    "value": self._get_input("通信协议", "任务分配→执行反馈→质量审核→交付优化"),
                    "_说明": "Agent间的通信协议"
                },
                "conflict_resolution": {
                    "value": self._get_input("冲突解决", "主Agent仲裁+专业协商"),
                    "_说明": "团队冲突解决机制"
                }
            },
            "workflow_overview": {
                "primary_tasks": {
                    "value": self._get_list_input("主要任务类型", [
                        "文档创作与编辑",
                        "创意内容生成",
                        "项目管理与调度",
                        "质量审核与控制",
                        "技术问题解决"
                    ]),
                    "_说明": "团队承担的主要任务类型"
                },
                "interaction_patterns": {
                    "value": self._get_list_input("交互模式", [
                        "串行任务流：任务A→任务B→任务C",
                        "并行任务流：主任务+辅助任务",
                        "循环改进流：执行→审核→优化",
                        "紧急响应流：问题→诊断→解决"
                    ]),
                    "_说明": "Agent间的典型交互模式"
                },
                "success_metrics": {
                    "value": self._get_list_input("成功指标", [
                        "任务完成率95%+",
                        "质量满意度8/10+",
                        "协作效率提升30%+",
                        "用户反馈满意度85%+"
                    ]),
                    "_说明": "衡量团队成功的指标"
                }
            }
        }

        return team_info

    def fill_multiple_agent_profiles(self, team_size: int) -> List[Dict[str, Any]]:
        """填充多个Agent画像"""
        agent_profiles = []

        for i in range(team_size):
            print(f"\n{'='*60}")
            print(f"  第 {i+1}/{team_size} 个Agent画像填写")
            print(f"{'='*60}")

            print(f"请为第 {i+1} 个Agent定义以下专业特征")

            # 建议角色类型
            role_suggestions = [
                "项目管家/协调官",
                "技术架构专家",
                "创意内容写手",
                "质量审核专家",
                "文档编辑专家",
                "数据分析师",
                "用户交互设计师"
            ]

            suggestion_text = ", ".join(role_suggestions)
            print(f"常见角色类型参考：{suggestion_text}")

            agent_profile = self.fill_agent_profile()
            agent_profiles.append(agent_profile)

            print(f"✓ 第 {i+1} 个Agent画像填写完成")

        return agent_profiles

    def fill_collaboration_rules(self, agent_profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """填充协作规则"""
        self._print_header("多Agent协作规则定义")

        print("请定义Agent之间的协作规则和关系")

        # 提取Agent角色用于参考
        agent_roles = []
        for i, profile in enumerate(agent_profiles):
            role = profile.get("professional_identity", {}).get("role_definition", {}).get("value", f"Agent {i+1}")
            agent_roles.append(role)

        print(f"当前Agent角色：{', '.join(agent_roles)}")

        collaboration_rules = {
            "role_assignments": {
                "primary_coordinator": {
                    "value": self._get_input("主要协调Agent", agent_roles[0] if agent_roles else "项目管家"),
                    "_说明": "负责团队协调和任务分配的Agent"
                },
                "specialist_agents": {
                    "value": agent_roles,
                    "_说明": "专业领域Agent列表"
                },
                "backup_assignments": {
                    "value": self._get_list_input("备份角色分配", ["主Agent故障时由技术专家接管协调", "专业Agent故障时由其他相关Agent临时接管"]),
                    "_说明": "故障恢复时的角色备份分配"
                }
            },
            "communication_protocols": {
                "task_assignment_flow": {
                    "value": self._get_input("任务分配流程", "用户请求→主Agent分析→任务分解→专业Agent执行→结果汇总→质量审核→交付用户"),
                    "_说明": "任务分配的标准流程"
                },
                "status_reporting": {
                    "value": self._get_input("状态报告机制", "定时报告+关键节点报告+异常即时报告"),
                    "_说明": "Agent状态报告机制"
                },
                "error_handling": {
                    "value": self._get_input("错误处理流程", "错误检测→主Agent通知→问题分析→解决方案制定→执行修复→结果验证"),
                    "_说明": "错误处理的标准流程"
                },
                "escalation_procedures": {
                    "value": self._get_list_input("升级流程", [
                        "技术问题升级到技术专家Agent",
                        "协调冲突升级到主Agent仲裁",
                        "质量争议升级到质量审核Agent",
                        "系统故障升级到用户人工干预"
                    ]),
                    "_说明": "问题升级的标准流程"
                }
            },
            "quality_assurance": {
                "review_process": {
                    "value": self._get_input("审核流程", "专业Agent自审→交叉互审→主Agent终审→用户确认"),
                    "_说明": "质量审核流程"
                },
                "quality_standards": {
                    "value": self._get_list_input("质量标准", [
                        "内容准确性100%",
                        "格式规范性95%+",
                        "交付及时性90%+",
                        "用户满意度8/10+"
                    ]),
                    "_说明": "团队统一的质量标准"
                },
                "improvement_cycles": {
                    "value": self._get_input("改进周期", "每周复盘+每月优化+季度升级"),
                    "_说明": "持续改进的周期"
                }
            },
            "performance_monitoring": {
                "key_metrics": {
                    "value": self._get_list_input("关键指标", [
                        "任务完成率",
                        "平均响应时间",
                        "质量评分",
                        "协作效率",
                        "用户满意度"
                    ]),
                    "_说明": "团队性能监控的关键指标"
                },
                "reporting_frequency": {
                    "value": self._get_input("报告频率", "每日摘要+每周总结+月度分析"),
                    "_说明": "性能报告频率"
                },
                "optimization_triggers": {
                    "value": self._get_list_input("优化触发条件", [
                        "任务完成率<85%",
                        "用户满意度<7/10",
                        "协作冲突频率>3次/周",
                        "质量评分下降>10%"
                    ]),
                    "_说明": "触发团队优化的条件"
                }
            }
        }

        return collaboration_rules


class EnhancedInteractiveFiller(InteractiveTemplateFiller):
    """增强版交互式填充器 - 支持新工作流程"""

    def __init__(self, output_dir: str = "generated-config"):
        super().__init__(output_dir)
        self.selections = {}  # 存储用户选择
        self.document_analyzer = DocumentAnalyzer(debug=True)

    def select_platform_and_mode(self) -> tuple:
        """选择平台和Agent模式"""
        self._print_header("平台与模式选择")

        print("请选择要构建的Agent平台和模式：")
        print()
        print("1. 平台选择:")
        print("   [A] OpenClaw专业Agent配置")
        print("       - 配置文件：SOUL.md、IDENTITY.md、TOOLS.md、AGENTS.md、USER.md")
        print("       - 适用于：OpenClaw平台的Agent配置")
        print()
        print("   [B] Claude Code专业Agent配置")
        print("       - 配置文件：CLAUDE.md (项目手册) + .agents/{Agent名称}.md")
        print("       - 适用于：Claude Code IDE扩展的Agent配置")
        print()

        # 平台选择
        platform_choice = ""
        while platform_choice not in ["A", "B"]:
            platform_choice = self._get_input("请选择平台 [A/B]", "A").strip().upper()
            if platform_choice not in ["A", "B"]:
                print("  请选择 A 或 B")

        platform = "openclaw" if platform_choice == "A" else "claudecode"

        print()
        print("2. Agent模式选择:")
        print("   [1] 单Agent配置文件")
        print("       - 适用于：单一专业领域的Agent配置")
        print()
        print("   [2] 多Agent协作系统")
        print("       - 适用于：团队协作、角色分工、复杂业务流程")
        print()

        # 模式选择
        mode_choice = ""
        while mode_choice not in ["1", "2"]:
            mode_choice = self._get_input("请选择Agent模式 [1/2]", "1").strip()
            if mode_choice not in ["1", "2"]:
                print("  请选择 1 或 2")

        mode = "single-agent" if mode_choice == "1" else "multi-agent"

        self.selections["platform"] = platform
        self.selections["mode"] = mode

        print(f"\n✓ 已选择：{platform.upper()}平台 × {mode.replace('-', ' ')}")
        return platform, mode

    def select_input_method(self) -> str:
        """选择信息获取方式"""
        self._print_header("信息获取方式选择")

        print("请选择信息提供方式：")
        print()
        print("[A] 交互式问答模式 (推荐初次使用)")
        print("    - 我将通过一系列问题引导您逐步提供信息")
        print("    - 确保信息完整性和逻辑一致性")
        print("    - 适合：初次使用或不熟悉配置体系的用户")
        print()
        print("[B] 资料整理模式 (批量分析)")
        print("    - 您可以直接提供现有的个人信息和Agent画像资料")
        print("    - 我将分析、整理、结构化这些信息")
        print("    - 适合：已有明确需求或模板的用户")
        print()
        print("[C] 混合模式 (推荐高效使用)")
        print("    - 步骤1：您提供现有资料(文档、笔记、需求说明等)")
        print("    - 步骤2：AI分析整理，提取已有信息，识别缺失关键项")
        print("    - 步骤3：通过精确定向问答补充缺失信息")
        print("    - 适合：已有部分资料但需补充完善的情况")
        print()

        method_choice = ""
        while method_choice not in ["A", "B", "C"]:
            method_choice = self._get_input("请选择信息获取方式 [A/B/C]", "C").strip().upper()
            if method_choice not in ["A", "B", "C"]:
                print("  请选择 A、B 或 C")

        method_map = {
            "A": "interactive",
            "B": "document",
            "C": "hybrid"
        }

        input_method = method_map[method_choice]
        self.selections["input_method"] = input_method

        method_names = {
            "interactive": "交互式问答模式",
            "document": "资料整理模式",
            "hybrid": "混合模式"
        }

        print(f"\n✓ 已选择：{method_names[input_method]}")
        return input_method

    def collect_info_interactive(self, is_multi_agent: bool = False) -> Dict[str, Any]:
        """交互式模式信息收集"""
        self._print_header("交互式信息收集")

        if is_multi_agent:
            print("将引导您收集多Agent协作系统的信息...")

            # 收集用户个人信息
            print("\n[第一步] 填写用户个人信息")
            user_profile = self.fill_user_profile()

            # 收集团队信息
            print("\n[第二步] 填写团队信息")
            team_info = self.fill_team_info()
            team_size = team_info["basic_info"]["team_size"]["value"]

            # 收集多个Agent画像
            print(f"\n[第三步] 填写 {team_size} 个Agent的画像")
            agent_profiles = self.fill_multiple_agent_profiles(team_size)

            # 收集协作规则
            print("\n[第四步] 定义协作规则")
            collaboration_rules = self.fill_collaboration_rules(agent_profiles)

            return {
                "user_profile": user_profile,
                "team_info": team_info,
                "agent_profiles": agent_profiles,
                "collaboration_rules": collaboration_rules,
                "is_multi_agent": True
            }
        else:
            print("将引导您收集单Agent配置信息...")

            # 收集用户个人信息
            print("\n[第一步] 填写用户个人信息")
            user_profile = self.fill_user_profile()

            # 收集Agent画像
            print("\n[第二步] 填写Agent画像")
            agent_profile = self.fill_agent_profile()

            return {
                "user_profile": user_profile,
                "agent_profile": agent_profile,
                "is_multi_agent": False
            }

    def collect_info_from_documents(self, documents_path: str, is_multi_agent: bool = False) -> Dict[str, Any]:
        """从文档中提取信息（完整版文档分析）"""
        self._print_header("资料整理模式")
        print("正在分析您提供的文档资料...")
        print()

        try:
            # 使用文档分析器分析文档
            user_profile, agent_profile = self.document_analyzer.analyze_documents(documents_path)

            print("✓ 文档分析完成")
            print(f"  提取到用户信息字段: {len(user_profile)} 个类别")
            print(f"  提取到Agent信息字段: {len(agent_profile)} 个类别")
            print()

            # 如果信息不完整，提示用户补充
            missing_fields = self._check_missing_fields(user_profile, agent_profile)

            if missing_fields:
                print("⚠ 以下信息在文档中未找到或不够完整:")
                for field in missing_fields:
                    print(f"  - {field}")
                print()

                print("是否需要通过交互式问答补充这些信息？")
                print("[Y] 是 - 通过问答补充缺失信息")
                print("[N] 否 - 直接使用现有信息生成配置")

                choice = input("您的选择 [Y/N]: ").strip().upper()

                if choice == 'Y':
                    print("\n开始补充缺失信息...")
                    user_profile, agent_profile = self._supplement_missing_info(
                        user_profile, agent_profile, missing_fields
                    )

            # 对于多Agent模式，需要额外的团队信息
            team_info = None
            collaboration_rules = None
            agent_profiles = []

            if is_multi_agent:
                print("\n多Agent模式：需要收集团队信息和协作规则")
                team_info = self.fill_team_info()
                collaboration_rules = self.fill_collaboration_rules()

                # 收集多个Agent画像
                print("\n现在开始收集多个Agent的画像信息...")
                agent_profiles = self.fill_multiple_agent_profiles()

                return {
                    "user_profile": user_profile,
                    "team_info": team_info,
                    "collaboration_rules": collaboration_rules,
                    "agent_profiles": agent_profiles,
                    "is_multi_agent": True
                }
            else:
                return {
                    "user_profile": user_profile,
                    "agent_profile": agent_profile,
                    "is_multi_agent": False
                }

        except Exception as e:
            print(f"❌ 文档分析出错: {e}")
            print("是否切换到交互式问答模式？")
            choice = input("[Y] 是，切换到交互式问答 [N] 否，退出程序: ").strip().upper()

            if choice == 'Y':
                print("\n切换到交互式问答模式...")
                return self.collect_info_interactive(is_multi_agent)
            else:
                print("程序退出。")
                sys.exit(1)

    def _check_missing_fields(self, user_profile: Dict[str, Any], agent_profile: Dict[str, Any]) -> List[str]:
        """检查缺失的必需字段"""
        missing_fields = []

        # 检查用户基本信息
        required_user_fields = ["name", "professional_title", "organization"]
        basic_info = user_profile.get("basic_info", {})

        for field in required_user_fields:
            if field not in basic_info or not basic_info[field].get("value"):
                missing_fields.append(f"用户{field}")

        # 检查Agent基本信息
        required_agent_fields = ["role_definition", "domain_expertise", "experience_level"]
        professional_identity = agent_profile.get("professional_identity", {})

        for field in required_agent_fields:
            if field not in professional_identity or not professional_identity[field].get("value"):
                missing_fields.append(f"Agent{field}")

        return missing_fields

    def _supplement_missing_info(self, user_profile: Dict[str, Any], agent_profile: Dict[str, Any],
                                missing_fields: List[str]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """补充缺失的信息"""
        user_profile = user_profile.copy()
        agent_profile = agent_profile.copy()

        print("\n" + "=" * 60)
        print("  补充缺失信息")
        print("=" * 60)

        # 补充用户信息
        if any("用户" in field for field in missing_fields):
            print("\n--- 用户信息补充 ---")

            basic_info = user_profile.get("basic_info", {})

            if "用户姓名" in missing_fields or "name" in missing_fields:
                name = self._get_input("用户姓名", required=True)
                basic_info["name"] = {"value": name, "_说明": "用户的真实姓名或常用称呼"}

            if "用户professional_title" in missing_fields or "professional_title" in missing_fields:
                title = self._get_input("职业头衔", "技术总监")
                basic_info["professional_title"] = {"value": title, "_说明": "用户的职业头衔"}

            if "用户organization" in missing_fields or "organization" in missing_fields:
                org = self._get_input("组织/公司", "当前组织")
                basic_info["organization"] = {"value": org, "_说明": "用户所在的组织或公司"}

            user_profile["basic_info"] = basic_info

        # 补充Agent信息
        if any("Agent" in field for field in missing_fields):
            print("\n--- Agent信息补充 ---")

            professional_identity = agent_profile.get("professional_identity", {})

            if "Agentrole_definition" in missing_fields or "role_definition" in missing_fields:
                role = self._get_input("Agent角色", "专业顾问")
                professional_identity["role_definition"] = {"value": role, "_说明": "Agent的角色定义"}

            if "Agentdomain_expertise" in missing_fields or "domain_expertise" in missing_fields:
                domain = self._get_input("专业领域", "技术架构")
                professional_identity["domain_expertise"] = {"value": domain, "_说明": "Agent的专业领域"}

            if "Agentexperience_level" in missing_fields or "experience_level" in missing_fields:
                experience = self._get_input("经验水平", "高级（7-15年经验）")
                professional_identity["experience_level"] = {"value": experience, "_说明": "Agent的经验水平"}

            agent_profile["professional_identity"] = professional_identity

        print("\n✓ 信息补充完成")
        return user_profile, agent_profile

    def collect_info_hybrid(self, documents_path: str, is_multi_agent: bool = False) -> Dict[str, Any]:
        """混合模式信息收集（完整版：文档分析 + 交互补充）"""
        self._print_header("混合模式信息收集")
        print("将结合文档分析和定向问答收集信息...")
        print()

        try:
            # 第一步：分析文档提取信息
            print("步骤1: 分析您提供的文档资料...")
            user_profile, agent_profile = self.document_analyzer.analyze_documents(documents_path)

            print(f"✓ 文档分析完成")
            print(f"  提取到用户信息字段: {len(user_profile)} 个类别")
            print(f"  提取到Agent信息字段: {len(agent_profile)} 个类别")
            print()

            # 第二步：检查缺失字段
            missing_fields = self._check_missing_fields(user_profile, agent_profile)

            if missing_fields:
                print("步骤2: 通过定向问答补充缺失信息")
                print("以下信息在文档中未找到或不够完整:")
                for field in missing_fields:
                    print(f"  - {field}")
                print()

                print("现在开始补充这些信息...")
                user_profile, agent_profile = self._supplement_missing_info(
                    user_profile, agent_profile, missing_fields
                )
            else:
                print("✓ 文档信息完整，无需补充")
                print()

            # 第三步：对于多Agent模式，需要交互式收集团队信息
            team_info = None
            collaboration_rules = None
            agent_profiles = []

            if is_multi_agent:
                print("步骤3: 收集团队信息和协作规则")
                team_info = self.fill_team_info()
                collaboration_rules = self.fill_collaboration_rules()

                # 收集多个Agent画像
                print("\n现在开始收集多个Agent的画像信息...")
                agent_profiles = self.fill_multiple_agent_profiles()

                return {
                    "user_profile": user_profile,
                    "team_info": team_info,
                    "collaboration_rules": collaboration_rules,
                    "agent_profiles": agent_profiles,
                    "is_multi_agent": True
                }
            else:
                return {
                    "user_profile": user_profile,
                    "agent_profile": agent_profile,
                    "is_multi_agent": False
                }

        except Exception as e:
            print(f"❌ 文档分析出错: {e}")
            print("是否切换到交互式问答模式？")
            choice = input("[Y] 是，切换到交互式问答 [N] 否，退出程序: ").strip().upper()

            if choice == 'Y':
                print("\n切换到交互式问答模式...")
                return self.collect_info_interactive(is_multi_agent)
            else:
                print("程序退出。")
                sys.exit(1)

    def confirm_info(self, collected_info: Dict[str, Any]) -> bool:
        """信息确认机制"""
        self._print_header("信息确认")

        print("请确认以下收集的信息：")
        print()

        if collected_info.get("is_multi_agent", False):
            print("模式：多Agent协作系统")

            # 显示团队信息
            team_info = collected_info.get("team_info", {})
            team_name = team_info.get("basic_info", {}).get("team_name", {}).get("value", "未填写")
            team_size = team_info.get("basic_info", {}).get("team_size", {}).get("value", 0)
            print(f"团队名称：{team_name}")
            print(f"Agent数量：{team_size}")

            # 显示用户信息
            user_name = collected_info.get("user_profile", {}).get("basic_info", {}).get("name", {}).get("value", "未填写")
            print(f"用户姓名：{user_name}")

            # 显示Agent角色
            agent_profiles = collected_info.get("agent_profiles", [])
            if agent_profiles:
                print("Agent角色：")
                for i, profile in enumerate(agent_profiles):
                    role = profile.get("professional_identity", {}).get("role_definition", {}).get("value", f"Agent {i+1}")
                    print(f"  {i+1}. {role}")
        else:
            print("模式：单Agent配置")
            user_name = collected_info.get("user_profile", {}).get("basic_info", {}).get("name", {}).get("value", "未填写")
            agent_role = collected_info.get("agent_profile", {}).get("professional_identity", {}).get("role_definition", {}).get("value", "未填写")
            print(f"用户姓名：{user_name}")
            print(f"Agent角色：{agent_role}")

        print()
        confirm = self._get_input("确认信息无误？[Y/N]", "Y").strip().upper()

        if confirm == "Y":
            print("\n✓ 信息确认通过")
            return True
        else:
            print("\n⚠️  信息需要修改，将重新收集")
            return False


def learn_methodology_summary():
    """学习方法论摘要"""
    print("\n[文档] 学习方法论摘要")
    print("=" * 60)

    methodology_file = Path(__file__).parent / "docs" / "methodology-summary.md"

    if not methodology_file.exists():
        print("⚠️  方法论摘要文档未找到，将使用默认配置逻辑")
        print("📁 预期位置:", methodology_file)
        return

    try:
        with open(methodology_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取关键部分（前500字符作为摘要）
        summary = content[:800] + "..." if len(content) > 800 else content

        print("正在学习OpenClaw高级专业Agent配置方法论...")
        print("\n核心方法论摘要:")
        print("-" * 40)

        # 显示关键标题
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('# ') or line.startswith('## '):
                print(f"  {line}")
            if i > 50:  # 只显示前50行
                break

        print("-" * 40)
        print("[完成] 方法论学习完成，基于四层六维专业人格模型进行配置引导")
        print("  详细文档请查看: skill/docs/methodology-summary.md")

    except Exception as e:
        print(f"[警告] 读取方法论摘要时出错: {e}")
        print("将继续使用标准配置逻辑")

def run_interactive_mode(args):
    """运行交互式模式"""
    print("\n[目标] OpenClaw高级专业Agent配置生成器 - 交互式模式")
    print("=" * 60)

    # 0. 学习方法论
    learn_methodology_summary()

    filler = InteractiveTemplateFiller(args.output_dir)

    # 1. 填写用户个人信息
    print("\n[文档] 第一步：填写您的个人信息")
    user_profile = filler.fill_user_profile()

    user_profile_file = filler.output_dir / "user_profile.json"
    with open(user_profile_file, 'w', encoding='utf-8') as f:
        json.dump(user_profile, f, ensure_ascii=False, indent=2)

    print(f"✓ 用户个人信息已保存到: {user_profile_file}")

    # 2. 填写Agent画像
    print("\n🤖 第二步：定义您的专业Agent画像")
    agent_profile = filler.fill_agent_profile()

    agent_profile_file = filler.output_dir / "agent_profile.json"
    with open(agent_profile_file, 'w', encoding='utf-8') as f:
        json.dump(agent_profile, f, ensure_ascii=False, indent=2)

    print(f"✓ Agent画像已保存到: {agent_profile_file}")

    # 3. 生成配置文件
    print("\n→ 第三步：生成配置文件")
    generator = ConfigGenerator(
        user_profile_path=str(user_profile_file),
        agent_profile_path=str(agent_profile_file),
        output_dir=str(filler.output_dir / "agent-config"),
        domain=args.domain,
        optimization_level=args.optimization_level
    )

    generator.generate_all(args.format)

    # 4. 验证配置
    print("\n🔍 第四步：验证配置文件质量")
    validator = ConfigValidator(
        config_dir=str(filler.output_dir / "agent-config"),
        validation_level=ValidationLevel(args.validation_level)
    )

    report = validator.validate()

    # 保存验证报告
    report_file = filler.output_dir / "validation_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        generate_markdown_report(report, str(report_file))

    print(f"✓ 验证报告已保存到: {report_file}")

    print("\n" + "=" * 60)
    print("✅ 配置生成流程完成！")
    print("=" * 60)
    print(f"\n📁 生成的文件保存在: {filler.output_dir}")
    print(f"📋 用户个人信息: {user_profile_file}")
    print(f"🤖 Agent画像: {agent_profile_file}")
    print(f"→ Agent配置文件: {filler.output_dir / 'agent-config'}")
    print(f"🔍 验证报告: {report_file}")
    print("\n🚀 接下来，请将agent-config目录中的5个配置文件复制到您的OpenClaw Agent配置目录中，然后重启Agent服务。")

def generate_team_configuration(team_info: Dict[str, Any], collaboration_rules: Dict[str, Any],
                                agent_configs: List[Dict[str, Any]], output_dir: Path) -> str:
    """
    生成团队级配置文件

    Args:
        team_info: 团队信息
        collaboration_rules: 协作规则
        agent_configs: 各个Agent的配置信息
        output_dir: 输出目录

    Returns:
        生成的团队配置文件路径
    """
    # 创建团队配置目录
    team_config_dir = output_dir / "team-config"
    team_config_dir.mkdir(parents=True, exist_ok=True)

    # 提取团队基本信息
    team_basic_info = team_info.get("basic_info", {})
    team_name = team_basic_info.get("team_name", {}).get("value", "智能协作工作台")
    team_description = team_basic_info.get("team_description", {}).get("value", "多Agent协作系统")
    team_size = team_basic_info.get("team_size", {}).get("value", len(agent_configs))

    # 提取协作模型
    collaboration_model = collaboration_rules.get("collaboration_model", {})
    coordination_style = collaboration_model.get("coordination_style", {}).get("value", "领导协调型")
    decision_making = collaboration_model.get("decision_making_process", {}).get("value", "主Agent集中决策+专业Agent建议")

    # 收集Agent摘要信息
    agent_summaries = []
    for i, agent_config in enumerate(agent_configs):
        professional_identity = agent_config.get("professional_identity", {})
        agent_name = professional_identity.get("role_definition", {}).get("value", f"Agent_{i+1}")
        domain_expertise = professional_identity.get("domain_expertise", {}).get("value", "技术架构")
        experience_level = professional_identity.get("experience_level", {}).get("value", "高级")

        agent_summaries.append({
            "id": i+1,
            "name": agent_name,
            "domain": domain_expertise,
            "experience": experience_level,
            "role": agent_name
        })

    # 构建团队配置数据结构
    team_config_data = {
        "metadata": {
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "2.0",
            "configuration_type": "multi-agent-team"
        },
        "team": {
            "basic_info": {
                "name": team_name,
                "description": team_description,
                "size": team_size,
                "created_date": datetime.now().strftime("%Y-%m-%d")
            },
            "collaboration_model": {
                "coordination_style": coordination_style,
                "decision_making_process": decision_making,
                "communication_protocol": collaboration_rules.get("communication_protocol", {}),
                "workflow_integration": collaboration_rules.get("workflow_integration", {})
            },
            "agents": agent_summaries,
            "quality_assurance": {
                "review_process": collaboration_rules.get("quality_assurance", {}).get("review_process", {}),
                "improvement_cycle": collaboration_rules.get("quality_assurance", {}).get("improvement_cycle", {}),
                "performance_metrics": collaboration_rules.get("quality_assurance", {}).get("performance_metrics", {})
            },
            "performance_monitoring": {
                "key_metrics": collaboration_rules.get("performance_monitoring", {}).get("key_metrics", {}),
                "report_frequency": collaboration_rules.get("performance_monitoring", {}).get("report_frequency", {}),
                "optimization_triggers": collaboration_rules.get("performance_monitoring", {}).get("optimization_triggers", {})
            }
        }
    }

    # 保存团队配置为JSON
    team_config_file = team_config_dir / "team_configuration.json"
    with open(team_config_file, 'w', encoding='utf-8') as f:
        json.dump(team_config_data, f, ensure_ascii=False, indent=2)

    # 生成团队配置Markdown文档
    team_md_content = f"""# 团队配置文档 - {team_name}

## 团队概述

{team_description}

**团队规模**: {team_size} 个Agent

## 协作模型

### 协调风格
{coordination_style}

### 决策流程
{decision_making}

## Agent成员配置

| ID | 角色名称 | 专业领域 | 经验水平 |
|----|----------|----------|----------|
"""

    # 添加Agent表格行
    for agent in agent_summaries:
        team_md_content += f"| {agent['id']} | {agent['name']} | {agent['domain']} | {agent['experience']} |\n"

    team_md_content += f"""
## 质量保证体系

### 审核流程
{collaboration_rules.get('quality_assurance', {}).get('review_process', {}).get('value', '标准审核流程')}

### 改进周期
{collaboration_rules.get('quality_assurance', {}).get('improvement_cycle', {}).get('value', '持续优化')}

## 性能监控

### 关键指标
{collaboration_rules.get('performance_monitoring', {}).get('key_metrics', {}).get('value', '任务完成率、协作效率、用户满意度')}

### 报告频率
{collaboration_rules.get('performance_monitoring', {}).get('report_frequency', {}).get('value', '每周报告')}

---
**生成日期**: {datetime.now().strftime("%Y-%m-%d")}
**配置版本**: 2.0
**团队类型**: 多Agent协作系统

*本配置文件基于Expert Agent Builder方法论生成，定义{team_name}团队的协作模型、角色分配和性能监控体系。*
"""

    # 保存团队Markdown文档
    team_md_file = team_config_dir / "TEAM_CONFIGURATION.md"
    with open(team_md_file, 'w', encoding='utf-8') as f:
        f.write(team_md_content)

    return str(team_md_file)


def run_smart_mode(args):
    """运行智能模式 - 新交互流程"""
    print("\n[目标] Expert Agent Builder - 智能模式")
    print("=" * 60)
    print("基于四层六维专业人格模型的增强交互流程")

    # 0. 学习方法论
    learn_methodology_summary()

    # 创建增强版填充器
    filler = EnhancedInteractiveFiller(args.output_dir)

    # 1. 选择平台和模式
    platform, mode = filler.select_platform_and_mode()
    is_multi_agent = (mode == "multi-agent")

    # 2. 选择信息获取方式
    input_method = filler.select_input_method()

    # 3. 根据选择收集信息
    collected_info = None
    if input_method == "interactive":
        collected_info = filler.collect_info_interactive(is_multi_agent)
    elif input_method == "document":
        # 请求文档路径
        print("\n[文档] 请提供您的资料文件路径:")
        print("  支持格式：.txt, .md, .json, .docx (待实现)")
        documents_path = filler._get_input("资料文件路径", required=True)
        collected_info = filler.collect_info_from_documents(documents_path, is_multi_agent)
    else:  # hybrid
        print("\n[混合模式] 请先提供您的资料文件路径:")
        print("  支持格式：.txt, .md, .json, .docx (待实现)")
        documents_path = filler._get_input("资料文件路径", required=True)
        collected_info = filler.collect_info_hybrid(documents_path, is_multi_agent)

    # 4. 信息确认
    if not filler.confirm_info(collected_info):
        # 如果用户不确认，重新收集
        print("将重新收集信息...")
        # 这里可以重新开始或退出
        return

    # 5. 保存收集的信息
    info_dir = filler.output_dir / "collected-info"
    info_dir.mkdir(exist_ok=True)

    # 保存用户个人信息
    user_profile_file = info_dir / "user_profile.json"
    with open(user_profile_file, 'w', encoding='utf-8') as f:
        json.dump(collected_info["user_profile"], f, ensure_ascii=False, indent=2)
    print(f"✓ 用户个人信息已保存到: {user_profile_file}")

    # 保存Agent画像（单Agent）或团队配置（多Agent）
    if is_multi_agent:
        # 保存团队信息
        team_info_file = info_dir / "team_info.json"
        with open(team_info_file, 'w', encoding='utf-8') as f:
            json.dump(collected_info["team_info"], f, ensure_ascii=False, indent=2)
        print(f"✓ 团队信息已保存到: {team_info_file}")

        # 保存协作规则
        collaboration_rules_file = info_dir / "collaboration_rules.json"
        with open(collaboration_rules_file, 'w', encoding='utf-8') as f:
            json.dump(collected_info["collaboration_rules"], f, ensure_ascii=False, indent=2)
        print(f"✓ 协作规则已保存到: {collaboration_rules_file}")

        # 保存每个Agent的画像
        agent_profiles = collected_info.get("agent_profiles", [])
        agent_profiles_dir = info_dir / "agent_profiles"
        agent_profiles_dir.mkdir(exist_ok=True)

        for i, agent_profile in enumerate(agent_profiles):
            agent_file = agent_profiles_dir / f"agent_{i+1}_profile.json"
            with open(agent_file, 'w', encoding='utf-8') as f:
                json.dump(agent_profile, f, ensure_ascii=False, indent=2)
            print(f"✓ Agent {i+1} 画像已保存到: {agent_file}")

        # 创建多Agent配置摘要
        multi_agent_summary = {
            "team_info_path": str(team_info_file),
            "collaboration_rules_path": str(collaboration_rules_file),
            "agent_profiles_dir": str(agent_profiles_dir),
            "agent_count": len(agent_profiles),
            "is_multi_agent": True
        }

        summary_file = info_dir / "multi_agent_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(multi_agent_summary, f, ensure_ascii=False, indent=2)
        print(f"✓ 多Agent配置摘要已保存到: {summary_file}")
    else:
        agent_profile_file = info_dir / "agent_profile.json"
        with open(agent_profile_file, 'w', encoding='utf-8') as f:
            json.dump(collected_info["agent_profile"], f, ensure_ascii=False, indent=2)
        print(f"✓ Agent画像已保存到: {agent_profile_file}")

    # 6. 生成配置文件
    print("\n→ 生成配置文件")

    if is_multi_agent:
        # 多Agent配置生成（第一阶段简化版）
        print("⚠️  多Agent配置生成功能（第一阶段简化版）")
        print("  当前版本：每个Agent独立生成配置，团队协作规则将在后续版本中集成")

        # 为每个Agent生成独立配置
        agent_profiles = collected_info.get("agent_profiles", [])
        for i, agent_profile in enumerate(agent_profiles):
            print(f"\n[生成第 {i+1}/{len(agent_profiles)} 个Agent配置]")

            # 为每个Agent创建临时配置文件
            temp_agent_file = info_dir / f"temp_agent_{i+1}_profile.json"
            with open(temp_agent_file, 'w', encoding='utf-8') as f:
                json.dump(agent_profile, f, ensure_ascii=False, indent=2)

            # 创建独立的输出目录
            agent_output_dir = filler.output_dir / "agent-config" / f"agent_{i+1}"

            # 生成单Agent配置
            generator = ConfigGenerator(
                user_profile_path=str(user_profile_file),
                agent_profile_path=str(temp_agent_file),
                output_dir=str(agent_output_dir),
                domain=args.domain,
                optimization_level=args.optimization_level
            )

            # 根据平台选择输出格式
            output_format = platform  # openclaw或claudecode
            generator.generate_all(output_format)

            print(f"✓ 第 {i+1} 个Agent配置生成完成: {agent_output_dir}")

        # 生成团队级配置
        print("\n📋 生成团队级配置文件...")

        # 准备Agent配置数据
        agent_configs = []
        for i, agent_profile in enumerate(collected_info.get("agent_profiles", [])):
            agent_config = {
                "professional_identity": agent_profile.get("professional_identity", {}),
                "core_personality": agent_profile.get("core_personality", {}),
                "work_behavior": agent_profile.get("work_behavior", {}),
                "environment_understanding": agent_profile.get("environment_understanding", {}),
                "specialization_parameters": agent_profile.get("specialization_parameters", {}),
                "domain_specific_settings": agent_profile.get("domain_specific_settings", {}),
                "learning_and_development": agent_profile.get("learning_and_development", {}),
                "other_requirements": agent_profile.get("other_requirements", {})
            }
            agent_configs.append(agent_config)

        # 生成团队配置
        team_config_file = generate_team_configuration(
            team_info=collected_info.get("team_info", {}),
            collaboration_rules=collected_info.get("collaboration_rules", {}),
            agent_configs=agent_configs,
            output_dir=filler.output_dir / "agent-config"
        )

        print(f"✓ 团队级配置已生成: {team_config_file}")

    else:
        # 单Agent配置生成
        generator = ConfigGenerator(
            user_profile_path=str(user_profile_file),
            agent_profile_path=str(agent_profile_file),
            output_dir=str(filler.output_dir / "agent-config"),
            domain=args.domain,
            optimization_level=args.optimization_level
        )

        # 根据平台选择输出格式
        output_format = platform  # openclaw或claudecode
        generator.generate_all(output_format)

    # 7. 验证配置
    print("\n🔍 验证配置文件质量")

    if is_multi_agent:
        # 多Agent配置验证：验证每个Agent的配置
        print("验证多Agent协作系统配置...")

        agent_configs_dir = filler.output_dir / "agent-config"

        # 检查每个Agent的配置目录
        for i, agent_profile in enumerate(collected_info.get("agent_profiles", [])):
            agent_dir = agent_configs_dir / f"agent_{i+1}"
            if agent_dir.exists():
                print(f"  Agent {i+1} 配置目录: {agent_dir}")
                # 验证单个Agent配置
                try:
                    validator = ConfigValidator(
                        config_dir=str(agent_dir),
                        validation_level=ValidationLevel(args.validation_level)
                    )
                    agent_report = validator.validate()
                    print(f"    ✓ Agent {i+1} 配置验证通过")
                except Exception as e:
                    print(f"    ✗ Agent {i+1} 配置验证失败: {e}")
            else:
                print(f"  ✗ Agent {i+1} 配置目录不存在: {agent_dir}")

        # 验证团队配置
        team_config_dir = agent_configs_dir / "team-config"
        if team_config_dir.exists():
            print(f"  团队配置目录: {team_config_dir}")
            # 检查关键文件是否存在
            required_files = ["team_configuration.json", "TEAM_CONFIGURATION.md"]
            for file in required_files:
                if (team_config_dir / file).exists():
                    print(f"    ✓ {file} 存在")
                else:
                    print(f"    ✗ {file} 缺失")

            # 检查原始团队信息文件（向后兼容）
            legacy_files = ["team_info.json", "collaboration_rules.json"]
            for file in legacy_files:
                if (team_config_dir / file).exists():
                    print(f"    ⓘ {file} 存在（向后兼容）")
        else:
            print(f"  ✗ 团队配置目录不存在: {team_config_dir}")

        print("✓ 团队级配置验证完成")

        # 创建一个简化的验证报告
        report = {
            "status": "partial",
            "message": "多Agent配置验证（完整版）",
            "details": {
                "agent_count": len(collected_info.get("agent_profiles", [])),
                "team_config_valid": team_config_dir.exists(),
                "team_config_files": {
                    "team_configuration_json": (team_config_dir / "team_configuration.json").exists() if team_config_dir.exists() else False,
                    "team_configuration_md": (team_config_dir / "TEAM_CONFIGURATION.md").exists() if team_config_dir.exists() else False,
                    "legacy_files": {
                        "team_info_json": (team_config_dir / "team_info.json").exists() if team_config_dir.exists() else False,
                        "collaboration_rules_json": (team_config_dir / "collaboration_rules.json").exists() if team_config_dir.exists() else False
                    }
                },
                "note": "团队协作规则和集成验证已实现"
            }
        }
    else:
        # 单Agent配置验证
        validator = ConfigValidator(
            config_dir=str(filler.output_dir / "agent-config"),
            validation_level=ValidationLevel(args.validation_level)
        )

        report = validator.validate()

    # 保存验证报告
    report_file = filler.output_dir / "validation_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        if is_multi_agent:
            # 多Agent简化报告
            f.write(f"# 多Agent配置验证报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**验证状态**: {report.get('status', 'unknown')}\n")
            f.write(f"**消息**: {report.get('message', '')}\n\n")

            details = report.get('details', {})
            f.write(f"## 验证详情\n\n")
            f.write(f"- **Agent数量**: {details.get('agent_count', 0)}\n")
            f.write(f"- **团队配置有效**: {'是' if details.get('team_config_valid') else '否'}\n")

            team_config_files = details.get('team_config_files', {})
            if team_config_files:
                f.write(f"\n### 团队配置文件状态\n")
                f.write(f"- **团队配置JSON**: {'✓ 存在' if team_config_files.get('team_configuration_json') else '✗ 缺失'}\n")
                f.write(f"- **团队配置MD**: {'✓ 存在' if team_config_files.get('team_configuration_md') else '✗ 缺失'}\n")

                legacy_files = team_config_files.get('legacy_files', {})
                if legacy_files.get('team_info_json') or legacy_files.get('collaboration_rules_json'):
                    f.write(f"- **遗留文件**: {'✓ 存在' if legacy_files.get('team_info_json') else '✗ 缺失'} (team_info.json), ")
                    f.write(f"{'✓ 存在' if legacy_files.get('collaboration_rules_json') else '✗ 缺失'} (collaboration_rules.json)\n")

            f.write(f"- **备注**: {details.get('note', '')}\n\n")

            f.write(f"## 后续步骤\n\n")
            f.write(f"1. 检查每个Agent的配置目录: `agent-config/agent_*/`\n")
            f.write(f"2. 检查团队配置: `agent-config/team-config/`\n")
            f.write(f"3. 查看团队协作规则: `agent-config/team-config/TEAM_CONFIGURATION.md`\n")
            f.write(f"4. 团队配置已集成协作规则和性能监控体系\n")
        else:
            # 单Agent标准报告
            generate_markdown_report(report, str(report_file))

    print(f"✓ 验证报告已保存到: {report_file}")

    print("\n" + "=" * 60)
    print("✅ 智能模式配置生成流程完成！")
    print("=" * 60)
    print(f"\n📁 生成的文件保存在: {filler.output_dir}")
    print(f"📋 收集的信息: {info_dir}")
    print(f"→ 配置文件: {filler.output_dir / 'agent-config'}")
    print(f"🔍 验证报告: {report_file}")

    if platform == "openclaw":
        print("\n🚀 接下来，请将agent-config目录中的配置文件复制到您的OpenClaw Agent配置目录中，然后重启Agent服务。")
    else:  # claudecode
        print("\n🚀 接下来，请将agent-config目录中的CLAUDE.md复制到项目根目录，.agents/目录中的配置文件复制到相应位置。")


def run_generate_mode(args):
    """运行生成模式"""
    print("\n→ OpenClaw高级专业Agent配置生成器 - 生成模式")
    print("=" * 60)

    if not args.user_profile or not args.agent_profile:
        print("错误：生成模式需要 --user-profile 和 --agent-profile 参数")
        sys.exit(1)

    # 验证输入文件
    for file_path in [args.user_profile, args.agent_profile]:
        if not Path(file_path).exists():
            print(f"错误：文件不存在 - {file_path}")
            sys.exit(1)

    generator = ConfigGenerator(
        user_profile_path=args.user_profile,
        agent_profile_path=args.agent_profile,
        output_dir=args.output_dir,
        domain=args.domain,
        optimization_level=args.optimization_level
    )

    generator.generate_all(args.format)

def run_validate_mode(args):
    """运行验证模式"""
    print("\n🔍 OpenClaw高级专业Agent配置生成器 - 验证模式")
    print("=" * 60)

    if not args.config_dir:
        print("错误：验证模式需要 --config-dir 参数")
        sys.exit(1)

    if not Path(args.config_dir).exists():
        print(f"错误：配置目录不存在 - {args.config_dir}")
        sys.exit(1)

    validator = ConfigValidator(
        config_dir=args.config_dir,
        validation_level=ValidationLevel(args.validation_level)
    )

    report = validator.validate()

    # 保存验证报告
    if args.report_file:
        generate_markdown_report(report, args.report_file)
        print(f"✓ 验证报告已保存到: {args.report_file}")

def run_example_mode(args):
    """运行示例模式"""
    print("\n[示例] OpenClaw高级专业Agent配置生成器 - 示例模式")
    print("=" * 60)

    # 检查示例文件是否存在
    example_dir = Path(__file__).parent / "examples" / "technical-architect-advisor"

    if not example_dir.exists():
        print(f"错误：示例目录不存在 - {example_dir}")
        print("请确保examples/technical-architect-advisor目录存在")
        sys.exit(1)

    user_profile_file = example_dir / "user-profile.json"
    agent_profile_file = example_dir / "agent-profile.json"

    if not user_profile_file.exists() or not agent_profile_file.exists():
        print("错误：示例文件不完整")
        print(f"请检查以下文件是否存在:")
        print(f"  - {user_profile_file}")
        print(f"  - {agent_profile_file}")
        sys.exit(1)

    print(f"使用技术架构顾问示例:")
    print(f"  用户信息: {user_profile_file}")
    print(f"  Agent画像: {agent_profile_file}")

    generator = ConfigGenerator(
        user_profile_path=str(user_profile_file),
        agent_profile_path=str(agent_profile_file),
        output_dir=args.output_dir,
        domain="技术架构",
        optimization_level="high"
    )

    generator.generate_all(args.format)

    # 验证配置
    validator = ConfigValidator(
        config_dir=args.output_dir,
        validation_level=ValidationLevel(args.validation_level)
    )

    report = validator.validate()

    # 保存验证报告
    report_file = Path(args.output_dir) / "validation_report.md"
    generate_markdown_report(report, str(report_file))

    print(f"\n[完成] 示例运行完成!")
    print(f"[文件夹] 生成的文件保存在: {args.output_dir}")
    print(f"[报告] 验证报告: {report_file}")

def main():
    parser = argparse.ArgumentParser(
        description='OpenClaw高级专业Agent配置生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 智能模式（推荐 - 新交互流程）
  python openclaw-config-generator.py --mode smart

  # 交互式模式（传统 - 向后兼容）
  python openclaw-config-generator.py --mode interactive

  # 生成模式（使用现有模板）
  python openclaw-config-generator.py --mode generate \\
    --user-profile templates/user-profile.json \\
    --agent-profile templates/agent-profile.json \\
    --output-dir my-agent-config

  # 验证模式
  python openclaw-config-generator.py --mode validate \\
    --config-dir existing-config \\
    --validation-level strict

  # 示例模式
  python openclaw-config-generator.py --mode example
        """
    )

    parser.add_argument('--mode', default='smart',
                       choices=['smart', 'interactive', 'generate', 'validate', 'example'],
                       help='运行模式 (默认: smart)')

    # 通用参数
    parser.add_argument('--output-dir', default='generated-config',
                       help='输出目录 (默认: generated-config)')
    parser.add_argument('--format', default='openclaw',
                       choices=['openclaw', 'claudecode', 'both'],
                       help='输出格式 (默认: openclaw)')

    # 生成模式参数
    parser.add_argument('--user-profile',
                       help='用户个人信息JSON文件路径 (生成模式必需)')
    parser.add_argument('--agent-profile',
                       help='Agent画像JSON文件路径 (生成模式必需)')
    parser.add_argument('--domain', default='技术架构',
                       help='专业领域 (默认: 技术架构)')
    parser.add_argument('--optimization-level', default='medium',
                       choices=['low', 'medium', 'high'],
                       help='优化级别 (默认: medium)')

    # 验证模式参数
    parser.add_argument('--config-dir',
                       help='配置文件目录 (验证模式必需)')
    parser.add_argument('--validation-level', default='standard',
                       choices=['basic', 'standard', 'strict'],
                       help='验证级别 (默认: standard)')
    parser.add_argument('--report-file',
                       help='验证报告输出文件')

    parser.add_argument('--debug', action='store_true',
                       help='启用调试模式')

    args = parser.parse_args()

    if args.debug:
        print("调试模式启用")

    try:
        if args.mode == 'smart':
            run_smart_mode(args)
        elif args.mode == 'interactive':
            run_interactive_mode(args)
        elif args.mode == 'generate':
            run_generate_mode(args)
        elif args.mode == 'validate':
            run_validate_mode(args)
        elif args.mode == 'example':
            run_example_mode(args)
        else:
            print(f"错误：未知模式: {args.mode}")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误：{e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()