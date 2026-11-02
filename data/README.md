# Ortak veri ve çıktı sözleşmesi

Özgün görüntüler data/development/ (G1, G2) ve data/control/ (K1–K4) altında tutulur. Dönüştürülmüş kopyalar bağımsız örnek değildir. Geçici dosyalar results/scratch/ altındadır. Altı görüntü; normal ışık, gölge, küçük/uzak baret, aynı renkli başka nesne ve başta / elde-masada baret karşılaştırmasını kapsamalıdır.

## Kaynaklar ve etiketler

data/sources.csv her görüntü için bir satır içerir. relative_path depo köküne göredir (örneğin data/development/G1.jpg). width/height özgün piksel boyutlarıdır. Kaynak URL'si, lisans ve koşul kaydedilir; lisans tahmin edilmez. Kendi çekiminiz için source_type=own_photo kullanın.

annotations/ground_truth.json içindeki images listesi başlangıçta boştur. Her görüntü kaydı şu alanları içerir:

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

Üye sonuçları results/rgb_results.csv, results/hsv_results.csv ve diğer results alt klasörlerindedir. Nesli nihai tabloyu results/results.csv içinde birleştirir. Temel karşılaştırma 4 görüntü × 2 yöntem = 8 maske ve 8 satırdır; ek deneyler experiment_id/parameter ile ayrılır. Sonuç dosyaları şimdilik yalnızca başlık içerir.
