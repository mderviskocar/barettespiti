# Ahmet — Gaussian Blur görsel deney notu

## Deneyin amacı

Kontrol görüntülerinde Gaussian Blur şiddeti arttığında kenarların ve küçük ayrıntıların görünümünü karşılaştırmak. Bu aşama görsel incelemedir; baret tespiti başarısını ölçmez.

## Kullanılan dosyalar

Girdiler `data/control/K1.jpg`–`K4.jpg`; uygulama `src/gaussian_blur.py`; çıktılar `results/gaussian_blur/K1_sigma_comparison.png`–`K4_sigma_comparison.png`. Ön tahmin `docs/predictions.csv` içindeki `gaussian_blur_visual` kaydıdır.

## Sabit parametreler ve değişken

Çekirdek 15×15, özgün görüntü ölçeği 1 ve BGR girdi sabittir. Değişken sigma: 0 (filtresiz), 0.5, 1.5, 3.0. Her PNG dört paneli bu sırayla gösterir.

## Deney öncesinde kaydedilen tahmin

Sigma arttıkça renk sınırlarının yumuşamasını ve özellikle küçük baret ayrıntılarının kaybolmasını bekliyorum. Düşük ışıklı veya karmaşık arka planlı görüntülerde bu etkinin daha belirgin olabileceğini öngörüyorum.

## K1–K4 için görsel gözlemler

- **K1:** Zemin dokusu ve öndeki açık renkli nesnenin kenarları sigma 1.5 ve özellikle 3'te belirgin biçimde yumuşuyor; 0.5, filtresiz panele yakın görünüyor.
- **K2:** Gece sahnesinde baret kenarı, yelek ayrıntıları ve arka plan ışıkları sigma arttıkça yumuşuyor; 3'te ince çizgiler daha az seçiliyor.
- **K3:** Uzak çalışanların küçük baş/baret ayrıntıları ve çelik yapı çizgileri 3'te daha az keskin; 0.5'te fark sınırlı görünüyor.
- **K4:** Elde tutulan sarı baretin sınırı, yelek dokusu ve delikli arka plan 3'te yumuşuyor. Görsel, baretin başta olup olmadığına ilişkin bir yöntem kararı içermez.

## Sayısal sonuçlar — tamamlanmadı

RGB/HSV eşikleri ve ortak sınıflandırma kuralı hazır olmadığından maske, sınıf kararı veya performans metriği üretilmedi; `results/gaussian_blur/blur_results.csv` yalnızca başlık içeriyor.

## Sınırlılıklar ve sonraki kontrol

Gözlemler nitel ve dört görüntüyle sınırlıdır; görüntülerdeki filigranlar ile sahne koşulları ayrıntı algısını etkiler. RGB/HSV ve karar ayarları geliştirme verisiyle belirlenip dondurulduktan sonra aynı sigma düzeyleriyle kontrol görüntülerinin maske alanı, `head_roi` örtüşmesi ve sınıf sonuçları ölçülecek. Yapay zekâ kullanım kaydı: `docs/ai_usage.md`.
