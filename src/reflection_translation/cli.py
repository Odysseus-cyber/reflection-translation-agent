"""Command-line entry points sharing the same workflow as the web UI."""

import argparse
import json
import sys
import tempfile
from pathlib import Path

from pydantic import ValidationError

from . import __version__
from .llm import ProviderError
from .models import TranslationRequest


class CLIInputError(ValueError):
    """An actionable message produced locally, without raw library error contents."""


def _prepare_output(directory: Path) -> Path:
    """Reject an unusable output directory before spending time on a model call."""
    directory = directory.resolve()
    try:
        directory.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=directory) as probe:
            probe.write(b"x")
            probe.flush()
    except OSError:
        raise CLIInputError("输出目录无法写入，请检查路径、权限和磁盘空间。") from None
    return directory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="多语言反思翻译 Agent")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    ui = commands.add_parser("ui", help="启动中文演示界面")
    ui.add_argument("--host", default="127.0.0.1")
    ui.add_argument("--port", type=int, default=7860)

    translate = commands.add_parser("translate", help="翻译短文本并导出运行报告")
    source = translate.add_mutually_exclusive_group(required=True)
    source.add_argument("--text", help="待翻译短文本")
    source.add_argument("--text-file", type=Path, help="读取 UTF-8 纯文本；仍限 2000 字符")
    translate.add_argument("--source", required=True, help="源语言，如 zh 或 中文")
    translate.add_argument("--target", required=True, help="目标语言，如 en 或 English")
    translate.add_argument("--locale", default="")
    translate.add_argument("--style", default="自然、忠实原文")
    translate.add_argument("--glossary", type=Path, help="JSON 术语映射文件")
    translate.add_argument("--output", type=Path, default=Path("artifacts"))

    evaluate = commands.add_parser("evaluate", help="运行自编样例，保存配对结果与人工评审表")
    evaluate.add_argument("--case", action="append", default=[], help="只运行指定案例 ID，可重复")
    evaluate.add_argument("--locale-pair", action="store_true", help="额外运行同源英美地区对照")
    evaluate.add_argument("--output", type=Path, default=Path("artifacts/evaluation"))

    for command in (translate, evaluate):
        command.add_argument("--backend", choices=["ollama", "compatible"], default="ollama")
        command.add_argument("--model", default=None, help="覆盖 .env 中的模型名")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "ui":
            from .ui import build_app

            build_app().queue(default_concurrency_limit=1).launch(
                server_name=args.host, server_port=args.port, share=False,
                show_error=False,
            )
            return 0

        from .config import create_client
        from .reports import write_report
        from .workflow import translate

        if args.command == "translate":
            text = args.text if args.text is not None else args.text_file.read_text(encoding="utf-8")
            glossary = json.loads(args.glossary.read_text(encoding="utf-8")) if args.glossary else {}
            request = TranslationRequest(
                text=text, source_lang=args.source, target_lang=args.target,
                locale=args.locale, style=args.style, glossary=glossary,
            )
            args.output = _prepare_output(args.output)
            with create_client(args.backend, args.model) as client:
                result = translate(request, client)
            if result.status == "completed":
                print(result.revised_translation)
            else:
                print(f"翻译未完成：{result.error}", file=sys.stderr)
                if result.initial_translation:
                    print("已完成的初译：\n" + result.initial_translation)
            try:
                paths = write_report(result, args.output / result.run_id)
            except OSError:
                print("已取得的译文见上方；报告导出失败，请检查输出目录和磁盘空间。", file=sys.stderr)
                return 2
            print("\n报告：" + " | ".join(str(p.resolve()) for p in paths), file=sys.stderr)
            return 0 if result.status == "completed" else 1

        from .evaluation import evaluate_cases
        from .examples import load_cases, load_locale_pair

        cases = load_cases()
        if args.case:
            selected = set(args.case)
            missing = selected - {case["id"] for case in cases}
            if missing:
                raise CLIInputError("未知案例 ID；请使用项目样例中定义的案例 ID。")
            cases = [case for case in cases if case["id"] in selected]
        if args.locale_pair:
            cases.extend(load_locale_pair())
        args.output = _prepare_output(args.output)
        with create_client(args.backend, args.model) as client:
            summary = evaluate_cases(cases, client, args.output)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        if summary.get("status") == "failed" or summary.get("export_failed", 0):
            print(summary.get("error") or "评估报告导出失败，请检查输出目录。", file=sys.stderr)
            return 2
        return 1 if summary.get("failed", 0) else 0
    except KeyboardInterrupt:
        if args.command == "evaluate":
            print("评估已中断；已完成记录请查看输出目录内的 evaluation-*/summary.json。", file=sys.stderr)
        else:
            print("已中断。", file=sys.stderr)
        return 130
    except ValidationError as exc:
        # Avoid echoing complete input data or configuration values in errors.
        print("参数校验失败：", file=sys.stderr)
        for error in exc.errors():
            print(f"  {'.'.join(map(str, error['loc']))}: {error['msg']}", file=sys.stderr)
        return 2
    except ProviderError as exc:
        print(f"无法执行（{exc.code}）：{exc}", file=sys.stderr)
        return 2
    except CLIInputError as exc:
        print(f"无法执行：{exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError:
        print("无法执行：术语文件必须包含合法的 JSON 对象。", file=sys.stderr)
        return 2
    except UnicodeError:
        print("无法执行：输入文件必须使用 UTF-8 编码。", file=sys.stderr)
        return 2
    except OSError:
        print("无法执行：请检查输入文件、输出目录和磁盘空间。", file=sys.stderr)
        return 2
    except ValueError:
        print("无法执行：参数或案例数据无效，请检查输入格式。", file=sys.stderr)
        return 2
    except Exception:
        print("无法执行：发生内部错误，请检查服务与输出目录。", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
