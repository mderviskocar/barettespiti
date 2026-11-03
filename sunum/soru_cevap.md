# YZM411 — Grup sunumu soru-cevap hazırlığı

Bu yanıtlar güncel K1–K4 veri setini esas alır. Ön tahminlerdeki eski K2 düşük ışık örneği güncel K1, eski K3 küçük baret örneği güncel K2'dir. Tahmin metinleri `belgeler/tahminler.csv` içinde değiştirilmeden korunur.

## Nesli — veri seti ve etiketler

**Ground truth nedir?** Deney sonucu görülmeden elle belirlenen doğru sınıf, baş ROI'si ve gerçek baret kutularıdır. Maskelerin ve tahminlerin değerlendirilmesinde referans olarak kullanılır. (`etiketler/gercek_etiketler.json`)

**Hangi durumda belirsiz sınıfı verilir?** Hedef kişinin baş bölgesi görünmüyor veya seçilemiyorsa baş ROI yoktur ve ortak kural `belirsiz` döndürür. Güncel altı görüntünün hepsinde baş ROI bulunduğu için bu sınıfın kontrol örneği yoktur. (`kaynak/siniflandirma.py`, `etiketler/gercek_etiketler.json`)

**Geliştirme ve kontrol görüntülerini neden ayırdık?** G1/G2 renk aralıklarını ve ortak karar kuralını seçmek için kullanıldı; K1–K4, ayarlar dondurulduktan sonra kontrol edildi. Böylece kontrol sonuçlarına bakarak eşik değiştirme riskini azaltıyoruz. (`ayarlar/deney_ayarlari.json`)

**Veri kaynakları ve lisansları nelerdir?** G1, K1, K3 ve K4 Pexels fotoğraflarıdır; kaynak CSV'si Pexels lisansını kaydeder. G2 ve K2 Roboflow Universe CHV veri setinden gelir ve CSV'de CC BY 4.0 olarak kayıtlıdır. (`veri/kaynaklar.csv`)

## Omar — RGB

**RGB segmentasyonu nasıl çalışır?** Görüntü RGB kanallarına dönüştürülür ve her pikselin üç kanal değeri dondurulmuş alt/üst aralıkla karşılaştırılır. Eşleşen pikseller maske oluşturur; bu maske tek başına nesnenin baret olduğunu kanıtlamaz. (`kaynak/renk.py`, `ayarlar/deney_ayarlari.json`)

**RGB düşük ışıkta neden başarısız olabilir?** Sabit kanal aralığı aydınlatmayla değişen piksel değerlerine duyarlıdır. Güncel loş K1'de RGB toplam alanı %0,40 ve sınıf kararı `baret_yok` iken gerçek sınıf `basta_baret`tir; tek görüntü bu mekanizmanın kesin nedenini tek başına kanıtlamaz. (`sonuclar/temel_sonuclar.csv`, `etiketler/gercek_etiketler.json`)

**RGB eşikleri nasıl belirlendi?** Güncel ortak aralık alt `[180,140,0]`, üst `[255,255,120]` olarak G1/G2 üzerinde seçildi ve kontrol öncesi donduruldu. Önceki Omar denemesindeki farklı aralık güncel kontrol sonucunu açıklamak için kullanılmaz. (`ayarlar/deney_ayarlari.json`, `bireysel_notlar/omar.md`)

**K2 neden yanlış sınıflandırıldı?** K2 RGB baş örtüşmesi %17,74 ile %5 sınırının üstündedir, fakat toplam maske alanı %0,03 ile %2,5 sınırının altındadır. Alan testi önce yapıldığı için karar `baret_yok`; gerçek sınıf `basta_baret`tir. (`sonuclar/temel_sonuclar.csv`, `kaynak/siniflandirma.py`)

## Derviş — HSV

**HSV neden kullanıldı?** HSV, renk tonu, doygunluk ve parlaklığı ayrı kanallara ayırır; bu, RGB ile karşılaştırmak için ikinci bir sabit renk gösterimidir. Ön tahmin ışık değişiminde olası avantajdı, fakat güncel dört kontrolde HSV de K1 ve K2'yi yanlış sınıflandırdı. (`belgeler/tahminler.csv`, `sonuclar/temel_sonuclar.csv`)

