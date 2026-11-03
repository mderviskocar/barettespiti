"""Elle etiketleme: baş bölgesi (ROI) ve gerçek baret kutularını fareyle dikdörtgen olarak çizer.

Yönerge 5b: "başta kararı için baş bölgesini elle işaretleyin"; 6b: "gerçek baret kutularını elle çizin".

Kullanım:  python betikler/kutu_ciz.py G1 G2 K1 K3 K4      (seçili görüntüler)
           python betikler/kutu_ciz.py                     (altı görüntünün hepsi)

Her görüntü için iki pencere açılır:
  1) BAŞ    : hedef kişinin başını (baret takılıysa bareti DAHİL) dikdörtgenle çizin, Enter.
              Baş görünmüyorsa çizmeden 'c' tuşuna basın (bas_roi = null, uydurma kutu yok).
  2) BARET  : her bareti ayrı dikdörtgenle çizip Enter'a basın; hepsi bitince Esc.
              Görüntüde baret yoksa doğrudan Esc.
Kutular etiketler/gercek_etiketler.json dosyasına [xmin, ymin, xmax, ymax] (sağ/alt hariç)
olarak yazılır; kontrol görseli etiketler/onizlemeler/<ID>.png olarak kaydedilir.
Doğru sınıf ve gerekçe bu araçla değişmez; onlar yöntemlerden önce elle yazılır.
"""
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

import cv2  # noqa: E402

from kaynak.veri import goruntu_oku, veri_setini_oku  # noqa: E402

ETIKET = KOK / "etiketler" / "gercek_etiketler.json"
ONIZLEME = KOK / "etiketler" / "onizlemeler"
EKRAN = (1400, 850)


def olcekli(goruntu):
    h, w = goruntu.shape[:2]
    o = min(1.0, EKRAN[0] / w, EKRAN[1] / h)
    return (cv2.resize(goruntu, None, fx=o, fy=o, interpolation=cv2.INTER_AREA) if o < 1 else goruntu.copy()), o


def geri_cevir(rect, o, w, h):
    x, y, rw, rh = rect
    x1, y1 = int(round(x / o)), int(round(y / o))
    x2, y2 = int(round((x + rw) / o)), int(round((y + rh) / o))
    return [max(0, x1), max(0, y1), min(w, x2), min(h, y2)]


def etiketle(kayit):
    goruntu = goruntu_oku(kayit["dosya"])
    h, w = goruntu.shape[:2]
    kucuk, o = olcekli(goruntu)
    baslik = f"{kayit['kimlik']} BAS: basi ciz + Enter | bas gorunmuyorsa c"
    rect = cv2.selectROI(baslik, kucuk, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow(baslik)
    bas = geri_cevir(rect, o, w, h) if rect[2] > 0 and rect[3] > 0 else None
    goster = kucuk.copy()
    if bas:
        cv2.rectangle(goster, (int(bas[0] * o), int(bas[1] * o)), (int(bas[2] * o), int(bas[3] * o)), (180, 180, 180), 2)
    baslik = f"{kayit['kimlik']} BARET: her bareti ciz + Enter | bitince Esc"
    rects = cv2.selectROIs(baslik, goster, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow(baslik)
    baretler = []
    for r in (rects if len(rects) else []):
        kutu = geri_cevir(r, o, w, h)
        if r[2] > 0 and r[3] > 0 and kutu not in baretler:   # Enter'a iki kez basılırsa aynı kutu tekrar eklenmez
            baretler.append(kutu)
    onizleme = goruntu.copy()
    k = max(2, round(max(h, w) / 500))
    if bas:
        cv2.rectangle(onizleme, (bas[0], bas[1]), (bas[2] - 1, bas[3] - 1), (180, 180, 180), k)
    for b in baretler:
        cv2.rectangle(onizleme, (b[0], b[1]), (b[2] - 1, b[3] - 1), (0, 200, 0), k)
    ONIZLEME.mkdir(parents=True, exist_ok=True)
    ok, veri = cv2.imencode(".png", onizleme)
    (ONIZLEME / f"{kayit['kimlik']}.png").write_bytes(veri.tobytes())
    return bas, baretler


def main(secili):
    etiketler = json.loads(ETIKET.read_text(encoding="utf-8"))
    sira = {g["kimlik"]: g for g in etiketler["goruntuler"]}
    for kayit in veri_setini_oku():
        if secili and kayit["kimlik"] not in secili:
            continue
        bas, baretler = etiketle(kayit)
        g = sira[kayit["kimlik"]]
        g["bas_roi"], g["baret_kutulari"] = bas, baretler
        g["etiket_durumu"] = "tamam (elle çizilmiş kutu)"
        print(f"{kayit['kimlik']} ({g['dogru_sinif']}): baş {bas} | baret {baretler}")
        if bas is None and g["dogru_sinif"] in ("basta_baret", "baret_yok"):
            print("   UYARI: baş çizilmedi ama sınıf baş gerektiriyor; sınıfı veya çizimi kontrol edin.")
        ETIKET.write_text(json.dumps(etiketler, ensure_ascii=False, indent=2), encoding="utf-8")
    cv2.destroyAllWindows()
    print("Kaydedildi:", ETIKET.relative_to(KOK), "| önizlemeler:", ONIZLEME.relative_to(KOK))


if __name__ == "__main__":
    main(set(sys.argv[1:]))
