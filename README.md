# Baret Tespiti ve Sınıflandırması

YZM411 Bilgisayarlı Görü, 2026–2027 Güz dönemi. Altı kişilik ortak çalışma deposu.

**Durum:** Altı görüntü data/development ve data/control altına, dört sınıflı manuel ground truth ile eklendi. Üye görüntü işleme deneyleri ve ölçülmüş sonuçlar henüz eklenmemiştir. Kişisel notebook'lar başlangıç şablonudur; ortak demo deney uygulaması tamamlanana kadar bunu açıkça bildirir. Hazır dedektör isteğe bağlıdır.

## Yapı

~~~text
annotations/ground_truth.json       # Manuel sınıflar, baş ROI ve gerçek baret kutuları
configs/                           # Ortak karar, RGB, HSV, blur, ölçek ve dedektör ayarları
data/development/                   # G1 ve G2
data/control/                       # K1, K2, K3 ve K4
data/sources.csv                    # Kaynak, lisans, koşul, yol ve özgün boyutlar
docs/                              # Deney protokolü, ön tahminler ve yapay zekâ beyanı
individual_notes/                  # Altı kişisel not şablonu
models/model_source.md              # İsteğe bağlı modelin indirme ve lisans bilgileri
notebooks/main_demo.ipynb            # Ortak görüntü seçimi, maske ve sınıf kararı akışı
notebooks/<uye>_<deney>.ipynb        # Altı bağımsız deney notebook'u
results/results.csv                 # Ortak nihai sonuç tablosu
results/masks/rgb/                  # Dört temel RGB maskesi
results/masks/hsv/                  # Dört temel HSV maskesi
results/gaussian_blur/              # Bulanıklık tablosu ve görselleri
results/scale/                      # Ölçek tablosu ve görselleri
results/detector/                   # İsteğe bağlı kutu değerlendirmesi
src/                               # Üye modülleri ve ortak veri/demo yardımcıları
presentation/                      # En fazla altı slayt ve çevrimdışı kayıt
~~~

## Kurulum

Python 3.10 veya üzeri gerekir. Windows PowerShell'de depo kökünden:

~~~powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/validate_project.py
.\.venv\Scripts\python.exe -m jupyterlab
~~~

Kendi notebook'unuzu veya notebooks/main_demo.ipynb dosyasını açın. Notebook'lar depo kökünden veya notebooks klasöründen çalışabilir. Çalışan deney ortamı doğrulandıktan sonra bağımlılık sürümleri ayrıca sabitlenmelidir.

## Ekip sahipliği

| Üye | Branch | Ana dosyalar |
| --- | --- | --- |
| Nesli | feat/dataset-groundtruth | data/, annotations/, notebooks/nesli_dataset_analysis.ipynb |
| Omar | feat/rgb-segmentation | src/rgb.py, configs/rgb_config.json, notebooks/omar_rgb.ipynb |
| Derviş | feat/hsv-segmentation | src/hsv.py, configs/hsv_config.json, notebooks/dervis_hsv.ipynb |
| Ahmet | feat/gaussian-blur | src/gaussian_blur.py, configs/gaussian_blur.json, notebooks/ahmet_gaussian_blur.ipynb |
| Efe | feat/scale-analysis | src/scale.py, configs/scale_config.json, notebooks/efe_scale.ipynb |
| Murathan | feat/detector-evaluation | src/detection.py, src/metrics.py, notebooks/murathan_detection.ipynb |

Omar ve Derviş src/classification.py karar sözleşmesinin teknik sahipleridir; Nesli etiketleri doğrular ve ortak demo entegrasyonunu koordine eder. Her üye kendi bireysel notunu ve deney öncesi tahminini tamamlar.

## Ortak sözleşme

- Kimlikler: **G1, G2, K1, K2, K3, K4**. Ayrım: development/control.
- Sınıflar: helmet_on_head, helmet_off_head, no_helmet, uncertain.
- Kaynakların tek kaynağı data/sources.csv; gerçek sınıf ve kutuların tek kaynağı annotations/ground_truth.json.
- Alan ve baş örtüşmesi tüm sonuçlarda **0–100 arası yüzde**. Ölçülmeyen/uygulanmayan metrik N/A; sıfır değildir.
- RGB/HSV ayarları yalnızca geliştirmede seçilir; kontrol öncesinde renk ve ortak karar ayarları frozen=true yapılır.
- Kaynak ve lisans bilgisi mevcut olduğunda kaydedilir; bilinmeyen değerler uydurulmaz. Ayrıntılar: [veri sözleşmesi](data/README.md).

## GitHub akışı

Her üye için ayrı çalışma branch'i hazırdır. Main'e doğrudan push açıktır; PR veya inceleme onayı zorunlu değildir. Başlangıç, güncelleme ve birleştirme komutları [CONTRIBUTING.md](CONTRIBUTING.md) içindedir. Davet kabulü üyelerin kendi hesaplarından yapılır.

## Doğrulama ve teslim

~~~powershell
.\.venv\Scripts\python.exe scripts/validate_project.py
# Altı görüntü ve etiketler eklendiğinde:
.\.venv\Scripts\python.exe scripts/validate_project.py --require-data
~~~

Deney sırası: [protokol](docs/experiment_protocol.md). Sunum: [sunum planı](presentation/README.md). Yapay zekâ: [beyan](docs/ai_usage.md).

Sunum **4 Kasım 2026**; nihai teslim sunumdan en az 24 saat önce grup liderinin GitHub deposunda olmalıdır. Altı görüntülük eğitim prototipinden gerçek işyeri güvenilirliği sonucu çıkarılmaz.

Ödevde verilen veri kaynağı: https://universe.roboflow.com/ml-pzfty/chv-dataset
