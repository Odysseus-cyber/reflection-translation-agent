# 翻译运行报告

- 模式：真实模型调用
- 运行 ID：17807866-e311-4aa7-ad6d-00c5501be349
- 时间：2026-11-03T01:20:41.132049+00:00
- 后端：compatible
- 模型：gemma3:1b
- 状态：failed

## 请求与生成配置

```
{
  "request": {
    "text": "请保存更改。",
    "source_lang": "中文",
    "target_lang": "English",
    "locale": "en-US",
    "style": "自然、忠实原文",
    "glossary": {}
  },
  "generation_settings": {
    "max_output_tokens": 4096,
    "api_response_format": "json_schema"
  }
}
```

## 初译

```
Please save changes.
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
      "applicable": 0,
      "matched": 0,
      "terms": []
    },
    "placeholders": {
      "expected": {},
      "found": {},
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
| initial | completed | 1 | 1.620 | 234 | 6 |  |
| review | failed | 2 | 6.568 | 1850 | 481 | 审校 JSON 经一次纠正后仍无效。 |
| revision | skipped | 0 | 未测量 | 未提供 | 未提供 | 前序阶段失败，未执行。 |

## 错误

```
review / invalid_review: 审校 JSON 经一次纠正后仍无效。
```

完整逐次调用记录与原始输出见同名 JSON 文件。
