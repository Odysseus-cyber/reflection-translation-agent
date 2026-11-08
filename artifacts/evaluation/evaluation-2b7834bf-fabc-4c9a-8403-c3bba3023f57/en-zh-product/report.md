# 翻译运行报告

- 模式：真实模型调用
- 运行 ID：3085ff43-844c-44b3-a882-08ed1927eac6
- 时间：2026-11-03T01:16:49.984721+00:00
- 后端：ollama
- 模型：gemma3:1b
- 状态：completed

## 请求与生成配置

```
{
  "request": {
    "text": "Keep your team in sync with shared workspaces. Assign an owner to each task and receive a daily digest, without opening another dashboard.",
    "source_lang": "English",
    "target_lang": "中文",
    "locale": "zh-CN",
    "style": "自然简洁的产品文案，避免生硬直译",
    "glossary": {
      "workspaces": "工作区",
      "owner": "负责人",
      "daily digest": "每日摘要"
    }
  },
  "generation_settings": {
    "temperature": 0.2,
    "max_output_tokens": 4096,
    "ollama_num_ctx": 16384
  }
}
```

## 初译

```
团队成员与共享工作空间保持同步，为每个任务分配一名负责人，并接收一份每日摘要，无需打开其他仪表盘。
```

## 四维审校

### 准确性

未报告问题。

### 流畅性

未报告问题。

### 风格

未报告问题。

### 术语一致性

未报告问题。


## 修订

```
团队成员与共享工作空间保持同步，为每个任务分配一名负责人，并接收一份每日摘要，无需打开其他仪表盘。
```

## 规则检查

```
{
  "method": "术语按区分大小写的字面子串匹配，仅检查原文出现的术语；占位符按原样及出现次数比较。规则结果不是整体翻译质量评分。",
  "initial": {
    "terminology": {
      "applicable": 3,
      "matched": 2,
      "terms": [
        {
          "source": "workspaces",
          "target": "工作区",
          "matched": false,
          "target_occurrences": 0
        },
        {
          "source": "owner",
          "target": "负责人",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "daily digest",
          "target": "每日摘要",
          "matched": true,
          "target_occurrences": 1
        }
      ]
    },
    "placeholders": {
      "expected": {},
      "found": {},
      "missing": {},
      "extra": {},
      "preserved": true
    }
  },
  "revised": {
    "terminology": {
      "applicable": 3,
      "matched": 2,
      "terms": [
        {
          "source": "workspaces",
          "target": "工作区",
          "matched": false,
          "target_occurrences": 0
        },
        {
          "source": "owner",
          "target": "负责人",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "daily digest",
          "target": "每日摘要",
          "matched": true,
          "target_occurrences": 1
        }
      ]
    },
    "placeholders": {
      "expected": {},
      "found": {},
      "missing": {},
      "extra": {},
      "preserved": true
    }
  }
}
```

## 阶段记录

| 阶段 | 状态 | 调用次数 | 实测耗时（秒） | 输入 tokens | 输出 tokens | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| initial | completed | 1 | 0.692 | 283 | 30 |  |
| review | completed | 1 | 0.879 | 854 | 19 |  |
| revision | skipped | 0 | 未测量 | 未提供 | 未提供 | 审校未发现问题，无需修订；保留初译。 |

完整逐次调用记录与原始输出见同名 JSON 文件。
