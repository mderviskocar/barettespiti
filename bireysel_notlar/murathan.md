# Murathan — renk maskesi kutu değerlendirmesi (TP / FP / FN) ve hata analizi

- **Deney:** Renk maskesi kutu değerlendirmesi (hazır dedektör kullanılmadı). RGB ve HSV maskelerinin bağlı bileşenleri aday kutu olur; elle çizilmiş gerçek baret kutularıyla IoU ≥ 0.50 bire bir eşleştirme yapılır: eşleşme TP, eşleşmeyen aday FP, bulunamayan baret FN. Kutu düzeyi sayım, görüntü düzeyindeki dört sınıflı doğru/yanlış sayımından ayrı tutulur.
- **Dosyalar:** `kaynak/olcum.py`, `kaynak/kutular.py`, `kaynak/analiz.py`, `betikler/deneyleri_calistir.py`, `ayarlar/deney_ayarlari.json` (kutu_degerlendirme), `defterler/06_kutu_degerlendirme.ipynb`, `sonuclar/temel_sonuclar.csv`, `sonuclar/kutular/`.
- **Deney kimliği ve görüntüler:** `color_mask_box_eval`; ayar seçimi G1–G2, ölçüm K1–K4 (4 gerçek baret: K1'de 1, K2'de 2, K4'te 1; K3'te baret yok).
- **Deneyden önceki tahmin** (`belgeler/tahminler.csv`, 2 Kasım; kimlikler önceki veri setine göre): (1) Baret dışı sarı nesneler özellikle RGB'de çok sayıda FP üretecek; elde tutulan baret TP olacak ama başta olduğunu göstermeyecek. (2) Karanlıktaki baret FN olacak; uzak küçük baretler maskede parçalı kalıp IoU ≥ 0.50'yi sağlayamayacak.
- **Sabit / değişen:** Sabit: dondurulmuş RGB [180,140,0]–[255,255,120] ve HSV [18,120,80]–[30,255,255] (yönergedeki örnek aralık), 3×3 açma/kapama, en küçük bileşen 50 piksel, IoU eşiği 0.50, orijinal ölçek. Değişen: yalnızca renk uzayı.
- **Ölçülen sonuç (K1–K4):** RGB toplam **1 TP / 45 FP / 3 FN**; HSV toplam **3 TP / 36 FP / 1 FN**.
  K1 (loş): RGB 0/2/1 (baretin yalnızca bir kısmı seçildi, IoU 0.28) · HSV 1/0/0 (IoU 0.81).
  K2 (uzak): RGB 0/3/2 (IoU 0.35 ve 0.11) · HSV 1/2/1 (IoU 0.65; diğer baret 0.32).
  K3 (baret yok, sarı makine): RGB 0/27/0 · HSV 0/33/0.
  K4 (elde): RGB 1/13/0 · HSV 1/1/0 (IoU 0.91).
- **Tahmin ile karşılaştırma:** Yanlış alarmların RGB'de daha çok olacağı tutmadı/kısmen tuttu (RGB 45, HSV 36 FP; K3'te HSV daha fazla). Elde baretin TP olup "başta değil" kalacağı tuttu (K4, IoU 0.91). Loş ışıktaki baretin kaçırılacağı RGB'de tuttu, HSV'de tutmadı (K1 HSV TP). Uzak baretlerin kaçırılacağı RGB'de tamamen, HSV'de yarı yarıya tuttu.
- **Hata nedeni ve sınırlılık:** Yanlış alarm — K3: yöntem yalnızca renge baktığı için sarı-turuncu iş makinesi RGB'de %2.65 alan kapladı ve kural, baret yokken "baret var, başta değil" dedi (H1, S2). Kaçırma — K1 ve K2: baret baş bölgesinde seçildi (baş örtüşmesi %6–18, eşik %5) ama görüntünün tamamına bakan %2.5 alan eşiği küçük/uzak bareti "baret yok" saydı; hata bareti bulmakta değil, kuralın küresel alan eşiğinde. Kutu bulmak baretin başta olduğunu göstermez (K4, S3). Dört kontrol görüntüsüyle genelleme yapılamaz.
- **Sonraki kontrol:** Alan eşiğini görüntünün tamamı yerine baş ROI çevresinde hesaplayan kuralı yalnızca G1/G2'de tanımlayıp aynı K1–K4'te yeniden ölçmek; K3 tipi yanlış alarmlar için aday kutulara şekil ölçütü (en–boy oranı, doluluk) eklemek.
