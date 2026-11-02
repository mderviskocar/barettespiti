# Deney protokolü

Bu dosya uygulama planıdır; çalıştırılmış deney veya ölçülmüş sonuç değildir.

## Veri ve tahmin

Altı bağımsız görüntüyü data/development/ ve data/control/ altına ekleyin; kaynaklarını data/sources.csv içinde kaydedin. G1/G2 geliştirme, K1–K4 kontroldür. Gerçek sınıfları ve görünür baş kutularını yöntemlerden önce annotations/ground_truth.json içinde belirleyin. Baş görünmüyorsa kutu uydurmayın.

Her üye, yönergenin 5–7. adımlarındaki her deneyden önce docs/predictions.csv içine iki cümlelik tahmin yazar. Sonucu gördükten sonra tahmin değiştirilmez. Geçici örnekler nihai kontrol sonucu olarak sunulmaz.

## RGB, HSV ve ortak karar

RGB ve HSV aralıklarını yalnızca G1/G2 üzerinde seçin. İlgili configs/rgb_config.json ve configs/hsv_config.json dosyalarını, ortak sınıf kuralını da configs/experiment.json dosyasını güncelleyin. Kontrolden önce status=configured ve frozen=true kullanın. Kontrol sonucuna bakarak eşik değiştirmeyin.

OpenCV BGR girdisini ilgili renk uzayına açıkça dönüştürün. HSV 8 bit gösteriminde H 0–179, S/V 0–255'tir. Dört kontrol için RGB ve HSV toplam sekiz maske üretir. Maske alanı ve baş örtüşmesi yüzde (0–100) kaydedilir; oran ile yüzde karıştırılmaz.

Baş örtüşmesi, baş kutusundaki seçilen piksel sayısının baş kutusu alanına bölümünün 100 katıdır. Dört sınıflı kuralın eşikleri ve yetersiz kanıt durumları geliştirme sırasında belirlenir. Renk maskesi nesnenin baret olduğunu veya doğru takıldığını tek başına kanıtlamaz. RGB/HSV sınıf tahminlerini manuel sınıflarla ayrı ayrı karşılaştırın.

## Bulanıklık ve ölçek

Ahmet yalnızca sigma düzeyini; Efe yalnızca ölçeği değiştirir. RGB/HSV ve karar eşikleri sabittir. Blur sırasında çözünürlük; ölçek sırasında bulanıklık sabit tutulur. Sigma, çekirdek, ölçek ve interpolasyon kaydedilir. Görev paylaşımındaki sayılar ekip önerisidir.

Ölçek deneyinde baş ve gerçek baret kutularını yeni boyuta dönüştürün; yuvarlama nedeniyle gerçek boyut oranlarını kullanın. Yüzdeler deneyde kullanılan görüntü alanına göre hesaplanır. Yeniden büyütmeyi ölçümden ayrı gösterin.

## İsteğe bağlı kutu değerlendirmesi

Hazır model kullanılırsa kaynak, ağırlık, sınıflar, giriş boyutu ve çıkarım ayarları models/model_source.md içinde yazılır. Gerçek kutular elle çizilir. Uygun sınıf ve aynı görüntü içinde bire bir IoU >= 0.50 eşleşmesi TP; eşleşmeyen tahmin FP; eşleşmeyen gerçek kutu FN'dir. Aynı gerçek kutu iki TP olamaz. Confidence doğruluk yüzdesi değildir.

Hazır model yoksa çalışma renk tabanlı başlangıç yöntemidir. İstenirse renk maskesi aday kutuları ayrı yöntem adıyla incelenir; hazır dedektör sonucu denmez. Kutu değerlendirmesi yoksa tp/fp/fn N/A olur. Dört sınıflı doğru/yanlış sayımı ayrı tutulur.

## Sonuçlar ve hata analizi

Üyeler kendi results tablolarını ortak şemayla doldurur; Nesli results/results.csv içinde birleştirir. Şema ve yüzde tanımı data/README.md içindedir. Ortak demo önizlemedir; sonucu otomatik nihai tabloya yazmaz.

Bir yanlış alarm ve bir kaçırma açıklanır. Her biri için olası neden ve sonraki kontrol iki cümleyle yazılır. Hata bulunmazsa ek zorlayıcı geliştirme örneği kullanılabilir; bu dört kontrolün bağımsız test sonucu sayılmaz.

## Teslim

- En fazla altı slayt; notebook slayt yerine kullanılmaz.
- Baştan sona çalışan notebook, altı görüntünün kaynak listesi ve ölçülmüş tablo.
- Altı yarım sayfalık bireysel not, güncel AI beyanı.
- Seçilen görüntüde canlı çalıştırma ve kısa çevrimdışı kayıt.
- Çalışan ortamın bağımlılık sürümleri.
- Sunumdan en az 24 saat önce grup liderinin GitHub deposuna yükleme.
