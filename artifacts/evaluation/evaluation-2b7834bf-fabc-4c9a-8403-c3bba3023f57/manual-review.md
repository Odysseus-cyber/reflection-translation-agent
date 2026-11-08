# 人工 A/B 对照评审

先评审本文件，再打开 blind-mapping.json 揭盲。A/B 顺序按案例随机分配；两份译文来自同一次运行。

分别检查准确性、流畅性、目标风格和术语一致性；每维填写 A 更好／相当／B 更好，并引用具体片段。

不要把规则命中数当作整体质量分。此文件没有预填质量结论。

## zh-en-product · 产品文案

### 输入与要求

```
{
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
}
```

### 译文 A

```
Use CloudNote offline mode to edit your notes; sync changes when you reconnect. Start your free trial now!
```

### 译文 B

```
Use CloudNote offline mode to edit your notes; sync changes when you reconnect. Start your free trial now!
```

| 维度 | A 更好／相当／B 更好 | 片段与理由 |
| --- | --- | --- |
| 准确性 | | |
| 流畅性 | | |
| 风格 | | |
| 术语一致性 | | |

整体偏好：________；理由：________

揭盲后结论（修订更好／相当／初译更好）：________

## zh-en-business · 商务沟通

### 输入与要求

```
{
  "text": "您好，{name}：感谢您分享需求。我们预计周五前提供修订后的方案，最终交付时间仍需双方确认。若您有新的要求，请直接回复此邮件。谢谢，{name}。",
  "source_lang": "中文",
  "target_lang": "English",
  "locale": "en-US",
  "style": "礼貌、清晰的商务邮件；保留占位符",
  "glossary": {
    "交付时间": "delivery date"
  }
}
```

### 译文 A

```
Good morning, {name}: Thank you for sharing your requirements. We anticipate providing the revised plan by Thursday and final delivery time still requires confirmation from both of us. Please reply directly to this email if you have any new requests. Thanks, {name}.
```

### 译文 B

```
Good morning, {name}: Thank you for sharing your requirements. We anticipate providing the revised plan by Thursday and final delivery time still requires confirmation from both of us. Please reply directly to this email if you have any new requests. Thanks, {name}.
```

| 维度 | A 更好／相当／B 更好 | 片段与理由 |
| --- | --- | --- |
| 准确性 | | |
| 流畅性 | | |
| 风格 | | |
| 术语一致性 | | |

整体偏好：________；理由：________

揭盲后结论（修订更好／相当／初译更好）：________

## zh-en-technical · 技术说明

### 输入与要求

```
{
  "text": "客户端应为每次写入请求生成幂等键。若请求超时，可使用相同的幂等键重试，避免重复创建订单。请勿将访问令牌写入日志。",
  "source_lang": "中文",
  "target_lang": "English",
  "locale": "en-US",
  "style": "准确、简洁的开发者文档",
  "glossary": {
    "幂等键": "idempotency key",
    "访问令牌": "access token",
    "客户端": "client"
  }
}
```

### 译文 A

```
The client should generate an idempotent key for each request. If the request times out, retry with the same idempotency key to avoid creating duplicate orders. Do not write access tokens to logs.
```

### 译文 B

```
The client should generate an idempotent key for each request. If the request times out, retry with the same idempotency key to avoid creating duplicate orders. Do not write access tokens to logs.
```

| 维度 | A 更好／相当／B 更好 | 片段与理由 |
| --- | --- | --- |
| 准确性 | | |
| 流畅性 | | |
| 风格 | | |
| 术语一致性 | | |

整体偏好：________；理由：________

揭盲后结论（修订更好／相当／初译更好）：________

## en-zh-product · 产品文案

### 输入与要求

```
{
  "text": "Keep your team in sync with shared workspaces. Assign an owner to each task and receive a daily digest, without opening another dashboard.",
  "source_lang": "English",
  "target_lang": "中文",
  "locale": "zh-CN",
  "style": "自然简洁的产品文案，避免生硬直译",
  "glossary": {
    "workspaces": "工作区",
    "owner": "负责人",
    "daily digest": "每日摘要"
  }
}
```

### 译文 A

```
团队成员与共享工作空间保持同步，为每个任务分配一名负责人，并接收一份每日摘要，无需打开其他仪表盘。
```

