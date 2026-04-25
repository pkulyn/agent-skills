#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
高级专业Agent配置验证工具
验证生成的配置文件的完整性、一致性和质量
版本: 1.0
作者: pkulyn
日期: 2026-04-09
"""

import os
import re
import json
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

class ValidationLevel(Enum):
    """验证级别"""
    BASIC = "basic"      # 基础验证（文件存在性、格式）
    STANDARD = "standard" # 标准验证（完整性、基本一致性）
    STRICT = "strict"    # 严格验证（完整一致性、质量检查）

class ValidationResult(Enum):
    """验证结果"""
    PASS = "pass"
    WARNING = "warning"
    ERROR = "error"

@dataclass
class ValidationIssue:
    """验证问题"""
    file: str
    line: Optional[int]
    issue_type: ValidationResult
    message: str
    suggestion: Optional[str] = None

@dataclass
class ValidationReport:
    """验证报告"""
    config_dir: str
    validation_level: ValidationLevel
    validation_date: str
    total_files: int
    total_issues: int
    errors: int
    warnings: int
    issues_by_file: Dict[str, List[ValidationIssue]]
    summary: Dict[str, Any]
    recommendations: List[str]

class ConfigValidator:
    """配置验证器"""

    # 默认的必需配置文件（OpenClaw格式）
    DEFAULT_REQUIRED_FILES = ["SOUL.md", "IDENTITY.md", "TOOLS.md", "AGENTS.md", "USER.md"]

    # 多Agent团队级必需文件
    MULTI_AGENT_TEAM_FILES = ["team_configuration.json", "TEAM_CONFIGURATION.md"]

    # 多Agent遗留文件（向后兼容）
    MULTI_AGENT_LEGACY_FILES = ["team_info.json", "collaboration_rules.json"]

    # 默认的必需关键配置项（OpenClaw格式）
    DEFAULT_REQUIRED_SECTIONS = {
        "SOUL.md": [
            "性格底色",
            "价值观",
            "表达风格",
            "做事规矩",
            "边界和禁忌"
        ],
        "IDENTITY.md": [
            "Name",
            "Role",
            "One-liner"
        ],
        "TOOLS.md": [
            "本地技术环境",
            "领域专用工具"
        ],
        "AGENTS.md": [
            "会话启动协议",
            "记忆系统",
            "核心工作流程",
            "共享空间行为规范",
            "交付标准"
        ],
        "USER.md": [
            "基础信息",
            "专业背景",
            "沟通偏好",
            "项目上下文"
        ]
    }

    # 配置文件间的一致性检查项
    CONSISTENCY_CHECKS = [
        {
            "name": "领域一致性",
            "files": ["SOUL.md", "IDENTITY.md", "TOOLS.md", "AGENTS.md"],
            "patterns": [r"domain[：:]\s*([^\n]+)", r"领域[：:]\s*([^\n]+)"],
            "description": "各文件中的专业领域应一致"
        },
        {
            "name": "角色定义一致性",
            "files": ["SOUL.md", "IDENTITY.md", "AGENTS.md"],
            "patterns": [r"Role:\s*([^\n]+)", r"角色定义[：:]\s*([^\n]+)", r"Agent名称[：:]\s*([^\n]+)"],
            "description": "各文件中的角色定义应一致"
        },
        {
            "name": "SOUL/IDENTITY分工一致性",
            "files": ["SOUL.md", "IDENTITY.md"],
            "patterns": [r"(做事规矩|表达风格|边界和禁忌|性格底色|看家本事)", r"(角色定义|评分体系|情感表达模式|多维评分)"],
            "description": "SOUL.md和IDENTITY.md不应有内容重叠"
        }
    ]

    def __init__(self, config_dir: str, validation_level: ValidationLevel = ValidationLevel.STANDARD,
                 config_format: str = "openclaw"):
        """
        初始化验证器

        Args:
            config_dir: 配置文件目录
            validation_level: 验证级别
            config_format: 配置格式 (openclaw 或 claudecode)
        """
        self.config_dir = Path(config_dir)
        self.validation_level = validation_level
        self.config_format = config_format
        self.issues = []
        self.file_contents = {}

        # 根据配置格式设置必需的配置文件和章节
        if config_format == "claudecode":
            # Claude Code格式必需的文件
            self.REQUIRED_FILES = ["CLAUDE.md"]
            # 查找所有.md文件（除了CLAUDE.md）作为Agent配置文件
            # 这里我们不在初始化时检查，而是在验证时动态查找

            # Claude Code格式必需的章节
            self.REQUIRED_SECTIONS = {
                "CLAUDE.md": [
                    "项目概述",
                    "核心工作规则",
                    "标准通用工作流程",
                    "Agent配置说明",
                    "工具与环境",
                    "文件命名规范"
                ],
                # 通用的Agent配置文件必需章节
                "agent_config": [
                    "核心身份定位",
                    "强制遵守规则",
                    "遵循标准工作流程",
                    "核心工作职责",
                    "专业能力与工具",
                    "用户理解与沟通",
                    "工作质量标准"
                ]
            }
        else:
            # OpenClaw格式
            self.REQUIRED_FILES = self.DEFAULT_REQUIRED_FILES
            self.REQUIRED_SECTIONS = self.DEFAULT_REQUIRED_SECTIONS

    def _read_file(self, filepath: Path) -> Optional[List[str]]:
        """读取文件内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.readlines()
        except Exception as e:
            self.issues.append(ValidationIssue(
                file=filepath.name,
                line=None,
                issue_type=ValidationResult.ERROR,
                message=f"无法读取文件: {e}",
                suggestion="检查文件权限和编码"
            ))
            return None

    def _find_section(self, content: List[str], section_name: str) -> Tuple[bool, Optional[int]]:
        """查找章节，支持Markdown标题和key: value格式"""
        for i, line in enumerate(content):
            # 匹配Markdown标题格式 (## 标题)
            if re.search(rf'^#+.*{re.escape(section_name)}', line):
                return True, i
            # 匹配key: value格式 (IDENTITY.md锚点格式)
            if re.match(rf'^{re.escape(section_name)}\s*:', line):
                return True, i
        return False, None

    def _extract_pattern_value(self, content: List[str], pattern: str) -> List[str]:
        """提取模式匹配的值"""
        values = []
        for line in content:
            match = re.search(pattern, line)
            if match:
                values.append(match.group(1).strip())
        return values

    def validate_file_existence(self) -> List[ValidationIssue]:
        """验证文件存在性"""
        issues = []
        for filename in self.REQUIRED_FILES:
            filepath = self.config_dir / filename
            if not filepath.exists():
                issues.append(ValidationIssue(
                    file=filename,
                    line=None,
                    issue_type=ValidationResult.ERROR,
                    message=f"必需的文件不存在",
                    suggestion=f"确保{filename}文件在配置目录中"
                ))
            else:
                # 读取文件内容
                content = self._read_file(filepath)
                if content:
                    self.file_contents[filename] = content

        # 对于Claude Code格式，扫描.agents目录下的Agent配置文件
        if self.config_format == "claudecode":
            agents_dir = self.config_dir / ".agents"
            if agents_dir.exists():
                for agent_file in agents_dir.glob("*.md"):
                    content = self._read_file(agent_file)
                    if content:
                        self.file_contents[agent_file.name] = content
            else:
                # .agents目录不存在是警告，不是错误
                issues.append(ValidationIssue(
                    file=".agents/",
                    line=None,
                    issue_type=ValidationResult.WARNING,
                    message=f".agents目录不存在",
                    suggestion=f"创建.agents目录并添加Agent配置文件"
                ))

        return issues

    def validate_file_format(self) -> List[ValidationIssue]:
        """验证文件格式"""
        issues = []
        for filename, content in self.file_contents.items():
            # 检查文件是否为空
            if not content:
                issues.append(ValidationIssue(
                    file=filename,
                    line=None,
                    issue_type=ValidationResult.ERROR,
                    message="文件为空",
                    suggestion="重新生成配置文件"
                ))
                continue

            # 检查是否包含必要的元数据
            has_frontmatter = False
            for i, line in enumerate(content[:10]):
                if line.strip() == "---":
                    has_frontmatter = True
                    break

            if not has_frontmatter:
                issues.append(ValidationIssue(
                    file=filename,
                    line=None,
                    issue_type=ValidationResult.WARNING,
                    message="缺少Frontmatter元数据",
                    suggestion="添加Frontmatter元数据以包含版本和领域信息"
                ))

            # 检查Markdown格式
            header_count = sum(1 for line in content if re.match(r'^#+\s', line))

            # IDENTITY.md锚点格式只有一个主标题，不需要多个标题
            is_key_value_format = any(
                re.match(r'^(Name|Role|One-liner|Relationship vibe|Vibe|Emoji)\s*:', line)
                for line in content[:15]
            )

            if header_count < 3 and not is_key_value_format:
                issues.append(ValidationIssue(
                    file=filename,
                    line=None,
                    issue_type=ValidationResult.WARNING,
                    message=f"标题数量较少（{header_count}个），可能内容不完整",
                    suggestion="确保配置文件有完整的章节结构"
                ))

        return issues

    def validate_section_completeness(self) -> List[ValidationIssue]:
        """验证章节完整性"""
        issues = []
        for filename, required_sections in self.REQUIRED_SECTIONS.items():
            if filename not in self.file_contents:
                continue

            content = self.file_contents[filename]
            for section in required_sections:
                found, line_num = self._find_section(content, section)
                if not found:
                    issues.append(ValidationIssue(
                        file=filename,
                        line=None,
                        issue_type=ValidationResult.ERROR,
                        message=f"缺少必需章节: {section}",
                        suggestion=f"在{filename}中添加'{section}'章节"
                    ))
                else:
                    # 检查章节内容是否为空（至少有几行内容）
                    # 对于key: value格式（如IDENTITY.md锚点），单行也是有效的
                    section_content = []
                    for i in range(line_num + 1, min(line_num + 10, len(content))):
                        if re.match(r'^#+\s', content[i]):  # 遇到下一个章节
                            break
                        if content[i].strip():
                            section_content.append(content[i])

                    # key: value格式的行本身就是内容
                    if content[line_num].strip() and ':' in content[line_num] and not content[line_num].startswith('#'):
                        # 键值对格式，内容已在标题行中
                        continue

                    # SOUL.md的性格底色章节允许单行描述
                    if len(section_content) < 2 and filename == "SOUL.md" and section == "性格底色":
                        # 单句性格描述是正常的，跳过
                        continue

                    if len(section_content) < 2:
                        issues.append(ValidationIssue(
                            file=filename,
                            line=line_num + 1,
                            issue_type=ValidationResult.WARNING,
                            message=f"章节内容可能过少: {section}",
                            suggestion=f"丰富'{section}'章节的内容"
                        ))

        # 对于Claude Code格式，检查Agent配置文件的章节完整性
        if self.config_format == "claudecode":
            agent_sections = self.REQUIRED_SECTIONS.get("agent_config", [])
            for filename, content in self.file_contents.items():
                if filename != "CLAUDE.md" and filename.endswith(".md"):
                    for section in agent_sections:
                        found, line_num = self._find_section(content, section)
                        if not found:
                            issues.append(ValidationIssue(
                                file=filename,
                                line=None,
                                issue_type=ValidationResult.WARNING,
                                message=f"可能缺少建议章节: {section}",
                                suggestion=f"考虑在{filename}中添加'{section}'章节以增强配置完整性"
                            ))

        return issues

    def validate_parameter_consistency(self) -> List[ValidationIssue]:
        """验证参数一致性"""
        if self.validation_level != ValidationLevel.STRICT:
            return []

        issues = []
        consistency_data = {}

        # 收集各文件的参数值
        for check in self.CONSISTENCY_CHECKS:
            file_values = {}
            for filename in check["files"]:
                if filename not in self.file_contents:
                    continue

                values = []
                for pattern in check["patterns"]:
                    values.extend(self._extract_pattern_value(self.file_contents[filename], pattern))

                if values:
                    file_values[filename] = values

            # 检查一致性
            if len(file_values) > 1:
                all_values = []
                for values in file_values.values():
                    all_values.extend(values)

                # 检查是否所有值都相同
                unique_values = set(all_values)
                if len(unique_values) > 1:
                    value_str = ", ".join([f"{f}: {v}" for f, v in file_values.items()])
                    issues.append(ValidationIssue(
                        file="multiple",
                        line=None,
                        issue_type=ValidationResult.ERROR,
                        message=f"{check['name']}不一致: {value_str}",
                        suggestion=f"确保{check['description']}，统一为相同值"
                    ))

            consistency_data[check["name"]] = file_values

        return issues

    def validate_parameter_ranges(self) -> List[ValidationIssue]:
        """验证参数范围合理性"""
        issues = []

        # 检查配置文件中不应出现的数字评分和伪环境变量
        numeric_score_patterns = [
            (r'情感智能.*?(\d+)/10', "数字评分不应出现在配置文件中，应使用自然语言描述"),
            (r'技术深度.*?(\d+)/10', "数字评分不应出现在配置文件中，应使用自然语言描述"),
            (r'EMOTIONAL_INTELLIGENCE_LEVEL', "伪环境变量不应出现在配置文件中"),
            (r'ENCOURAGEMENT_FREQUENCY', "伪环境变量不应出现在配置文件中"),
            (r'STRESS_RECOGNITION_SENSITIVITY', "伪环境变量不应出现在配置文件中"),
        ]

        for filename in ["SOUL.md", "IDENTITY.md", "TOOLS.md", "AGENTS.md"]:
            if filename not in self.file_contents:
                continue

            content = self.file_contents[filename]
            for i, line in enumerate(content):
                for pattern, msg in numeric_score_patterns:
                    if re.search(pattern, line):
                        issues.append(ValidationIssue(
                            file=filename,
                            line=i + 1,
                            issue_type=ValidationResult.WARNING,
                            message=msg,
                            suggestion="将数字评分替换为自然语言行为描述"
                        ))

        return issues

    def validate_content_quality(self) -> List[ValidationIssue]:
        """验证内容质量"""
        if self.validation_level != ValidationLevel.STRICT:
            return []

        issues = []

        # 检查模板化内容
        template_phrases = [
            "待补充",
            "信息待补充",
            "示例",
            "_示例",
            "请填写"
        ]

        for filename, content in self.file_contents.items():
            for i, line in enumerate(content):
                for phrase in template_phrases:
                    if phrase in line:
                        issues.append(ValidationIssue(
                            file=filename,
                            line=i + 1,
                            issue_type=ValidationResult.WARNING,
                            message=f"包含模板占位符: {phrase}",
                            suggestion="替换为具体内容，避免使用模板占位符"
                        ))
                        break

        # 检查情感表达的自然度
        mechanical_phrases = [
            "根据情感智能参数",
            "基于配置",
            "根据设置",
            "自动生成",
            "真诚地帮助用户，而不是表演性地提供帮助",
            "配置说明",
            "优化提示"
        ]

        for filename in ["SOUL.md", "AGENTS.md"]:
            if filename not in self.file_contents:
                continue

            content = self.file_contents[filename]
            for i, line in enumerate(content):
                for phrase in mechanical_phrases:
                    if phrase in line:
                        issues.append(ValidationIssue(
                            file=filename,
                            line=i + 1,
                            issue_type=ValidationResult.WARNING,
                            message=f"表达可能过于机械: {phrase}",
                            suggestion="使用更自然、人性化的表达方式"
                        ))
                        break

        return issues

    def validate_official_spec_compliance(self) -> List[ValidationIssue]:
        """验证是否符合OpenClaw官方规范要求"""
        if self.validation_level != ValidationLevel.STRICT:
            return []

        issues = []

        # 检查AGENTS.md是否包含官方规范要素
        if "AGENTS.md" in self.file_contents:
            content = self.file_contents["AGENTS.md"]
            content_text = ''.join(content)

            required_elements = [
                ("会话启动协议", "AGENTS.md缺少会话启动协议（SOUL.md→USER.md→memory→MEMORY.md）"),
                ("记忆系统", "AGENTS.md缺少记忆系统配置（MEMORY.md + memory/目录）"),
                ("共享空间", "AGENTS.md缺少共享空间行为规范"),
            ]

            for element, message in required_elements:
                if element not in content_text:
                    issues.append(ValidationIssue(
                        file="AGENTS.md",
                        line=None,
                        issue_type=ValidationResult.WARNING,
                        message=message,
                        suggestion=f"在AGENTS.md中添加{element}相关章节"
                    ))

        # 检查SOUL.md是否包含边界规范
        if "SOUL.md" in self.file_contents:
            content = self.file_contents["SOUL.md"]
            content_text = ''.join(content)

            boundary_elements = [
                ("代言人", "SOUL.md缺少'不是用户代言人'边界声明"),
                ("私密信息", "SOUL.md缺少私密信息保护规则"),
            ]

            for element, message in boundary_elements:
                if element not in content_text:
                    issues.append(ValidationIssue(
                        file="SOUL.md",
                        line=None,
                        issue_type=ValidationResult.WARNING,
                        message=message,
                        suggestion=f"在SOUL.md的'边界和禁忌'章节中添加相关声明"
                    ))

        # 检查IDENTITY.md是否为锚点格式
        if "IDENTITY.md" in self.file_contents:
            content = self.file_contents["IDENTITY.md"]
            content_text = ''.join(content)

            # 检查是否包含旧格式的评分体系
            if "多维评分体系" in content_text or "情感表达模式库" in content_text:
                issues.append(ValidationIssue(
                    file="IDENTITY.md",
                    line=None,
                    issue_type=ValidationResult.WARNING,
                    message="IDENTITY.md仍使用旧格式（评分体系/情感模式库），应简化为锚点格式",
                    suggestion="将IDENTITY.md简化为Name/Role/One-liner/Relationship vibe/Vibe/Emoji格式"
                ))

        return issues

    def validate_cross_agent_user_consistency(self, other_config_dirs: List[str] = None) -> List[ValidationIssue]:
        """验证跨Agent USER.md事实信息一致性

        Args:
            other_config_dirs: 其他Agent配置文件目录列表
        """
        if self.validation_level != ValidationLevel.STRICT:
            return []

        if not other_config_dirs:
            return []

        issues = []

        # 先检查当前目录是否有user_facts.json
        facts_path = self.config_dir / "user_facts.json"
        if not facts_path.exists():
            issues.append(ValidationIssue(
                file="user_facts.json",
                line=None,
                issue_type=ValidationResult.WARNING,
                message="缺少user_facts.json，无法验证跨Agent USER.md一致性",
                suggestion="运行配置生成器生成user_facts.json以保证多Agent间事实信息一致"
            ))
            return issues

        # 加载基准事实
        try:
            with open(facts_path, 'r', encoding='utf-8') as f:
                base_facts = json.load(f)
        except Exception:
            return issues

        # 对比其他目录的USER.md
        base_name = base_facts.get("name", "")
        for other_dir in other_config_dirs:
            other_user_path = Path(other_dir) / "USER.md"
            if not other_user_path.exists():
                continue

            try:
                with open(other_user_path, 'r', encoding='utf-8') as f:
                    other_content = f.read()

                # 检查用户名称是否一致
                if base_name and base_name not in other_content:
                    # 尝试模糊匹配
                    name_variants = [base_name.lower(), base_name.upper(), base_name.capitalize()]
                    found = any(v in other_content for v in name_variants)
                    if not found:
                        issues.append(ValidationIssue(
                            file=f"{other_dir}/USER.md",
                            line=None,
                            issue_type=ValidationResult.WARNING,
                            message=f"用户名称不一致：基准'{base_name}'，该文件中未找到",
                            suggestion="使用user_facts.json保证跨Agent用户名称一致"
                        ))
            except Exception:
                continue

        return issues

    def validate(self) -> ValidationReport:
        """执行完整的验证"""
        print(f"开始验证配置文件...")
        print(f"配置目录: {self.config_dir}")
        print(f"验证级别: {self.validation_level.value}")

        # 执行各项验证
        all_issues = []

        # 1. 文件存在性验证
        print("[CHECK] 验证文件存在性...")
        all_issues.extend(self.validate_file_existence())

        # 2. 文件格式验证
        print("[CHECK] 验证文件格式...")
        all_issues.extend(self.validate_file_format())

        # 3. 章节完整性验证
        print("[CHECK] 验证章节完整性...")
        all_issues.extend(self.validate_section_completeness())

        # 4. 参数一致性验证
        if self.validation_level.value in ["standard", "strict"]:
            print("[CHECK] 验证参数一致性...")
            all_issues.extend(self.validate_parameter_consistency())

        # 5. 参数范围验证
        if self.validation_level.value in ["standard", "strict"]:
            print("[CHECK] 验证参数范围...")
            all_issues.extend(self.validate_parameter_ranges())

        # 6. 内容质量验证
        if self.validation_level.value == "strict":
            print("[CHECK] 验证内容质量...")
            all_issues.extend(self.validate_content_quality())

        # 7. 官方规范合规验证
        if self.validation_level.value == "strict":
            print("[CHECK] 验证官方规范合规性...")
            all_issues.extend(self.validate_official_spec_compliance())

        # 按文件分组问题
        issues_by_file = {}
        for issue in all_issues:
            if issue.file not in issues_by_file:
                issues_by_file[issue.file] = []
            issues_by_file[issue.file].append(issue)

        # 统计
        total_issues = len(all_issues)
        errors = sum(1 for issue in all_issues if issue.issue_type == ValidationResult.ERROR)
        warnings = sum(1 for issue in all_issues if issue.issue_type == ValidationResult.WARNING)

        # 生成摘要
        summary = {
            "total_files": len(self.file_contents),
            "missing_files": len([f for f in self.REQUIRED_FILES if f not in self.file_contents]),
            "total_issues": total_issues,
            "errors": errors,
            "warnings": warnings,
            "validation_level": self.validation_level.value,
            "passed": errors == 0
        }

        # 生成建议
        recommendations = []
        if errors > 0:
            recommendations.append("修复所有ERROR级别的问题后再部署")
        if warnings > 0:
            recommendations.append("考虑修复WARNING级别的问题以提升配置质量")
        if len(self.file_contents) < len(self.REQUIRED_FILES):
            recommendations.append(f"缺少{len(self.REQUIRED_FILES) - len(self.file_contents)}个必需文件，请重新生成")
        if total_issues == 0:
            recommendations.append("配置验证通过，可以部署使用")

        # 创建报告
        report = ValidationReport(
            config_dir=str(self.config_dir),
            validation_level=self.validation_level,
            validation_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_files=len(self.file_contents),
            total_issues=total_issues,
            errors=errors,
            warnings=warnings,
            issues_by_file=issues_by_file,
            summary=summary,
            recommendations=recommendations
        )

        print(f"\n[OK] 验证完成!")
        print(f"文件数: {report.total_files}/5")
        print(f"问题总数: {report.total_issues} (错误: {errors}, 警告: {warnings})")
        print(f"验证结果: {'通过' if errors == 0 else '失败'}")

        return report

