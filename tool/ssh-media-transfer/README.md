# SSH Media Transfer

在 SSH 服务器上下载图片/视频，并使用 `rsync` 传输到本机目录或另一台服务器。

## 交互模式

直接运行即可进入菜单：

```bash
uvx --from 'git+https://github.com/soul667/ai_workspace_1.git#subdirectory=tool/ssh-media-transfer' media-fetch
```

可以选择下载并传输、只下载，或发送已有文件。

## GitHub Packages

仓库已包含 GitHub Actions。推送版本标签即可发布：

```bash
git tag ssh-media-transfer-v0.1.0
git push origin ssh-media-transfer-v0.1.0
```

## 直接使用

在本项目目录测试：

```bash
uv run media-fetch --help
uv run media-fetch download 'https://example.com/video.mp4' -d ~/downloads
uv run media-fetch send ~/downloads/video.mp4 user@另一台服务器:/data/videos/
uv run media-fetch fetch 'https://example.com/image.jpg' --to user@另一台服务器:/data/images/
```

安装到任意 SSH 主机后，发布到 Git 仓库即可：

```bash
uvx --from 'git+https://github.com/你的用户名/ssh-media-transfer.git' media-fetch fetch URL --to user@host:/data/
```

也可以将本地项目直接作为 `uvx` 来源：

```bash
uvx --from . media-fetch fetch URL --to user@host:/data/
```

要求：目标机器安装 `rsync`，并且 SSH 密钥登录已经配置好。`--partial` 支持中断后继续传输；同名且非空的下载文件会自动跳过。
