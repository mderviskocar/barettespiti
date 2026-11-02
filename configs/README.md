# Ayarlar

experiment.json ortak kimlikleri, sınıfları ve karar kuralını içerir. RGB/HSV aralıklarının tek kaynağı rgb_config.json ve hsv_config.json dosyalarıdır.

null seçilmemiş ayardır. Eşikler yalnızca G1/G2 üzerinde seçilir; kontrol öncesinde status=configured ve frozen=true kaydedilir. RGB 0–255; OpenCV 8 bit HSV'de H 0–179, S/V 0–255 aralığındadır. Ortak karar eşikleri yüzde cinsindendir.

Blur/ölçek düzeyleri görev paylaşımındaki ekip önerileridir; ölçülmüş veya hocanın zorunlu tuttuğu parametreler değildir. Dedektör yalnızca uygun model doğrulanırsa etkinleştirilir.
