#!/usr/bin/env python3
"""知识库自查：失效 wikilink + 库卫生（孤儿附件 / 构建产物 / 系统垃圾 / 空目录 / 重复笔记）。

用法：
    python3 tools/vault_check/check_links.py            # 链接 + 卫生，全量自查
    python3 tools/vault_check/check_links.py --links     # 只查链接
    python3 tools/vault_check/check_links.py --junk      # 只查卫生
    python3 tools/vault_check/check_links.py --path DIR  # 指定库路径

wikilink 解析规则（贴近 Obsidian 行为）：
- [[name]]              -> 任意位置存在同名文件（basename 命中，忽略大小写）
- [[path/name]]         -> 精确路径命中，或 basename 命中
- [[name|alias]]        -> 取 name
- [[name#heading]]      -> 取 name

退出码：链接有死链返回 1；仅卫生有问题返回 0（卫生问题不阻塞同步）。
"""
import hashlib
import os
import re
import sys
from collections import defaultdict

DEFAULT_VAULT = "/Users/jiawangliang/konwledge base/lss"
INDEX_SKIP = {".git", ".obsidian", ".trash"}   # 完全不进入
SCAN_SKIP = {"backups", "tools", "skills"}     # 索引为链接目标，但不扫描其内部链接

LINK_RE = re.compile(r"\[\[([^\[\]]+?)\]\]")

# 卫生检查：不应进入库的目录 / 文件
JUNK_DIRS = {".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache",
             ".ruff_cache", "node_modules", ".ipynb_checkpoints"}
JUNK_DIR_SUFFIX = (".egg-info",)
JUNK_FILES = {".DS_Store", "Thumbs.db", "desktop.ini"}


def is_junk_dir(name):
    return name in JUNK_DIRS or name.endswith(JUNK_DIR_SUFFIX)


def is_junk_file(name):
    return (
        name in JUNK_FILES
        or name.startswith("._")
        or name.startswith("~$")
        or name.endswith(("~", ".tmp", ".temp", ".swp", ".pyc", ".pyo"))
        or ".bak" in name
    )


def walk_vault(vault):
    """返回 (all_files, scan_md, junk_dirs, junk_files, empty_dirs)。"""
    all_files, scan_md, junk_dirs, junk_files, empty_dirs = [], [], [], [], []
    for root, dirs, files in os.walk(vault):
        rel_root = os.path.relpath(root, vault)
        dirs[:] = [d for d in dirs if d not in INDEX_SKIP]
        scan = not any(part in SCAN_SKIP for part in rel_root.split(os.sep))

        def rel(p):
            return os.path.relpath(p, vault)

        # 垃圾目录单独记录（不再深入）
        keep = []
        for d in dirs:
            p = os.path.join(root, d)
            if scan and is_junk_dir(d):
                junk_dirs.append(rel(p))
            else:
                keep.append(d)
        dirs[:] = keep

        for f in files:
            p = os.path.join(root, f)
            all_files.append(p)
            if scan and is_junk_file(f):
                junk_files.append(rel(p))
                continue
            if scan and f.endswith(".md"):
                scan_md.append(p)

        if root != vault and not os.listdir(root):
            empty_dirs.append(rel_root)
    return all_files, scan_md, junk_dirs, junk_files, empty_dirs


def check_links(vault, all_files, scan_md):
    by_base = {}
    for p in all_files:
        base = os.path.splitext(os.path.basename(p))[0].lower()
        by_base.setdefault(base, []).append(os.path.relpath(p, vault))

    rel_set = {os.path.splitext(os.path.relpath(p, vault))[0].lower() for p in all_files}
    norm_set = {os.path.normpath(x).lower() for x in rel_set}

    folder_set = set()
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in INDEX_SKIP]
        for d in dirs:
            folder_set.add(os.path.relpath(os.path.join(root, d), vault).lower())

    broken, folders_only = defaultdict(list), defaultdict(list)
    total = 0
    for path in scan_md:
        rel_src = os.path.relpath(path, vault)
        with open(path, encoding="utf-8", errors="ignore") as fh:
            text = fh.read()
        for m in LINK_RE.finditer(text):
            raw = m.group(1).strip()
            target = raw.split("|")[0].split("#")[0].replace("\\", "").strip()
            if not target:
                continue
            total += 1
            t = target.lower()
            base = os.path.basename(t)
            t_noext = os.path.splitext(t)[0]
            base_noext = os.path.splitext(base)[0]
            ok = (
                t in rel_set
                or t_noext in rel_set
                or os.path.normpath(t).lower() in norm_set
                or os.path.normpath(t_noext).lower() in norm_set
                or base in by_base
                or base_noext in by_base
            )
            if ok:
                continue
            (folders_only if t in folder_set else broken)[rel_src].append(raw)

    n_broken = sum(len(v) for v in broken.values())
    print(f"markdown 文件: {len(scan_md)}  |  链接总数: {total}")
    print(f"文件级失效链接: {n_broken}  |  指向文件夹的链接: {sum(len(v) for v in folders_only.values())}")
    print("=" * 70)
    for src in sorted(broken):
        print(f"\n▸ {src}")
        for tgt in sorted(set(broken[src])):
            print(f"    [[{tgt}]]")
    if folders_only:
        print("\n---- 指向文件夹（Obsidian 中不可点击）----")
        for src in sorted(folders_only):
            print(f"▸ {src}: " + ", ".join(f"[[{x}]]" for x in sorted(set(folders_only[src]))))
    if n_broken:
        print("\n提示：文档里刻意写的语法示例（如 [[笔记名]]）会被算作死链，人工判断即可。")
    return n_broken


