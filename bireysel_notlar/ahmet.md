# Ahmet — Gaussian Blur ve renk tabanlı sınıflandırma dayanıklılığı

- **Deney kimliği:** `ahmet_gaussian_blur`.
- **Görüntüler:** G1/G2 geliştirme, K1–K4 kontrol görüntüleridir. Gaussian Blur deneyi, sabitlenmiş kontrol görüntüleri üzerinde yürütülecektir.

- **Deney öncesi tahmin:** Gaussian Blur'un sigma değeri arttıkça görüntüdeki keskin renk geçişlerinin yumuşamasını ve özellikle küçük veya düşük ışıkta bulunan baretlerde RGB/HSV maske alanlarının değişmesini bekliyorum. Bulanıklaştırmanın bazı küçük maske parçalarını ortadan kaldırabileceğini, birbirine yakın bölgeleri birleştirebileceğini ve baş ROI örtüşmesindeki değişimlerin sınıflandırma kararını etkileyebileceğini öngörüyorum.

- **Küçük baret ve bulanıklık hipotezi:** K3'teki küçük baretlerin görüntüde sınırlı sayıda piksel kaplaması nedeniyle yüksek sigma değerlerinden daha fazla etkilenmesini bekliyorum. Özellikle σ=3.0 seviyesinde baret sınırlarının çevredeki renklerle karışması ve baş ROI içerisindeki maskeli piksel oranının azalması olasıdır.

- **Düşük ışık hipotezi:** K2'de baretin düşük aydınlatma nedeniyle renk eşiklerine yakın pikseller içerebileceğini düşünüyorum. Gaussian Blur sonucunda bu piksellerin komşu renklerle karışması, RGB ve HSV yöntemlerinde farklı büyüklükte maske değişimlerine yol açabilir.

- **Maske bütünlüğü ve sınıflandırma hipotezi:** Düşük sigma değerlerinde gürültü niteliğindeki küçük renk bölgelerinin azalabileceğini, yüksek sigma değerlerinde ise gerçek baret ayrıntılarının da kaybolabileceğini öngörüyorum. Bu nedenle Gaussian Blur'un her görüntüde sınıflandırmayı iyileştirmesini beklemiyorum; bazı durumlarda karar değişebilirken bazı durumlarda aynı kalabilir.

- **Deney ayarları:** Gaussian çekirdek boyutu 15×15 olarak sabittir. Bağımsız değişken sigma olup filtresiz referans σ=0 ve filtreli seviyeler σ=0.5, 1.5, 3.0 olarak belirlenmiştir. Görüntü çözünürlüğü, baş ROI koordinatları, RGB/HSV eşikleri ve ortak sınıflandırma kuralları sabit tutulacaktır.

- **Ölçülecek sonuçlar:** Her kontrol görüntüsünde RGB/HSV maske alanı yüzdesi, baş ROI örtüşme yüzdesi, tahmin edilen sınıf ve ground truth ile eşleşme durumu karşılaştırılacaktır. Baş ROI bulunmayan K1 görüntüsünde örtüşme sonucu N/A olarak kaydedilecektir.

- **Beklenen sınırlılıklar:** Gaussian Blur küçük görüntülerde kaybolmuş ayrıntıları geri getirmez ve renk maskesinin gerçek bir baret nesnesini tanımasını sağlamaz. Olası iyileşmelerin veya başarısızlıkların yalnızca mevcut altı görüntülük veri seti kapsamında yorumlanması gerekir.

- **Sonraki kontrol:** Gaussian Blur uygulanmamış referans görüntü ile farklı sigma seviyelerindeki maske ve sınıflandırma sonuçları karşılaştırılarak ön tahminler değerlendirilecektir.

- **Yeniden üretim:** `src/gaussian_blur.py`, `notebooks/ahmet_gaussian_blur.ipynb` ve `results/gaussian_blur/` kullanılacaktır.

> Kayıt notu: Bu metin deney çalıştırılmadan önce yazılmıştır. Görüntü kimlikleri önceki veri setine göredir (metindeki K3 küçük baretler → yeni K2; K2 düşük ışık → yeni K1; "baş ROI bulunmayan K1" → yeni veri setinde tüm kontrol görüntülerinde baş ROI var). Yeni yapıdaki dosyalar: `kaynak/bulaniklik.py`, `defterler/04_bulaniklik.ipynb`, `sonuclar/bulaniklik/`.

## Güncel ölçümlerin ön tahminle karşılaştırılması (3 Kasım)

`sonuclar/bulaniklik/bulaniklik_sonuclari.csv` içindeki 32 satırda K1–K4 için hiçbir RGB/HSV sınıf kararı sigma ile değişmedi. Küçük baretli güncel K2'de σ=0→3 baş ROI örtüşmesi RGB'de %17,74→%14,91 azalırken HSV'de %17,88→%22,85 arttı. Böylece yüksek sigma için öngörülen örtüşme azalması RGB'de desteklendi, HSV'de desteklenmedi. K2'nin toplam maske alanı RGB'de %0,03→%0,02 ve HSV'de %0,03→%0,04 oldu; bütün düzeyler ortak %2,5 alan eşiğinin altında kaldığı için karar her seferinde `baret_yok` (gerçek sınıf `basta_baret`).

