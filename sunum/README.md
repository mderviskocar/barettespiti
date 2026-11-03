# Sunum ve çevrimdışı kayıt

## Sunum

- `baret_tespiti_sunum.pptx` — 6 slayt, konuşmacı notları her slaytın Notes bölümünde.
- `baret_tespiti_sunum.pdf` — aynı sunumun PDF hâli.
- Yeniden üretmek için: `python sunum/gorselleri_olustur.py` ardından `python sunum/sunumu_olustur.py` (sayılar `sonuclar/` klasöründen okunur).
- Olası sorular ve yanıtları: `soru_cevap.md`.

| Slayt | İçerik | Konuşmacı | Süre |
| --- | --- | --- | --- |
| 1 | Problem, dört sınıf, altı görüntü ve geliştirme/kontrol ayrımı | Nesli | 4 dk |
| 2 | RGB ve HSV renk maskesi: sekiz maske, dondurulmuş aralıklar ve karar kuralı | Omar · Derviş | 4 dk |
| 3 | Tek değişkenli deneyler: bulanıklık ve ölçek | Ahmet · Efe | 4 dk |
| 4 | Hata analizi ve TP / FP / FN (K3 yanlış alarmı) | Murathan | 3 dk |
| 5 | Sonuç tablosu ve canlı çalıştırma | Nesli · Murathan | 4 dk |
| 6 | Sınırlılık ve sonraki adım | Grup | 1 dk |

Toplam süre 20 dakikadır.

## Canlı çalıştırma

```
python arayuz/sunucu.py          # adım adım demo arayüzü -> http://127.0.0.1:8765
python betikler/canli_demo.py K3  # yedek: komut satırı demosu
```

Arayüzde öğretim elemanının seçtiği görüntü (veri setinden ya da yeni yüklenen) için HSV ve RGB adımları sırayla gösterilir; yeni görüntüde baş bölgesi fareyle çizilir. Ayarlar dondurulmuştur.

## Çevrimdışı kayıt

- Kayıt: [`demo_kaydi.mp4`](demo_kaydi.mp4) — 54 sn, demo arayüzünün ekran kaydı (K1 ve K4 için HSV adımları: kanal dönüşümü, kanal kanal aralık testi, birleşik maske, baş örtüşmesi, karar kuralı, aday kutular ve TP/FP/FN).
- Canlı çalıştırmada sorun çıkarsa bu kayıt gösterilir.
