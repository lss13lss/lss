#!/usr/bin/env python3
"""扫描 Obsidian 库内的失效 wikilink。

解析规则（贴近 Obsidian 行为）：
- [[name]]              -> 任意位置存在同名文件（basename 命中，忽略大小写）
- [[path/name]]         -> 精确路径命中，或 basename 命中
- [[name|alias]]        -> 取 name
- [[name#heading]]      -> 取 name
"""
import os
import re
import sys

VAULT = "/Users/jiawangliang/konwledge base/lss"
INDEX_SKIP = {".git", ".obsidian"}          # 完全不进入
SCAN_SKIP = {"backups", "tools", "skills"}  # 索引为目标，但不扫描其内部链接

LINK_RE = re.compile(r"\[\[([^\[\]]+?)\]\]")


def main():
    md_files = []
    all_files = []
    for root, dirs, files in os.walk(VAULT):
        # INDEX_SKIP：完全不进入；SCAN_SKIP：只索引（可作为链接目标），不扫描其内部链接
        dirs[:] = [d for d in dirs if d not in INDEX_SKIP]
        rel_root = os.path.relpath(root, VAULT)
        scan = not any(part in SCAN_SKIP for part in rel_root.split(os.sep))
        for f in files:
            p = os.path.join(root, f)
            all_files.append(p)
            if scan and f.endswith(".md"):
                md_files.append(p)

    # basename -> 相对路径列表（含附件，Obsidian 对附件也按 basename 解析）
    by_base = {}
    for p in all_files:
        rel = os.path.relpath(p, VAULT)
        base = os.path.splitext(os.path.basename(p))[0].lower()
        by_base.setdefault(base, []).append(rel)

    rel_set = {os.path.splitext(os.path.relpath(p, VAULT))[0].lower() for p in all_files}
    folder_set = set()
    for root, dirs, files in os.walk(VAULT):
        dirs[:] = [d for d in dirs if d not in INDEX_SKIP]
        for d in dirs:
            folder_set.add(os.path.relpath(os.path.join(root, d), VAULT).lower())

    broken = {}
    folders_only = {}
    total_links = 0
    for path in md_files:
        rel_src = os.path.relpath(path, VAULT)
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for m in LINK_RE.finditer(text):
            raw = m.group(1).strip()
            target = raw.split("|")[0].split("#")[0].replace("\\", "").strip()
            if not target:
                continue
            total_links += 1
            t = target.lower()
            base = os.path.basename(t)
            t_noext = os.path.splitext(t)[0]
            base_noext = os.path.splitext(base)[0]
            ok = (
                t in rel_set
                or t_noext in rel_set
                or os.path.normpath(t).lower() in {os.path.normpath(x) for x in rel_set}
                or os.path.normpath(t_noext).lower() in {os.path.normpath(x) for x in rel_set}
                or base in by_base
                or base_noext in by_base
            )
            if ok:
                continue
            if t in folder_set:
                folders_only.setdefault(rel_src, []).append(raw)
            else:
                broken.setdefault(rel_src, []).append(raw)

    print(f"markdown 文件: {len(md_files)}  |  链接总数: {total_links}")
    print(f"文件级失效链接: {sum(len(v) for v in broken.values())}  |  指向文件夹的链接: {sum(len(v) for v in folders_only.values())}")
    print("=" * 70)
    for src in sorted(broken):
        print(f"\n▸ {src}")
        for tgt in sorted(set(broken[src])):
            print(f"    [[{tgt}]]")
    if folders_only:
        print("\n---- 指向文件夹（Obsidian 中不可点击）----")
        for src in sorted(folders_only):
            print(f"▸ {src}: " + ", ".join(f"[[{x}]]" for x in sorted(set(folders_only[src]))))
    return 0 if not broken else 1


if __name__ == "__main__":
    sys.exit(main())
