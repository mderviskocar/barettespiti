# İsteğe bağlı hazır dedektör

Durum: Hazır dedektör kullanılmadı.

Ödev yönergesinin 6. maddesi hazır dedektör karşılaştırmasını isteğe bağlı tutar. Ekip renk tabanlı başlangıç yöntemiyle ilerlemiştir; bu nedenle model ağırlığı, sınıf listesi veya model çıktısı yoktur ve hiçbir yerde hazır model sonucu sunulmaz.

Kutu düzeyi TP/FP/FN sayımı bunun yerine **renk maskesi kutu değerlendirmesi** ile yapılmıştır: RGB/HSV maskesinin bağlı bileşenlerinden aday kutular üretilir ve elle çizilmiş gerçek baret kutularıyla IoU ≥ 0.50 bire bir eşleştirme yapılır (`src/detection.py`, `src/metrics.py`, `scripts/evaluate_color_mask_boxes.py`). Bu sonuç bir YOLO/dedektör sonucu değildir.
