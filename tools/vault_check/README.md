# vault_check

整理知识库后用来自查的小脚本。

## check_links.py

扫描全库 wikilink，列出指向不存在文件的链接（即 Obsidian 里的死链）。

```bash
python3 tools/vault_check/check_links.py
```

- 按 Obsidian 的解析规则处理：`[[名称]]` 匹配任意位置的同名文件（含附件），`[[路径/名称]]` 精确匹配，`[[名称|别名]]` 与 `[[名称#标题]]` 取前半部分。
- 跳过 `.git`、`.obsidian`、`backups`、`tools`、`skills`。
- 输出中若出现 `[[笔记名]]` 这类，通常是文档里刻意写的语法示例，可以忽略。

## 检查孤儿附件

找出 `attachments/` 中没有任何笔记引用的图片：

```bash
python3 - <<'PY'
import os
vault = "/Users/jiawangliang/konwledge base/lss"
SKIP = {".git", ".obsidian", "backups", "tools", "skills"}
texts = []
for root, dirs, files in os.walk(vault):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for f in files:
        if f.endswith(".md"):
            texts.append(open(os.path.join(root, f), encoding="utf-8", errors="ignore").read())
blob = "\n".join(texts)
files = sorted(os.listdir(os.path.join(vault, "attachments")))
for f in files:
    if f not in blob:
        print("未被引用:", f)
PY
```

> 删除笔记前先确认其引用的图片是否需要跟着迁到合并稿，否则图片会变成孤儿文件（文件还在，但没有任何笔记指向它）。

整理记录见 [[00-整理记录-2026-09-21]]。
