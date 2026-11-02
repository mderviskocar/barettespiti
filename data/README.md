
# Ortak veri ve çıktı sözleşmesi

Özgün görüntüler data/development/ (G1, G2) ve data/control/ (K1–K4) altında tutulur. Dönüştürülmüş kopyalar bağımsız örnek değildir. Geçici dosyalar results/scratch/ altındadır. Altı görüntü; normal ışık, gölge, küçük/uzak baret, aynı renkli başka nesne ve başta / elde-masada baret karşılaştırmasını kapsamalıdır.

Bu seçimde G1 gün ışığında sarı ekipman renk çeldiricisi, K2 gece/düşük ışık ve derin gölgeler, K3 küçük/uzak baretler, G2 başta baret ve K4 elde tutulan baret örneğidir. Bu koşullar kaynak tablosunda görüntü başına kaydedilmiştir.

## Kaynaklar ve etiketler

data/sources.csv her görüntü için bir satır içerir. relative_path depo köküne göredir (örneğin data/development/G1.jpg). width/height özgün piksel boyutlarıdır. Kaynak URL'si, lisans ve koşul kaydedilir; lisans tahmin edilmez. Kendi çekiminiz için source_type=own_photo kullanın. Kullanıcı tarafından sağlanan bir görselin kaynak URL'si verilmemişse source_url alanına not provided with user attachment, lisans alanına unknown yazın; URL veya lisans uydurmayın. Filigrandaki sağlayıcı ve görsel kimliği notes alanında belirtilmelidir.

Kullanıcının bildirimine göre bu altı başlangıç görüntüsünün kaynağı ML tarafından Roboflow Universe'te yayımlanan chv DATASET'tir. Dataset sayfasında CC BY 4.0 lisansı belirtilmiştir; bu nedenle her görüntü satırında source_type=roboflow_universe_dataset, source_url=https://universe.roboflow.com/ml-pzfty/chv-dataset ve license=CC BY 4.0 kayıtlıdır. Görseller yeniden adlandırılarak G1–K4 dosya adlarına yerleştirildi ve manuel ground truth etiketleri eklendi; piksel içeriği değiştirilmedi. Görseldeki Paixin/Dreamstime filigranları ve görünür stok kimlikleri ayrıca notes alanında korunmuştur.

### Veri kümesi atfı

ML, “chv DATASET Dataset,” Roboflow Universe, 2023. https://universe.roboflow.com/ml-pzfty/chv-dataset. Lisans: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Erişim tarihi: 2 Kasım 2026. Bu projede dosya adları ve veri kümesi ayrımı düzenlendi, ayrıca manuel ground truth anotasyonları eklendi; görsel piksel içeriği değiştirilmedi.

Altı başlangıç görüntüsü G1/G2 (development) ve K1–K4 (control) olarak sabitlenmiştir. Birden fazla kişi varsa görüntü sınıfı için hedef kişi, baş merkezi görüntü merkezine en yakın görünür kişi olarak seçilir; eşitlikte daha büyük baş kullanılır. Tüm görünür gerçek baretler helmet_boxes içinde kaydedilir. Baş görünmüyorsa head_roi null kalır ve sınıf uncertain olur.

annotations/ground_truth.json içindeki images listesinde altı görüntünün ground truth kaydı bulunur. Her görüntü kaydı şu alanları içerir:

- image_id: G1, G2 veya K1–K4.
- ground_truth_class: dört ortak sınıftan biri.
- reason: yöntemden önce görüntüdeki kanıta dayanan gerekçe.
- head_roi: baş görünüyorsa [xmin, ymin, xmax, ymax], görünmüyorsa null.
- helmet_boxes: gerçek baret kutularının listesi; kutu değerlendirmesi yapılacaksa doldurulur.

| Sınıf | Anlam |
| --- | --- |
| helmet_on_head | Görünen baret kişinin başındadır. |
| helmet_off_head | Baret görünür, kişinin başında değildir. |
| no_helmet | Baş görünür ve başta baret yoktur. |
| uncertain | Baş görünmemesi, karanlık veya küçük nesne gibi nedenlerle kanıt yetersizdir. |

Koordinatlar özgün piksel koordinatlarıdır, sol üst başlangıçlıdır; xmax/ymax hariçtir. 0 <= xmin < xmax <= width ve 0 <= ymin < ymax <= height olmalıdır. Baş kutusu uydurulmaz. Sarı kova gerçek baret kutusu olarak etiketlenmez. Ölçek deneyinde kutular da ölçeklenir. Birden çok kişi varsa hedef kişi ve tek sınıf karar kuralı önceden yazılır.

## Ortak sonuç şeması

~~~text
experiment_id,image_id,method,condition,parameter,mask_area_percent,head_overlap_percent,predicted_class,ground_truth_class,correct,tp,fp,fn,note
~~~

- parameter: baseline veya sigma/ölçek gibi değiştirilen parametre ve değeri.
- mask_area_percent = 100 × seçilen piksel / kullanılan görüntünün toplam pikseli.
- head_overlap_percent = 100 × baş kutusu içindeki seçilen piksel / baş kutusunun alanı. ROI yoksa N/A.
- correct: true/false; sınıf değerlendirmesi yapılmadıysa N/A.
- tp/fp/fn: kutu düzeyinde tam sayılar; değerlendirme yapılmadıysa N/A.
- Ölçülmeyen diğer metrikler N/A olur. Yüzdeler 0–100 aralığında, yüzde işareti olmadan yazılır.

Üye sonuçları results/rgb_results.csv, results/hsv_results.csv ve diğer results alt klasörlerindedir. Nesli nihai tabloyu results/results.csv içinde birleştirir. Temel karşılaştırma 4 görüntü × 2 yöntem = 8 maske ve 8 satırdır; ek deneyler experiment_id/parameter ile ayrılır. nesli_rgb_hsv_baseline deneyi dört kontrol görüntüsünde sekiz RGB/HSV renk maskesi ve sekiz sonuç satırı üretir. Eşikler yalnızca G1/G2 geliştirme görüntülerinden kalibre edilip kontrol değerlendirmesinden önce dondurulmuştur. Bu, renk tabanlı başlangıç sezgisidir; eğitilmiş dedektör değildir. Kutu düzeyinde IoU değerlendirmesi yapılmadığından tp/fp/fn değerleri N/A'dır. Ground truth kutu önizlemeleri annotations/previews/ içindedir ve özgün görüntülere ek bağımsız örnek sayılmaz.
