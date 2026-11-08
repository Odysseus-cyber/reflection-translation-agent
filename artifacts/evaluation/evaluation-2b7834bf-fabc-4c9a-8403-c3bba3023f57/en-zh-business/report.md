# 翻译运行报告

- 模式：真实模型调用
- 运行 ID：f35da117-46ba-4864-ad08-76b3538842d5
- 时间：2026-11-03T01:16:51.556587+00:00
- 后端：ollama
- 模型：gemma3:1b
- 状态：failed

## 请求与生成配置

```
{
  "request": {
    "text": "Hi {name}, could we move the review to Thursday? The proposal is ready, but the pricing is subject to final approval. Please let me know if that timing works for you.",
    "source_lang": "English",
    "target_lang": "中文",
    "locale": "zh-CN",
    "style": "礼貌的工作邮件，准确保留尚待批准的条件；保留占位符",
    "glossary": {
      "proposal": "方案",
      "final approval": "最终批准"
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
你好{name}, 是否可以调整审查时间到周五？提案已准备好，但价格受最终批准的影响。请告知我是否这个时间段适合你。
```

## 四维审校

（未完成）

## 修订

```
（未生成）
```

## 规则检查

```
{
  "method": "术语按区分大小写的字面子串匹配，仅检查原文出现的术语；占位符按原样及出现次数比较。规则结果不是整体翻译质量评分。",
  "initial": {
    "terminology": {
      "applicable": 2,
      "matched": 1,
      "terms": [
        {
          "source": "proposal",
          "target": "方案",
          "matched": false,
          "target_occurrences": 0
        },
        {
          "source": "final approval",
          "target": "最终批准",
          "matched": true,
          "target_occurrences": 1
        }
      ]
    },
    "placeholders": {
      "expected": {
        "{name}": 1
      },
      "found": {
        "{name}": 1
      },
      "missing": {},
      "extra": {},
      "preserved": true
    }
  },
  "revised": null
}
```

## 阶段记录

| 阶段 | 状态 | 调用次数 | 实测耗时（秒） | 输入 tokens | 输出 tokens | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| initial | completed | 1 | 0.750 | 293 | 37 |  |
| review | failed | 1 | 41.554 | 871 | 4096 | Ollama 未生成完整结果，请检查输出长度上限。 |
| revision | skipped | 0 | 未测量 | 未提供 | 未提供 | 前序阶段失败，未执行。 |

## 错误

```
review / truncated: Ollama 未生成完整结果，请检查输出长度上限。
```

完整逐次调用记录与原始输出见同名 JSON 文件。
