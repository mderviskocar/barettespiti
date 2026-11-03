# Denetim Raporu — Hocanın Kurallarına Uygunluk ve Önceki Çalışmalardaki Hatalar

*Hazırlayan: Murathan · ilk sürüm 3 Kasım 01:30, güncelleme 3 Kasım 23:30 · Kaynak: GitHub geçmişi (`git log --all`), `sonuclar/` ölçümleri ve ödev yönergesi (YZM411_G1_Baret_Tespiti_Siniflandirma.pdf).*

Amaç: Teslimden önce her üyenin çalışmasını yönergedeki kurallara göre denetlemek; hataları gizlemeden, kanıtıyla ve düzeltme yoluyla kaydetmek. Yönerge: *"Her örnekte doğru sonuç almanız beklenmez; ayarları sabit tutmanız, başarısızlığı gizlememeniz ve nedenini açıklamanız beklenir."*

---

## 1. Yönerge maddelerine uygunluk (güncel veri seti)

| Yönerge maddesi | Durum | Kanıt / not | Sorumlu |
|---|---|---|---|
| 2a. 2 geliştirme + 4 kontrol, bağımsız görüntüler | ✅ | `veri/kaynaklar.csv` (Pexels ve CHV; URL ve lisans) | Nesli / ekip |
| 2b. Normal ışık, gölge/loş, uzak-küçük, aynı renkte nesne, başta ↔ elde | ✅ | G1 normal ışık · K1 loş ışık · K2 uzak-küçük · K3 sarı makine (baret yok) · K4 elde baret | Ekip |
| 3. Sınıflar yöntemden önce, gerekçeli | ✅ | `etiketler/gercek_etiketler.json` | Ekip |
| 3b. Görünmeyen baş için kutu uydurulmadı | ✅ | Baş ROI ve baret kutuları elle çizildi (`betikler/kutu_ciz.py`) | Ekip |
| 4. Her deneyden önce iki cümlelik tahmin | ✅ | `belgeler/tahminler.csv`: Nesli, Omar, Derviş, Ahmet, Efe, Murathan | Her üye |
| 5a. Bir RGB + bir HSV aralığı G1/G2'de seçilip donduruldu; 8 maske ve alan | ✅ | `ayarlar/deney_ayarlari.json` (gerekçeli), `sonuclar/maskeler/` | Omar, Derviş |
| 5b. Maskeden sınıfa kural, baş ROI örtüşmesi | ✅ | `karar_kurali` (G1/G2'de kontrol edildi) | Omar, Derviş |
| 5c. Kontrol sınıfı ↔ doğru sınıf | ✅ | `sonuclar/sonuc_tablosu.md`: RGB 1/4, HSV 2/4 doğru | Omar, Derviş |
| 6. Hazır dedektör (isteğe bağlı) | — | Kullanılmadı; TP/FP/FN renk maskesi kutularıyla (IoU ≥ 0.50) | Murathan |
| 7. Bir yanlış alarm + bir kaçırma, neden + sonraki kontrol | ✅ | Bölüm 3 ve `defterler/06_kutu_degerlendirme.ipynb` | Murathan + deney sahipleri |
| H4. Bulanıklık ve küçültme, tek değişkenli, ölçülü | ✅ | `sonuclar/bulaniklik/`, `sonuclar/olcek/`; yorumlar 04 ve 05 defterlerinde | Ahmet, Efe |
| 8a. En fazla 6 slayt, çalışan defter, kaynak listesi, sonuç tablosu, çevrimdışı kayıt | ⚠️ | Defter, kaynak listesi, tablo hazır; **slayt ve kayıt bekleniyor** | Ekip |
| 8b. Sonuç tablosu sütunları | ✅ | `sonuclar/sonuc_tablosu.md` (+ sınıf doğruluğu ve TP/FP/FN özeti) | Ortak hat |
| 8d. Yarım sayfa bireysel not | ⚠️ | Güncel: Efe, Omar, Murathan. Derviş ve Ahmet'te sonuç bölümü, Nesli'de yeni veri bekleniyor | Her üye |
| 8e. Yapay zekâ beyanı | ⚠️ | Var: iskelet, Nesli, Omar (güncel ek dahil), Efe. Derviş, Ahmet ve Murathan ekleyecek | Her üye |

**Eşiklerin dayanağı ve geçmiş:** Karar eşikleri (%2.5 alan, %5 baş örtüşmesi) ekibin önceki veri setinde G1/G2'den seçtiği başlangıç kuralıdır; yeni G1/G2'de kontrol edilip K1–K4'ten önce dondurulmuştur. Yeni G2'de sarı piksel olmadığı için %2.5 alan eşiği geliştirme setinde sınanamamıştır; bu bir sınırlılıktır. Önceki veri setinde RGB eşiğinin kontrol sonucu görüldükten sonra değiştirilip geri alındığı git geçmişinde görünür (bkz. 2.2); güncel çalıştırmada eşikler kontrol öncesi dondurulmuş ve değiştirilmemiştir. Veri seti 3 Kasım'da kaynağı ve lisansı belirsiz/filigranlı görüntüler yerine kaynaklı görüntülerle yenilenmiş, bütün deneyler yeni veriyle baştan çalıştırılmıştır.

---

## 2. Önceki çalışmalardaki hatalar (kişi bazında)

### 2.1 Nesli — veri ve etiketler
1. **K3 kutuları kaymıştı (düzeltildi).** İlk sürümde baş ROI `[1092,826,1140,887]`, ikinci baret kutusu `[1634,897,1694,946]` idi; gerçek konumlar `[1093,858,1136,909]` ve `[1633,963,1658,1005]`. İkinci kutu yaklaşık 66 piksel yukarıdaydı. Eski kutularla yapılan her TP/FP/FN ve örtüşme ölçümü geçersizdir. PR #3/#4 ile düzeltildi; ölçümler yeniden hesaplandı. **Ders:** her etiket önizleme görseliyle gözle doğrulanmalı.
2. **K1 sınıfı tartışmalı.** Gerekçe "başlar kadraj dışında". Görüntüde soldaki işçinin başı kadraj dışında, **sağdaki işçinin başı şapkalı ve görünür**. Yönerge tanımına göre baş görünür ve baret yoksa sınıf *baret yok* olmalı. K1 şu an "belirsiz" olduğu için iki yöntem de "doğru" sayılıyor; bu, doğruluğu yapay olarak artırır.
3. **Kontrol setinde aynı renkte bağımsız nesne yok.** Yönergenin "sarı kova" senaryosu (H1) yalnızca G1'deki sarı testereyle var; G1 geliştirme görüntüsü olduğu için test sonucu sayılmaz.
4. **Görüntü kalitesi:** G2, K2, K4 stok fotoğraf filigranı (Dreamstime/Paixin) taşıyor; filigran ve logo renk maskesinde **yanlış alarm** üretiyor (K2/K4'te alt banttaki kırmızı kutular). G1 ve K1 256×256; ölçek deneyinde ×0.25'te 64×64'e iniyor.
5. **Kaynak beyanı** "kullanıcının bildirimine göre" yazılmış; dosya adları kayıtlı ama her görüntünün CHV içindeki doğrudan bağlantısı yok.

### 2.2 Omar — RGB ve karar kuralı
1. **Kontrol sonucu görüldükten sonra eşik değiştirildi.** Sıra: 21:07 kendi aralığıyla `[170,150,0]–[255,255,100]`, kural %2 / %10 → K1–K4 çalıştırıldı (ff49b67). 22:03 Nesli'nin aralığına geçip **kontrolü yeniden çalıştırdı** (6eb5343). 22:05 geri aldı (3501c18). Yönerge: *"Test sonucu görünce eşikleri yeniden ayarlama."* Kontrol görüntüleri üzerinde iki ayarın karşılaştırılması, kontrol setini geliştirme setine çevirir.
2. **Takımda iki farklı RGB aralığı ve iki farklı kural sırası** vardı: Omar önce baş örtüşmesine (≥ %10), sonra alana (≥ %2) bakıyor; Nesli önce alana (≥ %2.5), sonra örtüşmeye (≥ %5). Aynı K3 görüntüsü Omar'ın kuralıyla *başta baret*, Nesli'ninkiyle *baret yok* çıkıyor. Yönerge tek bir dondurulmuş kural ister. **Yeni yapıda tek kural:** Nesli'nin kontrol öncesi dondurduğu kural.
3. Omar'ın kendi notunda belirttiği gibi **%2 alan eşiği ölçülmüş değil varsayım** (G2 belirlemiyor, G1 alt sınır). Dürüst kaydedilmiş; ama varsayımsal eşik raporda açıkça yazılmalı.

### 2.3 Ahmet — Gaussian Blur
1. **Deney ölçülmemişti.** İlk sürüm yalnızca sigma görsellerini üretti; `blur_results.csv` yalnızca başlık satırıydı; notunda "bu aşama görsel incelemedir; baret tespiti başarısını ölçmez" yazıyor. H4 maske ve tespit sonucunun **nasıl değiştiğinin ölçülmesini** ister.
2. Tahmin cümleleri renk eşiği olmadan yazılmış ("no color thresholds"); maske alanı, örtüşme veya sınıf hakkında ölçülebilir bir beklenti içermiyor. Sayısal deneyden önce ölçülebilir bir tahmin eklenmeli (ör. "σ arttıkça K3'te baş örtüşmesi azalır").

### 2.4 Derviş — HSV
1. Depoyu, iş akışını ve doğrulama betiğini kurdu; ancak **HSV dalı boş**: tahmin, HSV maskesi, karşılaştırma ve not yok. Şu an kullanılan HSV aralığı Nesli'nin başlangıç analizinden geliyor.
2. Depo ayarı `30acc68` "doğrudan main'e push açık" bırakıldı; ekip planı "kimse doğrudan main'e basmaz" diyordu.

### 2.5 Efe — Ölçek
1. **Ölçek dalı boş.** Tahmin, deney, yorum ve not yok. Ortak hat sayısal tabloyu üretiyor; ancak tahmin deneyden **önce** yazılmalı. Bu nedenle tahmin, yeni veriyle yapılacak nihai çalıştırmadan önce kaydedilmeli.

### 2.6 Murathan — kutu değerlendirmesi
1. **İlk tahmin hazır dedektör için yazılmıştı;** yöntem renk maskesi kutularına değişince tahmin, kontrol çalıştırılmadan **önce** yeniden yazıldı (commit c63f6ce; K1–K4 sonucu 21d8fff'te). Değişiklik git geçmişinde görünür.
2. **K3 HSV TP'lerinden biri sınırda** (IoU 0.51): birkaç piksellik kutu farkı sonucu FN'ye çevirebilir; sonuç kırılgan.
3. **Ölçek deneyinde en küçük bileşen eşiği (50 piksel) ölçekle değişmiyor.** Bu bilinçli olarak sabit tutuldu, ama küçültmede kaybolan küçük baretlerin bir kısmı bu eşikten kaynaklanır; yorumlanırken ayrıca belirtilmeli.

---

## 3. Ölçümlerin gösterdiği yöntem hataları (güncel veri, ekip hata analizi)

| Hata | Görüntü | Ölçüm | Olası neden | Sonraki kontrol |
|---|---|---|---|---|
| **Yanlış alarm** (H1, S2) | K3 | RGB alan %2.65, 27 FP → baret yokken "baret var, başta değil"; HSV 33 FP, alan %1.46 → sınıf doğru | Yöntem yalnızca renge bakıyor; sarı-turuncu makine aralığa giriyor | Aday kutulara en–boy oranı/doluluk ölçütü (G1/G2'de) |
| **Kaçırma — kural** | K1, K2 | HSV K1'de bareti buldu (IoU 0.81, baş örtüşmesi %12.69), K2'de örtüşme %17.88; toplam alan %0.81 / %0.03 < %2.5 → "baret yok" | Küresel alan eşiği küçük/uzak bareti cezalandırıyor | Alanı baş ROI çevresinde hesaplayan kural (G1/G2'de) |
| **Kaçırma — renk** (S1) | K1 | RGB baretin yalnızca bir kısmını seçti (IoU 0.28 → FN) | Loş ışıkta R ≥ 180 alt sınırının altında kalan pikseller | HSV ile karşılaştırma (HSV IoU 0.81) |
| **Kutu ≠ başta** (S3) | K4 | Elde baret iki yöntemde IoU 0.91 ile bulundu; sınıf doğru "baret var, başta değil" | Kutu nesnenin konumunu verir, başta olduğunu değil | Karar baş ROI ile ayrı verildi |
| **Bulanıklık** | K2 HSV, K3 RGB | σ 0 → 3.0: K2 HSV baş örtüşmesi %17.88 → %22.85; K3 RGB FP 27 → 18; sınıf değişmedi | Bulanıklık küçük parçaları birleştiriyor/eliyor | Ahmet'in yorumuna bırakılır |
| **Küçültme** (S5) | K2 HSV | ×1.0 → ×0.25: TP 1 → 0, en küçük baret 1050 → 66 px; geri büyütmede PSNR 27.5 dB | Piksel kaybı ve sabit 50 px eşiği | Efe'nin notu: eşiği ölçekle küçültüp ayrıştırmak |
| **Sınıf değişimi** | Tümü | Bulanıklık ve ölçek hiçbir görüntünün sınıfını değiştirmedi | Kararı alan eşiği belirliyor | — |

---

## 4. Teslim öncesi kalanlar

| Konu | Sorumlu |
|---|---|
| En fazla 6 slayt + konuşmacı notları + soru-cevap | Ahmet (sunum), herkes kendi slaytı |
| Çevrimdışı kayıt (canlı demonun ekran videosu) | Murathan |
| Bireysel notlara yeni veriyle sonuç ve yorum (Omar ve Efe tamamladı) | Nesli, Derviş, Ahmet |
| Yapay zekâ beyanı | Ahmet, Derviş, Murathan (ve kullanan herkes) |