Düşük ışıklı güncel K1'de RGB alanı %0,40→%0,34, HSV alanı %0,81→%0,80 azaldı; kararlar değişmedi. Karmaşık arka planlı K3'te RGB alanı %2,65→%2,70 artarken HSV alanı %1,46→%1,26 azaldı; iki yöntemin etkisi aynı yönde değildi. Ön tahminin maske duyarlılığı kısmı destekleniyor; olası sınıf değişimi bu dört kontrolde görülmedi. Sunum görselleri `sonuclar/bulaniklik/sunum/` altındadır.

---

## Sonuç (güncel veri, 3 Kasım)

Gaussian Blur deneyinde 15×15 kernel boyutunu sabit tutarak σ=0, 0.5, 1.5 ve 3.0 değerlerini karşılaştırdım. K1–K4 kontrol görüntülerinde RGB ve HSV maske alanlarını, baş ROI örtüşmelerini ve sınıflandırma kararlarını inceledim.

Deney öncesinde, bulanıklık arttıkça küçük baretlerde baş örtüşmesinin azalabileceğini ve maske değişimlerinin bazı sınıflandırma kararlarını etkileyebileceğini öngörmüştüm.

Sonuçlarda tahminim kısmen desteklendi. Güncel K2 görüntüsünde RGB baş örtüşmesi %17,74'ten %14,91'e düşerken HSV baş örtüşmesi %17,88'den %22,85'e çıktı. Maske alanları da değişti ancak K1–K4 görüntülerinin hiçbirinde RGB veya HSV sınıflandırma kararı değişmedi.

Özellikle K2'de toplam maske alanı %2,5 eşiğinin altında kaldığı için baş örtüşmesindeki değişiklikler sınıflandırmaya yansımadı. Bu durum, küçük baretlerin görüntünün tamamı üzerinden hesaplanan alan oranıyla değerlendirilmesinin bir sınırlılık oluşturabileceğini gösterdi.

Sonraki kontrol olarak, yeni geliştirme görüntülerinde maske alanını tüm görüntü yerine baş ROI çevresinde hesaplayan alternatif bir yaklaşımı denemeyi öneriyorum. Bu yaklaşımın küçük baretlerde yanlış negatifleri azaltıp azaltmadığı ayrıca ölçülmelidir.

**Veri seti notu:** Ön tahminlerde geçen K3 küçük baret ifadesi önceki veri setine aittir. Güncel veri setindeki karşılığı K2'dir. Orijinal tahmin metni değiştirilmemiştir.

---

## Önceki görsel inceleme notu (2 Kasım, önceki veri seti)


## Deneyin amacı

Kontrol görüntülerinde Gaussian Blur şiddeti arttığında kenarların ve küçük ayrıntıların görünümünü karşılaştırmak. Bu aşama görsel incelemedir; baret tespiti başarısını ölçmez.

## Kullanılan dosyalar

Girdiler `data/control/K1.jpg`–`K4.jpg`; uygulama `src/gaussian_blur.py`; çıktılar `results/gaussian_blur/K1_sigma_comparison.png`–`K4_sigma_comparison.png`. Ön tahmin `docs/predictions.csv` içindeki `gaussian_blur_visual` kaydıdır.

## Sabit parametreler ve değişken

Çekirdek 15×15, özgün görüntü ölçeği 1 ve BGR girdi sabittir. Değişken sigma: 0 (filtresiz), 0.5, 1.5, 3.0. Her PNG dört paneli bu sırayla gösterir.

## Deney öncesinde kaydedilen tahmin

Sigma arttıkça renk sınırlarının yumuşamasını ve özellikle küçük baret ayrıntılarının kaybolmasını bekliyorum. Düşük ışıklı veya karmaşık arka planlı görüntülerde bu etkinin daha belirgin olabileceğini öngörüyorum.

## K1–K4 için görsel gözlemler

- **K1:** Zemin dokusu ve öndeki açık renkli nesnenin kenarları sigma 1.5 ve özellikle 3'te belirgin biçimde yumuşuyor; 0.5, filtresiz panele yakın görünüyor.
- **K2:** Gece sahnesinde baret kenarı, yelek ayrıntıları ve arka plan ışıkları sigma arttıkça yumuşuyor; 3'te ince çizgiler daha az seçiliyor.
- **K3:** Uzak çalışanların küçük baş/baret ayrıntıları ve çelik yapı çizgileri 3'te daha az keskin; 0.5'te fark sınırlı görünüyor.
- **K4:** Elde tutulan sarı baretin sınırı, yelek dokusu ve delikli arka plan 3'te yumuşuyor. Görsel, baretin başta olup olmadığına ilişkin bir yöntem kararı içermez.

## Sayısal sonuçlar — tamamlanmadı

RGB/HSV eşikleri ve ortak sınıflandırma kuralı hazır olmadığından maske, sınıf kararı veya performans metriği üretilmedi; `results/gaussian_blur/blur_results.csv` yalnızca başlık içeriyor.

## Sınırlılıklar ve sonraki kontrol

Gözlemler nitel ve dört görüntüyle sınırlıdır; görüntülerdeki filigranlar ile sahne koşulları ayrıntı algısını etkiler. RGB/HSV ve karar ayarları geliştirme verisiyle belirlenip dondurulduktan sonra aynı sigma düzeyleriyle kontrol görüntülerinin maske alanı, `head_roi` örtüşmesi ve sınıf sonuçları ölçülecek. Yapay zekâ kullanım kaydı: `docs/ai_usage.md`.
