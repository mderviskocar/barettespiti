"""Create presentation figures from the recorded Gaussian Blur experiment.

Only writes sonuclar/bulaniklik/sunum/. Existing measurements and figures stay intact.
"""

import csv
import json
import sys
from pathlib import Path

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kaynak.bulaniklik import bulaniklastir  # noqa: E402
from kaynak.renk import renk_maskesi  # noqa: E402
from kaynak.veri import goruntu_oku, veri_setini_oku  # noqa: E402

SOURCE = ROOT / "sonuclar/bulaniklik/bulaniklik_sonuclari.csv"
OUTPUT = ROOT / "sonuclar/bulaniklik/sunum"
COLORS = {"RGB": "#18618a", "HSV": "#c46b18"}
NAVY = "#193246"
GRAY = "#52616d"
GRID = "#d9e0e5"
SIGMAS = (0.0, 0.5, 1.5, 3.0)
DESCRIPTIONS = {
    "K1": "Loş ışıkta başta baret",
    "K2": "Uzak ve küçük baret",
    "K3": "Benzer renkli iş makinesi",
    "K4": "Elde tutulan baret",
}


def fmt2(value):
    return f"{value:.2f}".replace(".", ",")


def fmt_sigma(value):
    return "0" if value == 0 else str(value).replace(".", ",")


def measurements():
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        records = list(csv.DictReader(handle))
    indexed = {(r["kimlik"], float(r["sigma"]), r["yontem"]): r for r in records}
    expected = {(image, sigma, method) for image in DESCRIPTIONS
                for sigma in SIGMAS for method in COLORS}
    if len(records) != 32 or set(indexed) != expected:
        raise ValueError("Gaussian Blur CSV must contain 32 unique control measurements.")
    return indexed


def style_axis(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(GRID)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors=GRAY)


def roi_plot(ax, rows, labels=True):
    for method in COLORS:
        y = [float(rows["K2", sigma, method]["bas_ortusmesi_yuzde"]) for sigma in SIGMAS]
        ax.plot(SIGMAS, y, marker="o", linewidth=2.8, markersize=7,
                color=COLORS[method], label=method)
        if labels:
            for sigma, value in zip(SIGMAS, y):
                offset = -14 if method == "RGB" else 10
                ax.annotate(fmt2(value), (sigma, value), xytext=(0, offset),
                            textcoords="offset points", ha="center", fontsize=10,
                            color=COLORS[method])
    ax.axhline(5, color=GRAY, linestyle="--", linewidth=1.2,
               label="Baş örtüşmesi eşiği: %5")
    ax.set_xlim(-0.13, 3.13)
    ax.set_ylim(0, 27)
    ax.set_xticks(SIGMAS, ("0", "0,5", "1,5", "3,0"))
    ax.set_xlabel("Gaussian sigma (σ)")
    ax.set_ylabel("Baş ROI örtüşmesi (%)")
    ax.legend(loc="upper left", frameon=False, ncol=3, fontsize=9)
    style_axis(ax)


def k2_chart(rows, settings):
    fig, ax = plt.subplots(figsize=(12, 6.3), dpi=150)
    fig.patch.set_facecolor("white")
    roi_plot(ax, rows)
    ax.set_title("K2 | Küçük barette baş ROI örtüşmesi", loc="left",
                 fontsize=19, fontweight="bold", color=NAVY, pad=19)
    fig.subplots_adjust(left=0.09, right=0.97, top=0.79, bottom=0.26)
    areas = {method: [float(rows["K2", sigma, method]["maske_alani_yuzde"])
                      for sigma in SIGMAS] for method in COLORS}
    threshold = settings["karar_kurali"]["en_az_renk_alani_yuzde"]
    fig.text(0.09, 0.15,
             f"Toplam maske alanı: RGB %{fmt2(areas['RGB'][0])} → %{fmt2(areas['RGB'][-1])}   |   "
             f"HSV %{fmt2(areas['HSV'][0])} → %{fmt2(areas['HSV'][-1])}",
             fontsize=12, fontweight="bold", color=NAVY)
    fig.text(0.09, 0.09,
             f"Tüm alan değerleri %{str(threshold).replace('.', ',')} eşiğinin altında; alan testi önce yapıldığı için karar her σ'da baret_yok.",
             fontsize=11, color=GRAY)
    fig.text(0.09, 0.025, "Kaynak: sonuclar/bulaniklik/bulaniklik_sonuclari.csv · 3 Kasım 2026",
             fontsize=9, color=GRAY)
    fig.savefig(OUTPUT / "K2_bas_roi_ortusmesi.png", dpi=150, facecolor="white")
    plt.close(fig)


