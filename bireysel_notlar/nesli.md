# Önceki veri seti (2 Kasım)

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

## Güncel veri seti (3 Kasım)

### Görüntüler, sınıflar ve kaynaklar

G1–G2 geliştirme, K1–K4 kontrol grubudur. Aşağıdaki kayıtlar `veri/kaynaklar.csv` ve `etiketler/gercek_etiketler.json` dosyalarına dayanır.

| Görüntü | Bölüm | Doğru sınıf | Kaynak | Kayıtlı lisans |
| --- | --- | --- | --- | --- |
| G1 | gelistirme | `basta_baret` | [Pexels (fotoğrafçı: Mikael Blomkvist)](https://www.pexels.com/photo/man-in-black-crew-neck-t-shirt-wearing-yellow-hard-hat-while-standing-by-the-wooden-table-8961394/) | Pexels Lisansı (ücretsiz kullanım, atıf zorunlu değil; https://www.pexels.com/license/) |
| G2 | gelistirme | `baret_yok` | [Roboflow Universe veri seti (CHV)](https://universe.roboflow.com/ml-pzfty/chv-dataset) | CC BY 4.0 |
| K1 | kontrol | `basta_baret` | [Pexels (fotoğrafçı: Galib Rahman Nadim)](https://www.pexels.com/photo/construction-worker-with-safety-gear-in-industrial-setting-37556468/) | Pexels Lisansı (ücretsiz kullanım, atıf zorunlu değil; https://www.pexels.com/license/) |
| K2 | kontrol | `basta_baret` | [Roboflow Universe veri seti (CHV)](https://universe.roboflow.com/ml-pzfty/chv-dataset) | CC BY 4.0 |
| K3 | kontrol | `baret_yok` | [Pexels (fotoğrafçı: Amar Preciado)](https://www.pexels.com/photo/photo-of-a-man-leaning-on-construction-machine-12032546/) | Pexels Lisansı (ücretsiz kullanım, atıf zorunlu değil; https://www.pexels.com/license/) |
| K4 | kontrol | `baret_var_basta_degil` | [Pexels (fotoğrafçı: Mikael Blomkvist)](https://www.pexels.com/photo/man-in-black-shirt-holding-yellow-hard-hat-8961528/) | Pexels Lisansı (ücretsiz kullanım, atıf zorunlu değil; https://www.pexels.com/license/) |

### Sınıf gerekçeleri

- **G1:** Gün ışığında sarı baret kişinin başında; yüz ve baret net görünür.
- **G2:** Hedef kişi sağdaki çalışan: başı görünür ve gri kumaş şapka takıyor; kumaş şapka baret değildir. Soldaki çalışanın başı kadraj dışında olduğu için değerlendirilmez.
- **K1:** Sarı baret kişinin başında; sahne loş ve soğuk mavi ışıkla aydınlatılmış, baret doğrudan ışık almıyor. Sarı-yeşil reflektif yelek baretle benzer renk aralığında olabilir.
- **K2:** Görüntü merkezine en yakın çalışan başında sarı baret taşır. Diğer uzaktaki çalışan da baretlidir; iki görünür baret kutusu kaydedilmiştir.
- **K3:** Hedef kişinin başı ve yüzü görünür; başında kırmızı kumaş şapka var, baret yok. Çevredeki sarı-turuncu iş makinesi baretle aynı renk aralığına girebilen, baret olmayan bir nesnedir (H1: renkli bölge ≠ baret).
- **K4:** Kişinin başı açık ve görünür; sarı baret elde tutuluyor. Yönerge 3a-ii ve K-4 örneği: elde baret, kişi baretsiz.

### Elle kutu çizimi ve defter

Baş ROI ve baret kutuları, etiket dosyasındaki kayda göre `betikler/kutu_ciz.py` ile fare kullanılarak elle çizildi. Güncel K2, önceki veri setindeki K3 görüntüsüdür ve düzeltilmiş kutuları korur. Güncel G2 ise önceki K1 görüntüsüdür; hedef, sağdaki görünür ve kumaş şapkalı çalışandır.

`defterler/01_veri_ve_etiketler.ipynb` içindeki bütün kod hücreleri sırayla çalıştırıldı. Kaynak tablosu, etiket tablosu ve görüntü üzerindeki kutular deftere çıktılarıyla kaydedildi.

### PDF 2b durumlarının karşılanması

| İstenen durum | Görüntü ve kanıt |
| --- | --- |
| Normal ışıkta baret | G1: gün ışığında başta sarı baret. |
| Gölge / loş ışıkta baret | K1: loş, soğuk mavi ışıklı sahnede başta baret. |
| Uzak / küçük baret | K2: iki uzak çalışanın küçük baretleri. |
| Baretle aynı renkte başka nesne | K3: baret olmayan sarı-turuncu iş makinesi. |
| Başta baret ile elde/masada baret karşılaştırması | G1 ve K4: başta takılı baret ile elde tutulan baret. |

### Belirsizlik

Baş görünmüyorsa ya da görüntü karanlık, bulanık veya çok küçük olduğu için baret kullanımına karar veremiyorsam belirsiz derim. Yöntemin baret bulamaması, kişinin baret takmadığını tek başına göstermez.

### Etiketlemenin sınırlılığı

Kutuları elle çizdiğim için özellikle küçük ve uzaktaki başlarda sınırları birkaç piksel farklı belirleyebilirim. Veri setinde yalnızca altı görüntü olduğu için bütün ışık, uzaklık ve çalışma koşullarını temsil ettiğini söyleyemem.

### Veri setinin değişme nedeni

Önceki görüntülerin bazılarında filigran ve kaynak belirsizliği vardı. Kaynak ve lisans kayıtlarını daha açık tutabilmek için bu görüntülerin yerine Pexels’ten yeni örnekler seçtik. İstenen durumları karşılayan iki CHV görüntüsünü koruyarak geliştirme ve kontrol ayrımını yeniden düzenledik.

### Sonraki kontrol

Bir sonraki kontrolde özellikle küçük ve uzaktaki başların kutularını görüntüyü büyüterek tekrar kontrol etmek istiyorum. Kaynak notlarını da güncel etiketlerle karşılaştırıp tutarsız kalan yerleri not edeceğim.
