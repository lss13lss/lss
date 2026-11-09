"""Read the default personal context (resident card + confirmed communication rules) or one named
section from the vault."""
import argparse
import re
from pathlib import Path

VAULT = Path(__file__).resolve().parents[1]
DEFAULT_NOTE = "05-成长/对话成长/个人画像/COMMUNICATION.md"
CARD_NOTE = "05-成长/对话成长/上下文系统/CARD.md"
CURRENT_NOTE = "05-成长/对话成长/上下文系统/CURRENT.md"
CARD_MARKER = "<!-- CURRENT:auto -->"
CARD_SOFT_LIMIT = 2200  # 字符（中文 1 字算 1）；超过只提示，不截断

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

def first_sentence(text):
    """取一行正文的第一句，用于 CURRENT 条目尚未写加粗首句时的降级摘要。"""
    text = text.strip()
    text = re.sub(r"^\[\[[^\]]*\]\]\s*", "", text)  # 去掉行首的纯链接
    m = re.match(r"(.+?[。；！？])", text)
    return (m[1] if m else text).rstrip("。；！？")

def current_items():
    """从 CURRENT「## 当前目标」下抽每条的摘要和第一个 wikilink，按小节分组。

    摘要优先取加粗首句；条目未加粗时退回该条第一个句子，并在 stderr 提示待补齐。
    这样卡片在任何版本的 CURRENT 上都能用，CURRENT 的格式迁移可以分步进行。
    链接保留 #锚点（只把路径压成 basename），否则同一页的不同小节在卡片里无法区分。
    """
    lines = (VAULT / CURRENT_NOTE).read_text(encoding="utf-8").splitlines()
    out, group, inside, unformatted = [], None, False, []
    for line in lines:
        if re.match(r"^## ", line):
            inside = line.strip() == "## 当前目标"
            continue
        if not inside:
            continue
        h = re.match(r"^### (.+)$", line)
        if h:
            group = h[1].strip()
            continue
        if not (line.startswith("- ") and group):
            continue
        m = re.match(r"^- \*\*(.+?)\*\*", line)
        if m:
            summary, rest = m[1], line[m.end():]
        else:
            summary, rest = first_sentence(line[2:]), ""
            unformatted.append(summary[:24])
        link = re.search(r"\[\[([^\]|]+)", rest or line)
        if link:
            target_path, _, anchor = link[1].partition("#")
            shown = target_path.split("/")[-1]
            target = f" → [[{shown}#{anchor}]]" if anchor else f" → [[{shown}]]"
        else:
            target = ""
        out.append((group, summary.rstrip("。"), target))
    if unformatted:
        import sys
        print(
            "提示：CURRENT「当前目标」下有 {} 条未以加粗首句开头，已退回取首句：{}。"
            "补齐加粗首句后卡片摘要更准。".format(len(unformatted), "；".join(unformatted)),
            file=sys.stderr,
        )
    if not out:
        raise ValueError(f"{CURRENT_NOTE} 的「当前目标」下没有可抽取的条目")
    rendered, last = [], None
    for group, text, target in out:
        if group != last:
            rendered.append(f"- {group}")
            last = group
        rendered.append(f"  - {text}{target}")
    return "\n".join(rendered)

def render_card():
    text = (VAULT / CARD_NOTE).read_text(encoding="utf-8")
    body = text.split("\n---\n", 1)[1] if text.startswith("---") else text
    body = "\n".join(l for l in body.splitlines() if not l.startswith(">") and not l.startswith("# ")).strip()
    body = re.sub(r"\n{3,}", "\n\n", body)
    if CARD_MARKER not in body:
        raise ValueError(f"{CARD_NOTE} 缺少 {CARD_MARKER} 标记")
    body = body.replace(CARD_MARKER, current_items())
    return f"{CARD_NOTE}（「现在在推进」实时取自 {CURRENT_NOTE}）\n{body}"

def default_context():
    parts = []
    try:
        parts.append(render_card())
    except (OSError, ValueError) as exc:  # 卡片失败不影响沟通约定
        parts.append(f"未加载常驻卡片：{exc}")
    parts.append(read_section(DEFAULT_NOTE, "已确认"))
    out = "\n\n".join(parts)
    size = len(out)
    if size > CARD_SOFT_LIMIT:
        import sys
        print(f"提示：默认上下文 {size} 字，超过建议的 {CARD_SOFT_LIMIT}，考虑精简 CURRENT 摘要或卡片", file=sys.stderr)
    return out

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("note", nargs="?", help="vault 内的 Markdown 路径")
    parser.add_argument("heading", nargs="?", help="准确的章节标题")
    args = parser.parse_args()
    if (args.note is None) != (args.heading is None):
        parser.error("请同时指定笔记路径与标题，或都省略以加载默认上下文")
    try:
        print(read_section(args.note, args.heading) if args.note else default_context())
    except (OSError, ValueError) as exc:
        parser.exit(1, f"未加载：{exc}\n")

if __name__ == "__main__":
    main()
