"""Baret tespiti — adım adım canlı demo arayüzü (ekibin kendi arayüzü).

Çalıştırma:   python arayuz/sunucu.py          -> tarayıcıda http://127.0.0.1:8765 açılır
              python arayuz/sunucu.py --port 9000 --tarayici-acma

Ek kütüphane gerekmez: sunucu Python'un http.server modülüdür, ön yüz arayuz/arayuz.html.
Bütün hesaplar kaynak/ paketindeki aynı fonksiyonlarla yapılır (deneyler ve canli_demo.py ile
aynı yol). Renk aralıkları, karar eşikleri ve kutu ayarları ayarlar/deney_ayarlari.json'dan
okunur; arayüzden değiştirilemez (dondurulmuş ayarlar).
"""

import argparse
import base64
import json
import sys
import threading
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from kaynak.analiz import analiz_et  # noqa: E402
from kaynak.bulaniklik import bulaniklastir  # noqa: E402
from kaynak.gorsel import kalinlik, kutulari_ciz, maske_bindir  # noqa: E402
from kaynak.olcek import geri_buyut, kutu_olcekle, olcekle  # noqa: E402
from kaynak.renk import DONUSUM, renk_maskesi  # noqa: E402
from kaynak.sekil import sekil_ayarlarini_oku  # noqa: E402
from kaynak.veri import ayarlari_oku, goruntu_oku, veri_setini_oku  # noqa: E402

sys.path.insert(0, str(KOK / "betikler"))
from sekil_deneyi import sekil_analizi  # noqa: E402

AYARLAR = ayarlari_oku()
SEKIL = sekil_ayarlarini_oku()
ARALIK = AYARLAR["renk_araliklari"]
KURAL = AYARLAR["karar_kurali"]
KAYITLAR = {k["kimlik"]: k for k in veri_setini_oku()}
DEMO_KLASORU = KOK / "veri" / "demo"
HTML = Path(__file__).with_name("arayuz.html")

SINIF_ADI = {"basta_baret": "Başta baret", "baret_var_basta_degil": "Baret var, başta değil",
             "baret_yok": "Baret yok", "belirsiz": "Belirsiz"}
KANAL_ADLARI = {"RGB": ("R", "G", "B"), "HSV": ("H", "S", "V")}
BOS = {"eslesmeler": [], "yanlis_alarmlar": []}

YUKLENEN = {}          # anahtar -> BGR görüntü (yalnızca bellekte, diske yazılmaz)
ONBELLEK = {}
KILIT = threading.Lock()


# ---------------------------------------------------------------- yardımcılar
def veri_url(goruntu, en=960, yakin=False, kalite=85):
    """Görüntüyü gösterim için en piksel genişliğe getirip JPEG data-URL yapar (hesap etkilenmez)."""
    h, w = goruntu.shape[:2]
    if w != en:
        oran = en / w
        yontem = cv2.INTER_NEAREST if yakin else (cv2.INTER_AREA if oran < 1 else cv2.INTER_LINEAR)
        goruntu = cv2.resize(goruntu, (en, max(1, round(h * oran))), interpolation=yontem)
    ok, tampon = cv2.imencode(".jpg", goruntu, [cv2.IMWRITE_JPEG_QUALITY, kalite])
    return "data:image/jpeg;base64," + base64.b64encode(tampon.tobytes()).decode()


def yuzde(x):
    return None if x is None else round(float(x), 2)


