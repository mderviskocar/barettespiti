"""Tek görüntü analizi: renk maskesi -> alan ve baş örtüşmesi -> dört sınıflı karar
-> aday kutular -> TP/FP/FN (-> fırça maskesi varsa piksel karşılaştırması).

Bütün deneyler (temel, bulanıklık, ölçek) ve canlı demo bu fonksiyonu kullanır;
böylece yalnızca bir değişken değiştirilir, gerisi aynı kalır.
"""

from kaynak.kutular import maskeden_kutular
from kaynak.olcum import alan_ve_ortusme, kutulari_degerlendir, piksel_karsilastir
from kaynak.renk import renk_maskesi
from kaynak.siniflandirma import sinifla


def analiz_et(goruntu, uzay, ayarlar, bas_roi=None, baret_kutulari=None, baret_maskesi=None):
    maske = renk_maskesi(goruntu, uzay, ayarlar["renk_araliklari"])
    alan, ortusme = alan_ve_ortusme(maske, bas_roi)
    sinif = sinifla(alan, ortusme, bas_roi, ayarlar["karar_kurali"])
    kutu_ayari = ayarlar["kutu_degerlendirme"]
    adaylar = maskeden_kutular(maske, kutu_ayari["en_kucuk_bilesen_piksel"],
                               kutu_ayari["morfoloji_cekirdegi"])
    sonuc = {"uzay": uzay, "maske": maske, "alan_yuzde": alan, "ortusme_yuzde": ortusme,
             "sinif": sinif, "adaylar": adaylar, "degerlendirme": None, "piksel": None}
    if baret_kutulari is not None:
        sonuc["degerlendirme"] = kutulari_degerlendir([a["kutu"] for a in adaylar], baret_kutulari,
                                                      kutu_ayari["iou_esigi"])
    if baret_maskesi is not None:
        sonuc["piksel"] = piksel_karsilastir(maske, baret_maskesi)
    return sonuc
