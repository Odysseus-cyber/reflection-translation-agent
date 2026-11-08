# 翻译运行报告

- 模式：真实模型调用
- 运行 ID：cfcad84a-0370-4ab5-bac9-c06da5a96114
- 时间：2026-11-03T01:18:11.658481+00:00
- 后端：ollama
- 模型：gemma3:1b
- 状态：completed

## 请求与生成配置

```
{
  "request": {
    "text": "設定を変更した後は、アプリを再起動してください。再起動しても問題が解決しない場合は、エラーコード {error_code} をサポート窓口にお知らせください。",
    "source_lang": "日本語",
    "target_lang": "中文",
    "locale": "zh-CN",
    "style": "简明、清晰的故障排查说明，保留占位符",
    "glossary": {
      "再起動": "重启",
      "エラーコード": "错误代码",
      "サポート窓口": "客服"
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
重新启动应用程序后，请重启应用。如果问题仍然没有解决，请告知支持客服代码 {error_code}。
```

## 四维审校

### 准确性

| 严重程度 | 原文片段 | 译文片段 | 原因 | 修改建议 |
| --- | --- | --- | --- | --- |
| minor | 重新启动应用程序后，请重启应用。再起動しても問題が解決しない場合は、エラーコード {error_code} をサポート窓口にお知らせください。 | 重新启动应用程序后，请重启应用。如果问题仍然没有解决，请告知支持客服代码 {error_code}。 | The translation is accurate and conveys the same meaning as the source text. No issues detected. | No suggestion needed. |

### 流畅性

| 严重程度 | 原文片段 | 译文片段 | 原因 | 修改建议 |
| --- | --- | --- | --- | --- |
| minor | 重新启动应用程序后，请重启应用。再起動しても問題が解決しない場合は、エラーコード {error_code} をサポート窓口にお知らせください。 | 重新启动应用程序后，请重启应用。如果问题仍然没有解决，请告知支持客服代码 {error_code}。 | The translation is natural and well-written. No issues detected. | No suggestion needed. |

### 风格

| 严重程度 | 原文片段 | 译文片段 | 原因 | 修改建议 |
| --- | --- | --- | --- | --- |
| minor | 重新启动应用程序后，请重启应用。再起動しても問題が解決しない場合は、エラーコード {error_code} をサポート窓口にお知らせください。 | 重新启动应用程序后，请重启应用。如果问题仍然没有解决，请告知支持客服代码 {error_code}。 | The translation maintains the tone and style of the original text. No issues detected. | No suggestion needed. |

### 术语一致性

| 严重程度 | 原文片段 | 译文片段 | 原因 | 修改建议 |
| --- | --- | --- | --- | --- |
| minor | 重新启动应用程序后，请重启应用。再起動しても問題が解決しない場合は、エラーコード {error_code} をサポート窓口にお知らせください。 | 重新启动应用程序后，请重启应用。如果问题仍然没有解决，请告知支持客服代码 {error_code}。 | The terminology is consistent and appropriate. No issues detected. | No suggestion needed. |


## 修订

```
重新启动应用程序后，请重启应用。如果问题仍然没有解决，请告知支持客服代码 {error_code} 。
```

## 规则检查

```
{
  "method": "术语按区分大小写的字面子串匹配，仅检查原文出现的术语；占位符按原样及出现次数比较。规则结果不是整体翻译质量评分。",
  "initial": {
    "terminology": {
      "applicable": 3,
      "matched": 2,
      "terms": [
        {
          "source": "再起動",
          "target": "重启",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "エラーコード",
          "target": "错误代码",
          "matched": false,
          "target_occurrences": 0
        },
        {
          "source": "サポート窓口",
          "target": "客服",
          "matched": true,
          "target_occurrences": 1
        }
      ]
    },
    "placeholders": {
      "expected": {
        "{error_code}": 1
      },
      "found": {
        "{error_code}": 1
      },
      "missing": {},
      "extra": {},
      "preserved": true
    }
  },
  "revised": {
    "terminology": {
      "applicable": 3,
      "matched": 2,
      "terms": [
        {
          "source": "再起動",
          "target": "重启",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "エラーコード",
          "target": "错误代码",
          "matched": false,
          "target_occurrences": 0
        },
        {
          "source": "サポート窓口",
          "target": "客服",
          "matched": true,
          "target_occurrences": 1
        }
      ]
    },
    "placeholders": {
      "expected": {
        "{error_code}": 1
      },
      "found": {
        "{error_code}": 1
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
| initial | completed | 1 | 0.673 | 296 | 28 |  |
| review | completed | 1 | 5.467 | 865 | 497 |  |
| revision | completed | 1 | 0.870 | 815 | 27 |  |

完整逐次调用记录与原始输出见同名 JSON 文件。
