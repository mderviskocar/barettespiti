"""Sonuç görselleri: gerçek kutu yeşil, TP mavi, FP kırmızı, baş ROI gri, maske sarı."""

import cv2
import numpy as np

YESIL, MAVI, KIRMIZI, GRI = (0, 200, 0), (255, 120, 0), (0, 0, 255), (180, 180, 180)


def kalinlik(goruntu):
    return max(1, round(max(goruntu.shape[:2]) / 400))


def maske_bindir(goruntu, maske, renk=(0, 255, 255), oran=0.55):
    tuval = goruntu.copy()
    secili = maske > 0
    tuval[secili] = ((1 - oran) * tuval[secili] + oran * np.array(renk)).astype(np.uint8)
    return tuval


def kutulari_ciz(goruntu, adaylar, gercekler, degerlendirme, bas_roi=None):
    tuval = goruntu.copy()
    k = kalinlik(tuval)
    if bas_roi is not None:
        x1, y1, x2, y2 = bas_roi
        cv2.rectangle(tuval, (x1, y1), (x2 - 1, y2 - 1), GRI, k)
    for x1, y1, x2, y2 in gercekler:
        cv2.rectangle(tuval, (x1, y1), (x2 - 1, y2 - 1), YESIL, k + 1)
    tp = {e["tahmin"] for e in degerlendirme["eslesmeler"]}
    for i, aday in enumerate(adaylar):
        x1, y1, x2, y2 = aday["kutu"]
        cv2.rectangle(tuval, (x1, y1), (x2 - 1, y2 - 1), MAVI if i in tp else KIRMIZI, k)
    return tuval


def bgr2rgb(goruntu):
    return cv2.cvtColor(goruntu, cv2.COLOR_BGR2RGB)
