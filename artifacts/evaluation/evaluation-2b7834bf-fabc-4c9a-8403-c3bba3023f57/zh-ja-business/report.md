# 翻译运行报告

- 模式：真实模型调用
- 运行 ID：af701960-9e4c-4160-8a98-d092105c2fb3
- 时间：2026-11-03T01:17:49.568774+00:00
- 后端：ollama
- 模型：gemma3:1b
- 状态：completed

## 请求与生成配置

```
{
  "request": {
    "text": "感谢您参加今天的会议。附件是更新后的报价单，请于下周二前确认。如需调整交货数量，请联系我们。",
    "source_lang": "中文",
    "target_lang": "日本語",
    "locale": "ja-JP",
    "style": "面向客户的礼貌商务邮件，恰当使用敬语",
    "glossary": {
      "报价单": "見積書",
      "交货数量": "納品数量"
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
ご出席いただきました会議の件、誠にありがとうございます。添付いたしました最新の見積書をございますので、つきましては、来週火曜日の前日までにご連絡いただけますでしょうか？調整させていただく交貨数量につきまして、お気軽にお問い合わせください。
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
ご出席いただきました会議の件、誠にありがとうございます。添付いたしました最新の見積書をございますので、つきましては、来週火曜日の前日までにご連絡いただけますでしょうか？調整させていただく交貨数量につきまして、お気軽にお問い合わせください。
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
          "source": "报价单",
          "target": "見積書",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "交货数量",
          "target": "納品数量",
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
          "source": "报价单",
          "target": "見積書",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "交货数量",
          "target": "納品数量",
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
| initial | completed | 1 | 0.892 | 287 | 53 |  |
| review | completed | 1 | 0.671 | 881 | 23 |  |
| revision | skipped | 0 | 未测量 | 未提供 | 未提供 | 审校未发现问题，无需修订；保留初译。 |

完整逐次调用记录与原始输出见同名 JSON 文件。