**HSV hangi koşullarda bozulabilir?** Çok düşük parlaklık ve doygunluk, seçili HSV aralığının dışında piksel bırakabilir; benzer tonlu nesneler de maskeye girebilir. Bunlar kayıtlı ön tahmin ve yöntem sınırlılıklarıdır, tek tek piksel nedeni ayrıca ölçülmedikçe kesin hata nedeni diye sunulmamalıdır. (`belgeler/tahminler.csv`, `ayarlar/deney_ayarlari.json`)

**Benzer renkli nesneler neden yanlış pozitif oluşturur?** Renk maskesi şekli ve nesne kimliğini bilmez. K3'te baret yokken HSV maskesinden 33 eşleşmeyen aday kutu üretildi; görüntü sınıfı yine de `baret_yok` kaldı. (`sonuclar/temel_sonuclar.csv`, `sonuclar/kutular/K3_hsv.png`)

**RGB ve HSV sonuçları neden farklı olabilir?** İki yöntem farklı kanal uzaylarında farklı piksel kümeleri seçer. K3'te RGB alanı %2,65 olup %2,5 sınırını geçerken HSV alanı %1,46'da kaldı; görüntü kararları bu yüzden ayrıldı. (`sonuclar/temel_sonuclar.csv`, `ayarlar/deney_ayarlari.json`)

## Ahmet — Gaussian Blur

**Gaussian Blur nedir?** Piksel değerlerini komşuluklarında Gauss ağırlıklarıyla ortalayarak keskin geçişleri yumuşatan filtredir. Bu deneyde 15×15 çekirdek kullanıldı; sigma sıfır filtresiz referanstır. (`kaynak/bulaniklik.py`, `ayarlar/deney_ayarlari.json`)

**Sigma ile kernel arasındaki fark nedir?** Kernel 15×15 komşuluk boyutunu belirler, sigma ise Gauss ağırlıklarının yayılımını değiştirir. Bu deneyde kernel sabit, sigma 0/0,5/1,5/3 olarak değişkendir. (`ayarlar/deney_ayarlari.json`, `kaynak/bulaniklik.py`)

**Konvolüsyon nasıl çalışır?** Filtre, her çıktı pikselini komşu piksellerin ağırlıklı toplamından hesaplar. Gauss ağırlıkları merkeze yakın piksellere daha fazla pay verir; uygulamada OpenCV'nin GaussianBlur işlemi kullanılır. (`kaynak/bulaniklik.py`)

**Neden yalnızca sigma değiştirildi?** Etkiyi sigma düzeyleri arasında karşılaştırabilmek için çözünürlük, baş ROI, renk aralıkları ve karar eşikleri sabit tutuldu. Böylece aynı görüntüdeki sonuç farkı deneyin değişkeniyle ilişkilendirilebilir; bu yine de küçük veri setinin sınırlılığını kaldırmaz. (`ayarlar/deney_ayarlari.json`, `sonuclar/bulaniklik/bulaniklik_sonuclari.csv`)

**Blur maske alanını her zaman azaltır mı?** Hayır. K2'de σ=0→3 RGB alanı %0,03→%0,02 düşerken HSV alanı %0,03→%0,04 yükseldi. (`sonuclar/bulaniklik/bulaniklik_sonuclari.csv`)

**K2'de HSV örtüşmesi artarken sınıf neden değişmedi?** HSV baş örtüşmesi %17,88→%22,85 yükseldi, fakat toplam alan her sigmada %2,5 sınırının çok altında kaldı. Ortak kural alanı önce kontrol ettiği için tüm tahminler `baret_yok` oldu. (`sonuclar/bulaniklik/bulaniklik_sonuclari.csv`, `kaynak/siniflandirma.py`)

**Hiçbir sınıfın değişmemesi dayanıklılık kanıtı mıdır?** Hayır; K1 ve K2'nin yanlış `baret_yok` kararları da tüm sigmalarda sabit kaldı. Yalnız dört kontrol görüntüsüyle saha güvenilirliği veya genel sağlamlık iddiası kurulamaz. (`sonuclar/bulaniklik/bulaniklik_sonuclari.csv`, `sonuclar/ozet.json`)

## Efe — Resize

