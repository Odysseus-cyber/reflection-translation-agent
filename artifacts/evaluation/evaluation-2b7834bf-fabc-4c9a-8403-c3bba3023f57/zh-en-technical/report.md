# 翻译运行报告

- 模式：真实模型调用
- 运行 ID：e678d46f-9c51-4b53-a27a-8644bc3a5b68
- 时间：2026-11-03T01:16:41.872377+00:00
- 后端：ollama
- 模型：gemma3:1b
- 状态：completed

## 请求与生成配置

```
{
  "request": {
    "text": "客户端应为每次写入请求生成幂等键。若请求超时，可使用相同的幂等键重试，避免重复创建订单。请勿将访问令牌写入日志。",
    "source_lang": "中文",
    "target_lang": "English",
    "locale": "en-US",
    "style": "准确、简洁的开发者文档",
    "glossary": {
      "幂等键": "idempotency key",
      "访问令牌": "access token",
      "客户端": "client"
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
The client should generate an idempotent key for each request. If the request times out, retry with the same idempotency key to avoid creating duplicate orders. Do not write access tokens to logs.
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
The client should generate an idempotent key for each request. If the request times out, retry with the same idempotency key to avoid creating duplicate orders. Do not write access tokens to logs.
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
          "source": "幂等键",
          "target": "idempotency key",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "访问令牌",
          "target": "access token",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "客户端",
          "target": "client",
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
      "matched": 3,
      "terms": [
        {
          "source": "幂等键",
          "target": "idempotency key",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "访问令牌",
          "target": "access token",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "客户端",
          "target": "client",
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
| initial | completed | 1 | 0.743 | 292 | 39 |  |
| review | completed | 2 | 7.367 | 2403 | 585 | 结构已纠正。 |
| revision | skipped | 0 | 未测量 | 未提供 | 未提供 | 审校未发现问题，无需修订；保留初译。 |

完整逐次调用记录与原始输出见同名 JSON 文件。
