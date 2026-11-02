"""Gaussian Blur sağlamlık deneyi — Ahmet.

apply_blur fonksiyonundan aktarıldı (src/gaussian_blur.py, commit 50d70ff); sigma
düzeyleri ve 15x15 çekirdek Ahmet'in deney ayarıdır. sigma=0 filtresiz referanstır.
"""

import math

import cv2
import numpy as np


def bulaniklastir(goruntu_bgr, sigma, cekirdek):
    goruntu = np.asarray(goruntu_bgr)
    if goruntu.dtype != np.uint8 or goruntu.ndim != 3:
        raise ValueError("uint8 BGR görüntü bekleniyor.")
    if not math.isfinite(sigma) or sigma < 0:
        raise ValueError("Sigma sonlu ve negatif olmayan bir sayı olmalı.")
    if len(cekirdek) != 2 or any(n <= 0 or n % 2 == 0 for n in cekirdek):
        raise ValueError("Çekirdek boyutları pozitif tek sayı olmalı.")
    if sigma == 0:
        return goruntu.copy()
    return cv2.GaussianBlur(goruntu, tuple(cekirdek), sigmaX=float(sigma), sigmaY=float(sigma))
