"""Bütün deneyleri dondurulmuş ayarlarla çalıştırır ve sonuçları sonuclar/ altına yazar.

Kullanım:  python betikler/deneyleri_calistir.py

1) Temel deney     : 6 görüntü × RGB/HSV -> maske, alan, baş örtüşmesi, dört sınıf, TP/FP/FN
2) Bulanıklık (H4) : K1-K4 × sigma × RGB/HSV (tek değişken: sigma)
3) Ölçek (H4)      : K1-K4 × katsayı × RGB/HSV (tek değişken: ölçek) + geri büyütme (S5)
4) Hocanın sonuç tablosu: sonuclar/sonuc_tablosu.csv ve .md

Ayarlar ayarlar/deney_ayarlari.json içinde sabittir; bu betik hiçbir eşiği değiştirmez.
"""
import csv
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

import cv2  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from kaynak.analiz import analiz_et  # noqa: E402
from kaynak.bulaniklik import bulaniklastir  # noqa: E402
from kaynak.gorsel import bgr2rgb, kutulari_ciz, maske_bindir  # noqa: E402
from kaynak.olcek import geri_buyut, kutu_olcekle, olcekle  # noqa: E402
from kaynak.veri import ayarlari_oku, goruntu_oku, maske_oku, veri_setini_oku  # noqa: E402

SONUC = KOK / "sonuclar"
UZAYLAR = ("RGB", "HSV")
SINIF_ADI = {"basta_baret": "Başta baret", "baret_var_basta_degil": "Baret var, başta değil",
             "baret_yok": "Baret yok", "belirsiz": "Belirsiz"}


def yuzde(deger):
    return "N/A" if deger is None else f"{deger:.2f}"


def png_yaz(yol, goruntu):
    yol.parent.mkdir(parents=True, exist_ok=True)
    ok, veri = cv2.imencode(".png", goruntu)
    yol.write_bytes(veri.tobytes())


def csv_yaz(yol, satirlar):
    yol.parent.mkdir(parents=True, exist_ok=True)
    with yol.open("w", encoding="utf-8", newline="") as dosya:
        yazici = csv.DictWriter(dosya, fieldnames=list(satirlar[0]))
        yazici.writeheader()
        yazici.writerows(satirlar)


def satir(kayit, sonuc, **ek):
    d = sonuc["degerlendirme"]
    p = sonuc["piksel"] or {}
    return {
        "kimlik": kayit["kimlik"], "bolum": kayit["bolum"], "kosul": kayit["kosul"], **ek,
        "yontem": sonuc["uzay"], "dogru_sinif": kayit["dogru_sinif"], "kural_sinifi": sonuc["sinif"],
        "dogru_mu": "evet" if sonuc["sinif"] == kayit["dogru_sinif"] else "hayir",
        "maske_alani_yuzde": yuzde(sonuc["alan_yuzde"]), "bas_ortusmesi_yuzde": yuzde(sonuc["ortusme_yuzde"]),
        "aday_kutu": len(sonuc["adaylar"]), "tp": d["tp"], "fp": d["fp"], "fn": d["fn"],
        "eslesen_iou": " ".join(f"{e['iou']:.2f}" for e in d["eslesmeler"]) or "-",
        "piksel_kesinlik_yuzde": yuzde(p.get("kesinlik_yuzde")),
        "piksel_duyarlilik_yuzde": yuzde(p.get("duyarlilik_yuzde")),
    }


def temel_deney(kayitlar, ayarlar):
    satirlar = []
    for kayit in kayitlar:
        goruntu = goruntu_oku(kayit["dosya"])
        for uzay in UZAYLAR:
            sonuc = analiz_et(goruntu, uzay, ayarlar, kayit["bas_roi"], kayit["baret_kutulari"],
                              maske_oku(kayit["kimlik"], "baret"))
            satirlar.append(satir(kayit, sonuc))
            ad = f"{kayit['kimlik']}_{uzay.lower()}.png"
            png_yaz(SONUC / "maskeler" / ad, sonuc["maske"])
            png_yaz(SONUC / "kutular" / ad, kutulari_ciz(goruntu, sonuc["adaylar"], kayit["baret_kutulari"],
                                                         sonuc["degerlendirme"], kayit["bas_roi"]))
    csv_yaz(SONUC / "temel_sonuclar.csv", satirlar)
    return satirlar


