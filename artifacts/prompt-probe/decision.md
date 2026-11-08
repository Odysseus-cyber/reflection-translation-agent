# 提示词候选结论：保留现行 v1-json

本轮候选没有提供可采纳的改进证据。诊断组审校结构通过数从现行 **1/4** 变成候选 **0/4**，候选三次未完整结束；编辑仍有事实遗漏，并新增复制分隔符或附加 JSON 的现象。建议保持生产提示词不变，保留本次失败记录供后续定位。

## 对照范围与实际设置

- 新调用严格 **20 次**：4 个诊断案例 × 现行/候选 × 审校/编辑，共16次；2个留出案例 × 候选审校/编辑，共4次。没有初译调用，没有重试。
- 全部使用已有本机 `gemma3:1b`，temperature 0.2，输出上限4096 tokens，上下文16384，单次超时120秒。未调用云端，也未下载模型。
- 审校比较使用同一份历史初译；编辑比较使用同一份**手工诊断审校报告**。它是受控测试输入，不是模型审校输出。本轮不测端到端流程提升。
- 候选模板在第一条新模型调用前冻结。完整消息、Schema、初译、合成建议和设置见 [plan.json](plan.json)，20份逐次结果保留原始文本、耗时、实际用量及异常。

## 诊断组结果

| 项目 | 现行提示词 | 候选提示词 |
| --- | ---: | ---: |
| 审校结构通过 | 1/4 | 0/4 |
| 审校请求完整返回 | 4/4 | 1/4 |
| 审校耗时合计 | 23.138秒 | 87.023秒 |
| 审校输出tokens | 1796 | 总数未知；已知小计8328，1次未提供 |
| 编辑请求完整返回 | 4/4 | 4/4 |
| 编辑耗时合计 | 3.915秒 | 3.662秒 |

“结构通过”只表示符合 `ReviewReport`。例如现行 `zh-ja-product` 返回四个空数组，尽管历史初译没有采用“お気に入り”的术语表译法。

候选审校的两个案例达到4096输出tokens；第三个未完成响应没有提供token用量，保留未知，不计为零。该例仍保存了部分响应文本。

### 编辑阶段的可核验现象

| 案例 | 现行编辑 | 候选编辑 |
| --- | --- | --- |
| en-zh-business | 按受控建议把周五改成周四，输出译文 | 同样改为周四，但追加“原翻译”说明和JSON，导致 `{name}` 重复 |
| zh-en-product | 仍遗漏14天，并重复“Start your free trial now!” | 仍遗漏14天和工作区，复制 `<<<` / `>>>` 分隔符 |
| zh-ja-product | 保留“コレクションアルバム”，未采用“お気に入り” | 同样没有修复术语 |
| zh-ja-technical | 缺失条件没有修复成正文，追加日语解释与建议 | 复制初译和分隔符，仍缺双重验证条件与手机恢复用途 |

对应原始输出：[商务现行](diagnosis-en-zh-business-revision-current.json)、[商务候选](diagnosis-en-zh-business-revision-candidate.json)、[英文产品现行](diagnosis-zh-en-product-revision-current.json)、[英文产品候选](diagnosis-zh-en-product-revision-candidate.json)、[日文产品现行](diagnosis-zh-ja-product-revision-current.json)、[日文产品候选](diagnosis-zh-ja-product-revision-candidate.json)、[日文技术现行](diagnosis-zh-ja-technical-revision-current.json)、[日文技术候选](diagnosis-zh-ja-technical-revision-candidate.json)。

预先设置的少量字符串标记没有覆盖“原翻译”、日语解释标题和分隔符复制，所以自动 `dialogue_or_payload_flags=0` **不代表输出格式合格**。上表由直接核对保留原文得出，没有把这些事后发现冒充预注册检查。

## 留出组结果

留出组仅运行冻结候选，不把历史结果当作同次采样的现行对照。

- `zh-en-business`：审校返回合规但空的问题清单；受控编辑按手工建议将 Thursday 改为 Friday，并保留两个 `{name}`。这只证明对该指定编辑指令的执行，不代表审校自行发现问题，也不以英文星期字面命中判定整体时间语义。[审校](holdout-zh-en-business-review-candidate.json)、[编辑](holdout-zh-en-business-revision-candidate.json)
- `ja-zh-technical`：审校的 `dimension` 与分组不一致，结构失败；编辑仍以“重新启动应用程序后，请重启应用”开头，没有恢复原文“更改设置后”的条件。[审校](holdout-ja-zh-technical-review-candidate.json)、[编辑](holdout-ja-zh-technical-revision-candidate.json)

## 候选内容与复查

候选审校改成英文的精炼指令：最多三条有依据的问题；先检查数字、日期、否定和条件；明确引用原文/初译；每条理由与建议使用简短中文。候选编辑将原文、初译用分隔符标明，仅传入必要建议，并重复要求完整目标语言译文。合同和Ollama Schema保持原样。

候选的具体模板及消息构造实现在 [prompt_probe.py](../../scripts/prompt_probe.py)，完整实例在 [plan.json](plan.json)。当前结果不支持将这套候选替换进生产。

只重新汇总已有记录，不发模型请求：

```sh
UV_CACHE_DIR=.uv-cache uv run --no-sync python scripts/prompt_probe.py --summarize-only
```

脚本现在使用显式 `--baseline-dir`，默认固定到本轮历史评估目录，避免按随机UUID猜测最新评估。该目录路径作为补充元数据写入计划；冻结的20份输入与生成设置未改动，未重新运行模型。
