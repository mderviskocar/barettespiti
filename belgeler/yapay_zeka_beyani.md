# Yapay zekâ kullanım beyanı

## İlk proje iskeleti

- Araç: OpenAI Codex.
- Amaç: Ana ödev gerekliliklerine göre başlangıç depo yapısı, belgeler ve şemalar oluşturmak.
- Etkilenen dosyalar: İlk commit'teki README, veri/deney belgeleri, ayarlar, CSV ve notebook şablonları.
- Doğrulama: JSON ve CSV yapıları, geliştirme/kontrol ayrımı ve Git durumu kontrol edildi. Deney çalıştırılmadı.

## Altı kişilik görev planına uyarlama

- Araç: OpenAI Codex.
- Amaç: Dosya yollarını ve veri sözleşmesini görev paylaşımıyla eşleştirmek; altı kişisel notebook, ortak demo altyapısı, modül arayüzleri, bireysel not şablonları ve GitHub çalışma akışını hazırlamak.
- Etkilenen dosyalar: README.md, CONTRIBUTING.md, .gitattributes, .gitignore, requirements.txt; annotations/, configs/, data/, docs/, individual_notes/, models/, notebooks/, results/, scripts/ ve src/ altındaki bu değişiklikle eklenen/güncellenen dosyalar.
- Doğrulama: JSON/notebook/CSV sözleşmeleri, Python sözdizimi, boş veri durumunda notebook başlangıcı ve ortak demo entegrasyonu kontrol edildi. Gerçek görüntüler üzerinde üye deneyleri çalıştırılmadı.
- Sınır: Üye algoritmaları NotImplementedError veren açık arayüzlerdir. RGB/HSV eşikleri seçilmedi; model, etiket ve ölçülmüş sonuç üretilmedi.

Her üye sonraki AI kullanımlarında araç, amaç, etkilenen dosya/hücre ve gerçekten yaptığı doğrulamayı ekler. İlgili üye içeriği ve sonuçları kendi ortamında doğrular.

## Altı görüntünün ground truth anotasyonu

- Araç: OpenAI Codex (görsel inceleme ve dosya düzenleme).
- Amaç: Kullanıcının sağladığı altı görüntüyü G1/G2 development ve K1–K4 control düzenine yerleştirmek; proje sözleşmesindeki dört sınıf, hedef baş ROI ve gerçek baret kutularını doldurmak.
- Etkilenen dosyalar: `data/development/`, `data/control/`, `data/sources.csv`, `data/README.md`, `annotations/ground_truth.json`, `README.md`.
- Sınıf kararları: G1 `no_helmet`, G2 `helmet_on_head`, K1 `uncertain`, K2/K3 `helmet_on_head`, K4 `helmet_off_head`. K1'de baş kadraj dışında olduğundan kutu eklenmedi; K4'te elde tutulan baret başta takılı sayılmadı.
- Kaynaklar: Kullanıcının bildirimine göre altı görsel ML tarafından Roboflow Universe'te yayımlanan chv DATASET'ten alınmıştır. Dataset sayfasında CC BY 4.0 belirtilir; data/sources.csv içindeki altı satır bu URL ve lisansla güncellendi. Görünen Paixin/Dreamstime filigranları ve stok kimlikleri notes alanında ayrıca kaydedildi.
- Doğrulama: Kaynak boyutları görsel dosyalarla karşılaştırıldı ve tüm kutuların görüntü sınırları içinde olduğu denetlendi. `python scripts/validate_project.py --require-data` başarıyla tamamlandı; hiçbir segmentasyon/model deneyi veya sonuç ölçümü bu değişiklikte yapılmadı.
- Sınırlılık: Kutular manuel görsel tahmindir; K3 gibi uzak işçi örneklerinde kutu sınırları yaklaşık tutulmuştur ve piksel hassasiyeti için ikinci gözden geçirme gerekir.

## Nesli veri analizi ve RGB/HSV başlangıç ölçümü

