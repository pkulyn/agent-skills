# 专业领域与高级功能

## 内置专业领域（10个）

| 领域 | 核心立场 | 典型应用场景 |
|------|----------|-------------|
| **技术架构** | 好的架构是删出来的，不是加出来的 | 云原生架构、分布式系统、微服务设计 |
| **法律咨询** | 法律不是障碍，是护栏 | 法律文书、案例管理、合规审查 |
| **商业战略** | 数据不说谎，但数据也不说话——解读得靠人 | 竞争分析、商业模式、投资决策 |
| **创意设计** | 好看不等于好用，但难看一定不好用 | 品牌设计、创意策划、用户体验 |
| **医学研究** | 证据等级决定推荐力度 | 临床研究、文献综述、伦理审查 |
| **党政公文写作** | 措辞即立场，政治正确不是口号是底线 | 党务公文、党建材料、领导讲话稿 |
| **科幻小说创作** | 设定是为故事服务的，不是拿来炫技的 | 大纲设计、人物塑造、世界观构建 |
| **团队协作管理** | 流程不是目的，协作才是 | 项目管理、流程优化、团队协调 |
| **评审评估** | 评审不是找茬，是帮东西变好 | 技术评审、方案评审、质量评估 |
| **知识管理** | 知识不流动就是死知识 | 知识体系建设、信息组织、知识图谱 |

## 自定义领域扩展

通过JSON配置文件定义新的专业领域，无需修改源代码：

1. 在 `custom_domains/` 目录创建领域JSON配置文件（如`教育咨询.json`）
2. 定义领域特有的参数：`personality_base`、`domain_stance`、`speaking_rules`、`work_rules`、`taboos`、`emotional_style`等
3. 通过 `CustomDomainManager` API加载自定义领域

也可通过 `utils/domain_adapter.py` 的 `DOMAINS` 字典直接添加新领域。

## 高级功能

### 智能领域检测

```python
from utils.domain_detector import DomainDetector, suggest_domain

detector = DomainDetector()
results = detector.detect_domain("资深云原生架构师", top_k=3)
# 输出: [('技术架构', 95.5), ('商业战略', 42.1), ...]
```

### 模板覆盖机制

支持多级模板查找（自定义 → 领域特定 → 默认）和变量替换：

```python
from utils.template_manager import TemplateManager

manager = TemplateManager(custom_templates_dir="my_templates")
rendered = manager.render_template("soul_template.md", variables={"agent_name": "技术顾问"})
```

### 情感智能自然语言翻译

六维数字参数保留为内部计算维度，通过`_translate_emotional_params()`方法翻译为自然语言行为描述：

- EI>=8 → "对人的状态比较敏感，你不用说我也能感觉到哪里不对"
- EI 6-7 → "能注意到明显的情绪变化，一般状态还行"
- EI<6 → "主要关注事情本身，不太会主动关注情绪"

翻译结果写入SOUL.md的"表达风格"章节，配置文件中不再出现数字评分和伪环境变量。

## 故障排除

| 问题 | 解决 |
|------|------|
| Python版本不兼容 | 升级到Python 3.8+ |
| 模板文件缺失 | 确保模板文件存在于 `templates/` 目录 |
| JSON格式错误 | 检查引号、逗号、括号匹配 |
| 编码问题 | 确保文件使用UTF-8编码 |
| 权限问题 | 检查文件读写权限 |

调试命令：`python openclaw-config-generator.py --mode smart --debug`
