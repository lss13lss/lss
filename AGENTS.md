# lss 个人知识库

开始任何实质性任务前，必须完整读取：

`/Users/jiawangliang/konwledge base/lss/05-成长/对话成长/上下文系统/BOOTSTRAP.md`

按照该文件继续加载个人画像、当前目标、工作区索引和必要的导师材料。不要一次加载全部原始会话或全部导师库。

编辑 vault 时保留现有目录、frontmatter、标签和 wikilink 约定。未经用户明确授权，不进行大范围移动、重命名或删除。

## 整理与自查

- 删除任何笔记前先留可恢复副本：`backups/obsidian-cleanup-YYYYMMDD/`（含 `整理前笔记与配置.zip` 与 `原始文件清单.json`），并记录到对应的整理记录页。
- 合并笔记时把原笔记引用的截图一并迁到合并稿，否则图片会沦为孤儿文件。
- 整理后用 `python3 tools/vault_check/check_links.py` 全库自查死链，孤儿附件检查见 `tools/vault_check/README.md`。
- 完成整理后按 `vault backup: YYYY-MM-DD HH:MM:SS` 的风格提交，并推送到 origin/main 供另一台设备同步。

## 本机 Git 限制

GitHub 的 22 端口在本机常被网络策略拦截（表现为 `Connection closed by ... port 22`）。改用 443 端口即可：

```bash
GIT_SSH_COMMAND="ssh -p 443" git push ssh://git@ssh.github.com:443/lss13lss/lss.git main
```


