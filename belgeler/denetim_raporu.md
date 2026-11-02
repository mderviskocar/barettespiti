# Denetim Raporu — Hocanın Kurallarına Uygunluk ve Önceki Çalışmalardaki Hatalar

*Hazırlayan: Murathan · 3 Kasım 2026, 01:30 · Kaynak: GitHub geçmişi (`git log --all`), `sonuclar/` ölçümleri ve ödev yönergesi (YZM411_G1_Baret_Tespiti_Siniflandirma.pdf).*

Amaç: Teslimden önce her üyenin çalışmasını yönergedeki kurallara göre denetlemek; hataları gizlemeden, kanıtıyla ve düzeltme yoluyla kaydetmek. Yönerge: *"Her örnekte doğru sonuç almanız beklenmez; ayarları sabit tutmanız, başarısızlığı gizlememeniz ve nedenini açıklamanız beklenir."*

---

## 1. Yönerge maddelerine uygunluk

| Yönerge maddesi | Durum | Kanıt / eksik | Sorumlu |
|---|---|---|---|
| 2a. 2 geliştirme + 4 kontrol, bağımsız görüntüler | ✅ | `veri/kaynaklar.csv` | Nesli |
| 2b. Normal ışık, gölge, uzak/küçük, **aynı renkte nesne**, başta ↔ elde/masada | ⚠️ | Aynı renkte bağımsız nesne yalnızca G1'de (geliştirme). Kontrolde yok; "gölge" gece görüntüsüyle (K2) temsil ediliyor. Yeni veri seçimiyle kapatılacak. | Nesli |
| 3. Sınıflar yöntemden önce belirlendi | ✅ | `etiketler/gercek_etiketler.json` (commit 593ae0a, yöntemlerden önce) | Nesli |
| 3b. Örtülü baş "baret yok" denmez, kanıt yetersizse "belirsiz" | ⚠️ | K1 "başlar kadraj dışında → belirsiz" diye etiketli; ancak sağdaki işçinin başı şapkayla görünür durumda. Etiket yeniden incelenmeli (bkz. 2.1). | Nesli |
| 4. **Her deneyden önce iki cümlelik tahmin** ("tahmini olmayan deney puanlanmaz") | ⚠️ | Var: Nesli, Omar, Ahmet, Murathan. **Yok: Derviş (HSV), Efe (ölçek).** | Her üye |
| 5a. Bir RGB + bir HSV aralığı G1/G2'de seçilip **dondurulmuş**; 8 maske ve alan oranı | ⚠️ | Takımda iki farklı RGB aralığı vardı (bkz. 2.2). Yeni yapıda tek aralık: `ayarlar/deney_ayarlari.json`. 8 maske: `sonuclar/maskeler/`. | Omar, Derviş |
| 5b. Maskeden sınıfa kural açıkça yazılı, baş ROI ile örtüşme | ✅ | `ayarlar/deney_ayarlari.json → karar_kurali`, `kaynak/siniflandirma.py` | Omar, Derviş |
| 5c. Kontrol sınıfı ↔ doğru sınıf karşılaştırması | ✅ | `sonuclar/sonuc_tablosu.md` (RGB 2/4, HSV 2/4 doğru) | Omar, Derviş |
| 6. Hazır dedektör (isteğe bağlı) | — | Kullanılmadı; "renk tabanlı başlangıç yöntemi" olarak adlandırıldı. TP/FP/FN renk maskesi kutularıyla ölçüldü (IoU ≥ 0.50). | Murathan |
| 7. Bir yanlış alarm + bir kaçırma, neden ve sonraki kontrol | ✅ | Bölüm 3 ve `bireysel_notlar/murathan.md` | Murathan + deney sahipleri |
| H4. Bulanıklık ve küçültme, **tek değişkenli ve ölçülü** | ⚠️ | Ahmet'in ilk çalışması yalnızca görseldi (`blur_results.csv` boştu). Ortak hat şimdi sayısal tabloyu üretiyor; **yorum ve not deney sahibine ait.** Ölçek: Efe'den gönderim yok. | Ahmet, Efe |
| 8a. En fazla 6 slayt, çalışan defter, kaynak listesi, sonuç tablosu, çevrimdışı kayıt | ❌ / ✅ | Defter, kaynak listesi ve tablo hazır. **Slayt ve kayıt yok.** | Ekip |
| 8b. Sonuç tablosu sütunları (Görüntü, Koşul, Doğru sınıf, Kuralın sınıfı, Maske alanı, TP/FP/FN) | ✅ | `sonuclar/sonuc_tablosu.csv/.md` | Ortak hat |
| 8d. Her üyeden yarım sayfa not | ⚠️ | Dolu: Nesli, Omar, Ahmet, Murathan. **Boş: Derviş, Efe.** Dolu notlar eski dosya yollarını anlatıyor; yeni veriyle güncellenmeli. | Her üye |
| 8e. Yapay zekâ beyanı (araç, amaç, dosya, doğrulama) | ⚠️ | Var: proje iskeleti, Nesli, Omar. **Yok: Ahmet, Derviş, Efe, Murathan.** Kullanılmadıysa "Üretici yapay zekâ kullanmadım" yazılmalı. | Her üye |
| Bilimsel dürüstlük: çalıştırılmamış çıktı/uydurma ölçüm yok | ✅ | Bütün tablolar `betikler/deneyleri_calistir.py` ile üretilir; elle sayı girilmez. | Ekip |

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

