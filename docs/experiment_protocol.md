# Deney protokolü

Bu dosya uygulama planıdır; deneylerin çalıştırıldığına dair bir kayıt değildir.

## 1. Veri ve doğru sınıflar

Altı bağımsız görüntüyü ve kaynaklarını kaydedin. İki geliştirme görüntüsünü eşik ve karar kuralı seçimi için kullanın. Dört kontrol görüntüsünün doğru sınıflarını yöntemleri çalıştırmadan önce belirleyin. Kontrol sonuçlarına bakarak eşik değiştirirseniz bunu yeni bir geliştirme turu olarak açıklayın; eski kontrolü bağımsız test gibi sunmayın.

## 2. Önceden yazılan tahminler

Yönergenin 5–7. adımlarındaki her deneyden önce `predictions.csv` dosyasına iki cümlelik tahmin ekleyin. Deney kimliği, tarih, üye, görüntüler ve değişkenler kaydedilsin. Sonuç görüldükten sonra tahmini yeniden yazmayın. Hata incelemesinde önerilen sonraki kontrolü çalıştırmadan önce de tahmin yazın.

## 3. Renk tabanlı başlangıç yöntemi

- RGB ve HSV aralıklarını geliştirme görüntülerinde seçip `configs/experiment.json` içine kaydedin. `null` alanlar seçilmemiş ayarlardır; varsayılan deney sonucu değildir.
- OpenCV görüntüyü BGR olarak okur. RGB aralığı için açıkça RGB'ye, HSV aralığı için açıkça HSV'ye dönüştürün. 8 bit OpenCV HSV'de H 0–179, S ve V 0–255 aralığındadır.
- Kontrolde her görüntü için bir RGB ve bir HSV maskesi gösterin: toplam sekiz temel maske.
- Maske alan oranı = seçili piksel sayısı / görüntünün toplam piksel sayısı. CSV'de 0–1 arası oran kaydedin; sunumda yüzdeye dönüştürebilirsiniz.
- Baş örtüşme oranının paydasını uygulamadan önce belirleyin. Önerilen tanım: baş kutusu içindeki seçili piksel sayısı / baş kutusunun alanı.
- Dört sınıfa giden kuralı ve kanıt yetersizliği durumunu açıkça yazıp sabitleyin. Renk maskesi nesnenin baret olduğunu tek başına kanıtlamaz. Baş bölgesiyle örtüşme de tek başına doğru takılmayı kanıtlamaz.
- Her kontrol görüntüsünün tahminini önceden belirlenmiş doğru sınıfla karşılaştırın. RGB ve HSV için doğru/yanlış sayılarını ayrı verin.

## 4. Bulanıklık ve ölçek

Aynı özgün görüntüyü temel alın. Bulanıklık deneyinde ölçeği ve eşikleri; küçültme deneyinde bulanıklığı ve eşikleri sabit tutun. Gauss çekirdeğini/sigmasını, ölçek faktörünü ve interpolasyon yöntemini kaydedin. Her iki etkiyi aynı anda değiştirerek tek değişkenli deney sonucu üretmeyin.

Baş ve gerçek baret kutularını küçültülmüş görüntüye aynı geometrik dönüşümle taşıyın. Maske oranını deneyde kullanılan görüntünün alanına göre hesaplayın. Küçük görüntüyü yalnızca gösterim için büyütüyorsanız bunu ölçümden ayrı belirtin.

## 5. Hazır dedektör: isteğe bağlı

Ağırlık kaynağı, sınıf listesi, giriş boyutu, confidence ve NMS ayarları kaydedilir. Gerçek baret kutuları elle işaretlenir. Aynı görüntü ve uygun sınıf içindeki tahmin/gerçek kutular bire bir eşleştirilir; değerlendirmede IoU >= 0.50 kullanılır. Bir gerçek kutu en fazla bir TP oluşturur. Eşleşmeyen tahmin FP, eşleşmeyen gerçek baret FN'dir.

Confidence başarı yüzdesi değildir. Baret kutusunun bulunması, başta olduğunun belirlenmesinden ayrı değerlendirilir. Hazır dedektör kullanılmazsa çalışma “renk tabanlı başlangıç yöntemi” olarak sunulur.

## 6. Hata analizi ve sonuç kaydı

Bir yanlış alarm ve bir kaçırma örneği açıklanır: her biri için olası neden ve sonraki kontrol iki cümleyle yazılır. Örnek bulunmazsa eklenen zorlayıcı görüntü geliştirme örneği olarak işaretlenir; dört kontrol görüntüsüne gizlice eklenmez.

`outputs/results.csv` içinde her görüntü/yöntem/deney birleşimi için ayrı satır kullanın. Temel karşılaştırmada RGB ve HSV için toplam sekiz satır bulunacaktır. `mask_area_ratio` 0–1 aralığındadır. `tp`, `fp`, `fn` yalnızca tanımlı bir kutu değerlendirmesi yapıldıysa doldurulur; uygulanmıyorsa boş bırakılır, sıfır yazılarak ölçüm yapılmış izlenimi verilmez. Dedektörsüz sayımın kapsamı yönergede tam açıklanmadığından sunumda bu tercih açıkça belirtilmelidir.

## 7. Teslim kontrolü

- En fazla altı slayt; notebook sunum yerine kullanılmaz.
- Baştan sona çalıştırılabilen notebook, altı görüntünün kaynak listesi ve ölçülmüş sonuç tablosu.
- Her üye için yarım sayfalık deney notu ve güncel yapay zekâ beyanı.
- Öğretim elemanının seçtiği örnek üzerinde canlı çalıştırma ve kısa çevrimdışı kayıt.
- Deneyler tamamlandığında çalışma ortamındaki bağımlılık sürümlerinin kaydı.
- Dosyaların grup liderinin GitHub deposuna sunumdan en az 24 saat önce yüklenmesi.
