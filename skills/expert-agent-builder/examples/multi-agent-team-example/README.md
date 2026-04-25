# 多Agent团队协作示例

本示例演示如何使用Expert Agent Builder创建和管理多Agent协作系统。

## 示例概述

这是一个技术团队协作示例，包含4个专业Agent：

1. **项目管家** - 首席协调官，负责全局调度和项目管理
2. **技术架构师** - 架构设计专家，负责系统架构设计和技术选型
3. **开发专家** - 代码实现专家，负责代码开发和实现
4. **测试专家** - 质量保障专家，负责软件测试和质量保障

## 文件结构

```
multi-agent-team-example/
├── README.md                    # 本说明文件
├── user-profile.json           # 用户个人信息
├── team-info.json              # 团队信息
├── collaboration-rules.json    # 协作规则
├── agent-profile-project-manager.json      # 项目管家画像
├── agent-profile-technical-architect.json  # 技术架构师画像
├── agent-profile-developer-expert.json     # 开发专家画像
└── agent-profile-tester-expert.json        # 测试专家画像
```

## 使用方式

### 方法1：使用智能模式（推荐）

```bash
# 进入示例目录
cd examples/multi-agent-team-example

# 运行智能模式，选择多Agent配置
python ../../openclaw-config-generator.py --mode smart

# 按照交互提示选择：
# 1. 平台：openclaw 或 claudecode
# 2. 模式：multi-agent (多Agent)
# 3. 信息获取方式：document (资料整理模式)
# 4. 提供文档路径：当前目录 (.)
```

### 方法2：使用生成模式

```bash
# 使用现有文件生成多Agent配置
python ../../openclaw-config-generator.py \
  --mode generate \
  --user-profile user-profile.json \
  --agent-profile agent-profile-project-manager.json \
  --output-dir generated-config \
  --format both

# 注意：生成模式目前主要支持单Agent，多Agent需要智能模式
```

### 方法3：使用交互式模式

```bash
# 交互式创建多Agent配置
python ../../openclaw-config-generator.py --mode interactive

# 在交互过程中选择多Agent模式
```

## 团队协作模型

### 协调风格
- **领导协调型**：项目管家作为主要协调者
- **专业分工**：每个Agent专注于自己的专业领域
- **决策流程**：主Agent集中决策 + 专业Agent建议

### 通信协议
- **任务分配流程**：用户 → 项目管家 → 专业Agent
- **状态报告机制**：每日状态报告 + 关键里程碑报告 + 问题即时上报
- **错误处理流程**：错误识别 → 技术分析 → 方案制定 → 实施修复 → 结果验证

### 质量保证
- **审核流程**：代码审查 + 设计评审 + 测试验证 + 部署审核
- **质量标准**：代码规范符合率95%、测试覆盖率80%、性能指标达标率100%、用户满意度90%
- **改进周期**：每周回顾 + 每月评估 + 季度优化

### 性能监控
- **关键指标**：任务完成率、响应时间、问题解决率、用户满意度、协作效率
- **报告频率**：每日状态报告 + 每周性能报告 + 月度评估报告
- **优化触发条件**：性能下降10%、用户满意度低于80%、任务积压超过3天、协作效率低于预期

## 生成的配置

运行示例后，将生成以下配置：

### OpenClaw格式
```
generated-config/
├── collected-info/             # 收集的信息
│   ├── user_profile.json
│   ├── team_info.json
│   ├── collaboration_rules.json
│   └── agent_profiles/
│       ├── agent_1_profile.json
│       ├── agent_2_profile.json
│       ├── agent_3_profile.json
│       └── agent_4_profile.json
├── agent-config/
│   ├── agent_1/               # 项目管家配置
│   │   ├── SOUL.md
│   │   ├── IDENTITY.md
│   │   ├── TOOLS.md
│   │   ├── AGENTS.md
│   │   └── USER.md
│   ├── agent_2/               # 技术架构师配置
│   ├── agent_3/               # 开发专家配置
│   ├── agent_4/               # 测试专家配置
│   └── team-config/           # 团队级配置
│       ├── team_configuration.json
│       ├── TEAM_CONFIGURATION.md
│       ├── team_info.json     # 原始文件（向后兼容）
│       └── collaboration_rules.json
└── validation_report.md       # 验证报告
```

### Claude Code格式
```
generated-config/
├── claudecode-config/
│   ├── CLAUDE.md              # 项目手册
│   └── .agents/
│       ├── project-manager.md    # 项目管家
│       ├── technical-architect.md # 技术架构师
│       ├── developer-expert.md   # 开发专家
│       └── tester-expert.md      # 测试专家
└── validation_report.md
```

## 扩展和定制

### 添加新Agent
1. 创建新的Agent画像JSON文件
2. 更新`team-info.json`中的`team_size`字段
3. 更新`collaboration-rules.json`中的`specialized_agents`列表
4. 重新运行配置生成

### 修改协作规则
1. 编辑`collaboration-rules.json`文件
2. 调整角色分配、通信协议、质量保证或性能监控参数
3. 重新运行配置生成

### 调整团队规模
1. 修改`team-info.json`中的`team_size`字段
2. 添加或删除Agent画像文件
3. 更新协作规则中的角色列表
4. 重新运行配置生成

## 最佳实践

1. **角色定义清晰**：确保每个Agent有明确的职责边界
2. **协作规则具体**：定义清晰的通信协议和决策流程
3. **质量指标可衡量**：设置具体的、可量化的质量指标
4. **性能监控持续**：建立持续的监控和改进机制
5. **团队规模适中**：根据实际需求确定团队规模，避免过度复杂化

## 注意事项

1. 多Agent配置需要Expert Agent Builder v2.0.0或更高版本
2. 智能模式是创建多Agent配置的推荐方式
3. 团队配置生成功能已集成协作规则到生成的配置文件中
4. 验证报告会检查团队配置的完整性

## 故障排除

### 常见问题
1. **文件找不到错误**：确保所有JSON文件在正确目录中
2. **JSON格式错误**：使用JSON验证工具检查文件格式
3. **权限问题**：确保有读写权限
4. **版本不兼容**：确保使用v2.0.0或更高版本

### 调试模式
```bash
# 启用详细日志
python ../../openclaw-config-generator.py --mode smart --debug
```

## 技术支持

- 文档：查看项目根目录的README.md
- 问题：在GitHub Issues中报告问题
- 社区：OpenClaw社区论坛

---
**版本**: 1.0  
**生成日期**: 2026-04-11  
**示例类型**: 多Agent团队协作  
**适用场景**: 技术团队协作、项目管理、质量保障