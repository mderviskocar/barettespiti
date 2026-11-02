# Baret Tespiti ve Sınıflandırması

**YZM 411 Bilgisayarlı Görü · 2026–2027 Güz · Grup sunumu (6. hafta, 4 Kasım 2026)**
Ekip: Nesli · Omar · Derviş · Ahmet · Efe · Murathan

## Problem
Bir İSG kamerasının "baretsiz çalışan" uyarısı verebilmesi için iki karar gerekir: **görüntüde baret var mı** ve **baret başta mı**. Sarı bir maske bulmak bu kararların hiçbirini tek başına vermez: aynı renkte bir kova baret gibi görünebilir, elde taşınan baret "baret var" dedirtir ama kişi baretsizdir, uzaktaki baret birkaç piksele iner.

Bu çalışmada altı görüntülük küçük bir veri setinde **renk tabanlı bir başlangıç yöntemi** sınanır, her görüntü dört sınıftan birine ayrılır ve kararların **ışık, bulanıklık ve ölçekle** nasıl değiştiği ölçülür. **Hazır dedektör kullanılmamıştır; sıfırdan model eğitilmemiştir.** Bu bir eğitim prototipidir; altı görüntülük deneyden gerçek işyeri güvenilirliği iddia edilmez.

## Yöntem
1. **Renk maskesi** — RGB ve HSV aralıklarıyla `cv2.inRange` (aralıklar yalnızca G1/G2'de seçilip dondurulmuştur).
2. **Dört sınıflı karar** — renkli alan ve elle işaretlenmiş baş bölgesiyle örtüşme:
   baş görünmüyor → *belirsiz*; renkli alan < %2.5 → *baret yok*; baş örtüşmesi ≥ %5 → *başta baret*; aksi halde → *baret var, başta değil*.
3. **Kutu düzeyi sayım** — maskenin bağlı bileşenleri aday kutu; elle çizilmiş baret kutularıyla IoU ≥ 0.50 → TP / FP / FN.
4. **Piksel karşılaştırması** — fırçayla boyanmış gerçek baret maskesiyle kesinlik ve duyarlılık (renkli bölge ≠ baret nesnesi, H1).
5. **Tek değişkenli deneyler** — Gaussian Blur (σ) ve küçültme (ölçek katsayısı); diğer her şey sabit.

## Klasör yapısı
| Klasör | İçerik |
|---|---|
| `veri/` | `gelistirme/` (G1–G2), `kontrol/` (K1–K4), `kaynaklar.csv` (kaynak, lisans, çözünürlük) |
| `etiketler/` | `gercek_etiketler.json` (sınıf, gerekçe, baş ROI, baret kutuları), `maskeler/` (fırça maskeleri), `onizlemeler/` |
| `ayarlar/` | `deney_ayarlari.json` — dondurulmuş renk aralıkları, karar kuralı, bulanıklık ve ölçek parametreleri |
| `kaynak/` | Ortak kod: `renk.py`, `siniflandirma.py`, `olcum.py`, `kutular.py`, `bulaniklik.py`, `olcek.py`, `analiz.py`, `gorsel.py`, `veri.py` |
| `betikler/` | `etiket_boyama.py`, `etiketleri_uret.py`, `deneyleri_calistir.py`, `defterleri_calistir.py`, `canli_demo.py`, `dogrula.py` |
| `defterler/` | `00_canli_demo` ve üye defterleri (01–06) |
| `sonuclar/` | `sonuc_tablosu.csv/.md`, `temel_sonuclar.csv`, `maskeler/`, `kutular/`, `bulaniklik/`, `olcek/`, `ozet.json` |
| `belgeler/` | `tahminler.csv`, `deney_protokolu.md`, `bireysel_not_sablonu.md`, `yapay_zeka_beyani.md` |
| `bireysel_notlar/` | Her üyenin yarım sayfalık notu |
| `sunum/` | En fazla 6 slayt ve çevrimdışı kayıt bağlantısı |
| `testler/` | Ölçüm fonksiyonlarının testleri |

## Görev dağılımı
Kimin ne yaptığının GitHub geçmişine dayalı kaydı: [`belgeler/katkilar.md`](belgeler/katkilar.md)

| Üye | Sorumluluk | Defter |
|---|---|---|
| Nesli | Veri seçimi, gerçek etiketler, koordinasyon | `01_veri_ve_etiketler` |
| Omar | RGB segmentasyonu, karar kuralı | `02_rgb_segmentasyonu` |
| Derviş | HSV segmentasyonu, RGB karşılaştırması | `03_hsv_segmentasyonu` |
| Ahmet | Gaussian Blur deneyi | `04_bulaniklik` |
| Efe | Küçültme / ölçek deneyi | `05_olcek` |
| Murathan | Kutu değerlendirmesi, TP/FP/FN, piksel karşılaştırması | `06_kutu_degerlendirme` |

## Çalıştırma
```bash
python -m pip install -r requirements.txt
python betikler/dogrula.py                 # veri, etiket ve ayar kontrolü
python testler/test_olcum.py               # ölçüm testleri
python betikler/deneyleri_calistir.py      # bütün deneyler + sonuç tablosu
python betikler/defterleri_calistir.py     # defterleri çıktılarıyla yeniden üretir
python betikler/canli_demo.py K3           # canlı demo (yeni görüntü için dosya yolu verin)
```
Etiketleme: `python betikler/etiket_boyama.py` → `python betikler/etiketleri_uret.py --yaz` · Aralık seçimi (yalnızca G1/G2): `python betikler/aralik_kalibrasyonu.py`

## Sonuç tablosu
`sonuclar/sonuc_tablosu.md` — Görüntü · Koşul · Doğru sınıf · Kuralın sınıfı · Maske alanı · TP / FP / FN. Tablo `deneyleri_calistir.py` tarafından üretilir; elle düzenlenmez.

## Bilimsel dürüstlük
Her deneyden önce iki cümlelik tahmin `belgeler/tahminler.csv` dosyasına yazılır. Eşikler kontrol sonuçları görüldükten sonra değiştirilmez. Yanlış sınıflar ve hatalar gizlenmez. Çalıştırılmamış çıktı veya uydurma ölçüm yoktur. Yapay zekâ kullanımı `belgeler/yapay_zeka_beyani.md` içinde beyan edilir.
