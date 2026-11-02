"""Renk maskesinden aday kutular — renk maskesi kutu değerlendirmesi (Murathan).

Kutu = sarı renkli bağlı bölge; nesne dedektörü değildir. Aynı renkteki yelek,
kova, kordon da kutu üretir (FP); aralık dışında kalan baret kutu üretmez (FN).
"""

import cv2
import numpy as np


def maskeyi_temizle(maske, cekirdek):
    if not cekirdek:
        return maske
    k = np.ones((cekirdek, cekirdek), dtype=np.uint8)
    return cv2.morphologyEx(cv2.morphologyEx(maske, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k)


def maskeden_kutular(maske, en_kucuk_piksel, cekirdek=0):
    """Bağlı bileşen kutuları [xmin, ymin, xmax, ymax] (sağ/alt hariç), büyükten küçüğe."""
    temiz = maskeyi_temizle(maske, cekirdek)
    adet, _, istatistik, _ = cv2.connectedComponentsWithStats(temiz, connectivity=8)
    kutular = []
    for i in range(1, adet):
        x, y, w, h, alan = (int(v) for v in istatistik[i])
        if alan >= en_kucuk_piksel:
            kutular.append({"kutu": [x, y, x + w, y + h], "alan_piksel": alan})
    return sorted(kutular, key=lambda k: -k["alan_piksel"])
