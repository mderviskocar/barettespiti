# Ekip çalışma sözleşmesi

Her üye kendi branch'inde ve notebook'unda çalışır; main'e doğrudan push yapılmaz. Pull request için en az bir onay gerekir. Nesli veri/etiket incelemesini ve entegrasyonu koordine eder; kendi PR'ını başka bir üye inceler.

## Başlama

~~~bash
git clone https://github.com/mderviskocar/barettespiti.git
cd barettespiti
git fetch origin
# Kendi branch'inizi README tablosundan seçin; aşağıdaki Derviş örneğidir:
git switch --track origin/feat/hsv-segmentation
~~~

Branch yerelde zaten varsa git switch feat/hsv-segmentation kullanın.

## Güncelleme ve PR

~~~bash
git fetch origin
git merge origin/main
git status
git add <degistirdiginiz-dosyalar>
git commit -m "Describe your experiment change"
git push
~~~

GitHub'da kendi branch'inizden main'e pull request açın. Amaç, dosyalar, ön tahmin, gerçekten çalıştırılan kontroller ve sınırlılıkları yazın. Ortak dosyaları değiştirmeden önce ilgili sahiplerle veri sözleşmesini koruyun.

## Kabul koşulları

- scripts/validate_project.py hatasız tamamlanır; veri hazırsa --require-data da kullanılır.
- Kimlik, kutu biçimi, yüzde birimi ve sonuç başlıkları değiştirilmez.
- Geçici örnek nihai kontrol sonucu sayılmaz. Kontrol sonucuna göre eşik ayarlanmaz.
- Deneyden önce iki cümlelik tahmin yazılır. Kişisel not ve AI beyanı güncellenir.
- Model ağırlıkları Git'e eklenmez; kaynak ve kurulum talimatı models/model_source.md içine yazılır.

## Ortak arayüzler

src/rgb.py ve src/hsv.py: create_mask(image_bgr, config) -> aynı yükseklik/genişlikte 0/255 maske. Girdi BGR'dir; renk dönüşümü modülün sorumluluğudur.

src/classification.py: classify_mask(mask, head_roi, config) -> dört sınıf kodundan biri. Baş görünmüyorsa head_roi=None, görünüyorsa [xmin, ymin, xmax, ymax].

Diğer arayüzler modül docstring'lerindedir. Üye modülleri başlangıçta açıkça NotImplementedError verir; bunlar tamamlanmış deney değildir. Ortak demo eksikliği gösterir. Entegrasyon kodu src/common.py ve src/demo.py altındadır.