def area_change_chart(rows):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), dpi=140, sharey=True)
    fig.suptitle("Gaussian Blur | σ=0'a göre maske alanı değişimi",
                 fontsize=19, fontweight="bold", color=NAVY, y=0.97)
    colors = {"K1": "#18618a", "K2": "#c46b18", "K3": "#73895a", "K4": "#8d5b79"}
    for ax, method in zip(axes, COLORS):
        for image in DESCRIPTIONS:
            base = float(rows[image, 0.0, method]["maske_alani_yuzde"])
            values = [float(rows[image, sigma, method]["maske_alani_yuzde"]) - base
                      for sigma in SIGMAS]
            ax.plot(SIGMAS, values, marker="o", linewidth=2, color=colors[image], label=image)
        ax.axhline(0, color=GRAY, linewidth=1)
        ax.set_title(method, fontsize=15, color=NAVY)
        ax.set_xticks(SIGMAS, ("0", "0,5", "1,5", "3,0"))
        ax.set_xlabel("Gaussian sigma (σ)")
        ax.set_ylim(-0.26, 0.18)
        style_axis(ax)
    axes[0].set_ylabel("Maske alanı farkı (yüzde puan)")
    axes[1].legend(title="Görüntü", frameon=False, loc="lower left", ncol=2)
    fig.text(0.07, 0.02, "Farklar kayıtlı, iki ondalığa yuvarlanmış CSV değerlerinden hesaplandı.",
             fontsize=9, color=GRAY)
    fig.subplots_adjust(top=0.82, bottom=0.18, left=0.07, right=0.98, wspace=0.16)
    fig.savefig(OUTPUT / "maske_alani_degisim_sunum.png", dpi=140, facecolor="white")
    plt.close(fig)


def comparison_figures(dataset, settings):
    for image_id, record in dataset.items():
        image = goruntu_oku(record["dosya"])
        fig, axes = plt.subplots(2, 4, figsize=(16, 7.7), dpi=120)
        fig.suptitle(f"{image_id} | {DESCRIPTIONS[image_id]}", x=0.04, ha="left",
                     fontsize=21, fontweight="bold", color=NAVY, y=0.97)
        for index, sigma in enumerate(SIGMAS):
            blurred = bulaniklastir(image, sigma, settings["bulaniklik"]["cekirdek"])
            mask = renk_maskesi(blurred, "HSV", settings["renk_araliklari"])
            upper, lower = axes[:, index]
            upper.imshow(cv2.cvtColor(blurred, cv2.COLOR_BGR2RGB))
            lower.imshow(mask, cmap="gray", vmin=0, vmax=255)
            upper.set_title(f"σ = {fmt_sigma(sigma)}" + (" · filtresiz" if sigma == 0 else ""),
                            fontsize=14, color=NAVY, pad=10)
            lower.set_title("HSV renk maskesi", fontsize=11, color=GRAY, pad=8)
            for ax in (upper, lower):
                ax.axis("off")
        fig.text(0.04, 0.025,
                 "15×15 çekirdek · Aynı görüntü ve dondurulmuş HSV aralığı · Üst: görüntü  Alt: maske",
                 fontsize=11, color=GRAY)
        fig.subplots_adjust(left=0.035, right=0.985, top=0.85, bottom=0.075,
                            wspace=0.035, hspace=0.16)
        fig.savefig(OUTPUT / f"{image_id}_sigma_sunum.png", dpi=120, facecolor="white")
        plt.close(fig)


def k2_crop(image, roi, sigma, kernel):
    x1, y1, x2, y2 = roi
    pad = 110
    left, top = max(0, x1 - pad), max(0, y1 - pad)
    right, bottom = min(image.shape[1], x2 + pad), min(image.shape[0], y2 + pad)
    blurred = bulaniklastir(image, sigma, kernel)
    return cv2.cvtColor(blurred[top:bottom, left:right], cv2.COLOR_BGR2RGB), (
        x1 - left, y1 - top, x2 - x1, y2 - y1)


def show_crop(ax, image, roi, sigma, kernel):
    crop, box = k2_crop(image, roi, sigma, kernel)
    ax.imshow(crop)
    ax.add_patch(Rectangle((box[0], box[1]), box[2], box[3], fill=False,
                           edgecolor="#f4e0a5", linewidth=2))
    ax.set_title(f"σ={fmt_sigma(sigma)}" + (" · filtresiz" if sigma == 0 else ""),
                 color=NAVY, fontsize=13, pad=8)
    ax.axis("off")


def k2_closeup(dataset, settings):
    record = dataset["K2"]
    image = goruntu_oku(record["dosya"])
    fig, axes = plt.subplots(1, 4, figsize=(15, 4.5), dpi=140)
    fig.suptitle("K2 | Küçük baretin yakın planı", x=0.04, ha="left",
                 fontsize=19, fontweight="bold", color=NAVY, y=0.96)
    for ax, sigma in zip(axes, SIGMAS):
        show_crop(ax, image, record["bas_roi"], sigma, settings["bulaniklik"]["cekirdek"])
    fig.text(0.04, 0.055, "Sarı çerçeve: aynı baş ROI · 15×15 çekirdek · Yalnızca sigma değişir",
             color=GRAY, fontsize=11)
    fig.subplots_adjust(left=0.035, right=0.985, top=0.82, bottom=0.12, wspace=0.06)
    fig.savefig(OUTPUT / "K2_yakin_plan.png", dpi=140, facecolor="white")
    plt.close(fig)


