from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import questionary
from rich.console import Console
from rich.panel import Panel


console = Console()


REMOTE_RE = re.compile(r"^(?:(?P<user>[^@:/]+)@)?(?P<host>[^:/]+):(?P<path>.+)$")


def is_remote(value: str) -> bool:
    return bool(REMOTE_RE.match(value)) and not value.startswith(("/", "./", "../"))


def run(cmd: list[str]) -> None:
    print("+", " ".join(map(str, cmd)))
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        raise SystemExit(f"未找到命令：{cmd[0]}，请先安装它。")
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode)


def filename_from_url(url: str) -> str:
    name = Path(urllib.parse.urlparse(url).path).name
    return name or "download.bin"


def download(url: str, dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / filename_from_url(url)
    if target.exists() and target.stat().st_size > 0:
        print(f"已存在，跳过下载：{target}")
        return target
    console.print(f"[cyan]下载地址[/]  {url}\n[cyan]保存位置[/]  {target}")
    request = urllib.request.Request(url, headers={"User-Agent": "ssh-media-transfer/0.1"})
    try:
        with urllib.request.urlopen(request) as response, target.open("wb") as output:
            shutil.copyfileobj(response, output, length=1024 * 1024)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    return target


def transfer(source: Path, target: str, delete_source: bool = False) -> None:
    if not shutil.which("rsync"):
        raise SystemExit("未找到 rsync，请安装 rsync 后重试。")
    if is_remote(target):
        host, remote_path = target.split(":", 1)
        run(["ssh", host, "mkdir", "-p", remote_path])
    else:
        target = str(Path(target).expanduser())
        Path(target).mkdir(parents=True, exist_ok=True)
    run(["rsync", "-avh", "--partial", "--progress", str(source), target])
    if delete_source:
        source.unlink()


def interactive() -> None:
    console.print(Panel.fit(
        "[bold cyan]SSH Media Transfer[/bold cyan]\n"
        "下载图片 / 视频，并传输到本机或远程服务器",
        border_style="cyan",
    ))
    action = questionary.select(
        "请选择操作：",
        choices=[
            questionary.Choice("下载并传输（推荐）", value="fetch"),
            questionary.Choice("只下载到当前服务器", value="download"),
            questionary.Choice("发送已有文件", value="send"),
            questionary.Choice("退出", value="exit"),
        ],
    ).ask()
    if action in (None, "exit"):
        return

    if action == "download":
        url = questionary.text("图片/视频 URL：").ask()
        directory = questionary.path("保存目录：", default="~/downloads").ask()
        if url and directory:
            download(url, Path(directory).expanduser())
        return

    if action == "send":
        source = questionary.path("已有文件路径：", only_files=True).ask()
        target = questionary.text(
            "目标目录（本机目录或 user@host:/path/）：",
            default="~/downloads/",
        ).ask()
        if source and target:
            transfer(Path(source).expanduser(), target)
        return

    url = questionary.text("图片/视频 URL：").ask()
    target = questionary.text(
        "目标目录（本机目录或 user@host:/path/）：",
        default="user@host:/data/",
    ).ask()
    cache = questionary.path("服务器临时缓存目录：", default="/tmp/media-fetch").ask()
    if url and target and cache:
        source = download(url, Path(cache).expanduser())
        transfer(source, target)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-fetch",
        description="在 SSH 主机下载图片/视频，并通过 rsync 发送到本地或另一台服务器。",
    )
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("download", help="只下载到当前 SSH 主机")
    p.add_argument("url")
    p.add_argument("-d", "--dir", default=".", help="保存目录，默认当前目录")

    p = sub.add_parser("send", help="发送已有文件")
    p.add_argument("source")
    p.add_argument("target", help="本地目录或 user@host:/remote/path/")
    p.add_argument("--remove-source", action="store_true")

    p = sub.add_parser("fetch", help="下载后直接发送")
    p.add_argument("url")
    p.add_argument("--to", required=True, dest="target", help="本地目录或 user@host:/remote/path/")
    p.add_argument("--cache-dir", default="/tmp/media-fetch", help="临时下载目录")
    p.add_argument("--remove-source", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if not args.command:
        interactive()
        return
    try:
        if args.command == "download":
            download(args.url, Path(args.dir).expanduser())
        elif args.command == "send":
            transfer(Path(args.source).expanduser(), args.target, args.remove_source)
        else:
            source = download(args.url, Path(args.cache_dir).expanduser())
            transfer(source, args.target, args.remove_source)
    except (urllib.error.URLError, OSError) as exc:
        print(f"失败：{exc}", file=sys.stderr)
        raise SystemExit(1)
