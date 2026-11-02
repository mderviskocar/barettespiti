"""Küçültme / ölçek deneyi — görev sahibi Efe (deney, tahmin ve yorum).

Ortak fonksiyonlar yeniden yapılanmada yazıldı; ölçek düzeyleri ve INTER_AREA ekip
planındaki önerilerdir. Yalnızca doğrusal ölçek katsayısı değişir.
"""

import cv2

YONTEM = {"INTER_AREA": cv2.INTER_AREA, "INTER_LINEAR": cv2.INTER_LINEAR,
          "INTER_NEAREST": cv2.INTER_NEAREST, "INTER_CUBIC": cv2.INTER_CUBIC}


def olcekle(goruntu, katsayi, yontem="INTER_AREA"):
    """Görüntüyü katsayıyla yeniden boyutlandırır; (yeni_görüntü, (sx, sy)) döndürür."""
    if not 0 < katsayi <= 1:
        raise ValueError("Küçültme katsayısı (0, 1] aralığında olmalı.")
    h, w = goruntu.shape[:2]
    yeni_w, yeni_h = max(1, round(w * katsayi)), max(1, round(h * katsayi))
    if katsayi == 1:
        return goruntu.copy(), (1.0, 1.0)
    yeni = cv2.resize(goruntu, (yeni_w, yeni_h), interpolation=YONTEM[yontem])
    return yeni, (yeni_w / w, yeni_h / h)


def geri_buyut(kucuk, hedef_boyut, yontem="INTER_LINEAR"):
    """Küçültülmüş görüntüyü (genişlik, yükseklik) boyutuna geri büyütür; ayrıntı geri gelmez."""
    return cv2.resize(kucuk, hedef_boyut, interpolation=YONTEM[yontem])


def kutu_olcekle(kutu, oranlar, boyut):
    """xyxy kutuyu gerçek ölçek oranıyla dönüştürür; None ise None kalır."""
    if kutu is None:
        return None
    sx, sy = oranlar
    w, h = boyut
    x1, y1, x2, y2 = kutu
    yeni = [int(x1 * sx), int(y1 * sy), int(round(x2 * sx)), int(round(y2 * sy))]
    yeni[2] = min(w, max(yeni[2], yeni[0] + 1))
    yeni[3] = min(h, max(yeni[3], yeni[1] + 1))
    return yeni
