# 页面模板

**重要**：所有页面章节标题统一使用中文，禁止混用中英文。

## 摘要模板

```yaml
---
title: {标题}
date: YYYY-MM-DD
source: {源文件相对路径}
source_hash: {MD5哈希值}
tags: [摘要, {主题标签}]
batch_task_id: {任务ID或null}
---

# {标题}

## 核心要点

- 要点1
- 要点2
- 要点3

## 详细摘要

{全面摘要内容}

## 关联实体

- [[实体1]]
- [[实体2]]

## 关联主题

- [[主题1]]
- [[主题2]]

## 引用语录

> 来自源文件的重要引述

---
**来源**：[[../{源文件路径}]]
**录入时间**：YYYY-MM-DD
**源文件哈希**：{MD5哈希值}
**批量任务**：[[log.md#{任务ID}]]
```

## 实体模板

```yaml
---
title: {实体名称}
type: {人物/组织/工具/概念/地点/事件/武器装备}
aliases: [{别名1}, {别名2}]
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [entity, {类型标签}]
batch_task_id: {任务ID或null}
---

# {实体名称}

## 定义

{一句话定义}

## 详细信息

{全面描述}

## 相关实体

- [[实体A]] - 关系描述
- [[实体B]] - 关系描述

## 相关主题

- [[主题X]]
- [[主题Y]]

## 来源

- [[来源1]]
- [[来源2]]

---
**更新时间**：YYYY-MM-DD
```

**注意**：`type`字段必须使用中文类型值；`aliases`字段无别名时省略；日期不加引号。

## 主题模板

```yaml
---
title: {主题名称}
type: topic
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [topic, {领域标签}]
batch_task_id: {任务ID或null}
---

# {主题名称}

## 主题描述

{1-2句话描述涵盖范围}

## 核心概念

- [[概念A]]
- [[概念B]]

## 相关实体

- [[实体1]]
- [[实体2]]

## 相关摘要

- [[摘要1]]
- [[摘要2]]

## 子主题

- [[子主题1]]
- [[子主题2]]

## 相关主题

- [[相关主题1]]

---
**更新时间**：YYYY-MM-DD
```

## 索引模板

````yaml
---
title: Wiki全局索引
description: 知识库导航中心
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [index, navigation, meta]
---

# Wiki全局索引

## 结构

```
Wiki/
├── index.md      # 本文件
├── log.md        # 操作日志
├── .state/       # 状态管理
├── .snapshots/   # 回滚快照
├── entities/     # 实体页面
├── topics/       # 主题页面
└── summaries/    # 来源摘要
```

## 统计信息

| 分类 | 数量 |
|------|------|
| 实体 | {精确数字} |
| 主题 | {精确数字} |
| 摘要 | {精确数字} |
| 来源 | {精确数字} |

---
**由AI管理员维护**
**更新时间**：YYYY-MM-DD
````

## 批量任务报告模板

```yaml
---
title: 批量处理任务报告 {任务ID}
date: YYYY-MM-DD
task_type: 批量入库 / 批量修复
status: 已完成 / 处理失败 / 已回滚
tags: [batch, report, 批量]
---

# 批量处理任务报告 {任务ID}

## 任务基本信息
- **任务类型**: {批量入库/批量修复}
- **开始时间**: YYYY-MM-DD HH:MM
- **完成时间**: YYYY-MM-DD HH:MM
- **处理时长**: {X}分钟
- **源路径**: {source-path}

## 处理统计
| 指标 | 数量 |
|------|------|
| 总文件数 | {total} |
| 处理成功 | {success} |
| 处理失败 | {failed} |
| 跳过（已处理） | {skipped} |

## 质量检查统计

| 等级 | 数量 | 占比 |
|------|------|------|
| A (9/9) | {count} | {percent}% |
| B (7-8/9) | {count} | {percent}% |
| C (5-6/9) | {count} | {percent}% |
| D (<5/9) | {count} | {percent}% |

---
**任务ID**: {任务ID}
```

## 日志格式

### 普通操作
```markdown
## YYYY-MM-DD HH:MM [类型] 描述

- **类型**: 入库 / 查询 / 检查 / 更新
- **页面**: [[页面1]], [[页面2]]
- **来源**: [[来源]]
- **源文件哈希**: {MD5哈希值}
- **摘要**: 简要操作说明

---
```

### 批量任务
```markdown
## YYYY-MM-DD HH:MM [BATCH] 批量处理任务 {任务ID} - {状态}

- **任务ID**: {任务ID}
- **状态**: 已开始 / 已完成 / 处理失败 / 已回滚
- **统计**: 总文件{total}，成功{success}，失败{failed}，跳过{skipped}
- **报告**: [[Wiki/reports/batch-{任务ID}.md]]

---
```
