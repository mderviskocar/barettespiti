# Omar — bireysel deney notu

Durum: Tamamlandı (RGB temel deneyi). Dosya yaklaşık yarım sayfadır.

- Deney: BGR→RGB dönüşümüyle sabit renk aralığı; dört kontrol maskesi, alan yüzdesi, baş örtüşmesi, dört sınıf ve doğru/yanlış sayısı.
- Notebook: notebooks/omar_rgb.ipynb
- Branch: feat/rgb-segmentation
- Deney kimliği ve kullanılan görüntüler: `rgb_baseline`. Aralık yalnızca G1/G2 üzerinde seçildi; K1–K4 dondurulmuş ayarla bir kez çalıştırıldı.
- Deneyden önceki iki cümlelik tahmin: docs/predictions.csv içinde `rgb_baseline` satırı (2026-11-02T19:05:44+03:00). K2 ve K3'teki sarı baretlerin bulunacağını ama küçük/uzak baretin ve gece görüntüsünün zorlayacağını; K4'ün yanlış sınıflanabileceğini ve K1'in `uncertain` çıkacağını bekledim.
- Sabit ve değişen parametreler: RGB aralığı alt [170, 150, 0], üst [255, 255, 100]; karar kuralı baş örtüşmesi ≥ %10 ve maske alanı ≥ %2; baş kutusu yoksa `uncertain`. Kontrol sırasında hiçbir parametre değişmedi.
- Gerçekten çalıştırılan işlem/hücre: src/rgb.py `create_mask`, src/classification.py `classify_mask`; notebooks/omar_rgb.ipynb bölüm 3–5 baştan sona çalıştırıldı.
- Ölçülen sonuç ve ilgili tablo/görsel: results/rgb_results.csv ve results/masks/rgb/. 4 görüntüden 3'ü doğru: K1 `uncertain` (doğru), K2 `no_helmet` (yanlış; gerçek `helmet_on_head`, alan %0,09, örtüşme %0,71), K3 `helmet_on_head` (doğru; örtüşme %12,12), K4 `helmet_off_head` (doğru; alan %2,70, örtüşme %0,00). TP/FP/FN: N/A.
- Tahmin ile sonucun karşılaştırması: Gece görüntüsündeki zorluk ve K1 tahminim doğru çıktı. K4 için yanlış sınıf bekledim, ama kural doğru sınıfı verdi; baş örtüşmesi sıfır olduğu için elde tutulan baret başta sayılmadı.
- Hata nedeni ve sınırlılık: K2'de baret pikselleri yaklaşık RGB (92, 73, 9); sabit alt sınırın altında kaldığı için maske baretin neredeyse hiçbirini seçmedi (kaçırma). K3 doğru ama sınırda (örtüşme %12,12, eşik %10, alan %0,02) ve baret kutusu yaklaşık. Yanlış alarm için geliştirme örneği G2 kullanıldı: seçilen piksellerin yaklaşık %67,5'i baş kutusunun dışında (yelek ve yansıtıcı şerit); bu bir test sonucu değildir. %2 alan eşiği G1/G2'den ayarlanamadı: yalnızca G1 onu sınırlar (alan %0,54; eşik bunun üstünde olmalı), G2'de (alan %4,47) önce baş örtüşmesi testi tetiklendiği için alan eşiği hiç kullanılmaz ve elde baret içeren geliştirme görüntüsü yoktur. Bu nedenle %2 ölçülmüş değil, varsayımdır; eşik kontrol sonuçlarına bakılarak değiştirilmedi.
- Sonraki kontrol: K2'yi parlaklığa daha az duyarlı HSV ile ölçmek (Derviş) ve baş kutusu dışındaki bileşenlere şekil ölçütü (en–boy oranı, doluluk) ekleyip G2'yi yeniden ölçmek. Kontrol sonucuna bakarak RGB eşiği değiştirilmedi.
- Yapay zekâ kullanımı ve doğrulama: docs/ai_usage.md kaydına (Claude Code girdisi) bakınız.
