# lss 个人知识库

开始任何实质性任务前，必须完整读取：

`/Users/jiawangliang/konwledge base/lss/05-成长/对话成长/上下文系统/BOOTSTRAP.md`

按照该文件继续加载个人画像、当前目标、工作区索引和必要的导师材料。不要一次加载全部原始会话或全部导师库。

编辑 vault 时保留现有目录、frontmatter、标签和 wikilink 约定。未经用户明确授权，不进行大范围移动、重命名或删除。

## 整理与自查

- 删除任何笔记前先留可恢复副本：`backups/obsidian-cleanup-YYYYMMDD/`（含 `整理前笔记与配置.zip` 与 `原始文件清单.json`），并记录到对应的整理记录页。
- **注意区分「被 Git 跟踪」与「未跟踪」的文件**：被跟踪的删了能从历史找回，未跟踪的（虚拟环境、`.bak`、生成产物、运行日志）删掉就没了——这部分必须单独打包留档。
- 删除文件一律移入废纸篓（`~/.Trash/`）而非 `rm`，并保留废纸篓目录名与备份包对应。
- 合并笔记时把原笔记引用的截图一并迁到合并稿，否则图片会沦为孤儿文件。
- 整理后用 `python3 tools/vault_check/check_links.py` 一次自查死链与库卫生（孤儿附件、构建产物、系统垃圾、空目录、零字节与重复笔记），说明见 `tools/vault_check/README.md`。
- 完成整理后按 `vault backup: YYYY-MM-DD HH:MM:SS` 的风格提交，并推送到 origin/main 供另一台设备同步。

## 库内不该有的东西

这个库在 Mac 与 Windows 两台设备间同步，所以只放内容，不放环境：

- **虚拟环境**（`.venv/`、`venv/`）与 Python 构建产物（`__pycache__/`、`.pytest_cache/`、`*.egg-info/`）。虚拟环境写死了本机绝对路径，同步过去只会留下一个跑不起来的环境；需要时在目标设备重建。
- **生成产物与运行日志**（如 skill 跑出来的示例文件、`logs/`）。
- **系统垃圾**（`.DS_Store`、`._*`、`*.bak-*`）。

以上均已在 `.gitignore` 中挡住，新装 skill 后请检查有没有带进 `.venv`。

## 本机 Git 与同步

GitHub 的 **22 端口在本机被网络策略拦截**（表现为 `Connection closed by ... port 22`）。已在本地配置 URL 改写，所有 `git@github.com:` 开头的地址自动走 443：

```bash
git config --local url."ssh://git@ssh.github.com:443/".insteadOf "git@github.com:"
```

配置后 `git push origin main`、`git pull` 以及 Obsidian Git 插件都能正常同步，无需每次手动指定端口。若换设备或重装，重新执行上面那条命令；未配置时的手动兜底：

```bash
GIT_SSH_COMMAND="ssh -p 443" git push ssh://git@ssh.github.com:443/lss13lss/lss.git main
```

同步前先 `git fetch` 检查另一端是否有新提交，避免非快进冲突。


