| Görüntü | Koşul | Doğru sınıf | Yöntem | Kuralın sınıfı | Doğru mu | Maske alanı (%) | Baş örtüşmesi (%) | TP / FP / FN |
|---|---|---|---|---|---|---|---|---|
| K1 | Loş, soğuk mavi iç mekân ışığı; sarı baret başta; sarı-yeşil reflektif yelek | Başta baret | RGB | Baret yok | Hayır | 0.40 | 6.08 | 0 / 2 / 1 |
| K1 | Loş, soğuk mavi iç mekân ışığı; sarı baret başta; sarı-yeşil reflektif yelek | Başta baret | HSV | Baret yok | Hayır | 0.81 | 12.69 | 1 / 0 / 0 |
| K2 | Uzak; küçük baş ve baret | Başta baret | RGB | Baret yok | Hayır | 0.03 | 17.74 | 0 / 3 / 2 |
| K2 | Uzak; küçük baş ve baret | Başta baret | HSV | Baret yok | Hayır | 0.03 | 17.88 | 1 / 2 / 1 |
| K3 | Gün ışığı; başı açık işçi (kumaş şapka), sarı-turuncu iş makinesi (aynı renkte nesne) | Baret yok | RGB | Baret var, başta değil | Hayır | 2.65 | 0.00 | 0 / 27 / 0 |
| K3 | Gün ışığı; başı açık işçi (kumaş şapka), sarı-turuncu iş makinesi (aynı renkte nesne) | Baret yok | HSV | Baret yok | Evet | 1.46 | 2.57 | 0 / 33 / 0 |
| K4 | Gün ışığı; sarı baret elde, başı açık ve görünür | Baret var, başta değil | RGB | Baret var, başta değil | Evet | 17.59 | 2.61 | 1 / 13 / 0 |
| K4 | Gün ışığı; sarı baret elde, başı açık ve görünür | Baret var, başta değil | HSV | Baret var, başta değil | Evet | 17.01 | 0.00 | 1 / 1 / 0 |

**Özet (K1–K4).** Görüntü düzeyi dört sınıflı karar ve kutu düzeyi sayım ayrı tutulur:

| Yöntem | Sınıf doğru / toplam | TP | FP | FN |
|---|---|---|---|---|
| RGB | 1 / 4 | 1 | 45 | 3 |
| HSV | 2 / 4 | 3 | 36 | 1 |

TP/FP/FN: elle çizilmiş baret kutularıyla IoU ≥ 0.50 bire bir eşleştirme (renk maskesi kutuları; hazır dedektör yok).