- Araç: OpenAI Codex; Python 3.14, NumPy ve OpenCV.
- Amaç: Altı kaynak/etiket kaydını ve özgün boyutları denetlemek; manuel kutu önizlemelerini oluşturmak; G1/G2 ile renk eşiklerini kalibre edip dondurduktan sonra K1–K4 üzerinde RGB/HSV maskelerini ölçmek.
- Etkilenen dosyalar: notebooks/nesli_dataset_analysis.ipynb, scripts/run_nesli_dataset_analysis.py, configs/rgb_config.json, configs/hsv_config.json, configs/experiment.json, data/sources.csv, annotations/previews/, results/masks/, results/rgb_results.csv, results/hsv_results.csv, results/results.csv, docs/predictions.csv, individual_notes/nesli.md, data/README.md ve README.md.
- Sabit ayarlar: RGB alt/üst [180,140,0]/[255,255,120]; OpenCV HSV alt/üst [18,80,80]/[50,255,255]; maske alanı eşiği 2.5%; baş örtüşme eşiği 5%. Renk aralıkları ve karar kuralı yalnızca G1/G2 geliştirme ölçülerinden seçilip K görüntülerinden önce donduruldu.
- Ölçülen kontrol sonucu: 8 maske ve 8 CSV satırı. Sınıf doğruluğu RGB 2/4, HSV 2/4; iki yöntemde K2 ve K3 yanlış sınıflandı. Kutu düzeyinde dedektör/IoU ölçümü yapılmadı; tp/fp/fn N/A bırakıldı.
- Doğrulama: python scripts/run_nesli_dataset_analysis.py ile ölçüm çıktıları tekrar üretildi; notebook beş kod hücresiyle yürütülüp çıktılar kaydedildi; python scripts/validate_project.py --require-data başarılı oldu.
- Sınırlılık: Renk maskesi baret nesnesini tek başına kanıtlamaz. Karanlık ve uzak örneklerdeki hatalar saklanmadı; altı görüntü genelleme veya gerçek saha performansı iddiasını desteklemez.

## Omar — RGB deneyi

- Araç: Claude Code (Anthropic).
- Amaç: RGB maske ve ortak karar kuralını uygulamak, aralığı G1/G2 üzerinde seçmek, ön tahmini kaydetmek, ayarları dondurmak, K1–K4 sonuçlarını üretmek ve notebook ile bireysel notu doldurmak.
- Etkilenen dosyalar: `src/rgb.py`, `src/classification.py`, `configs/rgb_config.json`, `configs/experiment.json`, `docs/predictions.csv`, `results/rgb_results.csv`, `results/masks/rgb/`, `notebooks/omar_rgb.ipynb`, `individual_notes/omar.md`.
- Ön tahmin: İki cümlelik tahmin taslağı Claude Code tarafından yazıldı; Omar kontrol çalıştırılmadan önce onayladı ve kayda alındı.
- Doğrulama: Aralık adayları yalnızca G1/G2 üzerinde karşılaştırıldı. Kontrol görüntüleri ayarlar dondurulduktan sonra bir kez çalıştırıldı ve sonuçlar notebook içinde yeniden hesaplanıp CSV ile karşılaştırıldı. K2 baret rengi ve G2 dışı piksel oranı doğrudan piksel ölçümüyle denetlendi. `scripts/validate_project.py` hatasız tamamlandı.
- Sınır: Karar kuralının eşikleri Derviş ile birlikte gözden geçirilmelidir; %2 alan eşiği G1/G2'den ayarlanamadı. Maskeler görsel olarak yalnızca G1/G2 için incelendi; kontrol maskeleri notebook çıktısında gösterilir.

### Omar — güncel veriyle ek (3 Kasım)