def generate_markdown_report(report: ValidationReport, output_file: str) -> str:
    """生成Markdown格式的验证报告"""

    # 按严重程度排序问题
    all_issues = []
    for file_issues in report.issues_by_file.values():
        all_issues.extend(file_issues)

    # 按文件排序
    sorted_files = sorted(report.issues_by_file.keys())

    # 生成报告
    report_content = f"""# 高级专业Agent配置验证报告

## 验证概览

**验证时间**：{report.validation_date}

**配置目录**：{report.config_dir}

**验证级别**：{report.validation_level.value}

**验证结果**：{'[OK] 通过' if report.summary['passed'] else '[ERROR] 失败'}

## 验证摘要

| 项目 | 结果 |
|------|------|
| 配置文件数量 | {report.total_files}/5 |
| 验证问题总数 | {report.total_issues} |
| 错误(ERROR) | {report.errors} |
| 警告(WARNING) | {report.warnings} |
| 验证通过 | {'是' if report.summary['passed'] else '否'} |

## 详细问题列表

"""

    if report.total_issues == 0:
        report_content += "[OK] 未发现任何问题，配置验证通过。\n\n"
    else:
        for filename in sorted_files:
            issues = report.issues_by_file[filename]
            if not issues:
                continue

            report_content += f"### {filename}\n\n"

            # 按问题类型分组
            error_issues = [i for i in issues if i.issue_type == ValidationResult.ERROR]
            warning_issues = [i for i in issues if i.issue_type == ValidationResult.WARNING]

            if error_issues:
                report_content += "#### [ERROR] 错误\n\n"
                for issue in error_issues:
                    line_info = f"第{issue.line}行" if issue.line else "未知行"
                    report_content += f"- **{line_info}**: {issue.message}\n"
                    if issue.suggestion:
                        report_content += f"  - 建议: {issue.suggestion}\n"
                report_content += "\n"

            if warning_issues:
                report_content += "#### [WARNING] 警告\n\n"
                for issue in warning_issues:
                    line_info = f"第{issue.line}行" if issue.line else "未知行"
                    report_content += f"- **{line_info}**: {issue.message}\n"
                    if issue.suggestion:
                        report_content += f"  - 建议: {issue.suggestion}\n"
                report_content += "\n"

    # 生成建议部分
    report_content += "## 修复建议\n\n"
    if report.recommendations:
        for rec in report.recommendations:
            report_content += f"- {rec}\n"
    else:
        report_content += "无特定建议。\n"

    # 生成部署建议
    report_content += "\n## 部署建议\n\n"
    if report.errors > 0:
        report_content += "**[ERROR] 不建议部署**\n\n"
        report_content += "由于存在错误级别的问题，建议先修复所有错误后再部署。\n"
    elif report.warnings > 0:
        report_content += "**[WARNING] 可以部署，但建议修复警告**\n\n"
        report_content += "配置基本可用，但存在一些警告级别的问题。建议在部署前或部署后修复这些问题以提升配置质量。\n"
    else:
        report_content += "**[OK] 可以立即部署**\n\n"
        report_content += "配置验证通过，无任何问题。可以立即部署使用。\n"

    # 生成后续步骤
    report_content += "\n## 后续步骤\n\n"
    if report.errors > 0:
        report_content += "1. **修复错误**：根据错误列表修复所有错误\n"
        report_content += "2. **重新验证**：修复后重新运行验证工具\n"
        report_content += "3. **部署测试**：在测试环境部署验证\n"
        report_content += "4. **生产部署**：确认无误后部署到生产环境\n"
    else:
        report_content += "1. **备份配置**：部署前备份现有配置（如有）\n"
        report_content += "2. **测试部署**：先在测试环境部署验证\n"
        report_content += "3. **监控性能**：部署后监控Agent性能指标\n"
        report_content += "4. **收集反馈**：收集用户反馈，持续优化\n"

    # 生成联系信息
    report_content += f"""
---

**验证工具版本**：1.0
**验证日期**：{report.validation_date}
**配置目录**：{report.config_dir}

**重要提示**：
- 本报告为自动生成，基于配置验证规则
- 验证结果仅供参考，实际效果可能因具体环境而异
- 建议结合人工审查确保配置质量
"""

    # 保存报告
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    return report_content