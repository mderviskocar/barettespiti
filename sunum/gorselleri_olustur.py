"""Sunum için mevcut fotoğraf, etiket ve maskeleri bir araya getirir.

Sayılar yalnızca sonuclar/temel_sonuclar.csv dosyasından okunur. Bu betik
deneyleri yeniden çalıştırmaz ve kaynak görüntüleri değiştirmez.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


KOK = Path(__file__).resolve().parents[1]
CIKTI = KOK / "sunum" / "gorseller"
CIKTI.mkdir(parents=True, exist_ok=True)

ETIKETLER = {
    item["kimlik"]: item
    for item in json.loads((KOK / "etiketler/gercek_etiketler.json").read_text(encoding="utf-8"))[
        "goruntuler"
    ]
}
with (KOK / "sonuclar/temel_sonuclar.csv").open(encoding="utf-8-sig", newline="") as stream:
    SONUCLAR = {
        (row["kimlik"], row["yontem"]): row
        for row in csv.DictReader(stream)
    }


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size)


def foto(kimlik: str) -> Image.Image:
    bolum = "gelistirme" if kimlik.startswith("G") else "kontrol"
    return Image.open(KOK / "veri" / bolum / f"{kimlik}.jpg").convert("RGB")


def anotasyon_izgarasi() -> Path:
    panel_w, panel_h, gap = 470, 260, 12
    canvas = Image.new("RGB", (3 * panel_w + 4 * gap, 2 * panel_h + 3 * gap), "#f5f7fa")
    draw = ImageDraw.Draw(canvas)
    for index, kimlik in enumerate(("G1", "G2", "K1", "K2", "K3", "K4")):
        row, col = divmod(index, 3)
        x, y = gap + col * (panel_w + gap), gap + row * (panel_h + gap)
        original = foto(kimlik)
        annotated = original.copy()
        overlay = ImageDraw.Draw(annotated)
        item = ETIKETLER[kimlik]
        if item["bas_roi"]:
            overlay.rectangle(item["bas_roi"], outline="#00d5d0", width=max(3, original.width // 250))
        for box in item["baret_kutulari"]:
            overlay.rectangle(box, outline="#ffd166", width=max(3, original.width // 250))
        displayed = ImageOps.contain(annotated, (panel_w, panel_h - 42), Image.Resampling.LANCZOS)
        canvas.paste(displayed, (x + (panel_w - displayed.width) // 2, y + 32))
        draw.text((x + 12, y + 3), f"{kimlik}  |  {'Geliştirme' if kimlik.startswith('G') else 'Kontrol'}",
                  fill="#132b40", font=font(23, True))
    path = CIKTI / "alti_goruntu_anotasyon.png"
    canvas.save(path)
    return path


def maske_izgarasi() -> Path:
    panel_w, panel_h, gap = 372, 290, 10
    canvas = Image.new("RGB", (4 * panel_w + 5 * gap, 2 * panel_h + 3 * gap), "#f5f7fa")
    draw = ImageDraw.Draw(canvas)
    for row, yontem in enumerate(("RGB", "HSV")):
        for col, kimlik in enumerate(("K1", "K2", "K3", "K4")):
            x, y = gap + col * (panel_w + gap), gap + row * (panel_h + gap)
            original = foto(kimlik)
            mask = Image.open(KOK / "sonuclar/maskeler" / f"{kimlik}_{yontem.lower()}.png").convert("L")
            assert mask.size == original.size, (kimlik, yontem)
            scaled = ImageOps.contain(original, (panel_w - 12, 195), Image.Resampling.LANCZOS)
            scaled_mask = mask.resize(scaled.size, Image.Resampling.NEAREST)
            # Maskeyi görsel olarak belirginleştirir; ölçülmüş alan CSV'den alınır.
            tint = Image.new("RGB", scaled.size, "#11d4c1" if yontem == "RGB" else "#ffb547")
            overlay = Image.blend(scaled, tint, 0.72)
            scaled.paste(overlay, (0, 0), scaled_mask)
            canvas.paste(scaled, (x + (panel_w - scaled.width) // 2, y + 34))
            result = SONUCLAR[kimlik, yontem]
            draw.text((x + 12, y + 5), f"{kimlik}  {yontem}", fill="#132b40", font=font(23, True))
            label = "Doğru" if result["dogru_mu"] == "evet" else "Yanlış"
            short_class = {
                "baret_yok": "Baret yok",
                "baret_var_basta_degil": "Başta değil",
                "basta_baret": "Başta baret",
                "belirsiz": "Belirsiz",
            }[result["kural_sinifi"]]
            draw.text((x + 12, y + 233), f"Alan %{float(result['maske_alani_yuzde']):.2f}",
                      fill="#132b40", font=font(23, True))
            draw.text((x + 12, y + 259), f"{short_class}  •  {label}",
                      fill="#11657b" if label == "Doğru" else "#a64138", font=font(20, True))
    path = CIKTI / "sekiz_maske.png"
    canvas.save(path)
    return path


if __name__ == "__main__":
    for output in (anotasyon_izgarasi(), maske_izgarasi()):
        print(output.relative_to(KOK))
