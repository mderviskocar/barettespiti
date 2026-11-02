"""Sunum için özet görsel: TP/FP/FN tablosu + yanlış alarm (K4) + kaçırma (K2) örnekleri.

Kullanım: python scripts/make_mask_box_figure.py
Girdi:   results/detector/raw_mask_boxes.json ve *_boxes.png (evaluate_color_mask_boxes.py çıktıları)
Çıktı:   results/detector/mask_box_summary.png
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import cv2  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = ROOT / "results/detector"


def rgb(path):
    return cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB)


def crop(image, box, pad):
    x1, y1, x2, y2 = box
    return image[max(0, y1 - pad):y2 + pad, max(0, x1 - pad):x2 + pad]


def main():
    data = json.loads((OUT / "raw_mask_boxes.json").read_text(encoding="utf-8"))["images"]
    rows, totals = [], {"rgb": [0, 0, 0], "hsv": [0, 0, 0]}
    for image_id in ("K1", "K2", "K3", "K4"):
        cells = [image_id]
        for method in ("rgb", "hsv"):
            ev = data[image_id][method]["evaluation"]
            cells.append(f"{ev['tp']} / {ev['fp']} / {ev['fn']}")
            for i, key in enumerate(("tp", "fp", "fn")):
                totals[method][i] += ev[key]
        rows.append(cells)
    rows.append(["Toplam"] + [" / ".join(map(str, totals[m])) for m in ("rgb", "hsv")])

    fig = plt.figure(figsize=(16, 9))
    grid = fig.add_gridspec(2, 3, height_ratios=[1, 1.1])
    fig.suptitle("Renk maskesi kutu değerlendirmesi (IoU ≥ 0.50) — K1–K4, 4 gerçek baret",
                 fontsize=16, fontweight="bold")

    ax = fig.add_subplot(grid[0, 0])
    ax.axis("off")
    table = ax.table(cellText=rows, colLabels=["Görüntü", "RGB  TP/FP/FN", "HSV  TP/FP/FN"],
                     loc="center", cellLoc="center")
    table.scale(1, 1.8)
    table.set_fontsize(12)
    for (r, _), cell in table.get_celld().items():
        if r in (0, len(rows)):
            cell.set_text_props(fontweight="bold")
    ax.set_title("Kutu düzeyi sayım", fontsize=13)

    ax = fig.add_subplot(grid[0, 1:])
    ax.axis("off")
    ax.text(0, 0.95, "Renk kutusu = sarı renkli bağlı bölge; nesne dedektörü değildir.\n"
                     "Yeşil: gerçek baret · Mavi: TP · Kırmızı: FP · Gri: baş ROI\n\n"
                     "• Yanlış alarm (K4): yelek, sarı kordon, ten rengi, filigran → RGB 17, HSV 19 FP\n"
                     "• Kaçırma (K2, gece): RGB bareti hiç seçmedi; HSV seçti ama iki parçaya böldü\n"
                     "   (IoU 0.39 ve 0.19 < 0.50) → FN\n"
                     "• K3 (uzak): HSV iki bareti de buldu (IoU 0.51 ve 0.70); RGB kısmi kaldı → 2 FN\n"
                     "• K4: baret bulundu (IoU 0.92) ama elde → kutu ≠ \"başta\" (S3)",
            fontsize=12.5, va="top", family="DejaVu Sans")

    k4 = rgb(OUT / "K4_rgb_boxes.png")
    ax = fig.add_subplot(grid[1, 0])
    ax.imshow(k4)
    ax.set_title("Yanlış alarm: K4 RGB (1 TP, 17 FP)", fontsize=12)
    ax.axis("off")

    k2 = rgb(OUT / "K2_hsv_boxes.png")
    gt = data["K2"]["gt_helmet_boxes"][0]
    ax = fig.add_subplot(grid[1, 1])
    ax.imshow(crop(k2, gt, 70))
    ax.set_title("Kaçırma: K2 HSV — baret parçalandı (FN)", fontsize=12)
    ax.axis("off")

    k3 = rgb(OUT / "K3_hsv_boxes.png")
    gt = data["K3"]["gt_helmet_boxes"][0]
    ax = fig.add_subplot(grid[1, 2])
    ax.imshow(crop(k3, gt, 45))
    ax.set_title("Sınırda doğru: K3 HSV (IoU 0.51)", fontsize=12)
    ax.axis("off")

    fig.tight_layout()
    fig.savefig(OUT / "mask_box_summary.png", dpi=130)
    print("Kaydedildi:", OUT / "mask_box_summary.png")


if __name__ == "__main__":
    main()
