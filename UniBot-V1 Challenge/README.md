# UniBot-V1 Challenge

下载脚本对应 Hugging Face 的 [UniBot-V1 Challenge collection](https://huggingface.co/collections/unitreerobotics/unibot-v1-challenge)。

## 下载

```bash
export HF_TOKEN=hf_...
export HF_USERNAME=your_huggingface_username
chmod +x "UniBot-V1 Challenge/tools"/*.sh
"UniBot-V1 Challenge/tools/download_unibot_v1.sh"
```

默认下载到 `tools/datasets/`。查看清单：

```bash
"UniBot-V1 Challenge/tools/download_unibot_v1.sh" --list
```

只下载一个数据集：

```bash
"UniBot-V1 Challenge/tools/download_unibot_v1.sh" --dataset unitreerobotics/G1_Dex1_HangCup
```

`hfd.sh` 支持断点续传、`aria2c`/`wget` 切换，以及 `--include`/`--exclude` 文件过滤。不要把 `HF_TOKEN` 写入脚本或提交到 Git。
