# Baret Tespiti ve Sınıflandırması

YZM411 Bilgisayarlı Görü, 2026–2027 Güz dönemi grup projesi.

Bu depo, altı bağımsız görüntü üzerinde renk tabanlı baret tespiti ve dört sınıflı karar verme çalışması için hazırlanmıştır. **Şu an yalnızca proje iskeleti bulunur; veri, tamamlanmış deney kodu ve ölçülmüş sonuç yoktur.** Sıfırdan model eğitimi kapsamda değildir. Hazır dedektör karşılaştırması isteğe bağlıdır.

## Proje yapısı

```text
barettespiti/
├── configs/experiment.json        # Geliştirme sırasında seçilip sabitlenecek ayarlar
├── data/
│   ├── raw/development/           # 2 bağımsız geliştirme görüntüsü
│   ├── raw/control/               # 4 bağımsız kontrol görüntüsü
│   ├── annotations/               # Kaynaklar, doğru sınıflar ve elle çizilen kutular
│   └── README.md                  # Veri ve etiketleme sözleşmesi
├── docs/
│   ├── experiment_protocol.md     # Deney sırası ve değerlendirme kuralları
│   ├── predictions.csv            # Deney çalıştırılmadan önce yazılacak tahminler
│   ├── member_note_template.md    # Kişisel deney notu şablonu
│   └── ai_usage.md                # Yapay zekâ kullanım beyanı
├── notebooks/01_experiments.ipynb  # Deney akışının başlangıç şablonu
├── src/baret_tespiti/             # İleride yazılacak ortak görüntü işleme kodu
├── outputs/
│   ├── figures/                   # Maskeler, karşılaştırmalar ve kutulu görseller
│   └── results.csv                # Ölçülmüş sonuç tablosu; şimdilik yalnızca başlık
├── presentation/                  # En fazla 6 slayt ve çevrimdışı kayıt
├── requirements.txt
├── .gitattributes
└── .gitignore
```

## Ortamı hazırlama

Python 3.10 veya üzeri ve Git gerekir. Windows PowerShell için:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m jupyterlab
```

Notebook'u `notebooks/01_experiments.ipynb` üzerinden açın. `src` altındaki kod, uygulama aşamasında notebook'tan çağrılacaktır. Bağımlılık sürümleri henüz sabitlenmemiştir; çalışan ortam doğrulandıktan sonra kullanılan sürümler kaydedilmelidir.

## Çalışma sırası

1. Altı bağımsız görüntüyü seçin; geliştirme/kontrol ayrımını ve kaynaklarını kaydedin.
2. Yöntemleri çalıştırmadan önce doğru sınıfları ve gerekli baş bölgelerini etiketleyin.
3. Her deney için iki cümlelik tahmini `docs/predictions.csv` içine önceden yazın.
4. RGB/HSV eşiklerini ve karar kurallarını yalnızca geliştirme görüntülerinde belirleyin; sonra ayarları sabitleyin.
5. Kontrol görüntülerinde RGB ve HSV için toplam sekiz temel maskeyi, alan oranlarını ve sınıf kararlarını ölçün.
6. Bulanıklık ve küçültmeyi ayrı deneylerde inceleyin; bir yanlış alarmı ve bir kaçırmayı açıklayın.
7. İstenirse hazır dedektör karşılaştırmasını ekleyin; kaynak ve değerlendirme bilgilerini kaydedin.
8. Sonuç tablosunu, sunumu, bireysel notları ve yapay zekâ beyanını tamamlayın.

Ayrıntılar: [deney protokolü](docs/experiment_protocol.md), [veri kuralları](data/README.md), [sunum planı](presentation/README.md).

## Teslim

Belgede sunum tarihi **4 Kasım 2026** olarak verilmiştir. Dosyalar sunumdan en az 24 saat önce grup liderinin GitHub deposuna yüklenmelidir; kesin saat sunum saatine bağlıdır. Yerel Git deposunun oluşturulması GitHub'a yükleme yapıldığı anlamına gelmez.

Kaynak veri adresi: https://universe.roboflow.com/ml-pzfty/chv-dataset

Bu çalışma eğitim prototipidir; altı görüntüden gerçek işyeri güvenilirliği sonucu çıkarılmaz.
