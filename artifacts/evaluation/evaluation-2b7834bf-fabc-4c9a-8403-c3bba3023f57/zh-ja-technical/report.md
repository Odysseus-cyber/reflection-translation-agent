# 翻译运行报告

- 模式：真实模型调用
- 运行 ID：c25883cf-fd1f-4471-983c-fc0fa5c5133e
- 时间：2026-11-03T01:17:51.133095+00:00
- 后端：ollama
- 模型：gemma3:1b
- 状态：completed

## 请求与生成配置

```
{
  "request": {
    "text": "启用双重验证后，登录时除密码外还需输入验证码。请妥善保存恢复码，以便在无法使用手机时恢复访问。",
    "source_lang": "中文",
    "target_lang": "日本語",
    "locale": "ja-JP",
    "style": "清楚的用户操作说明，使用です・ます体",
    "glossary": {
      "双重验证": "二段階認証",
      "验证码": "認証コード",
      "恢复码": "リカバリーコード"
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
ご登録の際に、パスワード以外に、検証コードを入力してください。復旧コードを保管しておきましょう。
```

## 四维审校

### 准确性

| 严重程度 | 原文片段 | 译文片段 | 原因 | 修改建议 |
| --- | --- | --- | --- | --- |
| minor | ご登録の際に、パスワード以外に、検証コードを入力してください。 復旧コードを保管しておましょう。 | 您在注册时，除了密码外还需输入验证码。请妥善保存恢复代码，以便在无法使用手机时恢复访问。 | The original text is clear and concise. No issues detected. | No suggestion needed. |

### 流畅性

| 严重程度 | 原文片段 | 译文片段 | 原因 | 修改建议 |
| --- | --- | --- | --- | --- |
| minor | ご登録の際に、パスワード以外に、検証コードを入力してください。 復旧コードを保管しておきましょう。 | 您在注册时，除了密码外还需输入验证码。请妥善保存恢复代码，以便在无法使用手机时恢复访问。 | The language is natural and easy to understand. No issues detected. | No suggestion needed. |

### 风格

| 严重程度 | 原文片段 | 译文片段 | 原因 | 修改建议 |
| --- | --- | --- | --- | --- |
| minor | ご登録の際に、パスワード以外に、検証コードを入力してください。 復旧コードを保管しておきましょう。 | 您在注册时，除了密码外还需输入验证码。请妥善保存恢复代码，以便在无法使用手机时恢复访问。 | The text uses polite language and a clear structure. No issues detected. | No suggestion needed. |

### 术语一致性

| 严重程度 | 原文片段 | 译文片段 | 原因 | 修改建议 |
| --- | --- | --- | --- | --- |
| minor | ご登録の際に、パスワード以外に、検証コードを入力してください。 復旧コードを保管しておきましょう。 | 您在注册时，除了密码外还需输入验证码。请妥善保存恢复代码，以便在无法使用手机时恢复访问。 | The terms 'verification code' and 'recovery code' are used correctly. | No suggestion needed. |


## 修订

```
{"source_lang": "中文", "target_lang": "日本語", "locale": "ja-JP", "style": "清楚的用户操作说明，使用です・ます体", "glossary": {"双重验证": "二段階認証", "验证码": "認証コード", "恢复码": "リカバリーコード"}, "source_text": "启用双重验证后，登录时除密码外还需输入验证码。请妥善保存恢复码，以便在无法使用手机时恢复访问。", "initial_translation": "ご登録の際に、パスワード以外に、検証コードを入力してください。\n復旧コードを保管しておきましょう。", "review": {"accuracy": [{"dimension": "accuracy", "source_excerpt": "ご登録の際に、パスワード以外に、検証コードを入力してください。\n復旧コードを保管しておましょう。", "translation_excerpt": "您在注册时，除了密码外还需输入验证码。请妥善保存恢复代码，以便在无法使用手机时恢复访问。", "explanation": "The original text is clear and concise. No issues detected.", "suggestion": "No suggestion needed.", "severity": "minor"}], "fluency": [{"dimension": "fluency", "source_excerpt": "ご登録の際に、パスワード以外に、検証コードを入力してください。\n復旧コードを保管しておきましょう。", "translation_excerpt": "您在注册时，除了密码外还需输入验证码。请妥善保存恢复代码，以便在无法使用手机时恢复访问。", "explanation": "The language is natural and easy to understand. No issues detected.", "suggestion": "No suggestion needed.", "severity": "minor"}], "style": [{"dimension": "style", "source_excerpt": "ご登録の際に、パスワード以外に、検証コードを入力してください。\n復旧コードを保管しておきましょう。", "translation_excerpt": "您在注册时，除了密码外还需输入验证码。请妥善保存恢复代码，以便在无法使用手机时恢复访问。", "explanation": "The text uses polite language and a clear structure. No issues detected.", "suggestion": "No suggestion needed.", "severity": "minor"}], "terminology": [{"dimension": "terminology", "source_excerpt": "ご登録の際に、パスワード以外に、検証コードを入力してください。\n復旧コードを保管しておきましょう。", "translation_excerpt": "您在注册时，除了密码外还需输入验证码。请妥善保存恢复代码，以便在无法使用手机时恢复访问。", "explanation": "The terms 'verification code' and 'recovery code' are used correctly.", "suggestion": "No suggestion needed.", "severity": "minor"}}]}}
```

## 规则检查

```
{
  "method": "术语按区分大小写的字面子串匹配，仅检查原文出现的术语；占位符按原样及出现次数比较。规则结果不是整体翻译质量评分。",
  "initial": {
    "terminology": {
      "applicable": 3,
      "matched": 0,
      "terms": [
        {
          "source": "双重验证",
          "target": "二段階認証",
          "matched": false,
          "target_occurrences": 0
        },
        {
          "source": "验证码",
          "target": "認証コード",
          "matched": false,
          "target_occurrences": 0
        },
        {
          "source": "恢复码",
          "target": "リカバリーコード",
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
      "applicable": 3,
      "matched": 3,
      "terms": [
        {
          "source": "双重验证",
          "target": "二段階認証",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "验证码",
          "target": "認証コード",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "恢复码",
          "target": "リカバリーコード",
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
| initial | completed | 1 | 0.647 | 294 | 24 |  |
| review | completed | 1 | 5.490 | 860 | 483 |  |
| revision | completed | 1 | 5.965 | 786 | 576 |  |

完整逐次调用记录与原始输出见同名 JSON 文件。