def bulaniklik_deneyi(kayitlar, ayarlar):
    b = ayarlar["bulaniklik"]
    satirlar = []
    for kayit in kayitlar:
        goruntu = goruntu_oku(kayit["dosya"])
        paneller = []
        for sigma in b["sigma_degerleri"]:
            bulanik = bulaniklastir(goruntu, sigma, b["cekirdek"])
            for uzay in UZAYLAR:
                sonuc = analiz_et(bulanik, uzay, ayarlar, kayit["bas_roi"], kayit["baret_kutulari"],
                                  maske_oku(kayit["kimlik"], "baret"))
                satirlar.append(satir(kayit, sonuc, sigma=sigma))
                if uzay == "HSV":
                    paneller.append((sigma, bulanik, sonuc["maske"]))
        fig, eksen = plt.subplots(2, len(paneller), figsize=(4 * len(paneller), 6))
        for i, (sigma, bulanik, maske) in enumerate(paneller):
            eksen[0, i].imshow(bgr2rgb(bulanik)); eksen[0, i].set_title(f"σ = {sigma}")
            eksen[1, i].imshow(maske, cmap="gray"); eksen[1, i].set_title(f"HSV maske, σ = {sigma}")
            for e in eksen[:, i]:
                e.axis("off")
        fig.suptitle(f"{kayit['kimlik']} — Gaussian Blur (çekirdek {b['cekirdek'][0]}×{b['cekirdek'][1]})")
        fig.tight_layout(); fig.savefig(SONUC / "bulaniklik" / f"{kayit['kimlik']}_sigma.png", dpi=90); plt.close(fig)
    csv_yaz(SONUC / "bulaniklik" / "bulaniklik_sonuclari.csv", satirlar)
    egri_ciz(satirlar, "sigma", "σ (Gaussian sigma)", SONUC / "bulaniklik" / "sigma_maske_alani.png")
    return satirlar