def kaynak_coz(kaynak, roi_oran=None, bas_yok=False):
    """İstekteki kaynağı (veri seti / demo / yüklenen) görüntü + etiketlere çevirir."""
    tur = kaynak.get("tur")
    if tur == "veri":
        k = KAYITLAR[kaynak["kimlik"]]
        return {"ad": k["kimlik"], "goruntu": goruntu_oku(k["dosya"]), "roi": k.get("bas_roi"),
                "kutular": k.get("baret_kutulari"), "dogru": k.get("dogru_sinif"),
                "etiketli": True, "kosul": k.get("kosul", "")}
    if tur == "demo":
        yol = DEMO_KLASORU / Path(kaynak["ad"]).name
        goruntu = goruntu_oku(yol)
    elif tur == "yuklenen":
        goruntu = YUKLENEN[kaynak["anahtar"]]
    else:
        raise ValueError("Bilinmeyen kaynak")
    h, w = goruntu.shape[:2]
    roi = None
    if roi_oran and not bas_yok:
        x1, y1, x2, y2 = roi_oran
        roi = [int(min(x1, x2) * w), int(min(y1, y2) * h), int(round(max(x1, x2) * w)),
               int(round(max(y1, y2) * h))]
        if roi[2] - roi[0] < 2 or roi[3] - roi[1] < 2:
            roi = None
    return {"ad": kaynak.get("ad", "Yüklenen görüntü"), "goruntu": goruntu, "roi": roi,
            "kutular": None, "dogru": None, "etiketli": False, "kosul": ""}


def virgul(x, b=2):
    return f"{x:.{b}f}".replace(".", ",")


def karar_izi(alan, ortusme, roi):
    """Dondurulmuş kuralın hangi adımda karar verdiğini sırayla döndürür."""
    adimlar = [{"soru": "Baş bölgesi (ROI) var mı?", "deger": "var" if roi else "yok",
                "sonuc": None if roi else "belirsiz"}]
    if roi is None:
        return adimlar
    esik_a = KURAL["en_az_renk_alani_yuzde"]
    adimlar.append({"soru": f"Renkli alan < %{virgul(esik_a, 1)} mi?", "deger": f"%{virgul(alan)}",
                    "sonuc": "baret_yok" if alan < esik_a else None})
    if alan < esik_a:
        return adimlar
    esik_o = KURAL["en_az_bas_ortusmesi_yuzde"]
    adimlar.append({"soru": f"Baş örtüşmesi ≥ %{virgul(esik_o, 0)} mi?", "deger": f"%{virgul(ortusme)}",
                    "sonuc": "basta_baret" if ortusme >= esik_o else "baret_var_basta_degil"})
    return adimlar


def degerlendirme_ozeti(s):
    d = s["degerlendirme"]
    return None if d is None else {"tp": d["tp"], "fp": d["fp"], "fn": d["fn"]}


def ozet(s, dogru):
    return {"alan": yuzde(s["alan_yuzde"]), "ortusme": yuzde(s["ortusme_yuzde"]),
            "sinif": s["sinif"], "sinif_adi": SINIF_ADI[s["sinif"]],
            "dogru_mu": None if dogru is None else s["sinif"] == dogru,
            "aday": len(s["adaylar"]), "kutu": degerlendirme_ozeti(s)}


# ---------------------------------------------------------------- adım adım yöntem
def kanal_adimlari(goruntu, uzay):
    pikseller = cv2.cvtColor(goruntu, DONUSUM[uzay])
    alt, ust = ARALIK[uzay]["alt"], ARALIK[uzay]["ust"]
    kanallar, birlesik = [], np.full(goruntu.shape[:2], True)
    for i, ad in enumerate(KANAL_ADLARI[uzay]):
        ch = pikseller[:, :, i]
        gecen = (ch >= alt[i]) & (ch <= ust[i])
        birlesik &= gecen
        if uzay == "HSV" and i == 0:   # ton kanalını renk tekerleği olarak göster
            dolu = np.full_like(ch, 255)
            gorsel = cv2.cvtColor(np.dstack([ch, dolu, dolu]), cv2.COLOR_HSV2BGR)
        elif uzay == "RGB":            # kanalı kendi rengiyle göster (BGR sırası: R=2, G=1, B=0)
            gorsel = np.zeros_like(goruntu)
            gorsel[:, :, 2 - i] = ch
        else:
            gorsel = ch
        kanallar.append({"ad": ad, "alt": int(alt[i]), "ust": int(ust[i]),
                         "gecen_yuzde": round(100 * float(gecen.mean()), 2),
                         "gorsel": veri_url(gorsel, 420), "maske": veri_url(gecen.astype(np.uint8) * 255, 420)})
    return kanallar, birlesik.astype(np.uint8) * 255


