# 翻译运行报告

- 模式：真实模型调用
- 运行 ID：28114c76-b0f9-4b6b-868e-2cde490628f9
- 时间：2026-11-03T01:16:40.095513+00:00
- 后端：ollama
- 模型：gemma3:1b
- 状态：completed

## 请求与生成配置

```
{
  "request": {
    "text": "您好，{name}：感谢您分享需求。我们预计周五前提供修订后的方案，最终交付时间仍需双方确认。若您有新的要求，请直接回复此邮件。谢谢，{name}。",
    "source_lang": "中文",
    "target_lang": "English",
    "locale": "en-US",
    "style": "礼貌、清晰的商务邮件；保留占位符",
    "glossary": {
      "交付时间": "delivery date"
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
Good morning, {name}: Thank you for sharing your requirements. We anticipate providing the revised plan by Thursday and final delivery time still requires confirmation from both of us. Please reply directly to this email if you have any new requests. Thanks, {name}.
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
Good morning, {name}: Thank you for sharing your requirements. We anticipate providing the revised plan by Thursday and final delivery time still requires confirmation from both of us. Please reply directly to this email if you have any new requests. Thanks, {name}.
```

## 规则检查

```
{
  "method": "术语按区分大小写的字面子串匹配，仅检查原文出现的术语；占位符按原样及出现次数比较。规则结果不是整体翻译质量评分。",
  "initial": {
    "terminology": {
      "applicable": 1,
      "matched": 0,
      "terms": [
        {
          "source": "交付时间",
          "target": "delivery date",
          "matched": false,
          "target_occurrences": 0
        }
      ]
    },
    "placeholders": {
      "expected": {
        "{name}": 2
      },
      "found": {
        "{name}": 2
      },
      "missing": {},
      "extra": {},
      "preserved": true
    }
  },
  "revised": {
    "terminology": {
      "applicable": 1,
      "matched": 0,
      "terms": [
        {
          "source": "交付时间",
          "target": "delivery date",
          "matched": false,
          "target_occurrences": 0
        }
      ]
    },
    "placeholders": {
      "expected": {
        "{name}": 2
      },
      "found": {
        "{name}": 2
      },
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
| initial | completed | 1 | 0.860 | 292 | 52 |  |
| review | completed | 1 | 0.916 | 887 | 23 |  |
| revision | skipped | 0 | 未测量 | 未提供 | 未提供 | 审校未发现问题，无需修订；保留初译。 |

完整逐次调用记录与原始输出见同名 JSON 文件。
