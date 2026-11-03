"""Veri, etiket ve ayar dosyalarını okuyan ortak yardımcılar."""

import csv
import json
from pathlib import Path

import cv2
import numpy as np

KOK = Path(__file__).resolve().parents[1]
SINIFLAR = ("basta_baret", "baret_var_basta_degil", "baret_yok", "belirsiz")


def ayarlari_oku():
    return json.loads((KOK / "ayarlar" / "deney_ayarlari.json").read_text(encoding="utf-8"))


def goruntu_oku(yol):
    """BGR görüntü okur; Windows'ta Türkçe karakterli yollarda da çalışır."""
    yol = Path(yol)
    if not yol.is_absolute():
        yol = KOK / yol
    goruntu = cv2.imdecode(np.frombuffer(yol.read_bytes(), dtype=np.uint8), cv2.IMREAD_COLOR)
    if goruntu is None:
        raise ValueError(f"Görüntü okunamadı: {yol}")
    return goruntu


def maske_oku(kimlik, katman):
    """İsteğe bağlı piksel düzeyi gerçek maske (etiketler/maskeler/<kimlik>_<katman>.png); yoksa None."""
    yol = KOK / "etiketler" / "maskeler" / f"{kimlik}_{katman}.png"
    if not yol.is_file():
        return None
    maske = cv2.imdecode(np.frombuffer(yol.read_bytes(), dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
    return None if maske is None else (maske > 127).astype(np.uint8) * 255


def veri_setini_oku(bolum=None):
    """Kaynak listesi + gerçek etiketler. bolum: None, 'gelistirme' veya 'kontrol'."""
    with (KOK / "veri" / "kaynaklar.csv").open(encoding="utf-8", newline="") as dosya:
        kaynaklar = list(csv.DictReader(dosya))
    etiketler = json.loads((KOK / "etiketler" / "gercek_etiketler.json").read_text(encoding="utf-8"))
    etiket = {g["kimlik"]: g for g in etiketler["goruntuler"]}
    kayitlar = []
    for satir in kaynaklar:
        if bolum is not None and satir["bolum"] != bolum:
            continue
        kayit = {**satir, **etiket.get(satir["kimlik"], {})}
        kayit["genislik"], kayit["yukseklik"] = int(satir["genislik"]), int(satir["yukseklik"])
        kayitlar.append(kayit)
    return kayitlar