def roi_kesiti(goruntu, maske, roi):
    if roi is None:
        return None
    x1, y1, x2, y2 = roi
    h, w = goruntu.shape[:2]
    pay_x, pay_y = (x2 - x1) // 2, (y2 - y1) // 2
    a1, b1, a2, b2 = max(0, x1 - pay_x), max(0, y1 - pay_y), min(w, x2 + pay_x), min(h, y2 + pay_y)
    tuval = maske_bindir(goruntu, maske)
    cv2.rectangle(tuval, (x1, y1), (x2 - 1, y2 - 1), (255, 255, 255), max(1, (x2 - x1) // 60))
    kesit = tuval[b1:b2, a1:a2]
    return veri_url(kesit, 420, yakin=(a2 - a1) < 200)


def tam_analiz(g):
    goruntu, roi, kutular, dogru = g["goruntu"], g["roi"], g["kutular"], g["dogru"]
    h, w = goruntu.shape[:2]
    genel = kutulari_ciz(goruntu, [], kutular or [], BOS, roi)
    cikti = {"ad": g["ad"], "boyut": [w, h], "etiketli": g["etiketli"], "kosul": g["kosul"],
             "dogru": dogru, "dogru_adi": SINIF_ADI.get(dogru), "roi": roi,
             "gercek_kutu": len(kutular or []), "orijinal": veri_url(goruntu), "genel": veri_url(genel),
             "uzaylar": {}}
    for uzay in ("HSV", "RGB"):
        s = analiz_et(goruntu, uzay, AYARLAR, roi, kutular)
        kanallar, birlesik = kanal_adimlari(goruntu, uzay)
        if not np.array_equal(birlesik, s["maske"]):
            raise AssertionError("Kanal kanal birleşik maske cv2.inRange ile aynı olmalı")
        renkli = int(np.count_nonzero(s["maske"]))
        roi_pk = None if roi is None else (roi[2] - roi[0]) * (roi[3] - roi[1])
        roi_renkli = None if roi is None else int(np.count_nonzero(s["maske"][roi[1]:roi[3], roi[0]:roi[2]]))
        kutulu = kutulari_ciz(goruntu, s["adaylar"], kutular or [], s["degerlendirme"] or BOS, roi)
        cikti["uzaylar"][uzay] = {
            **ozet(s, dogru),
            "alt": ARALIK[uzay]["alt"], "ust": ARALIK[uzay]["ust"],
            "kanallar": kanallar,
            "maske": veri_url(s["maske"]), "bindirme": veri_url(maske_bindir(goruntu, s["maske"])),
            "renkli_piksel": renkli, "toplam_piksel": w * h,
            "roi_piksel": roi_pk, "roi_renkli": roi_renkli, "roi_kesit": roi_kesiti(goruntu, s["maske"], roi),
            "karar_izi": karar_izi(s["alan_yuzde"], s["ortusme_yuzde"], roi),
            "kutulu": veri_url(kutulu),
        }
    return cikti


# ---------------------------------------------------------------- tek değişkenli deneyler
def deney(g, tur, secili):
    goruntu, roi, kutular, dogru = g["goruntu"], g["roi"], g["kutular"], g["dogru"]
    h, w = goruntu.shape[:2]
    if tur == "bulaniklik":
        ayar = AYARLAR["bulaniklik"]
        duzeyler = ayar["sigma_degerleri"]
    else:
        ayar = AYARLAR["olcek"]
        duzeyler = ayar["katsayilar"]
    tablo, gorsel = [], None
    for d in duzeyler:
        if tur == "bulaniklik":
            islenmis, r, kts, ek = bulaniklastir(goruntu, d, ayar["cekirdek"]), roi, kutular, {}
        else:
            islenmis, oran = olcekle(goruntu, d, ayar["kucultme_yontemi"])
            boyut = (islenmis.shape[1], islenmis.shape[0])
            r = kutu_olcekle(roi, oran, boyut)
            kts = None if kutular is None else [kutu_olcekle(k, oran, boyut) for k in kutular]
            geri = geri_buyut(islenmis, (w, h), ayar["geri_buyutme_yontemi"])
            psnr = cv2.PSNR(goruntu, geri)
            ek = {"boyut": list(boyut), "psnr": None if d == 1 or not np.isfinite(psnr) else round(psnr, 2)}
        satir = {"duzey": d, **ek}
        sonuc = {}
        for uzay in ("HSV", "RGB"):
            s = analiz_et(islenmis, uzay, AYARLAR, r, kts)
            satir[uzay] = ozet(s, dogru)
            sonuc[uzay] = (s, r, kts)
        tablo.append(satir)
        if float(d) == float(secili):
            gorsel = {"islenmis": veri_url(islenmis, 960, yakin=(tur == "olcek"))}
            for uzay, (s, r2, k2) in sonuc.items():
                gorsel[uzay] = veri_url(kutulari_ciz(maske_bindir(islenmis, s["maske"]), s["adaylar"],
                                                     k2 or [], s["degerlendirme"] or BOS, r2),
                                        640, yakin=(tur == "olcek"))
    return {"tur": tur, "secili": secili, "duzeyler": duzeyler, "tablo": tablo, "gorsel": gorsel,
            "ayar": ayar, "etiketli": g["etiketli"], "dogru_adi": SINIF_ADI.get(dogru)}



# ---------------------------------------------------------------- şekil ölçütü (ek, keşif amaçlı)
def sekil_kutulari_ciz(goruntu, adaylar, gercekler, degerlendirme, roi, elenenler=()):
    tuval = kutulari_ciz(goruntu, [{"kutu": a["kutu"]} for a in adaylar], gercekler or [], degerlendirme or BOS, roi)
    k = kalinlik(tuval)
    for a in elenenler:
        x1, y1, x2, y2 = a["kutu"]
        cv2.rectangle(tuval, (x1, y1), (x2 - 1, y2 - 1), (150, 150, 150), max(1, k - 1))
        cv2.line(tuval, (x1, y1), (x2 - 1, y2 - 1), (150, 150, 150), max(1, k - 1))
    return tuval


def aday_kesiti(goruntu, maske, a):
    x1, y1, x2, y2 = a["kutu"]
    h, w = goruntu.shape[:2]
    px, py = max(6, (x2 - x1) // 3), max(6, (y2 - y1) // 3)
    b1, c1, b2, c2 = max(0, x1 - px), max(0, y1 - py), min(w, x2 + px), min(h, y2 + py)
    tuval = maske_bindir(goruntu, maske, oran=0.35)
    kal = max(1, round(max(x2 - x1, y2 - y1) / 70))
    cv2.rectangle(tuval, (x1, y1), (x2 - 1, y2 - 1), (255, 255, 255), kal)
    cv2.drawContours(tuval, [a["zarf"]], -1, (138, 122, 10), kal)
    cv2.drawContours(tuval, [a["kontur"]], -1, (30, 190, 245), kal)
    kesit = tuval[c1:c2, b1:b2]
    return veri_url(kesit, 240, yakin=(b2 - b1) < 240)


def sekil_tek(g, uzay):
    goruntu, roi, kutular, dogru = g["goruntu"], g["roi"], g["kutular"], g["dogru"]
    once, sonra, adaylar = sekil_analizi(goruntu, uzay, AYARLAR, SEKIL, roi, kutular)
    ham = renk_maskesi(goruntu, uzay, ARALIK)
    elenen = [a for a in adaylar if not a["gecti"]]
    nedenler = {}
    for a in elenen:
        for n in a["nedenler"]:
            nedenler[n] = nedenler.get(n, 0) + 1
    tp_kume = {e["tahmin"] for e in (once["degerlendirme"] or BOS)["eslesmeler"]}
    once_kutular = [a["kutu"] for a in once["adaylar"]]

    def tp_mi(a):
        return any(once_kutular[i] == a["kutu"] for i in tp_kume)
    ornekler = []
    secim = sorted(adaylar, key=lambda a: (not tp_mi(a), -a["alan_piksel"]))[:6]
    for a in secim:
        ornekler.append({"gorsel": aday_kesiti(goruntu, ham, a), "alan": a["alan_piksel"], "tp": tp_mi(a),
                         "en_boy": round(a["en_boy"], 2), "doluluk": round(a["doluluk"], 2),
                         "disbukeylik": round(a["disbukeylik"], 2), "gecti": a["gecti"], "nedenler": a["nedenler"]})
    so = {"alan": yuzde(sonra["alan_yuzde"]), "ortusme": yuzde(sonra["ortusme_yuzde"]), "sinif": sonra["sinif"],
          "sinif_adi": SINIF_ADI[sonra["sinif"]], "dogru_mu": None if dogru is None else sonra["sinif"] == dogru,
          "aday": len(sonra["adaylar"]), "kutu": degerlendirme_ozeti(sonra)}
    return {
        "uzay": uzay, "etiketli": g["etiketli"], "dogru_adi": SINIF_ADI.get(dogru),
        "once": ozet(once, dogru), "sonra": so, "elenen": len(elenen), "nedenler": nedenler, "ornekler": ornekler,
        "once_gorsel": veri_url(kutulari_ciz(goruntu, once["adaylar"], kutular or [], once["degerlendirme"] or BOS, roi)),
        "sonra_gorsel": veri_url(sekil_kutulari_ciz(goruntu, sonra["adaylar"], kutular, sonra["degerlendirme"], roi, elenen)),
        "maske_once": veri_url(maske_bindir(goruntu, ham, renk=(255, 0, 255))),
        "maske_sonra": veri_url(maske_bindir(goruntu, sonra["maske"], renk=(255, 0, 255))),
    }


def sekil_toplam():
    if "sekil_toplam" in ONBELLEK:
        return ONBELLEK["sekil_toplam"]
    toplam = {}
    for k in KAYITLAR.values():
        if k["bolum"] != "kontrol":
            continue
        goruntu = goruntu_oku(k["dosya"])
        for uzay in ("HSV", "RGB"):
            once, sonra, _ = sekil_analizi(goruntu, uzay, AYARLAR, SEKIL, k["bas_roi"], k["baret_kutulari"])
            t = toplam.setdefault(uzay, {"tp": [0, 0], "fp": [0, 0], "fn": [0, 0], "dogru": [0, 0]})
            for i, s in enumerate((once, sonra)):
                for a in ("tp", "fp", "fn"):
                    t[a][i] += s["degerlendirme"][a]
                t["dogru"][i] += s["sinif"] == k["dogru_sinif"]
    ONBELLEK["sekil_toplam"] = toplam
    return toplam


def sekil(g, uzay):
    return {**sekil_tek(g, uzay), "toplam": sekil_toplam(), "esik": SEKIL}


def piksel(g, fx, fy):
    goruntu = g["goruntu"]
    h, w = goruntu.shape[:2]
    x, y = min(w - 1, max(0, int(fx * w))), min(h - 1, max(0, int(fy * h)))
    b, gr, r = (int(v) for v in goruntu[y, x])
    hsv = [int(v) for v in cv2.cvtColor(goruntu[y:y + 1, x:x + 1], cv2.COLOR_BGR2HSV)[0, 0]]
    rgb = [r, gr, b]

    def icinde(uzay, deger):
        return [ARALIK[uzay]["alt"][i] <= deger[i] <= ARALIK[uzay]["ust"][i] for i in range(3)]
    return {"x": x, "y": y, "RGB": rgb, "HSV": hsv, "RGB_icinde": icinde("RGB", rgb),
            "HSV_icinde": icinde("HSV", hsv), "renk": "#%02x%02x%02x" % (r, gr, b)}


def liste():
    if "liste" in ONBELLEK:
        return ONBELLEK["liste"]
    ogeler = []
    for k in KAYITLAR.values():
        ogeler.append({"tur": "veri", "kimlik": k["kimlik"], "ad": k["kimlik"], "bolum": k["bolum"],
                       "dogru_adi": SINIF_ADI.get(k.get("dogru_sinif")), "kosul": k.get("kosul", ""),
                       "kucuk": veri_url(goruntu_oku(k["dosya"]), 220)})
    for yol in sorted(DEMO_KLASORU.glob("*")):
        if yol.suffix.lower() in (".jpg", ".jpeg", ".png"):
            ogeler.append({"tur": "demo", "ad": yol.name, "bolum": "demo", "dogru_adi": None,
                           "kosul": "Etiketsiz yedek demo görüntüsü (veri/demo)", "kucuk": veri_url(goruntu_oku(yol), 220)})
    ONBELLEK["liste"] = {"ogeler": ogeler, "ayarlar": {
        "RGB": ARALIK["RGB"], "HSV": ARALIK["HSV"], "kural": KURAL,
        "kutu": AYARLAR["kutu_degerlendirme"], "bulaniklik": AYARLAR["bulaniklik"], "olcek": AYARLAR["olcek"]}}
    return ONBELLEK["liste"]


# ---------------------------------------------------------------- HTTP
class Isleyici(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def gonder(self, kod, govde, tip="application/json; charset=utf-8"):
        if isinstance(govde, (dict, list)):
            govde = json.dumps(govde, ensure_ascii=False).encode("utf-8")
        self.send_response(kod)
        self.send_header("Content-Type", tip)
        self.send_header("Content-Length", str(len(govde)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(govde)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self.gonder(200, HTML.read_bytes(), "text/html; charset=utf-8")
        if self.path == "/api/liste":
            return self.gonder(200, liste())
        self.gonder(404, {"hata": "bulunamadı"})

    def do_POST(self):
        try:
            uzunluk = int(self.headers.get("Content-Length", 0))
            istek = json.loads(self.rfile.read(uzunluk) or b"{}")
            if self.path == "/api/yukle":
                veri = istek["veri"].split(",", 1)[-1]
                goruntu = cv2.imdecode(np.frombuffer(base64.b64decode(veri), np.uint8), cv2.IMREAD_COLOR)
                if goruntu is None:
                    return self.gonder(400, {"hata": "Görüntü okunamadı"})
                anahtar = uuid.uuid4().hex
                YUKLENEN[anahtar] = goruntu
                return self.gonder(200, {"anahtar": anahtar, "ad": istek.get("ad", "Yüklenen görüntü"),
                                         "onizleme": veri_url(goruntu)})
            g = kaynak_coz(istek["kaynak"], istek.get("roi"), istek.get("bas_yok", False))
            anahtar = json.dumps([self.path, istek], sort_keys=True, ensure_ascii=False)
            if self.path == "/api/piksel":
                return self.gonder(200, piksel(g, istek["fx"], istek["fy"]))
            with KILIT:
                if anahtar not in ONBELLEK:
                    if self.path == "/api/analiz":
                        ONBELLEK[anahtar] = tam_analiz(g)
                    elif self.path == "/api/sekil":
                        ONBELLEK[anahtar] = sekil(g, istek.get("uzay", "HSV"))
                    elif self.path == "/api/deney":
                        ONBELLEK[anahtar] = deney(g, istek["tur"], istek["secili"])
                    else:
                        return self.gonder(404, {"hata": "bulunamadı"})
                sonuc = ONBELLEK[anahtar]
            self.gonder(200, sonuc)
        except Exception as hata:  # arayüz hatayı kullanıcıya gösterir
            self.gonder(500, {"hata": f"{type(hata).__name__}: {hata}"})


def main():
    p = argparse.ArgumentParser(description="Baret tespiti adım adım demo arayüzü")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--tarayici-acma", action="store_true")
    a = p.parse_args()
    sunucu = ThreadingHTTPServer(("127.0.0.1", a.port), Isleyici)
    adres = f"http://127.0.0.1:{a.port}"
    print(f"Arayüz hazır: {adres}   (durdurmak için Ctrl+C)")
    if not a.tarayici_acma:
        threading.Timer(0.8, lambda: webbrowser.open(adres)).start()
    try:
        sunucu.serve_forever()
    except KeyboardInterrupt:
        print("\nKapatıldı.")


if __name__ == "__main__":
    main()
