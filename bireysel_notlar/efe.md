# Efe — bireysel deney notu

Durum: Tamamlandı.

- Deney: Küçültme/ölçek; `kaynak/olcek.py`, `sonuclar/olcek/`.
- Notebook: `defterler/05_olcek.ipynb`
- Branch: `main`
- Deney kimliği ve kullanılan görüntüler: `efe_olcek`; K1–K4.
- Deneyden önceki iki cümlelik tahmin: Görüntü ×0.5 ve özellikle ×0.25 ölçeğine küçültüldüğünde K2'deki uzak ve küçük baretleri bulmaya devam edemeyiz; maske alanı yüzdesi (%) ise teorik olarak sabit kalması beklenirken pratikte değişir (genellikle azalır). Küçültülen görüntüyü tekrar orijinal boyutuna büyütmek kaybolan ayrıntıları geri getirmez.
- Sabit ve değişen parametreler: Ölçek 1.0/0.75/0.5/0.25 değişti; INTER_AREA, RGB/HSV aralıkları, karar kuralı ve 50 piksel eşiği sabitti. Baş ROI ve kutular aynı oranla ölçeklendi.
- Gerçekten çalıştırılan işlem/hücre: Defterin beş kod hücresi sırayla yürütüldü; hazır ölçüm CSV'leri ve görseller çıktılara kaydedildi.
- Ölçülen sonuç ve ilgili tablo/görsel: `sonuclar/olcek/olcek_sonuclari.csv`: ölçek sırasıyla K2 en küçük etiket kutusu 1050/640/273/66 piksel²; HSV TP/FN 1/1→1/1→0/2→0/2, RGB her ölçekte 0/2. K3 FP: RGB 27→19→8→3, HSV 33→22→10→1; K1–K4 sınıfları değişmedi. `sonuclar/olcek/geri_buyutme.csv`: K2 ×0.25 PSNR 27.52 dB, ortalama mutlak fark 5.26. Küçültülen görüntüyü eski boyutuna büyütmek kaybolan ayrıntıları geri getirmemiştir.
- Tahmin ile sonucun karşılaştırması: Görüntü ×0.5 ve ×0.25 ölçeklerine küçültüldüğünde K2'deki uzak ve küçük baretlerin kaçırılacağı tahmini tutmuştur. Buna karşılık, küçük nesnelerin filtrelenmesiyle maske alanı yüzdesinin (%) belirgin şekilde düşeceği tahmini tutmamıştır.
- Hata nedeni ve sınırlılık: Maske alanı yüzdesi bağlı bileşen filtresinden önce hesaplandığı için bu eşikten etkilenmese de, aday kutu seçimindeki minimum alan eşiğinin tüm ölçeklerde 50 piksel olarak sabit tutulması yöntemsel bir sınırlılıktır. Ancak filtre öncesi bileşen alanları ölçülmediğinden bu durum kaçırmaların kesin nedeni olarak değil, ölçek değişmezliğini kısıtlayan olası bir etken olarak değerlendirilmelidir.
- Sonraki kontrol: Sonraki kontrolde, 50 piksel filtresi uygulanmadan önceki ham bağlı bileşen alanları kaydedilmeli ve eşik değeri ölçek katsayısının karesiyle (50×s2) küçültülerek kaçırmanın renk kaybından mı yoksa sabit alan filtresinden mi kaynaklandığı ayrıştırılmalıdır. (Öneridir; bu deneyde uygulanmadı.)
- Yapay zekâ kullanımı ve doğrulama: `belgeler/yapay_zeka_beyani.md`, Efe kaydı; sayılar iki CSV ile karşılaştırıldı, `python betikler/dogrula.py` hatasız çalıştı.
