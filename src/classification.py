from src.common import mask_percentages


def classify_mask(mask, head_roi, config):
    """Ortak sınıf kodunu döndürür; head_roi None olabilir. Kurallar yalnızca G1/G2'de geliştirilir. Sahipler: Omar + Derviş."""
    # Baş görünmüyorsa kanıt yetersizdir; "baret yok" denmez.
    if head_roi is None:
        return "uncertain"
    area, overlap = mask_percentages(mask, head_roi)
    # Baret rengi baş kutusunun içindeyse baret başta kabul edilir.
    if overlap >= config["min_head_overlap_percent"]:
        return "helmet_on_head"
    # Renk görüntüde var ama başta değilse (elde, masada) baret var, başta değil.
    # Not: %2 alan eşiğini yalnızca G1 sınırlar (alan %0,54, eşik bunun üstünde olmalı).
    # G2'de önce örtüşme testi tetiklendiği için alan eşiğini belirlemez; elde baret
    # içeren geliştirme görüntüsü olmadığından %2 ölçülmüş değil, varsayımdır.
    if area >= config["min_color_area_percent"]:
        return "helmet_off_head"
    return "no_helmet"
