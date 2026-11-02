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