- Araç: Claude Code (Anthropic).
- Amaç: `defterler/02_rgb_segmentasyonu.ipynb` defterini çalıştırmak, sonuçları dosyalardan özetlemek, defterdeki hata yorumunu ve bireysel notu benim cevaplarımın taslağıyla düzenlemek.
- Etkilenen dosyalar: `defterler/02_rgb_segmentasyonu.ipynb`, `bireysel_notlar/omar.md`, `belgeler/yapay_zeka_beyani.md`.
- Doğrulama: Sayıları `sonuclar/temel_sonuclar.csv` ve `sonuclar/sonuc_tablosu.md` ile karşılaştırdım (RGB 1/4); `python betikler/dogrula.py` hatasız çalıştı. Yorum cümlelerinin taslağını Claude Code yazdı; içeriği kontrol edip kendi görüşüm olarak kabul ettim. Tahminim (`rgb_baseline`) ve ayar dosyaları değiştirilmedi.

### Ahmet — Bulanıklık deneyi

- **Araç:** OpenAI Codex.
- **Kullanım amacı:** Gaussian Blur deney defterinin çalıştırılması, mevcut sonuç dosyalarındaki ölçümlerin özetlenmesi ve kendi hazırladığım yorumların notebook ile bireysel notuma aktarılması.
- **Etkilenen dosyalar:** `defterler/04_bulaniklik.ipynb`, `bireysel_notlar/ahmet.md`, `belgeler/yapay_zeka_beyani.md`.
- **İnsan katkısı:** Deney sonuçlarına ilişkin değerlendirmeler, sınırlılık açıklaması ve sonraki kontrol önerisi tarafımdan belirlenmiştir.
- **Doğrulama:** Sayısal değerler mevcut Gaussian Blur CSV dosyasıyla karşılaştırılmıştır. Notebook ve proje doğrulama betiğinin sonuçları ayrıca kontrol edilmiştir.

## Ahmet — Sunum

- **Araç:** OpenAI Codex.
- **Amaç:** Projenin gerçek çıktılarını kullanarak altı slaytlık sunum, konuşmacı notları, görseller ve soru-cevap belgesi hazırlamak.
- **Etkilenen dosyalar:** `sunum/` altındaki sunum, PDF, görseller, üretim betikleri ve soru-cevap dosyası.
- **Doğrulama:** Sayısal değerler kaynak CSV ve JSON dosyalarıyla karşılaştırıldı; slayt sayısı, 16:9 oranı, altı Notes bölümü, PowerPoint paket bütünlüğü ve altı sayfalık PDF kontrol edildi. PDF slaytları görsel olarak incelendi.

## Efe — ölçek deneyi

- Araç: OpenAI Codex.
- Amaç: tahmin ve yorumlarımı dosyalara kaydetmek, 05_olcek defterini çalıştırmak, bireysel notu düzenlemek.
- Etkilenen dosyalar: belgeler/tahminler.csv, defterler/05_olcek.ipynb, bireysel_notlar/efe.md.
- Doğrulama: tahmin ve yorum cümleleri benimdir; sayıları sonuclar/olcek/olcek_sonuclari.csv ve geri_buyutme.csv ile karşılaştırdım; python betikler/dogrula.py hatasız çalıştı.

## Derviş — HSV deneyi

- Araç: OpenAI Codex.
- Amaç: Tahmin metnimin ve sonuç/hata yorumlarımın taslaklarını yazmak/düzenlemek, HSV defterini çalıştırmak ve bireysel notumu düzenlemek.
- Etkilenen dosyalar: `defterler/03_hsv_segmentasyonu.ipynb`, `bireysel_notlar/dervis.md`.
- Doğrulama: Tahmin ve yorum cümlelerinin taslakları Codex tarafından yazıldı; metinleri gözden geçirip kendi görüşüm olarak onayladım. Defter Run All ile çalıştırılıp çıktıları kaydedildi. Sayılar `sonuclar/temel_sonuclar.csv` ve `sonuclar/sonuc_tablosu.csv` ile karşılaştırıldı; `python betikler/dogrula.py` hatasız tamamlandı (yalnızca sunum dosyasının henüz bulunmadığı uyarısı var).
- Korunan içerik: `dervis_hsv_baseline` tahmini, notumdaki mevcut deney öncesi metin ve dondurulmuş ayarlar değiştirilmedi.
