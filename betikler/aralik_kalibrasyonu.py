"""Renk aralığı ve karar eşiklerini YALNIZCA geliştirme görüntülerinde (G1, G2) ölçer.

Kullanım:  python betikler/aralik_kalibrasyonu.py
Fırçayla boyanmış G1 baret maskesi ve G1/G2 baş ROI'leri gerekir. Kontrol görüntüleri
(K1-K4) hiç okunmaz. Çıktı:
  1) G1 baret piksellerinin RGB ve HSV dağılımı (yüzdelik 2-98) -> aralık önerisi
  2) Mevcut ayardaki aralıkla G1/G2 ölçümü: baret piksel yakalama, yanlış renkli alan,
     baş örtüşmesi ve kuralın sınıfı.
Aralığı seçen üye (RGB: Omar, HSV: Derviş) ayarlar/deney_ayarlari.json dosyasına yazar ve
"dondurulmus": true yapar; ancak ondan sonra betikler/deneyleri_calistir.py çalışır.
"""
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from kaynak.olcum import alan_ve_ortusme, piksel_karsilastir  # noqa: E402
from kaynak.renk import renk_maskesi  # noqa: E402
from kaynak.siniflandirma import sinifla  # noqa: E402
from kaynak.veri import ayarlari_oku, goruntu_oku, maske_oku, veri_setini_oku  # noqa: E402

ayarlar = ayarlari_oku()
gelistirme = veri_setini_oku("gelistirme")
print("Yalnızca geliştirme görüntüleri:", [k["kimlik"] for k in gelistirme])

for k in gelistirme:
    baret = maske_oku(k["kimlik"], "baret")
    if baret is None or not baret.any():
        continue
    g = goruntu_oku(k["dosya"])
    secili = baret > 0
    for uzay, donusum in (("RGB", cv2.COLOR_BGR2RGB), ("HSV", cv2.COLOR_BGR2HSV)):
        p = cv2.cvtColor(g, donusum)[secili]
        alt, ust = np.percentile(p, 2, axis=0).astype(int), np.percentile(p, 98, axis=0).astype(int)
        print(f"{k['kimlik']} baret pikselleri ({secili.sum()} px) {uzay} yüzdelik 2-98: alt {alt.tolist()} üst {ust.tolist()}")

print("\nMevcut aralık ve kuralla geliştirme ölçümü:")
for k in gelistirme:
    g = goruntu_oku(k["dosya"])
    baret = maske_oku(k["kimlik"], "baret")
    for uzay in ("RGB", "HSV"):
        m = renk_maskesi(g, uzay, ayarlar["renk_araliklari"])
        alan, ortusme = alan_ve_ortusme(m, k["bas_roi"])
        sinif = sinifla(alan, ortusme, k["bas_roi"], ayarlar["karar_kurali"])
        satir = (f"  {k['kimlik']} {uzay}: alan %{alan:.2f}, baş örtüşmesi "
                 f"{'N/A' if ortusme is None else '%' + format(ortusme, '.2f')}, sınıf {sinif} (doğru: {k['dogru_sinif']})")
        if baret is not None:
            pk = piksel_karsilastir(m, baret)
            satir += (f", baret yakalama %{pk['duyarlilik_yuzde'] or 0:.1f}, "
                      f"renkli piksellerin baret olanı %{pk['kesinlik_yuzde'] or 0:.1f}")
        print(satir)
print("\nKontrol görüntüleri bu betikte kullanılmaz; aralık dondurulduktan sonra değiştirilmez.")