def check_hygiene(vault, all_files, scan_md, junk_dirs, junk_files, empty_dirs):
    print("=" * 70)
    print("库卫生检查")
    print("=" * 70)

    issues = 0

    # 1. 孤儿附件
    att_dir = os.path.join(vault, "attachments")
    orphans = []
    if os.path.isdir(att_dir):
        blob = "\n".join(
            open(p, encoding="utf-8", errors="ignore").read() for p in scan_md
        )
        for f in sorted(os.listdir(att_dir)):
            fp = os.path.join(att_dir, f)
            if os.path.isfile(fp) and f not in blob:
                orphans.append((f, os.path.getsize(fp)))
    print(f"\n[1] 孤儿附件（attachments/ 中无任何笔记引用）: {len(orphans)}")
    for f, s in orphans:
        print(f"    {s / 1024:>8.1f} KB  {f}")
    issues += len(orphans)

    # 2. 构建产物与系统垃圾
    print(f"\n[2] 构建产物 / 系统垃圾: 目录 {len(junk_dirs)}，文件 {len(junk_files)}")
    for d in junk_dirs:
        print(f"    目录  {d}")
    for f in junk_files[:30]:
        print(f"    文件  {f}")
    if len(junk_files) > 30:
        print(f"    ... 另有 {len(junk_files) - 30} 个")
    issues += len(junk_dirs) + len(junk_files)

    # 3. 空目录（提示，不计入问题：多为设计上保留的分类占位）
    print(f"\n[3] 空目录（提示，不计入问题）: {len(empty_dirs)}")
    for d in empty_dirs:
        print(f"    {d}")
    if empty_dirs:
        print("    若是设计上保留的分类占位可忽略；Git 无法跟踪空目录，另一台设备 pull 后需重建。")

    # 4. 零字节笔记
    zeros = [os.path.relpath(p, vault) for p in scan_md
             if os.path.getsize(p) == 0]
    print(f"\n[4] 零字节笔记: {len(zeros)}")
    for z in zeros:
        print(f"    {z}")
    issues += len(zeros)

    # 5. 内容完全相同的笔记
    hashes = defaultdict(list)
    for p in scan_md:
        with open(p, "rb") as fh:
            hashes[hashlib.md5(fh.read()).hexdigest()].append(os.path.relpath(p, vault))
    dups = {k: v for k, v in hashes.items() if len(v) > 1}
    print(f"\n[5] 内容完全重复的笔记: {len(dups)} 组")
    for k, v in dups.items():
        print("    重复组:")
        for x in sorted(v):
            print(f"      - {x}")
    issues += sum(len(v) - 1 for v in dups.values())

    print(f"\n{'─' * 70}")
    if issues:
        print(f"卫生问题合计: {issues} 项（清理前请先备份：见 AGENTS.md 的整理流程）")
    else:
        print("卫生检查通过：无孤儿附件、无构建产物、无系统垃圾、无零字节笔记、无重复笔记。")
    return issues


def main():
    args = sys.argv[1:]
    if "--help" in args or "-h" in args:
        print(__doc__)
        return 0
    vault = DEFAULT_VAULT
    if "--path" in args:
        vault = args[args.index("--path") + 1]
    do_links = "--junk" not in args
    do_junk = "--links" not in args

    all_files, scan_md, junk_dirs, junk_files, empty_dirs = walk_vault(vault)

    n_broken = 0
    if do_links:
        n_broken = check_links(vault, all_files, scan_md)
    if do_junk:
        if do_links:
            print()
        check_hygiene(vault, all_files, scan_md, junk_dirs, junk_files, empty_dirs)

    return 1 if n_broken else 0


if __name__ == "__main__":
    sys.exit(main())
