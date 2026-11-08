# 翻译运行报告

- 模式：真实模型调用
- 运行 ID：869ff68e-b1cb-4fa1-99b4-46daabba356c
- 时间：2026-11-03T01:18:20.113256+00:00
- 后端：ollama
- 模型：gemma3:1b
- 状态：completed

## 请求与生成配置

```
{
  "request": {
    "text": "请在账户设置中选择你喜欢的颜色，并将发货地址设为办公室地址。新版本优化了收藏夹，方便你整理常用内容。",
    "source_lang": "中文",
    "target_lang": "English",
    "locale": "en-GB",
    "style": "友好、简洁的产品说明；采用目标地区自然的拼写与用词",
    "glossary": {
      "账户设置": "account settings"
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
Please select your preferred color in the account settings and set your shipping address to your office address. The new version has optimized the bookmark, making it easier for you to organize frequently used content.
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
Please select your preferred color in the account settings and set your shipping address to your office address. The new version has optimized the bookmark, making it easier for you to organize frequently used content.
```

## 规则检查

```
{
  "method": "术语按区分大小写的字面子串匹配，仅检查原文出现的术语；占位符按原样及出现次数比较。规则结果不是整体翻译质量评分。",
  "initial": {
    "terminology": {
      "applicable": 1,
      "matched": 1,
      "terms": [
        {
          "source": "账户设置",
          "target": "account settings",
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
      "applicable": 1,
      "matched": 1,
      "terms": [
        {
          "source": "账户设置",
          "target": "account settings",
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
| initial | completed | 1 | 0.775 | 279 | 39 |  |
| review | completed | 1 | 0.900 | 860 | 38 |  |
| revision | skipped | 0 | 未测量 | 未提供 | 未提供 | 审校未发现问题，无需修订；保留初译。 |

完整逐次调用记录与原始输出见同名 JSON 文件。