### 译文 B

```
团队成员与共享工作空间保持同步，为每个任务分配一名负责人，并接收一份每日摘要，无需打开其他仪表盘。
```

| 维度 | A 更好／相当／B 更好 | 片段与理由 |
| --- | --- | --- |
| 准确性 | | |
| 流畅性 | | |
| 风格 | | |
| 术语一致性 | | |

整体偏好：________；理由：________

揭盲后结论（修订更好／相当／初译更好）：________

## en-zh-technical · 技术说明

### 输入与要求

```
{
  "text": "The cache expires after 30 minutes. A cache miss does not mean the record has been deleted; query the primary database before returning a not-found response.",
  "source_lang": "English",
  "target_lang": "中文",
  "locale": "zh-CN",
  "style": "严谨的开发者文档，保留否定与条件关系",
  "glossary": {
    "cache miss": "缓存未命中",
    "primary database": "主数据库",
    "cache": "缓存"
  }
}
```

### 译文 A

```
缓存过期时间为30分钟。缓存未命中并不意味着记录已被删除；在主数据库前检索后再返回未找到响应。
```

### 译文 B

```
缓存过期时间为30分钟。缓存未命中并不意味着记录已被删除；在主数据库前检索后再返回未找到响应。
```

| 维度 | A 更好／相当／B 更好 | 片段与理由 |
| --- | --- | --- |
| 准确性 | | |
| 流畅性 | | |
| 风格 | | |
| 术语一致性 | | |

整体偏好：________；理由：________

揭盲后结论（修订更好／相当／初译更好）：________

## zh-ja-product · 产品文案

### 输入与要求

```
{
  "text": "把灵感记下来，稍后再整理。收藏夹可在手机与电脑之间同步，让你随时找到需要的内容。",
  "source_lang": "中文",
  "target_lang": "日本語",
  "locale": "ja-JP",
  "style": "自然、亲切的日语产品介绍，使用です・ます体",
  "glossary": {
    "收藏夹": "お気に入り",
    "同步": "同期"
  }
}
```

### 译文 A

```
コレクションアルバムにアイデアをメモしておき、後で整理するだけです。コレクションアルバムは、スマートフォンとパソコン間で同期できるので、いつでも必要なものを探すことができます。
```

### 译文 B

```
好的，我理解了。请提供您需要翻译的 JSON 数据。
```

| 维度 | A 更好／相当／B 更好 | 片段与理由 |
| --- | --- | --- |
| 准确性 | | |
| 流畅性 | | |
| 风格 | | |
| 术语一致性 | | |

整体偏好：________；理由：________

揭盲后结论（修订更好／相当／初译更好）：________

## zh-ja-business · 商务沟通

### 输入与要求

```
{
  "text": "感谢您参加今天的会议。附件是更新后的报价单，请于下周二前确认。如需调整交货数量，请联系我们。",
  "source_lang": "中文",
  "target_lang": "日本語",
  "locale": "ja-JP",
  "style": "面向客户的礼貌商务邮件，恰当使用敬语",
  "glossary": {
    "报价单": "見積書",
    "交货数量": "納品数量"
  }
}
```

### 译文 A

```
ご出席いただきました会議の件、誠にありがとうございます。添付いたしました最新の見積書をございますので、つきましては、来週火曜日の前日までにご連絡いただけますでしょうか？調整させていただく交貨数量につきまして、お気軽にお問い合わせください。
```

### 译文 B

```
ご出席いただきました会議の件、誠にありがとうございます。添付いたしました最新の見積書をございますので、つきましては、来週火曜日の前日までにご連絡いただけますでしょうか？調整させていただく交貨数量につきまして、お気軽にお問い合わせください。
```

| 维度 | A 更好／相当／B 更好 | 片段与理由 |
| --- | --- | --- |
| 准确性 | | |
| 流畅性 | | |
| 风格 | | |
| 术语一致性 | | |

整体偏好：________；理由：________

揭盲后结论（修订更好／相当／初译更好）：________

## zh-ja-technical · 技术说明

### 输入与要求

```
{
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
}
```

### 译文 A

```
ご登録の際に、パスワード以外に、検証コードを入力してください。復旧コードを保管しておきましょう。
```

### 译文 B

