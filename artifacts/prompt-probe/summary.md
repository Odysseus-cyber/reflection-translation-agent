# 本地提示词诊断：冻结初译的阶段对照

Stage-level, single-generation diagnostic comparison; no quality score or claim of end-to-end improvement. Revision uses synthetic controlled reviews, never model review output. Holdouts have no newly sampled current-prompt arm.

候选在首次新模型调用前固定。诊断组4例；留出组2例仅运行候选，不能当作同期双臂对照。

编辑阶段使用明确标注的手工诊断建议，两版得到相同事实建议；不是端到端流水线测试。

模型：gemma3:1b。新增调用 20 / 20；原始输入/输出/耗时/实际设置见每条 JSON。

| 分组/阶段/提示词 | 调用 | 请求完成 | 审校Schema通过 | 输出tokens | 秒 |
| --- | ---: | ---: | ---: | ---: | ---: |
| diagnosis/review/current | 4 | 4 | 1 | 1796 | 23.138 |
| diagnosis/review/candidate | 4 | 1 | 0 | 未知（已知小计8328；1次未提供） | 87.023 |
| diagnosis/revision/current | 4 | 4 | — | 219 | 3.915 |
| diagnosis/revision/candidate | 4 | 4 | — | 214 | 3.662 |
| holdout/review/candidate | 2 | 2 | 1 | 294 | 5.179 |
| holdout/revision/candidate | 2 | 2 | — | 80 | 1.552 |

## 逐条结果

| 记录 | 请求错误 | Schema | 输出tokens |
| --- | --- | --- | ---: |
| [diagnosis-en-zh-business-review-current](diagnosis-en-zh-business-review-current.json) | 无 | False | 472 |
| [diagnosis-en-zh-business-review-candidate](diagnosis-en-zh-business-review-candidate.json) | truncated: Ollama 未生成完整结果，请检查输出长度上限。 | False | 4096 |
| [diagnosis-en-zh-business-revision-current](diagnosis-en-zh-business-revision-current.json) | 无 | — | 37 |
| [diagnosis-en-zh-business-revision-candidate](diagnosis-en-zh-business-revision-candidate.json) | 无 | — | 121 |
| [diagnosis-zh-en-product-review-current](diagnosis-zh-en-product-review-current.json) | 无 | False | 625 |
| [diagnosis-zh-en-product-review-candidate](diagnosis-zh-en-product-review-candidate.json) | truncated: Ollama 未生成完整结果，请检查输出长度上限。 | False | 4096 |
| [diagnosis-zh-en-product-revision-current](diagnosis-zh-en-product-revision-current.json) | 无 | — | 30 |
| [diagnosis-zh-en-product-revision-candidate](diagnosis-zh-en-product-revision-candidate.json) | 无 | — | 27 |
| [diagnosis-zh-ja-product-review-current](diagnosis-zh-ja-product-review-current.json) | 无 | True | 19 |
| [diagnosis-zh-ja-product-review-candidate](diagnosis-zh-ja-product-review-candidate.json) | truncated: Ollama 未生成完整结果，请检查输出长度上限。 | False | None |
| [diagnosis-zh-ja-product-revision-current](diagnosis-zh-ja-product-revision-current.json) | 无 | — | 37 |
| [diagnosis-zh-ja-product-revision-candidate](diagnosis-zh-ja-product-revision-candidate.json) | 无 | — | 37 |
| [diagnosis-zh-ja-technical-review-current](diagnosis-zh-ja-technical-review-current.json) | 无 | False | 680 |
| [diagnosis-zh-ja-technical-review-candidate](diagnosis-zh-ja-technical-review-candidate.json) | 无 | False | 136 |
| [diagnosis-zh-ja-technical-revision-current](diagnosis-zh-ja-technical-revision-current.json) | 无 | — | 115 |
| [diagnosis-zh-ja-technical-revision-candidate](diagnosis-zh-ja-technical-revision-candidate.json) | 无 | — | 29 |
| [holdout-zh-en-business-review-candidate](holdout-zh-en-business-review-candidate.json) | 无 | True | 23 |
| [holdout-zh-en-business-revision-candidate](holdout-zh-en-business-revision-candidate.json) | 无 | — | 52 |
| [holdout-ja-zh-technical-review-candidate](holdout-ja-zh-technical-review-candidate.json) | 无 | False | 271 |
| [holdout-ja-zh-technical-revision-candidate](holdout-ja-zh-technical-revision-candidate.json) | 无 | — | 28 |

字面检查只检出数字/占位符/术语及若干元话语信号；不能判定全部语义、条件、自然度或正确目标语言。原文条件是否保真必须人工对照。