def one_slide(rows, dataset, settings):
    fig = plt.figure(figsize=(16, 9), dpi=120, facecolor="white")
    fig.text(0.04, 0.94, "Gaussian Blur: K2'de örtüşme değişti, karar değişmedi",
             fontsize=22, fontweight="bold", color=NAVY)
    fig.text(0.04, 0.89, "Küçük baret · 15×15 çekirdek · σ = 0 / 0,5 / 1,5 / 3,0",
             fontsize=13, color=GRAY)
    grid = fig.add_gridspec(1, 2, left=0.04, right=0.97, top=0.81, bottom=0.31,
                           width_ratios=[0.9, 1.1], wspace=0.13)
    crops = grid[0].subgridspec(1, 2, wspace=0.06)
    image = goruntu_oku(dataset["K2"]["dosya"])
    for ax, sigma in zip((fig.add_subplot(crops[0]), fig.add_subplot(crops[1])), (0.0, 3.0)):
        show_crop(ax, image, dataset["K2"]["bas_roi"], sigma,
                  settings["bulaniklik"]["cekirdek"])
    ax = fig.add_subplot(grid[1])
    roi_plot(ax, rows, labels=False)
    ax.set_title("Baş ROI örtüşmesi", loc="left", fontsize=16, color=NAVY, pad=12)
    rgb = [float(rows["K2", sigma, "RGB"]["bas_ortusmesi_yuzde"]) for sigma in SIGMAS]
    hsv = [float(rows["K2", sigma, "HSV"]["bas_ortusmesi_yuzde"]) for sigma in SIGMAS]
    rgb_area = [float(rows["K2", sigma, "RGB"]["maske_alani_yuzde"]) for sigma in SIGMAS]
    hsv_area = [float(rows["K2", sigma, "HSV"]["maske_alani_yuzde"]) for sigma in SIGMAS]
    threshold = settings["karar_kurali"]["en_az_renk_alani_yuzde"]
    fig.text(0.04, 0.245,
             f"ROI: RGB %{fmt2(rgb[0])} → %{fmt2(rgb[-1])}   |   HSV %{fmt2(hsv[0])} → %{fmt2(hsv[-1])}",
             fontsize=17, fontweight="bold", color=NAVY)
    fig.text(0.04, 0.195,
             f"Toplam maske alanı: RGB %{fmt2(rgb_area[0])} → %{fmt2(rgb_area[-1])}; "
             f"HSV %{fmt2(hsv_area[0])} → %{fmt2(hsv_area[-1])}. Hepsi %{str(threshold).replace('.', ',')} eşiğinin altında.",
             fontsize=13, color=NAVY)
    fig.text(0.04, 0.142,
             "Ön tahmin kısmen desteklendi: RGB örtüşmesi azalırken HSV arttı. "
             "K1–K4'te hiçbir RGB/HSV sınıf kararı değişmedi.",
             fontsize=12, color=GRAY)
    fig.text(0.04, 0.076,
             "Alan kuralı önce çalışır → her σ için K2 tahmini baret_yok; gerçek sınıf basta_baret.",
             fontsize=13, fontweight="bold", color=COLORS["RGB"])
    fig.text(0.04, 0.025,
             "Kaynak: sonuclar/bulaniklik/bulaniklik_sonuclari.csv · Dondurulmuş eşikler ve mevcut etiketler",
             fontsize=9, color=GRAY)
    fig.savefig(OUTPUT / "gaussian_blur_tek_slayt.png", dpi=120, facecolor="white")
    plt.close(fig)


def main():
    settings = json.loads((ROOT / "ayarlar/deney_ayarlari.json").read_text(encoding="utf-8"))
    if (settings["bulaniklik"]["cekirdek"] != [15, 15]
            or tuple(settings["bulaniklik"]["sigma_degerleri"]) != SIGMAS
            or settings["karar_kurali"]["en_az_renk_alani_yuzde"] != 2.5):
        raise ValueError("Presentation figures expect the recorded 15×15 / sigma / 2.5% settings.")
    rows = measurements()
    if any(len({rows[image, sigma, method]["kural_sinifi"] for sigma in SIGMAS}) != 1
           for image in DESCRIPTIONS for method in COLORS):
        raise ValueError("Class decisions changed; update the slide conclusion before rendering.")
    if any(rows["K2", sigma, method]["kural_sinifi"] != "baret_yok"
           or rows["K2", sigma, method]["dogru_sinif"] != "basta_baret"
           for sigma in SIGMAS for method in COLORS):
        raise ValueError("K2 classification differs from the recorded slide conclusion.")
    dataset = {r["kimlik"]: r for r in veri_setini_oku("kontrol")}
    if set(dataset) != set(DESCRIPTIONS):
        raise ValueError("Expected K1–K4 control images.")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    k2_chart(rows, settings)
    area_change_chart(rows)
    comparison_figures(dataset, settings)
    k2_closeup(dataset, settings)
    one_slide(rows, dataset, settings)
    for path in sorted(OUTPUT.glob("*.png")):
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
