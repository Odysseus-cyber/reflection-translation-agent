# 翻译运行报告

- 模式：真实模型调用
- 运行 ID：62a2a993-7cfa-4325-ad69-6457f0f0ead8
- 时间：2026-11-03T01:18:03.237069+00:00
- 后端：ollama
- 模型：gemma3:1b
- 状态：completed

## 请求与生成配置

```
{
  "request": {
    "text": "毎日の支出をかんたんに記録。カテゴリ別の集計で、お金の使い方を振り返れます。まずは無料プランから始めましょう。",
    "source_lang": "日本語",
    "target_lang": "中文",
    "locale": "zh-CN",
    "style": "轻松自然的产品介绍，避免夸大收益",
    "glossary": {
      "カテゴリ": "类别",
      "無料プラン": "免费方案"
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
每天记录你的每日开销。使用不同的类别来查看钱的用途。从免费计划开始吧！
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
每天记录你的每日开销。使用不同的类别来查看钱的用途。从免费计划开始吧！
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
          "source": "カテゴリ",
          "target": "类别",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "無料プラン",
          "target": "免费方案",
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
          "source": "カテゴリ",
          "target": "类别",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "無料プラン",
          "target": "免费方案",
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
| initial | completed | 1 | 0.655 | 275 | 24 |  |
| review | completed | 1 | 0.625 | 840 | 24 |  |
| revision | skipped | 0 | 未测量 | 未提供 | 未提供 | 审校未发现问题，无需修订；保留初译。 |

完整逐次调用记录与原始输出见同名 JSON 文件。
