"""Ölçümler: maske alanı, baş örtüşmesi, IoU, kutu düzeyi TP/FP/FN ve piksel karşılaştırması.

Kutu biçimi: [xmin, ymin, xmax, ymax], piksel, sağ/alt sınır hariç (genişlik = xmax - xmin).
Kutu kuralı (Hedef 3): IoU >= 0.50 eşleşme TP, eşleşmeyen tahmin FP, bulunamayan gerçek baret
FN; bir gerçek kutu en fazla bir kez TP sayılır. Görüntü düzeyindeki dört sınıflı doğru/yanlış
sayımı bundan ayrı tutulur.
"""

import numpy as np


def alan_ve_ortusme(maske, bas_roi):
    """Görüntüdeki renkli alan (%) ve baş ROI içindeki renkli piksel oranı (%); ROI yoksa None."""
    secili = np.asarray(maske) != 0
    alan = 100.0 * np.count_nonzero(secili) / secili.size
    if bas_roi is None:
        return alan, None
    x1, y1, x2, y2 = bas_roi
    bolge = secili[y1:y2, x1:x2]
    if bolge.size == 0:
        raise ValueError("Baş ROI görüntünün dışında.")
    return alan, 100.0 * np.count_nonzero(bolge) / bolge.size


def _kutu(kutu):
    if kutu is None or len(kutu) != 4:
        raise ValueError(f"Kutu dört koordinat içermeli: {kutu!r}")
    x1, y1, x2, y2 = (float(v) for v in kutu)
    if x2 <= x1 or y2 <= y1:
        raise ValueError(f"Kutu boyutu pozitif olmalı: {kutu!r}")
    return x1, y1, x2, y2


def kutu_alani(kutu):
    x1, y1, x2, y2 = _kutu(kutu)
    return (x2 - x1) * (y2 - y1)


def iou(a, b):
    """Kesişim / birleşim (0-1)."""
    ax1, ay1, ax2, ay2 = _kutu(a)
    bx1, by1, bx2, by2 = _kutu(b)
    kesisim = max(0.0, min(ax2, bx2) - max(ax1, bx1)) * max(0.0, min(ay2, by2) - max(ay1, by1))
    birlesim = kutu_alani(a) + kutu_alani(b) - kesisim
    return kesisim / birlesim if birlesim > 0 else 0.0


def kutulari_degerlendir(tahminler, gercekler, iou_esigi=0.5):
    """Tahmin kutularını gerçek baret kutularıyla bire bir eşleştirir.

    tahminler: [[x1,y1,x2,y2], ...] veya [{"kutu": [...], "guven": 0.8}, ...]
    Güven değeri varsa yalnızca eşleştirme sırasını belirler; başarı yüzdesi değildir.
    """
    if not 0.0 < iou_esigi <= 1.0:
        raise ValueError("IoU eşiği (0, 1] aralığında olmalı.")
    adaylar = []
    for sira, t in enumerate(tahminler):
        kutu, guven = (t["kutu"], t.get("guven")) if isinstance(t, dict) else (t, None)
        _kutu(kutu)
        adaylar.append({"sira": sira, "kutu": list(kutu), "guven": guven})
    gercek = [list(_kutu(k)) for k in gercekler]
    adaylar.sort(key=lambda a: (-(a["guven"] or 0.0), a["sira"]))
    kullanildi = [False] * len(gercek)
    eslesmeler, yanlis_alarmlar = [], []
    for aday in adaylar:
        en_iyi, en_iyi_g = 0.0, None
        for g, gkutu in enumerate(gercek):
            if not kullanildi[g]:
                deger = iou(aday["kutu"], gkutu)
                if deger > en_iyi:
                    en_iyi, en_iyi_g = deger, g
        if en_iyi_g is not None and en_iyi >= iou_esigi:
            kullanildi[en_iyi_g] = True
            eslesmeler.append({"tahmin": aday["sira"], "gercek": en_iyi_g, "iou": en_iyi})
        else:
            yanlis_alarmlar.append({"tahmin": aday["sira"], "en_iyi_iou": en_iyi})
    kacirilanlar = [g for g, k in enumerate(kullanildi) if not k]
    return {"tp": len(eslesmeler), "fp": len(yanlis_alarmlar), "fn": len(kacirilanlar),
            "eslesmeler": eslesmeler, "yanlis_alarmlar": yanlis_alarmlar,
            "kacirilan_gercekler": kacirilanlar, "iou_esigi": iou_esigi}


def piksel_karsilastir(renk_maskesi, baret_maskesi):
    """Renk maskesini piksel düzeyi gerçek baret maskesiyle karşılaştırır (aralık kalibrasyonunda kullanılır).

    kesinlik : renkli piksellerin yüzde kaçı gerçekten baret (düşükse: yanlış alarm, H1)
    duyarlilik: baret piksellerinin yüzde kaçı yakalandı (düşükse: kaçırma)
    """
    renk = np.asarray(renk_maskesi) != 0
    baret = np.asarray(baret_maskesi) != 0
    ortak = np.count_nonzero(renk & baret)
    r, b = np.count_nonzero(renk), np.count_nonzero(baret)
    return {"kesinlik_yuzde": 100.0 * ortak / r if r else None,
            "duyarlilik_yuzde": 100.0 * ortak / b if b else None,
            "renk_piksel": int(r), "baret_piksel": int(b), "ortak_piksel": int(ortak)}
