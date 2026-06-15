# 状态管理与增量更新规范

## registry.json 结构

```json
{
  "version": 1,
  "lastUpdated": "2026-04-22T14:30:00+08:00",
  "files": {
    "Clippings/some-article.md": {
      "hash": "a1b2c3d4e5f6789012345678abcdef01",
      "mtime": "2026-04-10T12:00:00.000Z",
      "lastProcessed": "2026-04-22T14:30:00+08:00",
      "generatedPages": [
        "Wiki/summaries/2026-04-22_some-article.md",
        "Wiki/entities/Some-Entity.md"
      ],
      "status": "processed",
      "batchTaskId": null
    }
  }
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| hash | string | 源文件MD5哈希（32字符十六进制），与watcher.js对齐 |
| mtime | string | 源文件最后修改时间（ISO 8601） |
| lastProcessed | string | 最后成功处理时间 |
| generatedPages | string[] | 生成的Wiki页面相对路径列表 |
| status | string | `processed` / `error` / `source_deleted` / `skipped_invalid_content` |
| conflictSkipped | boolean | 可选，因冲突被跳过 |
| batchTaskId | string/null | 批量任务ID |

## 幂等性检查流程

```
INGEST/BATCH执行前：
  读取 registry.json → 计算源文件MD5哈希
  → 不在registry: 标记"新增"，完整执行INGEST
  → 在registry且哈希相同: 跳过（已处理）
  → 在registry但哈希不同: 标记"需更新"，创建快照后走更新流程
```

## 增量更新执行规范

当源文件哈希变化触发「需更新」时，**不得只更新摘要而忽略实体和主题**：

1. **摘要更新**：快照旧摘要 → 重新生成
2. **实体同步更新**：对比新旧摘要的实体列表 → 新增/保留/移除引用
3. **主题同步更新**：对比新旧摘要的主题列表 → 新增/移除/更新引用
4. **交叉引用修复**：确保所有双链引用一致，无孤立引用
5. **注册表更新**：更新hash、lastProcessed、generatedPages

**增量更新检查清单**：
- [ ] 新摘要已正确生成，旧摘要已快照
- [ ] 实体页面已同步更新
- [ ] 主题页面已同步更新
- [ ] 无孤立双链引用
- [ ] registry.json已更新

## 快照与回滚规范

### manifest.json 结构

```json
{
  "taskId": "batch-20260422-143000",
  "createdAt": "2026-04-22T14:30:00+08:00",
  "taskType": "INGEST",
  "source": "王孟源博客/军事/",
  "pages": [
    {
      "path": "Wiki/entities/F-22战斗机.md",
      "action": "update",
      "snapshotFile": "entities_F-22战斗机.md"
    }
  ]
}
```

- `create`：本次新建的页面。回滚时删除。
- `update`：本次修改的已有页面。回滚时从快照恢复。
- 快照文件命名：路径中`/`替换为`_`

### 快照创建校验

创建快照后立即验证：
1. manifest.json存在且可读取
2. 每个snapshotFile实际存在于快照目录中
3. 验证不通过则暂停任务，不可跳过快照继续

## 哈希计算规范

| 属性 | 规范 |
|------|------|
| 算法 | MD5（128位） |
| 输出 | 32字符十六进制字符串（小写） |
| 计算方式 | 读取文件完整二进制内容后计算 |
| 用途 | 幂等性判断、增量更新检测 |
| 存储 | registry.json的hash字段 + 摘要frontmatter的source_hash + log.md |

## 文件路径双重校验规范

所有Wiki页面写入前必须执行路径校验，**杜绝写入源文件目录**：

1. **写入前校验**：目标路径必须以Wiki/summaries/、Wiki/entities/或Wiki/topics/开头
2. **写入后验证**：用Glob确认文件实际写入到正确子目录
3. **批量任务结束校验**：扫描确认所有generatedPages存在 + 源目录无Wiki页面被误写

## 内容有效性判定标准

| 维度 | 无效标准 | 有效标准 |
|------|----------|----------|
| 内容实质 | 无字幕标记、纯广告推广、纯引流 | 有可提取的知识、观点、信息 |
| 信息密度 | 无明确主题、无具体知识点 | 至少1个主题、2个以上知识点 |
| 结构完整性 | 内容严重残缺、乱码、截断 | 内容完整可读 |
| 知识价值 | 日常闲聊、纯情绪宣泄 | 具有学习或参考价值 |

跳过时记录：registry.json标记`status: "skipped_invalid_content"`，log.md记录原因。
