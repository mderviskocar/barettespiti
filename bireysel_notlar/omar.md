# Omar — bireysel deney notu

## Önceki veri seti (2 Kasım)
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

## Güncel veri seti (3 Kasım)

Durum: Tamamlandı (RGB temel deneyi, ortak aralıkla). Notebook: `defterler/02_rgb_segmentasyonu.ipynb`.

- **Kullanılan ayar:** Ekibin ortak, dondurulmuş RGB aralığı alt [180, 140, 0], üst [255, 255, 120]. Kural: baş yoksa belirsiz; maske alanı < %2,5 ise baret yok; baş örtüşmesi ≥ %5 ise başta baret; aksi halde baret var, başta değil. Önceki aralığım [170, 150, 0]–[255, 255, 100] artık kullanılmıyor. Aralık G1/G2'de seçilip K1–K4 çalıştırılmadan önce donduruldu (gerekçe `ayarlar/deney_ayarlari.json` içinde).
- **Ölçülen sonuç:** 4 kontrol görüntüsünden 1'i doğru. K1: alan %0,40, örtüşme %6,08, sonuç baret yok (yanlış; doğrusu başta baret). K2: alan %0,03, örtüşme %17,74, baret yok (yanlış; doğrusu başta baret). K3: alan %2,65, örtüşme %0,00, baret var başta değil (yanlış; doğrusu baret yok). K4: alan %17,59, örtüşme %2,61, baret var başta değil (doğru).
- **Tahmin ve sonuç:** Düşük ışık ve küçük/uzak baret tahminim tuttu (K1 ve K2). K4 için yanlış sınıf beklemiştim ama doğru çıktı. K1'in belirsiz çıkacağı tahminim yeni veride tutmadı, çünkü yeni K1'de baş görünüyor.
- **Hata nedeni:** K3'te sarı-turuncu iş makinesi baret rengine yakın olduğu için maske alanı %2,65 oldu ve %2,5 eşiğini geçti; kural baret olmayan görüntüde "baret var" dedi. K2'de örtüşme eşiğin üstünde (%17,74) ama toplam alan çok küçük (%0,03) olduğu için alan testi önce "baret yok" dedi.
- **Sonraki kontrol:** Alanı yalnızca baş çevresinde hesaplamak veya şekil ölçütü (en–boy oranı, doluluk) eklemek; bunu G1/G2'de tanımlayıp K1–K4'te bir kez ölçmek. Kontrol sonucuna bakarak mevcut eşikleri değiştirmedim.
- **Yapay zekâ kullanımı:** `belgeler/yapay_zeka_beyani.md` içindeki Omar bölümüne bakınız.
