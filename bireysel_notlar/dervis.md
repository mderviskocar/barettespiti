# Derviş — HSV renk segmentasyonu ve RGB karşılaştırması

- **Deney kimliği:** dervis_hsv_baseline.
- **Görüntüler:** G1/G2 geliştirme, K1–K4 kontrol görüntüleridir. HSV eşikleri geliştirme görüntülerinde belirlenecek ve kontrol deneyinden önce sabitlenecektir.
- **Deney öncesi tahmin:** HSV’nin renk tonu, doygunluk ve parlaklığı ayrı değerlendirmesi sayesinde değişen aydınlatma koşullarında sarı baret piksellerini RGB’den daha iyi seçebilmesini bekliyorum. Ancak çok düşük parlaklık, düşük doygunluk ve benzer renkli nesneler nedeniyle HSV’nin de kaçırma veya yanlış alarm üretebileceğini öngörüyorum.
- **Düşük ışık hipotezi:** K2’deki sarı baretin karanlık nedeniyle RGB eşiklerinin dışında kalabileceğini düşünüyorum. HSV’de renk tonu korunuyorsa baretin daha belirgin seçilmesini bekliyorum; ancak parlaklık değeri seçilen V alt sınırının altında kalırsa HSV de bareti kaçırabilir.
- **Küçük baret hipotezi:** K3’teki baretlerin az sayıda piksel kaplaması nedeniyle HSV maskesinin küçük ve parçalı bölgeler oluşturabileceğini bekliyorum. Baş ROI içerisinde baret rengi seçilse bile toplam maske alanının düşük kalması, kullanılan ortak karar kuralına bağlı olarak yanlış sınıflandırmaya yol açabilir.
- **Benzer renkli nesne ve yanlış alarm hipotezi:** Sarı ekipman, yelek ve sarı ışık altındaki yüzeylerin baretle aynı HSV aralığına girebileceğini düşünüyorum. Bu nedenle HSV’nin yalnızca renge dayanarak gerçek baret ile benzer renkli nesneleri kesin biçimde ayıramayacağını ve yanlış seçimler oluşturabileceğini öngörüyorum.
- **Başta ve elde baret karşılaştırması:** K4’te elde tutulan sarı baretin maskede seçilmesini, ancak baş ROI ile örtüşmesinin düşük kalmasını bekliyorum. Ortak karar kuralının bu görüntüyü `helmet_off_head`, başların görünmediği K1 görüntüsünü ise `uncertain` olarak sınıflandırmasını bekliyorum.
- **Deney ayarları:** OpenCV’nin 8 bit HSV gösteriminde H=0–179, S/V=0–255 aralıkları kullanılacaktır. Alt ve üst HSV eşikleri yalnızca G1/G2 üzerinde seçilecek; kontrol sırasında görüntü çözünürlüğü, baş ROI koordinatları ve ortak karar kuralları sabit tutulacaktır.
- **Ölçülecek sonuçlar:** Her kontrol görüntüsünde HSV maskesi, maske alanı yüzdesi, baş ROI örtüşme yüzdesi, tahmin edilen sınıf ve doğru/yanlış durumu kaydedilecektir. Sonuçlar aynı görüntülerdeki RGB ölçümleriyle karşılaştırılacak; K1’de baş ROI bulunmadığından örtüşme N/A olarak belirtilecektir.
- **Beklenen sınırlılıklar:** HSV maskesi nesnenin şeklini veya gerçekten baret olup olmadığını tek başına değerlendirmez. Dört kontrol görüntüsündeki sonuçlar gerçek işyeri güvenilirliği veya genel başarı oranı olarak sunulamaz.
- **Sonraki kontrol:** RGB ve HSV’nin farklı sonuç verdiği görüntülerde maskeler ve baş örtüşmeleri karşılaştırılarak olası nedenler incelenecektir. Kontrol sonuçlarına bakılarak dondurulmuş eşikler değiştirilmeyecektir.
- **Yeniden üretim:** `src/hsv.py`, `configs/hsv_config.json`, `notebooks/dervis_hsv.ipynb`, `results/hsv_results.csv` ve `results/masks/hsv/` kullanılacaktır.

> Kayıt notu: Bu metin deney çalıştırılmadan önce yazılmıştır. Görüntü kimlikleri önceki veri setine göredir (metindeki K2 düşük ışık → yeni K1; K3 küçük baret → yeni K2; "başları görünmeyen K1" → artık G2). Yeni yapıdaki dosyalar: `kaynak/renk.py`, `ayarlar/deney_ayarlari.json`, `defterler/03_hsv_segmentasyonu.ipynb`, `sonuclar/temel_sonuclar.csv`, `sonuclar/maskeler/`.

## Sonuç (güncel veri, 3 Kasım)

- **Ölçüm kaynağı:** `sonuclar/temel_sonuclar.csv`; yeniden çalıştırılan `defterler/03_hsv_segmentasyonu.ipynb` çıktılarıyla karşılaştırıldı.
- **Güncel görüntüler:** K1 loş ışıkta başta baret; K2 uzak/küçük baret; K3 sarı iş makinesi ve baret yok; K4 elde baret. Önceki tahmin metni ve eski kimlik açıklaması yukarıda korunmuştur.
- **Dondurulmuş ayarlar:** HSV alt [18,120,80], üst [30,255,255]; toplam renk alanı eşiği %2,5, baş örtüşmesi eşiği %5.
- **Sınıf sonucu:** HSV 2/4, RGB 1/4 doğru.

| Görüntü | HSV alan (%) | HSV baş örtüşmesi (%) | HSV sınıfı | RGB alan / baş örtüşmesi (%) | RGB sınıfı |
| --- | ---: | ---: | --- | ---: | --- |
| K1 | 0,81 | 12,69 | Baret yok (yanlış) | 0,40 / 6,08 | Baret yok (yanlış) |
| K2 | 0,03 | 17,88 | Baret yok (yanlış) | 0,03 / 17,74 | Baret yok (yanlış) |
| K3 | 1,46 | 2,57 | Baret yok (doğru) | 2,65 / 0,00 | Baret var, başta değil (yanlış) |
| K4 | 17,01 | 0,00 | Baret var, başta değil (doğru) | 17,59 / 2,61 | Baret var, başta değil (doğru) |

- **Kutu ve sınıf sonuçları:** K1'de HSV 1 TP ile baret kutusunu buldu; görüntü sınıfı yine yanlış kaldı. K3'te HSV 33 FP ürettiği hâlde görüntü sınıfı doğru kaldı. K4'te HSV baş/yüz ROI'sindeki pikselleri seçmedi (baş örtüşmesi %0,00); eldeki baret için sınıf doğru çıktı.

- **Tahmin–sonuç:** Tahminim kısmen tuttu. HSV dört görüntünün ikisini, RGB ise birini doğru sınıflandırdı. K1’de HSV baş bölgesindeki baret rengini RGB’den daha fazla seçti; ancak ortak karar kuralı nedeniyle sınıf yine yanlış çıktı. Bu yüzden HSV’nin bu veri setinde avantaj sağladığını, fakat her durumda doğru karar vermediğini gördüm.

- **Hata nedeni ve sonraki kontrol:** K1’deki yanlış sınıf kararını seçtim. HSV bareti bulmasına ve baş örtüşmesi %12,69 olmasına rağmen toplam maske alanı %0,81 ile %2,5 eşiğinin altında kaldığı için “baret yok” sonucu çıktı. Sonraki kontrolde baş bölgesindeki renk oranını önceleyen bir kuralı geliştirme görüntülerinde incelerdim; mevcut kontrol sonuçlarına bakarak eşikleri değiştirmezdim.