def olcek_deneyi(kayitlar, ayarlar):
    o = ayarlar["olcek"]
    satirlar, geri = [], []
    for kayit in kayitlar:
        goruntu = goruntu_oku(kayit["dosya"])
        h, w = goruntu.shape[:2]
        for katsayi in o["katsayilar"]:
            kucuk, oran = olcekle(goruntu, katsayi, o["kucultme_yontemi"])
            boyut = (kucuk.shape[1], kucuk.shape[0])
            roi = kutu_olcekle(kayit["bas_roi"], oran, boyut)
            kutular = [kutu_olcekle(k, oran, boyut) for k in kayit["baret_kutulari"]]
            baret = maske_oku(kayit["kimlik"], "baret")
            if baret is not None:
                baret = cv2.resize(baret, boyut, interpolation=cv2.INTER_NEAREST)
            en_kucuk = min(((k[2] - k[0]) * (k[3] - k[1]) for k in kutular), default=None)
            for uzay in UZAYLAR:
                sonuc = analiz_et(kucuk, uzay, ayarlar, roi, kutular, baret)
                satirlar.append(satir(kayit, sonuc, olcek=katsayi, boyut=f"{boyut[0]}x{boyut[1]}",
                                      en_kucuk_baret_piksel=en_kucuk if en_kucuk is not None else "N/A"))
            if katsayi != 1:
                buyuk = geri_buyut(kucuk, (w, h), o["geri_buyutme_yontemi"])
                fark = float(np.mean(np.abs(goruntu.astype(np.int16) - buyuk.astype(np.int16))))
                psnr = float(cv2.PSNR(goruntu, buyuk))
                geri.append({"kimlik": kayit["kimlik"], "olcek": katsayi,
                             "ortalama_mutlak_fark": f"{fark:.2f}", "psnr_db": f"{psnr:.2f}"})
                if katsayi == min(o["katsayilar"]) and kayit["baret_kutulari"]:
                    x1, y1, x2, y2 = kayit["baret_kutulari"][-1]
                    pay = max(20, (x2 - x1))
                    kes = (slice(max(0, y1 - pay), y2 + pay), slice(max(0, x1 - pay), x2 + pay))
                    fig, eksen = plt.subplots(1, 2, figsize=(8, 4))
                    eksen[0].imshow(bgr2rgb(goruntu[kes])); eksen[0].set_title("Orijinal")
                    eksen[1].imshow(bgr2rgb(buyuk[kes])); eksen[1].set_title(f"×{katsayi} küçült → geri büyüt")
                    for e in eksen:
                        e.axis("off")
                    fig.suptitle(f"{kayit['kimlik']}: geri büyütme ayrıntıyı geri getirmez (PSNR {psnr:.1f} dB)")
                    fig.tight_layout(); fig.savefig(SONUC / "olcek" / f"{kayit['kimlik']}_geri_buyutme.png", dpi=110)
                    plt.close(fig)
    csv_yaz(SONUC / "olcek" / "olcek_sonuclari.csv", satirlar)
    csv_yaz(SONUC / "olcek" / "geri_buyutme.csv", geri)
    egri_ciz(satirlar, "olcek", "Ölçek katsayısı", SONUC / "olcek" / "olcek_maske_alani.png", ters=True)
    return satirlar


def egri_ciz(satirlar, anahtar, etiket, yol, ters=False):
    fig, eksen = plt.subplots(1, 2, figsize=(12, 4.5), sharey=False)
    for i, uzay in enumerate(UZAYLAR):
        for kimlik in sorted({s["kimlik"] for s in satirlar}):
            veri = [(float(s[anahtar]), float(s["maske_alani_yuzde"])) for s in satirlar
                    if s["kimlik"] == kimlik and s["yontem"] == uzay]
            eksen[i].plot(*zip(*veri), marker="o", label=kimlik)
        eksen[i].set_title(f"{uzay} maske alanı"); eksen[i].set_xlabel(etiket); eksen[i].set_ylabel("Maske alanı (%)")
        eksen[i].grid(alpha=0.3); eksen[i].legend()
        if ters:
            eksen[i].invert_xaxis()
    fig.tight_layout(); fig.savefig(yol, dpi=110); plt.close(fig)


