"""Şekil ölçütü (ek, keşif amaçlı) — renk adaylarını şekle göre süzme, model eğitimi yok.

Hata analizinde (slayt 4) önerilen "sonraki kontrol": renk maskesi yalnızca renge baktığı için
sarı makine parçası, direk ya da yelek de aday kutu üretir. Bu modül her aday bileşen için üç
geometrik ölçü hesaplar ve baret kubbesine benzemeyenleri eler:

  en-boy oranı   = genişlik / yükseklik          (ince dikey/yatay çubukları eler)
  doluluk        = bileşen pikseli / kutu alanı   (kutunun içini az dolduran çerçeve, çizgi)
  dışbükeylik    = bileşen pikseli / dışbükey zarf alanı (girintili, dağınık lekeler)

Eşikler ayarlar/sekil_olcutu.json dosyasındadır. Bu ölçüt ana yöntemin parçası değildir;
K1-K4 sonuçları bilindikten sonra eklendiği için yalnızca keşif amaçlı raporlanır ve ana sonuç
tablosu değişmez.
"""

import json

import cv2
import numpy as np

from kaynak.kutular import maskeyi_temizle
from kaynak.veri import KOK


def sekil_ayarlarini_oku():
    return json.loads((KOK / "ayarlar" / "sekil_olcutu.json").read_text(encoding="utf-8"))


def aday_olculeri(maske, en_kucuk_piksel, cekirdek, ayar):
    """Renk maskesindeki her aday bileşen için kutu, şekil ölçüleri ve süzgeç kararı.

    Bileşenler maskeden_kutular ile aynı yoldan çıkar (aynı temizleme, aynı en küçük piksel);
    büyükten küçüğe sıralanır. Dönüş: (adaylar, etiket_haritasi)."""
    temiz = maskeyi_temizle(maske, cekirdek)
    adet, etiket, istatistik, _ = cv2.connectedComponentsWithStats(temiz, connectivity=8)
    alt_eb, ust_eb = ayar["en_boy_orani"]
    adaylar = []
    for i in range(1, adet):
        x, y, w, h, alan = (int(v) for v in istatistik[i])
        if alan < en_kucuk_piksel:
            continue
        bilesen = (etiket[y:y + h, x:x + w] == i).astype(np.uint8)
        konturlar, _ = cv2.findContours(bilesen, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        en_buyuk = max(konturlar, key=cv2.contourArea)
        zarf = cv2.convexHull(en_buyuk)
        zarf_alani = cv2.contourArea(zarf)
        en_boy = w / h
        doluluk = alan / (w * h)
        disbukeylik = min(1.0, alan / zarf_alani) if zarf_alani > 0 else 1.0
        nedenler = []
        if not alt_eb <= en_boy <= ust_eb:
            nedenler.append("en-boy")
        if doluluk < ayar["en_az_doluluk"]:
            nedenler.append("doluluk")
        if disbukeylik < ayar["en_az_disbukeylik"]:
            nedenler.append("dışbükeylik")
        adaylar.append({"etiket": i, "kutu": [x, y, x + w, y + h], "alan_piksel": alan,
                        "en_boy": en_boy, "doluluk": doluluk, "disbukeylik": disbukeylik,
                        "gecti": not nedenler, "nedenler": nedenler,
                        "kontur": en_buyuk + [x, y], "zarf": zarf + [x, y]})
    adaylar.sort(key=lambda a: -a["alan_piksel"])
    return adaylar, etiket


def suzulmus_maske(etiket, adaylar):
    """Yalnızca şekil ölçütünü geçen bileşenlerden oluşan maske (0/255)."""
    gecen = [a["etiket"] for a in adaylar if a["gecti"]]
    return np.isin(etiket, gecen).astype(np.uint8) * 255 if gecen else np.zeros(etiket.shape, np.uint8)
