# Nesli — veri kümesi ve RGB/HSV başlangıç analizi

- **Deney kimliği:** nesli_rgb_hsv_baseline.
- **Görüntüler:** G1/G2 geliştirme; K1–K4 kontrol. Split ve ground truth, maskeler üretilmeden önce sabitlendi.
- **Deney öncesi tahmin:** K1'de baş kadraj dışında olduğundan doğru davranış uncertain olmalıdır; K4'te baş açıkça görünür ve baret elde tutulduğundan helmet_off_head beklenir. Karanlık K2 ve küçük/uzak K3 örneklerinde renk tabanlı yöntemlerin baret piksellerini kaçırması olasıdır.
- **Açık baş ile belirsiz baş karşılaştırması:** K2'de baş ve sarı baret görünür; bu nedenle gerçek sınıf helmet_on_head olarak karara bağlanabilir, düşük ışık yalnızca renk yönteminin ölçümünü zorlaştırır. K1'de kişilerin başları görüntü sınırında kesilmiştir; takılı veya çıkarılmış baret kanıtı yoktur. Bu yüzden K1'e baş kutusu çizilmemiş, sınıf uncertain seçilmiştir. Sonraki kontrol, tam başları içeren bir görüntüyle kadraj kaynaklı belirsizliği gidermektir.
- **Ayarlar:** RGB alt/üst [180,140,0] / [255,255,120]; OpenCV HSV alt/üst [18,80,80] / [50,255,255]; ortak maske alanı eşiği 2.5%, baş örtüşmesi eşiği 5.0%. Ayarlar yalnızca G1/G2'de kalibre edildi ve K görüntüleri ölçülmeden önce frozen=true yapıldı.
- **Kalibrasyon ölçüleri:** G1/G2 maske alanı RGB için 0.8652% / 9.7335%, HSV için 2.3224% / 3.7990% oldu. Baş örtüşmesi RGB için 0.0305% / 24.5560%, HSV için 0.0000% / 23.2201% oldu. Dondurulan eşikler iki development örneğini de ayırdı.
- **Kontrol sonuçları:** Dört kontrol görüntüsünde 8 maske ve 8 sonuç satırı üretildi. RGB doğruluğu 2/4, HSV doğruluğu 2/4 oldu. Her iki yöntemde K1 (uncertain) ve K4 (helmet_off_head) doğru; K2 ve K3 no_helmet tahminiyle yanlış sınıflandı.
- **Hata ve sınırlılık:** K2'de HSV baş örtüşmesi 16.0478% olmasına rağmen toplam renk-maskesi alanı 2.0203% ile 2.5% eşiğinin altında kaldı; RGB toplam alanı 0.0831% oldu. K3'te toplam maske alanı RGB 0.0266%, HSV 0.0394% kaldı. Sarı renk maskesi nesnenin baret olduğunu tek başına doğrulamaz; altı görüntü genelleme veya gerçek saha güvenilirliği iddiasını desteklemez.
- **Kutu ölçümü:** Hazır dedektör/IoU değerlendirmesi çalıştırılmadı; tp/fp/fn=N/A bırakıldı. Ground truth koordinat önizlemeleri annotations/previews/ altındadır.
- **Yeniden üretim:** notebooks/nesli_dataset_analysis.ipynb veya python scripts/run_nesli_dataset_analysis.py. Sonuçlar results/results.csv, maskeler results/masks/ altındadır.
- **Yapay zekâ kullanımı ve doğrulama:** docs/ai_usage.md içindeki bu deney kaydına bakın. Ortak doğrulama: python scripts/validate_project.py --require-data.

## K3 koordinat düzeltmesi

Önceki K3 önizlemesinde baş ROI ve iki baret kutusu nesnelerin üstünde kalıyordu. Özgün görüntü büyütülerek elle yeniden incelendi: head_roi=[1093,858,1136,909], helmet_boxes=[[1094,859,1135,908],[1633,963,1658,1005]]. Bu, ilk kontrol deneyinden sonra yapılan etiket koordinatı düzeltmesidir. Görüntüler, split, sınıf etiketleri ve renk eşikleri değiştirilmedi. Notebook ve sonuçlar yeniden üretildi; K3 baş örtüşmesi RGB için 17.7383%, HSV için 23.6662% oldu. Her iki yöntemin K3 tahmini no_helmet ve toplam doğruluğu 2/4 olarak kaldı.