**Resize nedir?** Görüntünün piksel boyutlarını seçilen ölçek katsayısıyla değiştirmektir. Bu deneyde 1, 0,75, 0,5 ve 0,25 katsayıları; küçültmede INTER_AREA kullanıldı. (`ayarlar/deney_ayarlari.json`, `kaynak/olcek.py`)

**Küçültme neden ayrıntı kaybettirir?** Daha az piksel, küçük nesnenin temsilini sınırlar. K2'de HSV kutu sonucu tam ölçekte 1 TP/1 FN iken yarı ölçekte 0 TP/2 FN oldu; bu gözlem kaybı gösterir ama tek başına hangi işlem adımının kaçırmaya yol açtığını belirlemez. (`sonuclar/olcek/olcek_sonuclari.csv`)

**Büyütme kaybolan bilgiyi geri getirir mi?** Hayır; yeni pikseller kalan verilerden enterpolasyonla oluşturulur. K2 ×0,25 geri büyütme örneğinin PSNR değeri 27,52 dB'dir ve görselde ayrıntılar yumuşamıştır. (`sonuclar/olcek/geri_buyutme.csv`, `sonuclar/olcek/K2_geri_buyutme.png`)

**PSNR nedir?** Referans ile işlenmiş görüntü arasındaki piksel hatasından türetilen desibel cinsinden görüntü benzerliği ölçüsüdür. Baret sınıf doğruluğuyla aynı ölçü değildir; burada yalnızca geri büyütülmüş görüntüyle özgün görüntüyü karşılaştırır. (`sonuclar/olcek/geri_buyutme.csv`)

**Resize ile Gaussian Blur arasındaki fark nedir?** Resize görüntü boyutunu değiştirir; Gaussian Blur aynı boyutta komşuluk ortalamasıyla görüntüyü yumuşatır. Bu projede iki deney ayrı yürütüldü ve her birinde ortak renk aralıkları ile karar kuralı sabit kaldı. (`ayarlar/deney_ayarlari.json`, `sonuclar/olcek/olcek_sonuclari.csv`, `sonuclar/bulaniklik/bulaniklik_sonuclari.csv`)

## Murathan — kutu değerlendirme

**IoU nedir ve nasıl hesaplanır?** Tahmin kutusu ile gerçek kutunun kesişim alanının birleşim alanına oranıdır. Bu deneyde IoU en az 0,50 olan bire bir eşleşme TP sayıldı. (`kaynak/olcum.py`, `ayarlar/deney_ayarlari.json`)

**TP, FP ve FN nedir?** Gerçek baretle eşleşen aday TP, eşleşmeyen aday FP, bulunamayan gerçek baret FN'dir. K1–K4 toplamı RGB 1/45/3, HSV 3/36/1 TP/FP/FN'dir; bunlar görüntü sınıf doğruluğu değildir. (`sonuclar/ozet.json`, `sonuclar/temel_sonuclar.csv`)

**Kutu tespiti baretin başta olduğunu gösterir mi?** Hayır. K4'te eldeki baret her iki yöntemde de TP olarak bulunur, ancak baş ROI örtüşmesi düşük olduğu için görüntü sınıfı `baret_var_basta_degil`dir. (`sonuclar/temel_sonuclar.csv`, `etiketler/gercek_etiketler.json`)

**Hazır nesne dedektörü neden kullanılmadı?** Projenin ölçtüğü adaylar renk maskesinin bağlı bileşenlerinden çıkarılır; burada eğitimli hazır dedektör çalıştırılmamıştır. Bu nedenle sonuçlar yalnızca renk temelli aday kutu yöntemine aittir. (`kaynak/kutular.py`, `ayarlar/deney_ayarlari.json`)

**Confidence neden gösterilmiyor?** Yöntem olasılık veya model güven skoru üretmiyor; sabit renk eşikleriyle piksel seçiyor. Sunumda olmayan bir dedektör skorunu uydurmak doğru olmaz. (`kaynak/renk.py`, `kaynak/kutular.py`)

**K3 yanlış alarmının nedeni nedir?** K3'teki sarı-turuncu iş makinesi maskede renkli alan oluşturuyor; RGB alanı %2,65 ile ortak %2,5 sınırını aşıyor. K3'te gerçek baret yokken RGB 27 FP kutu ve yanlış `baret_var_basta_degil` sınıfı üretiyor. (`sonuclar/temel_sonuclar.csv`, `sonuclar/kutular/K3_rgb.png`)