```
{"source_lang": "中文", "target_lang": "日本語", "locale": "ja-JP", "style": "清楚的用户操作说明，使用です・ます体", "glossary": {"双重验证": "二段階認証", "验证码": "認証コード", "恢复码": "リカバリーコード"}, "source_text": "启用双重验证后，登录时除密码外还需输入验证码。请妥善保存恢复码，以便在无法使用手机时恢复访问。", "initial_translation": "ご登録の際に、パスワード以外に、検証コードを入力してください。\n復旧コードを保管しておきましょう。", "review": {"accuracy": [{"dimension": "accuracy", "source_excerpt": "ご登録の際に、パスワード以外に、検証コードを入力してください。\n復旧コードを保管しておましょう。", "translation_excerpt": "您在注册时，除了密码外还需输入验证码。请妥善保存恢复代码，以便在无法使用手机时恢复访问。", "explanation": "The original text is clear and concise. No issues detected.", "suggestion": "No suggestion needed.", "severity": "minor"}], "fluency": [{"dimension": "fluency", "source_excerpt": "ご登録の際に、パスワード以外に、検証コードを入力してください。\n復旧コードを保管しておきましょう。", "translation_excerpt": "您在注册时，除了密码外还需输入验证码。请妥善保存恢复代码，以便在无法使用手机时恢复访问。", "explanation": "The language is natural and easy to understand. No issues detected.", "suggestion": "No suggestion needed.", "severity": "minor"}], "style": [{"dimension": "style", "source_excerpt": "ご登録の際に、パスワード以外に、検証コードを入力してください。\n復旧コードを保管しておきましょう。", "translation_excerpt": "您在注册时，除了密码外还需输入验证码。请妥善保存恢复代码，以便在无法使用手机时恢复访问。", "explanation": "The text uses polite language and a clear structure. No issues detected.", "suggestion": "No suggestion needed.", "severity": "minor"}], "terminology": [{"dimension": "terminology", "source_excerpt": "ご登録の際に、パスワード以外に、検証コードを入力してください。\n復旧コードを保管しておきましょう。", "translation_excerpt": "您在注册时，除了密码外还需输入验证码。请妥善保存恢复代码，以便在无法使用手机时恢复访问。", "explanation": "The terms 'verification code' and 'recovery code' are used correctly.", "suggestion": "No suggestion needed.", "severity": "minor"}}]}}
```

| 维度 | A 更好／相当／B 更好 | 片段与理由 |
| --- | --- | --- |
| 准确性 | | |
| 流畅性 | | |
| 风格 | | |
| 术语一致性 | | |

整体偏好：________；理由：________

揭盲后结论（修订更好／相当／初译更好）：________

## ja-zh-product · 产品文案

### 输入与要求

```
{
  "text": "毎日の支出をかんたんに記録。カテゴリ別の集計で、お金の使い方を振り返れます。まずは無料プランから始めましょう。",
  "source_lang": "日本語",
  "target_lang": "中文",
  "locale": "zh-CN",
  "style": "轻松自然的产品介绍，避免夸大收益",
  "glossary": {
    "カテゴリ": "类别",
    "無料プラン": "免费方案"
  }
}
```

### 译文 A

```
每天记录你的每日开销。使用不同的类别来查看钱的用途。从免费计划开始吧！
```

### 译文 B

```
每天记录你的每日开销。使用不同的类别来查看钱的用途。从免费计划开始吧！
```

| 维度 | A 更好／相当／B 更好 | 片段与理由 |
| --- | --- | --- |
| 准确性 | | |
| 流畅性 | | |
| 风格 | | |
| 术语一致性 | | |

整体偏好：________；理由：________

揭盲后结论（修订更好／相当／初译更好）：________

## ja-zh-business · 商务沟通

### 输入与要求

```
{
  "text": "お世話になっております。ご依頼の資料をお送りいたします。なお、記載の金額には送料が含まれておりません。ご不明な点がございましたら、お知らせください。",
  "source_lang": "日本語",
  "target_lang": "中文",
  "locale": "zh-CN",
  "style": "自然得体的中文商务邮件，不逐字翻译日语寒暄",
  "glossary": {
    "送料": "运费",
    "資料": "资料"
  }
}
```

### 译文 A

