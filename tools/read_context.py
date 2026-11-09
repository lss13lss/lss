"""Read the default personal context or one named section from the vault."""
import argparse
import re
from pathlib import Path

VAULT = Path(__file__).resolve().parents[1]
DEFAULT_NOTE = "05-成长/对话成长/个人画像/COMMUNICATION.md"


def read_section(note, heading):
    path = (VAULT / note).resolve()
    relative = path.relative_to(VAULT)
    if path.suffix.lower() != ".md":
        raise ValueError("请选择 Markdown 笔记")
    lines = path.read_text(encoding="utf-8").splitlines()
    headings = []
    fence = None
    for index, line in enumerate(lines):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1].startswith(fence) and not marker[2].strip():
                fence = None
            continue
        if marker:
            fence = marker[1]
            continue
        match = re.match(r"^ {0,3}(#{1,6})[ \t]+(.+)$", line)
        if match:
            title = re.sub(r"[ \t]+#+$", "", match[2].strip())
            headings.append((index, len(match[1]), title))
    matches = [(start, depth) for start, depth, title in headings if title == heading]
    if len(matches) != 1:
        raise ValueError(f"{relative} 中标题「{heading}」命中 {len(matches)} 次，请核对标题或直接读对应行")
    start, depth = matches[0]
    end = next((i for i, level, _ in headings if i > start and level <= depth), len(lines))
    if not any(line.strip() for line in lines[start + 1:end]):
        raise ValueError(f"{relative} 的「{heading}」没有正文")
    return f"{relative}:{start + 1}\n" + "\n".join(lines[start:end]).rstrip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("note", nargs="?", help="vault 内的 Markdown 路径")
    parser.add_argument("heading", nargs="?", help="准确的章节标题")
    args = parser.parse_args()
    if (args.note is None) != (args.heading is None):
        parser.error("请同时指定笔记路径与标题，或都省略以加载默认上下文")
    try:
        print(read_section(args.note or DEFAULT_NOTE, args.heading or "已确认"))
    except (OSError, ValueError) as exc:
        parser.exit(1, f"未加载：{exc}\n")


if __name__ == "__main__":
    main()
