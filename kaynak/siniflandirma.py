"""Ortak dört sınıflı karar kuralı — görev sahipleri Omar + Derviş; etiket denetimi Nesli.

Kural sırası ve eşikler (%2.5 alan, %5 baş örtüşmesi) Nesli'nin dondurduğu ortak başlangıç
kuralıdır (commit b29c635, 8b7546a). Omar'ın ROI-öncelikli sürümü (commit ff49b67, d637764)
defterler/ilk_calismalar/omar_rgb.ipynb içinde korunmuştur.

Renk maskesi yalnızca "baret rengi var/yok" diyebilir; "başta" kararı için elle
işaretlenmiş baş bölgesiyle örtüşme kullanılır. Eşikler G1/G2'de seçilip dondurulur.
"""


def sinifla(alan_yuzde, ortusme_yuzde, bas_roi, kural):
    if bas_roi is None:
        return "belirsiz"
    if alan_yuzde < kural["en_az_renk_alani_yuzde"]:
        return "baret_yok"
    if ortusme_yuzde >= kural["en_az_bas_ortusmesi_yuzde"]:
        return "basta_baret"
    return "baret_var_basta_degil"
