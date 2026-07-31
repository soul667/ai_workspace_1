#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HFD="${SCRIPT_DIR}/hfd.sh"
DATASET_ROOT="${SCRIPT_DIR}/datasets"
HF_ENDPOINT="${HF_ENDPOINT:-https://huggingface.co}"

usage() {
  cat <<'EOF'
Usage:
  download_unibot_v1.sh [options]

Options:
  --list                 Print the collection dataset IDs and exit.
  --dataset ID           Download only one dataset (may be repeated).
  --output DIR           Root directory for downloaded datasets.
  --tool aria2c|wget     Downloader passed to hfd.sh (default: aria2c).
  --help                 Show this help.

Authentication:
  export HF_TOKEN=hf_...
  export HF_USERNAME=your_huggingface_username   # only needed for gated repos
EOF
}

DATASETS=(
  unitreerobotics/G1_Dex1_HangCup
  unitreerobotics/G1_Dex1_ArrangePlates
  unitreerobotics/G1_Dex1_ArrangeTestTubes
  unitreerobotics/G1_Dex1_ZipUp
  unitreerobotics/G1_Dex1_ColorArrangement
  unitreerobotics/G1_Dex1_Unlock
  unitreerobotics/G1_Dex1_DisconnectEthernet
  unitreerobotics/G1_Dex1_ConveyorSorting
  unitreerobotics/G1_Dex1_FruitCollection
  unitreerobotics/G1_Dex1_FoldTowel
  unitreerobotics/G1_Dex1_OrganizeBookshelf
  unitreerobotics/G1_Dex1_FruitSorting
  unitreerobotics/G1_Dex1_SpellRobot
  unitreerobotics/G1_Dex1_OrganizePencilCase
  unitreerobotics/G1_Dex1_OrganizeStationery
  unitreerobotics/G1_Dex1_StackBowls
  unitreerobotics/G1_Dex1_StoreCups
  unitreerobotics/G1_Dex1_OrganizeTools
  unitreerobotics/G1_Dex1_PackDoll
  unitreerobotics/G1_Dex1_PackBag
  unitreerobotics/G1_Dex1_PackPhone
  unitreerobotics/G1_Dex1_StoreEarphones
  unitreerobotics/G1_Dex1_StorePaddle
  unitreerobotics/G1_Dex1_PaperCupStacking
  unitreerobotics/G1_Dex1_PickOutBatteries
  unitreerobotics/G1_Dex1_ToolboxStorage
  unitreerobotics/G1_Dex1_PlugCharger
  unitreerobotics/G1_Dex1_SyringeWaterTransfer
  unitreerobotics/G1_Dex1_PlugInEthernet
  unitreerobotics/G1_Dex1_PlacePhotoFrame
  unitreerobotics/G1_Dex1_RemovePinnedNote
  unitreerobotics/G1_Dex1_PourOutMedicine
)

SELECTED=()
TOOL=aria2c
while (($#)); do
  case "$1" in
    --list) printf '%s\n' "${DATASETS[@]}"; exit 0 ;;
    --dataset) (($# >= 2)) || { echo "--dataset requires an ID" >&2; exit 2; }; SELECTED+=("$2"); shift 2 ;;
    --output) (($# >= 2)) || { echo "--output requires a directory" >&2; exit 2; }; DATASET_ROOT="$2"; shift 2 ;;
    --tool) (($# >= 2)) || { echo "--tool requires aria2c or wget" >&2; exit 2; }; TOOL="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -x "$HFD" ]] || { echo "hfd.sh is not executable: $HFD" >&2; exit 1; }
if ((${#SELECTED[@]} == 0)); then SELECTED=("${DATASETS[@]}"); fi
mkdir -p "$DATASET_ROOT"

for repo in "${SELECTED[@]}"; do
  if [[ ! " ${DATASETS[*]} " == *" $repo "* ]]; then
    echo "Not in the UniBot-V1 collection: $repo" >&2
    exit 2
  fi
  name="${repo##*/}"
  echo "==== Downloading ${repo} ===="
  HF_ENDPOINT="$HF_ENDPOINT" "$HFD" "$repo" --dataset --tool "$TOOL" --local-dir "${DATASET_ROOT}/${name}"
done
