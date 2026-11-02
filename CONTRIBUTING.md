# Ekip çalışma sözleşmesi

Her üye için ayrı çalışma branch'i ve notebook hazırlanmıştır. Main'e doğrudan push açıktır; pull request ve inceleme onayı zorunlu değildir. Nesli veri/etiket kontrolünü ve entegrasyonu koordine eder. PR, ekip isterse değişiklikleri birlikte incelemek için kullanılabilir.

## Başlama

~~~bash
git clone https://github.com/mderviskocar/barettespiti.git
cd barettespiti
git fetch origin
# Kendi branch'inizi README tablosundan seçin; aşağıdaki Derviş örneğidir:
git switch --track origin/feat/hsv-segmentation
~~~

Branch yerelde zaten varsa git switch feat/hsv-segmentation kullanın.

## Güncelleme ve paylaşım

~~~bash
git fetch origin
git merge origin/main
git status
git add <degistirdiginiz-dosyalar>
git commit -m "Describe your experiment change"
git push
~~~

İsterseniz GitHub'da kendi branch'inizden main'e pull request açabilirsiniz; onay zorunluluğu yoktur. Kendi branch'inizdeki değişiklikleri doğrudan main'e almak için aşağıdaki örnekte kendi branch adınızı kullanın:

~~~bash
git switch main
git pull --ff-only origin main
git merge feat/hsv-segmentation
git push origin main
~~~

Main üzerinde çalışıyorsanız güncel değişiklikleri aldıktan sonra doğrudan commit ve push da yapabilirsiniz. Değişikliğin amacı, ön tahmini, gerçekten çalıştırılan kontroller ve sınırlılıkları kaydedin. Ortak dosyaları değiştirmeden önce ilgili sahiplerle veri sözleşmesini koruyun.

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
