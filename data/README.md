# Veri ve etiketleme

Özgün görüntüler değiştirilmeden `raw/development/` ve `raw/control/` altında saklanır. Dönüştürülmüş görüntüler yeni bağımsız örnek sayılmaz; geçici kopyalar `outputs/scratch/` altında tutulabilir.

## Görüntü seçimi

Geliştirme için `G-1`, `G-2`; kontrol için `K-1`–`K-4` kimlikleri ayrılmıştır. CSV dosyaları henüz veri içermez. Toplam altı görüntü normal ışık, gölge, küçük/uzak baret, baretle aynı renkte farklı nesne ve başta baret / elde veya masada baret karşılaştırmasını kapsamalıdır. Bir görüntü birden fazla koşulu karşılayabilir.

Bu küçük çalışma için hedef kişisi açık olan görüntüler seçin. Birden çok kişinin bulunduğu görüntüler kullanılacaksa hedef kişinin seçimini ve görüntü düzeyindeki sınıf kararını deneyden önce açıkça tanımlayın.

## CSV dosyaları

Tüm dosyalar UTF-8 ve virgülle ayrılmış biçimdedir. Koordinatlar özgün görüntünün piksel koordinatlarıdır: sol üst başlangıçlı, `x_max` ve `y_max` hariç tutulan kutular. Geçerli kutular için `0 <= x_min < x_max <= width` ve `0 <= y_min < y_max <= height` olmalıdır.

| Dosya | İçerik |
| --- | --- |
| `annotations/images.csv` | Her görüntü için bir satır; kimlik, ayrım, depoya göre yol, boyutlar, koşul, kaynak, lisans ve yöntemden önce belirlenen doğru sınıf |
| `annotations/heads.csv` | Elle belirlenen hedef baş bölgesi; `head_id` ile görüntüye bağlanır |
| `annotations/helmets.csv` | İsteğe bağlı dedektör değerlendirmesi için her gerçek baretin kutusu; başta olmayan baretler de dahildir |

`images.csv` içindeki `split`: `development` veya `control`. Kaynak URL'si görsele mümkün olduğunca doğrudan işaret etmelidir. Kendi çekiminizde `source_type=own_photo` yazın; belirsiz lisans bilgisini tahmin etmeyin. Yeniden dağıtım koşullarını kaynak kaydında belirtin.

| Sınıf kimliği | Anlamı |
| --- | --- |
| `helmet_on_head` | Baret görünür ve kişinin başındadır. |
| `helmet_off_head` | Baret vardır, ancak kişinin başında değildir. |
| `no_helmet` | Baş görünür ve başta baret yoktur. |
| `uncertain` | Başın görünmemesi, karanlık veya küçük nesne gibi nedenlerle kanıt yetersizdir. |

Baş görünmüyorsa bir baş kutusu uydurmayın; `images.csv` içindeki gerekçeyi ve `uncertain` sınıfını kullanın. Baş kutuları algoritmanın elle sağlanan girdisidir; sonuçlar otomatik baş tespiti yapılmış gibi sunulmaz.

Kutular ve doğru sınıflar model çıktılarından kopyalanmaz. Gerçek baret olmayan aynı renkli bir nesne `helmets.csv` dosyasına baret olarak eklenmez.
