# 翻译运行报告

- 模式：真实模型调用
- 运行 ID：242d7858-6016-4d19-b042-1d3245df9d77
- 时间：2026-11-03T01:16:34.032403+00:00
- 后端：ollama
- 模型：gemma3:1b
- 状态：completed

## 请求与生成配置

```
{
  "request": {
    "text": "欢迎使用云笺。开启离线模式后，你仍可编辑笔记；重新联网时，修改会自动同步到工作区。立即开始你的 14 天免费试用。",
    "source_lang": "中文",
    "target_lang": "English",
    "locale": "en-US",
    "style": "简洁、友好的产品文案，不夸大功能",
    "glossary": {
      "云笺": "CloudNote",
      "离线模式": "offline mode",
      "工作区": "workspace"
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
Use CloudNote offline mode to edit your notes; sync changes when you reconnect. Start your free trial now!
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
Use CloudNote offline mode to edit your notes; sync changes when you reconnect. Start your free trial now!
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
          "source": "云笺",
          "target": "CloudNote",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "离线模式",
          "target": "offline mode",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "工作区",
          "target": "workspace",
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
      "matched": 2,
      "terms": [
        {
          "source": "云笺",
          "target": "CloudNote",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "离线模式",
          "target": "offline mode",
          "matched": true,
          "target_occurrences": 1
        },
        {
          "source": "工作区",
          "target": "workspace",
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
| initial | completed | 1 | 0.688 | 299 | 23 |  |
| review | completed | 2 | 5.373 | 2259 | 454 | 结构已纠正。 |
| revision | skipped | 0 | 未测量 | 未提供 | 未提供 | 审校未发现问题，无需修订；保留初译。 |

完整逐次调用记录与原始输出见同名 JSON 文件。
