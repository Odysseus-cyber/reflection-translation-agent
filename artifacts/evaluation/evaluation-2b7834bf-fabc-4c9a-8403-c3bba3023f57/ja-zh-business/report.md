# 翻译运行报告

- 模式：真实模型调用
- 运行 ID：df8b276f-c93f-4752-b8f2-5130149e4db7
- 时间：2026-11-03T01:18:04.519360+00:00
- 后端：ollama
- 模型：gemma3:1b
- 状态：completed

## 请求与生成配置

```
{
  "request": {
    "text": "お世話になっております。ご依頼の資料をお送りいたします。なお、記載の金額には送料が含まれておりません。ご不明な点がございましたら、お知らせください。",
    "source_lang": "日本語",
    "target_lang": "中文",
    "locale": "zh-CN",
    "style": "自然得体的中文商务邮件，不逐字翻译日语寒暄",
    "glossary": {
      "送料": "运费",
      "資料": "资料"
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
您好，感谢您的合作。我将为您准备一份中文商务邮件。

请稍等…

以下是翻译结果：

您好，感谢您的合作。我将为您准备一份中文商务邮件。

**原文:** お世話になっております。ご依頼の資料をお送りいたします。なお、記載の金額には送料が含まれておりません。ご不明な点がございましたら、お知らせください。

**译文:** 很高兴能与您联系。我将在稍后向您发送资料。请注意，费用包含在金额中。如果您有任何疑问，请随时提出。

希望对您有所帮助！
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
您好，感谢您的合作。我将为您准备一份中文商务邮件。

请稍等…

以下是翻译结果：

您好，感谢您的合作。我将为您准备一份中文商务邮件。

**原文:** お世話になっております。ご依頼の資料をお送りいたします。なお、記載の金額には送料が含まれておりません。ご不明な点がございましたら、お知らせください。

**译文:** 很高兴能与您联系。我将在稍后向您发送资料。请注意，费用包含在金额中。如果您有任何疑问，请随时提出。

希望对您有所帮助！
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
          "source": "送料",
          "target": "运费",
          "matched": false,
          "target_occurrences": 0
        },
        {
          "source": "資料",
          "target": "资料",
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
      "applicable": 2,
      "matched": 1,
      "terms": [
        {
          "source": "送料",
          "target": "运费",
          "matched": false,
          "target_occurrences": 0
        },
        {
          "source": "資料",
          "target": "资料",
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
| initial | completed | 1 | 1.651 | 286 | 132 |  |
| review | completed | 2 | 5.486 | 2414 | 417 | 结构已纠正。 |
| revision | skipped | 0 | 未测量 | 未提供 | 未提供 | 审校未发现问题，无需修订；保留初译。 |

完整逐次调用记录与原始输出见同名 JSON 文件。
