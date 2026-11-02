"""RGB ve HSV renk aralığıyla maske üretimi (cv2.inRange).

RGB yöntemi — Omar: src/rgb.py uygulamasından aktarıldı (commit ff49b67, PR #2).
HSV yöntemi — görev sahibi Derviş. Dondurulmuş RGB/HSV aralıkları Nesli'nin
G1/G2 başlangıç analizinden gelir (commit b29c635). Aralıklar ayarlar/deney_ayarlari.json
içindedir. OpenCV görüntüyü BGR okur; dönüşüm burada açıkça yapılır.
"""

import cv2
import numpy as np

DONUSUM = {"RGB": cv2.COLOR_BGR2RGB, "HSV": cv2.COLOR_BGR2HSV}


def renk_maskesi(goruntu_bgr, uzay, araliklar):
    """uzay: 'RGB' veya 'HSV'. Üç kanal da aralıktaysa piksel 255, değilse 0."""
    if uzay not in DONUSUM:
        raise ValueError(f"Bilinmeyen renk uzayı: {uzay}")
    pikseller = cv2.cvtColor(goruntu_bgr, DONUSUM[uzay])
    alt = np.array(araliklar[uzay]["alt"], dtype=np.uint8)
    ust = np.array(araliklar[uzay]["ust"], dtype=np.uint8)
    return cv2.inRange(pikseller, alt, ust)