```
您好，感谢您的合作。我将为您准备一份中文商务邮件。

请稍等…

以下是翻译结果：

您好，感谢您的合作。我将为您准备一份中文商务邮件。

**原文:** お世話になっております。ご依頼の資料をお送りいたします。なお、記載の金額には送料が含まれておりません。ご不明な点がございましたら、お知らせください。

**译文:** 很高兴能与您联系。我将在稍后向您发送资料。请注意，费用包含在金额中。如果您有任何疑问，请随时提出。

希望对您有所帮助！
```

### 译文 B

```
您好，感谢您的合作。我将为您准备一份中文商务邮件。

请稍等…

以下是翻译结果：

您好，感谢您的合作。我将为您准备一份中文商务邮件。

**原文:** お世話になっております。ご依頼の資料をお送りいたします。なお、記載の金額には送料が含まれておりません。ご不明な点がございましたら、お知らせください。

**译文:** 很高兴能与您联系。我将在稍后向您发送资料。请注意，费用包含在金额中。如果您有任何疑问，请随时提出。

希望对您有所帮助！
```

| 维度 | A 更好／相当／B 更好 | 片段与理由 |
| --- | --- | --- |
| 准确性 | | |
| 流畅性 | | |
| 风格 | | |
| 术语一致性 | | |

整体偏好：________；理由：________

揭盲后结论（修订更好／相当／初译更好）：________

## ja-zh-technical · 技术说明

### 输入与要求

```
{
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
}
```

### 译文 A

```
重新启动应用程序后，请重启应用。如果问题仍然没有解决，请告知支持客服代码 {error_code}。
```

### 译文 B

```
重新启动应用程序后，请重启应用。如果问题仍然没有解决，请告知支持客服代码 {error_code} 。
```

| 维度 | A 更好／相当／B 更好 | 片段与理由 |
| --- | --- | --- |
| 准确性 | | |
| 流畅性 | | |
| 风格 | | |
| 术语一致性 | | |

整体偏好：________；理由：________

揭盲后结论（修订更好／相当／初译更好）：________

## locale-en-us · 英美地区对照

### 输入与要求

```
{
  "text": "请在账户设置中选择你喜欢的颜色，并将发货地址设为办公室地址。新版本优化了收藏夹，方便你整理常用内容。",
  "source_lang": "中文",
  "target_lang": "English",
  "locale": "en-US",
  "style": "友好、简洁的产品说明；采用目标地区自然的拼写与用词",
  "glossary": {
    "账户设置": "account settings"
  }
}
```

### 译文 A

```
Please select your preferred color in the account settings and set your shipping address to your office address. The latest version has improved the bookmark feature, making it easier for you to organize frequently used content.
```

### 译文 B

```
Please select your preferred color in the account settings and set your shipping address to your office address. The latest version has improved the bookmark feature, making it easier for you to organize frequently used content.
```

| 维度 | A 更好／相当／B 更好 | 片段与理由 |
| --- | --- | --- |
| 准确性 | | |
| 流畅性 | | |
| 风格 | | |
| 术语一致性 | | |

整体偏好：________；理由：________

揭盲后结论（修订更好／相当／初译更好）：________

## locale-en-gb · 英美地区对照

### 输入与要求

```
{
  "text": "请在账户设置中选择你喜欢的颜色，并将发货地址设为办公室地址。新版本优化了收藏夹，方便你整理常用内容。",
  "source_lang": "中文",
  "target_lang": "English",
  "locale": "en-GB",
  "style": "友好、简洁的产品说明；采用目标地区自然的拼写与用词",
  "glossary": {
    "账户设置": "account settings"
  }
}
```

### 译文 A

```
Please select your preferred color in the account settings and set your shipping address to your office address. The new version has optimized the bookmark, making it easier for you to organize frequently used content.
```

### 译文 B

```
Please select your preferred color in the account settings and set your shipping address to your office address. The new version has optimized the bookmark, making it easier for you to organize frequently used content.
```

| 维度 | A 更好／相当／B 更好 | 片段与理由 |
| --- | --- | --- |
| 准确性 | | |
| 流畅性 | | |
| 风格 | | |
| 术语一致性 | | |

整体偏好：________；理由：________

揭盲后结论（修订更好／相当／初译更好）：________
