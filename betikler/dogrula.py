"""Proje sözleşmesini denetler: veri, etiket, ayar, tahmin ve sonuç dosyaları.

Kullanım:  python betikler/dogrula.py
"""
import csv
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

from kaynak.veri import SINIFLAR, ayarlari_oku, goruntu_oku, veri_setini_oku  # noqa: E402

hatalar, uyarilar = [], []


def kontrol(kosul, mesaj, uyari=False):
    if not kosul:
        (uyarilar if uyari else hatalar).append(mesaj)


ayarlar = ayarlari_oku()
beklenen = set(ayarlar["gelistirme_kimlikleri"]) | set(ayarlar["kontrol_kimlikleri"])
kayitlar = veri_setini_oku()
kontrol({k["kimlik"] for k in kayitlar} == beklenen, "Altı görüntü (G1-G2, K1-K4) kaynak listesinde olmalı.")
for k in kayitlar:
    bolum = "gelistirme" if k["kimlik"] in ayarlar["gelistirme_kimlikleri"] else "kontrol"
    kontrol(k["bolum"] == bolum, f"{k['kimlik']}: bölüm {bolum} olmalı.")
    kontrol(all(k.get(a) for a in ("kosul", "kaynak_url", "lisans")), f"{k['kimlik']}: koşul/kaynak/lisans eksik.")
    kontrol("BELİRTİLECEK" not in (k.get("kaynak_url", "") + k.get("lisans", "")),
            f"{k['kimlik']}: kaynak URL'si ve lisans yazılmalı (veri/kaynaklar.csv).", uyari=True)
    kontrol(str(k.get("etiket_durumu", "tamam")).startswith("tamam"),
            f"{k['kimlik']}: baş/baret kutuları henüz çizilmedi (betikler/kutu_ciz.py).", uyari=True)
    try:
        g = goruntu_oku(k["dosya"])
        kontrol(g.shape[1] == k["genislik"] and g.shape[0] == k["yukseklik"], f"{k['kimlik']}: çözünürlük kaynak listesiyle uyuşmuyor.")
    except Exception as hata:  # noqa: BLE001
        hatalar.append(f"{k['kimlik']}: görüntü okunamadı ({hata}).")
        continue
    kontrol(k.get("dogru_sinif") in SINIFLAR, f"{k['kimlik']}: doğru sınıf eksik veya geçersiz.")
    kontrol(bool(k.get("gerekce", "").strip()), f"{k['kimlik']}: sınıf gerekçesi eksik.")
    for ad, kutu in [("bas_roi", k.get("bas_roi"))] + [("baret", b) for b in k.get("baret_kutulari", [])]:
        if kutu is None:
            continue
        x1, y1, x2, y2 = kutu
        kontrol(0 <= x1 < x2 <= k["genislik"] and 0 <= y1 < y2 <= k["yukseklik"], f"{k['kimlik']}: {ad} kutusu görüntü dışında {kutu}.")
    if k.get("bas_roi") is None:
        kontrol(k.get("dogru_sinif") in ("belirsiz", "baret_var_basta_degil"),
                f"{k['kimlik']}: baş ROI yok ama sınıf {k.get('dogru_sinif')}.", uyari=True)
for ad in ("renk_araliklari", "karar_kurali", "kutu_degerlendirme"):
    kontrol(ayarlar[ad]["dondurulmus"], f"Ayar dondurulmamış: {ad}")
with (KOK / "belgeler" / "tahminler.csv").open(encoding="utf-8") as dosya:
    uyeler = {r["uye"] for r in csv.DictReader(dosya)}
for uye in ("Nesli", "Omar", "Derviş", "Ahmet", "Efe", "Murathan"):
    kontrol(uye in uyeler, f"Tahmin eksik: {uye}", uyari=True)
    kontrol((KOK / "bireysel_notlar" / f"{uye.lower().replace('ş', 's')}.md").is_file(), f"Bireysel not eksik: {uye}")
tablo = KOK / "sonuclar" / "sonuc_tablosu.csv"
kontrol(tablo.is_file(), "Sonuç tablosu yok: python betikler/deneyleri_calistir.py", uyari=True)
slaytlar = [p for p in (KOK / "sunum").glob("*") if p.suffix.lower() in (".pptx", ".pdf")]
kontrol(bool(slaytlar), "Sunum (en fazla 6 slayt) henüz sunum/ klasöründe yok.", uyari=True)

for u in uyarilar:
    print("UYARI:", u)
for h in hatalar:
    print("HATA :", h)
print("TAMAM: proje sözleşmesi geçerli." if not hatalar else f"{len(hatalar)} hata bulundu.")
sys.exit(1 if hatalar else 0)
