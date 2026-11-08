# 翻译运行报告

- 模式：真实模型调用
- 运行 ID：2827fdef-c3ee-4272-be4d-175bd0ba5c53
- 时间：2026-11-03T01:14:27.950769+00:00
- 后端：ollama
- 模型：gemma3:1b
- 状态：completed

## 请求与生成配置

```
{
  "request": {
    "text": "免费试用结束后，您的工作区将保留 30 天。请在到期前导出数据。",
    "source_lang": "zh",
    "target_lang": "en",
    "locale": "en-GB",
    "style": "清晰、友好的产品提示",
    "glossary": {
      "工作区": "workspace",
      "免费试用": "free trial"
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
Free trial expires after 30 days. Your workspace will retain data until the expiration date.
```

## 四维审校

### 准确性

未报告问题。

### 流畅性

未报告问题。

### 风格

| 严重程度 | 原文片段 | 译文片段 | 原因 | 修改建议 |
| --- | --- | --- | --- | --- |
| minor | 清晰、友好的产品提示 | 清晰、友好的产品提示 | The translation maintains a clear and friendly tone, suitable for product prompts. | Consider adding more context regarding the data retention period to enhance clarity. |
| minor | 免费试用结束后，您的工作区将保留数据 | Free trial expires after 30 days. Your workspace will retain data until the expiration date | The translation maintains a clear and friendly tone, suitable for product prompts. | Consider adding more context regarding the data retention period to enhance clarity. |
| minor | 您的工作区将保留数据 | Your workspace will retain data until the expiration date | The translation maintains a clear and friendly tone, suitable for product prompts. | Consider adding more context regarding the data retention period to enhance clarity. |

### 术语一致性

| 严重程度 | 原文片段 | 译文片段 | 原因 | 修改建议 |
| --- | --- | --- | --- | --- |
| minor | 您的工作区将保留数据 | Your workspace will retain data until the expiration date | The translation maintains a clear and friendly tone, suitable for product prompts. | Consider adding more context regarding the data retention period to enhance clarity. |
| minor | 免费试用结束后，您的工作区将保留数据 | Free trial expires after 30 days. Your workspace will retain data until the expiration date | The translation maintains a clear and friendly tone, suitable for product prompts. | Consider adding more context regarding the data retention period to enhance clarity. |


## 修订

```
Free trial expires after 30 days. Your workspace will retain data until the expiration date?
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
          "source": "工作区",
          "target": "workspace",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "免费试用",
          "target": "free trial",
          "matched": false,
          "target_occurrences": 0
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
      "applicable": 2,
      "matched": 1,
      "terms": [
        {
          "source": "工作区",
          "target": "workspace",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "免费试用",
          "target": "free trial",
          "matched": false,
          "target_occurrences": 0
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
| initial | completed | 1 | 1.981 | 269 | 21 |  |
| review | completed | 1 | 5.123 | 831 | 430 |  |
| revision | completed | 1 | 0.758 | 747 | 20 |  |

完整逐次调用记录与原始输出见同名 JSON 文件。
