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
