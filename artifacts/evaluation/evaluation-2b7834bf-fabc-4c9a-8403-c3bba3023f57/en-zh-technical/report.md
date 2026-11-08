# 翻译运行报告

- 模式：真实模型调用
- 运行 ID：752e111c-6694-4978-a8ee-1ee291564aca
- 时间：2026-11-03T01:17:33.865203+00:00
- 后端：ollama
- 模型：gemma3:1b
- 状态：completed

## 请求与生成配置

```
{
  "request": {
    "text": "The cache expires after 30 minutes. A cache miss does not mean the record has been deleted; query the primary database before returning a not-found response.",
    "source_lang": "English",
    "target_lang": "中文",
    "locale": "zh-CN",
    "style": "严谨的开发者文档，保留否定与条件关系",
    "glossary": {
      "cache miss": "缓存未命中",
      "primary database": "主数据库",
      "cache": "缓存"
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
缓存过期时间为30分钟。缓存未命中并不意味着记录已被删除；在主数据库前检索后再返回未找到响应。
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
缓存过期时间为30分钟。缓存未命中并不意味着记录已被删除；在主数据库前检索后再返回未找到响应。
```

## 规则检查

```
{
  "method": "术语按区分大小写的字面子串匹配，仅检查原文出现的术语；占位符按原样及出现次数比较。规则结果不是整体翻译质量评分。",
  "initial": {
    "terminology": {
      "applicable": 3,
      "matched": 3,
      "terms": [
        {
          "source": "cache miss",
          "target": "缓存未命中",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "primary database",
          "target": "主数据库",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "cache",
          "target": "缓存",
          "matched": true,
          "target_occurrences": 2
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
      "matched": 3,
      "terms": [
        {
          "source": "cache miss",
          "target": "缓存未命中",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "primary database",
          "target": "主数据库",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "cache",
          "target": "缓存",
          "matched": true,
          "target_occurrences": 2
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
| initial | completed | 1 | 0.823 | 291 | 30 |  |
| review | completed | 1 | 6.698 | 862 | 19 |  |
| revision | skipped | 0 | 未测量 | 未提供 | 未提供 | 审校未发现问题，无需修订；保留初译。 |

完整逐次调用记录与原始输出见同名 JSON 文件。
