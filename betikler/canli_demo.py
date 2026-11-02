"""Canlı demo: öğretim elemanının seçtiği görüntüde bütün yöntemi tek adımda çalıştırır.

Kullanım:  python betikler/canli_demo.py K3                 (veri setindeki görüntü)
           python betikler/canli_demo.py yol/yeni_resim.jpg  (yeni görüntü: baş ROI fareyle seçilir)

Akış (hocanın problem tanımındaki iki karar):
  1) Görüntüde baret rengi var mı?   -> RGB ve HSV maskesi, renkli alan %
  2) Baret başta mı?                 -> baş ROI ile örtüşme %, dört sınıflı karar
  + aday kutular; gerçek etiket varsa TP/FP/FN ve doğru/yanlış.
Yeni görüntüde baş ROI'yi fareyle çizip Enter'a basın; baş görünmüyorsa Esc (-> belirsiz).
Ayarlar dondurulmuştur; demo sırasında hiçbir eşik değiştirilmez.
"""
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

import cv2  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

from kaynak.analiz import analiz_et  # noqa: E402
from kaynak.gorsel import bgr2rgb, kutulari_ciz, maske_bindir  # noqa: E402
from kaynak.veri import ayarlari_oku, goruntu_oku, veri_setini_oku  # noqa: E402

SINIF_ADI = {"basta_baret": "Başta baret", "baret_var_basta_degil": "Baret var, başta değil",
             "baret_yok": "Baret yok", "belirsiz": "Belirsiz"}


def bas_roi_sec(goruntu):
    olcek = min(1.0, 1200 / goruntu.shape[1], 800 / goruntu.shape[0])
    kucuk = cv2.resize(goruntu, None, fx=olcek, fy=olcek)
    x, y, w, h = cv2.selectROI("Bas bolgesini secin (Enter) - bas gorunmuyorsa Esc", kucuk, False)
    cv2.destroyAllWindows()
    if w == 0 or h == 0:
        return None
    return [int(x / olcek), int(y / olcek), int((x + w) / olcek), int((y + h) / olcek)]


def calistir(hedef, goster=True):
    ayarlar = ayarlari_oku()
    kayitlar = {k["kimlik"]: k for k in veri_setini_oku()}
    if hedef in kayitlar:
        kayit = kayitlar[hedef]
        goruntu = goruntu_oku(kayit["dosya"])
        roi, kutular, dogru = kayit["bas_roi"], kayit["baret_kutulari"], kayit["dogru_sinif"]
    else:
        goruntu = goruntu_oku(Path(hedef).resolve())
        roi, kutular, dogru = bas_roi_sec(goruntu), None, None
    sonuclar = [analiz_et(goruntu, uzay, ayarlar, roi, kutular) for uzay in ("RGB", "HSV")]
    for s in sonuclar:
        satir = (f"{s['uzay']}: renkli alan %{s['alan_yuzde']:.2f} | baş örtüşmesi "
                 f"{'N/A' if s['ortusme_yuzde'] is None else '%' + format(s['ortusme_yuzde'], '.2f')} | "
                 f"karar: {SINIF_ADI[s['sinif']]}")
        if dogru:
            satir += f" | doğru sınıf: {SINIF_ADI[dogru]} ({'DOĞRU' if s['sinif'] == dogru else 'YANLIŞ'})"
        if s["degerlendirme"]:
            d = s["degerlendirme"]
            satir += f" | TP/FP/FN {d['tp']}/{d['fp']}/{d['fn']}"
        print(satir)
    if goster:
        fig, eksen = plt.subplots(2, 3, figsize=(16, 9))
        bos = {"eslesmeler": [], "yanlis_alarmlar": []}
        for i, s in enumerate(sonuclar):
            eksen[i, 0].imshow(bgr2rgb(goruntu)); eksen[i, 0].set_title("Orijinal")
            eksen[i, 1].imshow(bgr2rgb(maske_bindir(goruntu, s["maske"])))
            eksen[i, 1].set_title(f"{s['uzay']} maske (alan %{s['alan_yuzde']:.2f})")
            eksen[i, 2].imshow(bgr2rgb(kutulari_ciz(goruntu, s["adaylar"], kutular or [],
                                                    s["degerlendirme"] or bos, roi)))
            eksen[i, 2].set_title(f"Karar: {SINIF_ADI[s['sinif']]}")
            for e in eksen[i]:
                e.axis("off")
        fig.suptitle(f"{hedef} — yeşil: gerçek baret, mavi: TP, kırmızı: FP, gri: baş ROI")
        fig.tight_layout()
        plt.show()
    return goruntu, sonuclar


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Kullanım: python betikler/canli_demo.py K3  |  python betikler/canli_demo.py resim.jpg")
    calistir(sys.argv[1])