## 3. Ölçümlerin gösterdiği yöntem hataları (ekip hata analizi)

Değerler `sonuclar/` altındaki gerçek çalıştırmalardır (mevcut 6 görüntü). Nihai sunum yeni veriyle yeniden üretilecek.

| Hata | Görüntü | Ölçüm | Olası neden | Sonraki kontrol |
|---|---|---|---|---|
| **Yanlış alarm** (H1, S2) | K4 | Baret bulundu (IoU 0.92) ama RGB 17, HSV 19 FP: yelek, sarı kordon, ten rengi, filigran | Yöntem yalnızca renge bakıyor | Şekil ölçütü (en-boy, doluluk) veya baş ROI çevresi koşulu, G1/G2'de tanımlanıp aynı görüntüde yeniden ölçme |
| **Kaçırma** (S1) | K2 (gece) | RGB: alan %0.08, baret seçilmedi → FN; HSV: baret iki parçaya bölündü (IoU 0.39 / 0.19) → FN, sokak ışığındaki çit 35 FP | Karanlıkta parlaklık RGB alt sınırının altında; HSV'de renkli ışık sahneyi sarıya çekiyor | Yakın lekeleri birleştirme kuralı |
| **Kural hatası** | K2 HSV, K3 RGB/HSV | Baş örtüşmesi %16–24 (eşik %5'in çok üstü) ama **toplam alan < %2.5** olduğu için *baret yok* | Küresel alan eşiği küçük/uzak baretleri cezalandırıyor; kural sırası (önce alan) | Alan eşiğini baş ROI çevresinde hesaplayan kural (geliştirme setinde) |
| **Kutu ≠ başta** (S3) | K4 | Kutu IoU 0.92 ile doğru; baret elde | Kutu yalnızca nesnenin konumunu verir | Sınıf kararı baş ROI ile ayrı tutuldu |
| **Bulanıklığın etkisi** | K2 HSV | σ 0 → 1.5: TP 0 → 1, FN 1 → 0, FP 35 → 34 | Bulanıklık baretin iki parçasını birleştiriyor | Ahmet'in yorumuna bırakılır |
| **Bulanıklığın etkisi** | K4 RGB | σ 0 → 3.0: FP 17 → 27 | Kenarlarda yeni karışım renkleri aralığa giriyor | Ahmet'in yorumuna bırakılır |
| **Küçültmenin etkisi** (S5) | K3 HSV | ×1.0: TP 2 · ×0.75: TP 1 · ×0.5 ve ×0.25: TP 0 (en küçük baret 1050 → 66 piksel) | Küçük baret piksel sayısı ve sabit 50 piksel eşiği | Efe'nin yorumuna bırakılır |
| **Geri büyütme** (S5) | K1–K4 | ×0.25 → geri büyütme: PSNR 20.7–27.7 dB, ortalama mutlak fark 3.9–16.2 | Kaybolan yüksek frekans geri gelmez | Efe'nin yorumuna bırakılır |
| **Sınıf değişimi** | Tümü | Bulanıklık ve ölçek hiçbir görüntünün sınıfını değiştirmedi | Kararı alan eşiği belirliyor; σ ve ölçek alan yüzdesini çok az değiştiriyor | Değişim olmaması da yorumlanmalı (yönerge izin veriyor) |

---

## 4. Puan kaybetmemek için her üyenin kendisinin yapması gerekenler

Tahmin ve bireysel yorum **üyenin kendisine aittir**; başkası yerine yazamaz (yönerge 4a, 8d ve sunumda "her üyenin kendi deneyi").

| Üye | Yapması gereken |
|---|---|
| Nesli | K1 sınıfını yeniden incelemek; yeni veride aynı renkli nesne içeren kontrol görüntüsünü seçmek; sınıfları yöntemden önce yazmak; fırça etiketleri; notu yeni yollara güncellemek |
| Omar | Ortak dondurulmuş kuralı kabul edip eşik değişikliğini notunda açıklamak; yeni veride RGB yorumunu yazmak |
| Derviş | **Tahmin (önce)**, HSV yorumu ve RGB karşılaştırması, yarım sayfa not, yapay zekâ beyanı |
| Ahmet | Ölçülebilir tahmin (sayısal deneyden önce), `04_bulaniklik` sonuçlarının yorumu, not güncellemesi, yapay zekâ beyanı |
| Efe | **Tahmin (önce)**, `05_olcek` sonuçlarının yorumu (en az bir kaçırma + S5), yarım sayfa not, yapay zekâ beyanı |
| Murathan | Yeni veriyle hata analizini güncellemek, yapay zekâ beyanı |
| Ekip | En fazla 6 slayt, çevrimdışı kayıt, PR ile main'e birleştirme |
