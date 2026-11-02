# Deney Protokolü

1. **Veri** — 6 bağımsız görüntü: G1–G2 geliştirme, K1–K4 kontrol. Kapsanan durumlar: normal ışıkta baret, gölgede baret, uzak/küçük baret, baretle aynı renkte nesne, başta ve elde/masada baret karşılaştırması. Dönüştürülmüş kopya bağımsız örnek sayılmaz.
2. **Doğru sınıf** — Yöntemler çalıştırılmadan önce her görüntüye dört sınıftan biri atanır (`etiketler/gercek_etiketler.json`). Örtülü baş "baret yok" diye etiketlenmez; kanıt yetersizse "belirsiz".
3. **Elle etiket** — Baş bölgesi ve baret pikselleri fırçayla boyanır (`betikler/etiket_boyama.py`); baş ROI ve baret kutuları maskeden üretilir (`betikler/etiketleri_uret.py`).
4. **Tahmin** — Her deneyden önce iki cümlelik tahmin `belgeler/tahminler.csv` dosyasına yazılır ve sonuç görüldükten sonra değiştirilmez.
5. **Ayar seçimi** — RGB/HSV aralıkları, karar eşikleri ve kutu parametreleri yalnızca G1/G2'de seçilir, `ayarlar/deney_ayarlari.json` içinde `dondurulmus: true` yapılır.
6. **Kontrol** — K1–K4 dondurulmuş ayarlarla bir kez çalıştırılır (`betikler/deneyleri_calistir.py`). Yanlış karar olsa bile kural değiştirilmez.
7. **Tek değişkenli deneyler** — Bulanıklıkta yalnızca σ, ölçekte yalnızca katsayı değişir; diğer her şey sabittir.
8. **Sayım** — TP/FP/FN nesne (kutu) düzeyidir; görüntü düzeyindeki dört sınıflı doğru/yanlış sayısı ayrı tutulur. Confidence başarı yüzdesi değildir.
9. **Hata analizi** — En az bir yanlış alarm ve bir kaçırma; her biri için iki cümlelik neden ve sonraki kontrol.
