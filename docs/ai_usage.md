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

## Omar — RGB deneyi

- Araç: Claude Code (Anthropic).
- Amaç: RGB maske ve ortak karar kuralını uygulamak, aralığı G1/G2 üzerinde seçmek, ön tahmini kaydetmek, ayarları dondurmak, K1–K4 sonuçlarını üretmek, %2 alan eşiğinin dayanağını belgelemek, ekip ortak ayarına (Nesli'nin dondurduğu aralık ve eşikler) geçip kontrolü yeniden çalıştırmak ve notebook ile bireysel notu doldurmak.
- Etkilenen dosyalar: `src/rgb.py`, `src/classification.py`, `configs/rgb_config.json`, `configs/experiment.json`, `docs/predictions.csv`, `results/rgb_results.csv`, `results/masks/rgb/`, `notebooks/omar_rgb.ipynb`, `individual_notes/omar.md`.
- Ön tahmin: İki cümlelik tahmin taslağı Claude Code tarafından yazıldı; Omar ilk kontrol çalıştırmasından önce onayladı ve kayda alındı.
- Doğrulama: Aralık adayları yalnızca G1/G2 üzerinde karşılaştırıldı. Kontrol görüntüleri ayarlar dondurulduktan sonra çalıştırıldı; ilk çalıştırma Omar'ın aralığıyla, ikincisi ortak ayarla yapıldı (ayrıntı bireysel notta). Ortak ayarla elde edilen değerler Nesli'nin yayımladığı temel ölçümlerle eşleşti. K2 baret rengi, G2 dışı piksel oranı ve K4 baret konumu doğrudan piksel ve kutu koordinatı ölçümüyle denetlendi. `scripts/validate_project.py` hatasız tamamlandı.
- Sınır: Karar kuralının eşikleri Derviş ile birlikte gözden geçirilmelidir; %2,5 alan eşiği G1/G2'den ayarlanamadı. K4 sonucu eşiğe yakındır ve örtüşme elde tutulan baretten gelmemektedir.
