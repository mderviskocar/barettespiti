"""Şekil ölçütü (ek, keşif amaçlı): renk adaylarını şekle göre süzünce TP/FP/FN ve sınıf nasıl değişir?

Kullanım: python betikler/sekil_deneyi.py   ->  sonuclar/sekil/sekil_sonuclari.csv ve ozet.md
Ana sonuç tablosunu değiştirmez. "Önce" sütunları ana yöntemin (analiz_et) sonuçlarıdır;
"sonra" sütunları yalnızca şekil ölçütünü geçen bileşenlerle hesaplanır.
"""
import csv
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

from kaynak.analiz import analiz_et  # noqa: E402
from kaynak.olcum import alan_ve_ortusme, kutulari_degerlendir  # noqa: E402
from kaynak.renk import renk_maskesi  # noqa: E402
from kaynak.sekil import aday_olculeri, sekil_ayarlarini_oku, suzulmus_maske, yerel_karar  # noqa: E402
from kaynak.siniflandirma import sinifla  # noqa: E402
from kaynak.veri import ayarlari_oku, goruntu_oku, veri_setini_oku  # noqa: E402


def sekil_analizi(goruntu, uzay, ayarlar, sekil, bas_roi, baret_kutulari):
    once = analiz_et(goruntu, uzay, ayarlar, bas_roi, baret_kutulari)
    k = ayarlar["kutu_degerlendirme"]
    maske = renk_maskesi(goruntu, uzay, ayarlar["renk_araliklari"])
    adaylar, etiket = aday_olculeri(maske, k["en_kucuk_bilesen_piksel"], k["morfoloji_cekirdegi"], sekil)
    yeni_maske = suzulmus_maske(etiket, adaylar)
    alan, ortusme = alan_ve_ortusme(yeni_maske, bas_roi)
    sonra = {"maske": yeni_maske, "alan_yuzde": alan, "ortusme_yuzde": ortusme,
             "sinif": sinifla(alan, ortusme, bas_roi, ayarlar["karar_kurali"]),
             "adaylar": [a for a in adaylar if a["gecti"]], "degerlendirme": None}
    sonra["ek_sinif"], sonra["ek_iz"] = yerel_karar(once["ortusme_yuzde"] or 0.0, alan, bas_roi,
                                                     ayarlar["karar_kurali"])
    if baret_kutulari is not None:
        sonra["degerlendirme"] = kutulari_degerlendir([a["kutu"] for a in sonra["adaylar"]],
                                                      baret_kutulari, k["iou_esigi"])
    return once, sonra, adaylar


def main():
    ayarlar, sekil = ayarlari_oku(), sekil_ayarlarini_oku()
    cikti = KOK / "sonuclar" / "sekil"
    cikti.mkdir(parents=True, exist_ok=True)
    satirlar, toplam = [], {}
    for kayit in veri_setini_oku():
        goruntu = goruntu_oku(kayit["dosya"])
        for uzay in ("HSV", "RGB"):
            once, sonra, adaylar = sekil_analizi(goruntu, uzay, ayarlar, sekil, kayit["bas_roi"],
                                                 kayit["baret_kutulari"])
            do, ds = once["degerlendirme"], sonra["degerlendirme"]
            satir = {"kimlik": kayit["kimlik"], "bolum": kayit["bolum"], "uzay": uzay,
                     "dogru_sinif": kayit["dogru_sinif"], "aday_once": len(adaylar),
                     "aday_sonra": len(sonra["adaylar"]),
                     "tp_once": do["tp"], "fp_once": do["fp"], "fn_once": do["fn"],
                     "tp_sonra": ds["tp"], "fp_sonra": ds["fp"], "fn_sonra": ds["fn"],
                     "sinif_once": once["sinif"], "sinif_sonra": sonra["sinif"], "sinif_ek_kural": sonra["ek_sinif"],
                     "alan_sonra_yuzde": round(sonra["alan_yuzde"], 2)}
            satirlar.append(satir)
            if kayit["bolum"] == "kontrol":
                t = toplam.setdefault(uzay, {k: 0 for k in ("tp_once", "fp_once", "fn_once", "tp_sonra",
                                                            "fp_sonra", "fn_sonra", "dogru_once", "dogru_sonra", "dogru_ek")})
                for anahtar in ("tp_once", "fp_once", "fn_once", "tp_sonra", "fp_sonra", "fn_sonra"):
                    t[anahtar] += satir[anahtar]
                t["dogru_once"] += satir["sinif_once"] == kayit["dogru_sinif"]
                t["dogru_sonra"] += satir["sinif_sonra"] == kayit["dogru_sinif"]
                t["dogru_ek"] += satir["sinif_ek_kural"] == kayit["dogru_sinif"]
    with (cikti / "sekil_sonuclari.csv").open("w", encoding="utf-8", newline="") as dosya:
        yazici = csv.DictWriter(dosya, fieldnames=list(satirlar[0]))
        yazici.writeheader()
        yazici.writerows(satirlar)
    ozet = ["# Şekil ölçütü (ek, keşif amaçlı) — K1–K4 toplamı", "",
            f"Eşikler: en-boy {sekil['en_boy_orani'][0]}–{sekil['en_boy_orani'][1]}, doluluk ≥ "
            f"{sekil['en_az_doluluk']}, dışbükeylik ≥ {sekil['en_az_disbukeylik']} (ayarlar/sekil_olcutu.json).",
            "", "| Uzay | TP önce → sonra | FP önce → sonra | FN önce → sonra | Doğru sınıf önce → sonra | Doğru sınıf (ek kural) |",
            "| --- | --- | --- | --- | --- | --- |"]
    for uzay, t in toplam.items():
        ozet.append(f"| {uzay} | {t['tp_once']} → {t['tp_sonra']} | {t['fp_once']} → {t['fp_sonra']} | "
                    f"{t['fn_once']} → {t['fn_sonra']} | {t['dogru_once']}/4 → {t['dogru_sonra']}/4 | {t['dogru_ek']}/4 |")
    ozet += ["", "Ek kural: " + " → ".join(sekil["yerel_kural"]["sira"]), "", sekil["not"],
             "", sekil["yerel_kural"]["not"]]
    (cikti / "ozet.md").write_text("\n".join(ozet) + "\n", encoding="utf-8")
    print("\n".join(ozet))


if __name__ == "__main__":
    main()