def sonuc_tablosu(temel):
    tablo = []
    for s in temel:
        if s["bolum"] != "kontrol":
            continue
        tablo.append({"Görüntü": s["kimlik"], "Koşul": s["kosul"], "Doğru sınıf": SINIF_ADI[s["dogru_sinif"]],
                      "Yöntem": s["yontem"], "Kuralın sınıfı": SINIF_ADI[s["kural_sinifi"]],
                      "Doğru mu": "Evet" if s["dogru_mu"] == "evet" else "Hayır",
                      "Maske alanı (%)": s["maske_alani_yuzde"], "Baş örtüşmesi (%)": s["bas_ortusmesi_yuzde"],
                      "TP / FP / FN": f"{s['tp']} / {s['fp']} / {s['fn']}"})
    csv_yaz(SONUC / "sonuc_tablosu.csv", tablo)
    basliklar = list(tablo[0])
    md = ["| " + " | ".join(basliklar) + " |", "|" + "---|" * len(basliklar)]
    md += ["| " + " | ".join(str(t[b]) for b in basliklar) + " |" for t in tablo]
    md.append("")
    md.append("**Özet (K1–K4).** Görüntü düzeyi dört sınıflı karar ve kutu düzeyi sayım ayrı tutulur:")
    md.append("")
    md.append("| Yöntem | Sınıf doğru / toplam | TP | FP | FN |")
    md.append("|---|---|---|---|---|")
    for uzay in UZAYLAR:
        k = [s for s in temel if s["bolum"] == "kontrol" and s["yontem"] == uzay]
        md.append(f"| {uzay} | {sum(s['dogru_mu'] == 'evet' for s in k)} / {len(k)} | {sum(s['tp'] for s in k)} | "
                  f"{sum(s['fp'] for s in k)} | {sum(s['fn'] for s in k)} |")
    md.append("")
    md.append("TP/FP/FN: elle çizilmiş baret kutularıyla IoU ≥ 0.50 bire bir eşleştirme (renk maskesi kutuları; hazır dedektör yok).")
    (SONUC / "sonuc_tablosu.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return tablo


def ozet(temel, bulanik, olcek):
    ozet = {}
    for uzay in UZAYLAR:
        k = [s for s in temel if s["bolum"] == "kontrol" and s["yontem"] == uzay]
        ozet[uzay] = {"sinif_dogru": sum(s["dogru_mu"] == "evet" for s in k), "sinif_toplam": len(k),
                      "tp": sum(s["tp"] for s in k), "fp": sum(s["fp"] for s in k), "fn": sum(s["fn"] for s in k)}
    ozet["bulaniklik_sinif_degisimi"] = degisimler(bulanik, "sigma")
    ozet["olcek_sinif_degisimi"] = degisimler(olcek, "olcek")
    (SONUC / "ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=2), encoding="utf-8")
    return ozet


def degisimler(satirlar, anahtar):
    cikti = []
    for kimlik in sorted({s["kimlik"] for s in satirlar}):
        for uzay in UZAYLAR:
            seri = [(s[anahtar], s["kural_sinifi"]) for s in satirlar if s["kimlik"] == kimlik and s["yontem"] == uzay]
            if len({c for _, c in seri}) > 1:
                cikti.append(f"{kimlik} {uzay}: " + " → ".join(f"{a}:{c}" for a, c in seri))
    return cikti


def main():
    ayarlar = ayarlari_oku()
    for ad in ("renk_araliklari", "karar_kurali", "kutu_degerlendirme"):
        if not ayarlar[ad]["dondurulmus"]:
            raise SystemExit(f"{ad} dondurulmamış; önce G1/G2 üzerinde seçip dondurun.")
    for klasor in ("maskeler", "kutular", "bulaniklik", "olcek"):
        (SONUC / klasor).mkdir(parents=True, exist_ok=True)
    tum = veri_setini_oku()
    eksik = [k["kimlik"] for k in tum if not str(k.get("etiket_durumu", "tamam")).startswith("tamam")]
    if eksik:
        raise SystemExit("Etiketi tamamlanmamış görüntüler: " + ", ".join(eksik) +
                         ". Önce: python betikler/kutu_ciz.py")
    kontrol = [k for k in tum if k["bolum"] == "kontrol"]
    temel = temel_deney(tum, ayarlar)
    bulanik = bulaniklik_deneyi(kontrol, ayarlar)
    olcek = olcek_deneyi(kontrol, ayarlar)
    tablo = sonuc_tablosu(temel)
    o = ozet(temel, bulanik, olcek)
    print((SONUC / "sonuc_tablosu.md").read_text(encoding="utf-8"))
    for uzay in UZAYLAR:
        print(f"{uzay}: sınıf {o[uzay]['sinif_dogru']}/{o[uzay]['sinif_toplam']} doğru | "
              f"TP {o[uzay]['tp']} FP {o[uzay]['fp']} FN {o[uzay]['fn']}")
    print("Bulanıklıkta sınıf değişimi:", o["bulaniklik_sinif_degisimi"] or "yok")
    print("Ölçekte sınıf değişimi:", o["olcek_sinif_degisimi"] or "yok")


if __name__ == "__main__":
    main()
