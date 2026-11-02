"""Fırçayla boyanmış maskelerden baş ROI ve baret kutularını üretir.

Kullanım:  python betikler/etiketleri_uret.py            (yalnızca fark raporu)
           python betikler/etiketleri_uret.py --yaz      (gercek_etiketler.json'u günceller)

- bas_roi        : <ID>_bas.png maskesinin en dış sınırı; boşsa null (baş görünmüyor).
- baret_kutulari : <ID>_baret.png içindeki her bağlı parça bir baret kutusu (küçük boşluklar
                   5x5 kapama ile birleştirilir; 10 pikselden küçük parçalar fırça hatası sayılır).
- dogru_sinif ve gerekce DEĞİŞMEZ: sınıf yöntemler çalıştırılmadan önce elle yazılır.
Maske dosyası olmayan görüntülere dokunulmaz.
"""
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from kaynak.olcum import iou  # noqa: E402
from kaynak.veri import maske_oku  # noqa: E402

ETIKET = KOK / "etiketler" / "gercek_etiketler.json"


def sinir_kutusu(maske):
    ys, xs = np.nonzero(maske)
    if len(xs) == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def baret_kutulari(maske):
    kapali = cv2.morphologyEx(maske, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    adet, _, ist, _ = cv2.connectedComponentsWithStats(kapali, connectivity=8)
    kutular = [[int(x), int(y), int(x + w), int(y + h)]
               for x, y, w, h, alan in ist[1:] if alan >= 10]
    return sorted(kutular)


def main(yaz):
    etiketler = json.loads(ETIKET.read_text(encoding="utf-8"))
    degisti = False
    for g in etiketler["goruntuler"]:
        bas, baret = maske_oku(g["kimlik"], "bas"), maske_oku(g["kimlik"], "baret")
        if bas is None and baret is None:
            print(f"{g['kimlik']}: maske yok, etiket aynı kaldı")
            continue
        yeni_roi = sinir_kutusu(bas) if bas is not None else g["bas_roi"]
        yeni_kutular = baret_kutulari(baret) if baret is not None else g["baret_kutulari"]
        print(f"{g['kimlik']} ({g['dogru_sinif']})")
        roi_iou = (f"IoU {iou(g['bas_roi'], yeni_roi):.2f}" if g["bas_roi"] and yeni_roi else "")
        print(f"   baş ROI : {g['bas_roi']} -> {yeni_roi} {roi_iou}")
        print(f"   baretler: {len(g['baret_kutulari'])} -> {len(yeni_kutular)}")
        for k in yeni_kutular:
            en_iyi = max((iou(k, e) for e in g["baret_kutulari"]), default=0.0)
            print(f"      {k}  (eski kutularla en iyi IoU {en_iyi:.2f})")
        if yeni_roi is None and g["dogru_sinif"] not in ("belirsiz", "baret_var_basta_degil"):
            print("   UYARI: baş boyanmamış ama sınıf baş gerektiriyor; sınıfı kontrol edin.")
        if yaz:
            g["bas_roi"], g["baret_kutulari"] = yeni_roi, yeni_kutular
            g["etiket_durumu"] = "tamam (fırça maskesi)"
            degisti = True
    if yaz and degisti:
        etiketler["kaynak"] = ("Baş ROI ve baret kutuları etiketler/maskeler altındaki fırça maskelerinden "
                               "betikler/etiketleri_uret.py ile üretildi; sınıflar elle yazıldı.")
        ETIKET.write_text(json.dumps(etiketler, ensure_ascii=False, indent=2), encoding="utf-8")
        print("gercek_etiketler.json güncellendi.")


if __name__ == "__main__":
    main("--yaz" in sys.argv)
