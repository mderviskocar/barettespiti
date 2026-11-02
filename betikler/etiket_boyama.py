"""Fırça ile piksel düzeyi gerçek etiket (ground truth) maskesi boyama aracı.

Orijinal görüntüler üzerinde baret ve baş bölgelerini elle boyar; maskeler
etiketler/maskeler/<ID>_baret.png ve etiketler/maskeler/<ID>_bas.png olarak,
görüntüyle aynı çözünürlükte (0/255) kaydedilir. Baret kutuları ve baş ROI bu
maskelerden otomatik çıkarılır. Maskeler YALNIZCA gerçek etikettir; renk eşiği
ayarında kullanılmaz.

Boyama kuralı:
  1 (baret) : yalnızca baretin kendisi (kubbe + siperlik); kayış ve gölge hariç.
              Her bareti tek parça boyayın.
  2 (baş)   : hedef kişinin başı; baret takılıysa baretin oturduğu bölge DAHİL
              (saç, yüz, kulaklar). Görünmeyen başı boyamayın.

Kullanım:  python betikler/etiket_boyama.py            (6 görüntünün hepsi)
           python betikler/etiket_boyama.py K2 K3      (seçili görüntüler)

Kontroller:
  Sol fare (sürükle) : boya            Sağ fare (sürükle) : sil
  1 : baret katmanı (sarı)             2 : baş katmanı (mavi)
  ] / [ : fırçayı büyüt / küçült       z : geri al
  c : aktif katmanı temizle            m : katmanları göster/gizle
  s : kaydet                           n / p : sonraki / önceki görüntü (otomatik kaydeder)
  q veya Esc : kaydet ve çık
"""
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MASK_DIR = ROOT / "etiketler" / "maskeler"
IMAGE_DIRS = [ROOT / "veri" / "gelistirme", ROOT / "veri" / "kontrol",
              ROOT / "data" / "development", ROOT / "data" / "control"]
LAYERS = {"baret": (0, 215, 255), "bas": (255, 120, 0)}  # BGR katman renkleri


def load_dataset():
    """G1, G2, K1-K4 görüntülerini (yeni ya da eski klasör yapısından) bulur."""
    found = {}
    for folder in IMAGE_DIRS:
        for path in sorted(folder.glob("*.jpg")):
            found.setdefault(path.stem, path)
    order = ["G1", "G2", "K1", "K2", "K3", "K4"]
    return [{"image_id": key, "path": found[key]} for key in order if key in found]


def load_image(path):
    image = cv2.imdecode(np.frombuffer(path.read_bytes(), dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Görüntü okunamadı: {path}")
    return image
MAX_VIEW = (1400, 850)  # ekrana sığdırma sınırı (genişlik, yükseklik)


def mask_path(image_id, layer):
    return MASK_DIR / f"{image_id}_{layer}.png"


def read_mask(path, shape):
    if path.is_file():
        data = np.frombuffer(path.read_bytes(), dtype=np.uint8)
        mask = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
        if mask is not None and mask.shape == shape:
            return (mask > 127).astype(np.uint8) * 255
    return np.zeros(shape, dtype=np.uint8)


def write_mask(path, mask):
    path.parent.mkdir(parents=True, exist_ok=True)
    ok, encoded = cv2.imencode(".png", mask)
    if not ok:
        raise RuntimeError(f"Maske yazılamadı: {path}")
    path.write_bytes(encoded.tobytes())


class Painter:
    def __init__(self, record):
        self.id = record["image_id"]
        self.image = load_image(record["path"])
        h, w = self.image.shape[:2]
        self.scale = min(1.0, MAX_VIEW[0] / w, MAX_VIEW[1] / h)
        self.masks = {name: read_mask(mask_path(self.id, name), (h, w)) for name in LAYERS}
        self.layer = "baret"
        self.brush = max(2, round(max(h, w) / 200))
        self.history = []
        self.drawing = None
        self.show = True
        self.cursor = None

    def to_image(self, x, y):
        return int(x / self.scale), int(y / self.scale)

    def stroke(self, x, y, value):
        cv2.circle(self.masks[self.layer], (x, y), self.brush, value, -1)

    def on_mouse(self, event, x, y, flags, _):
        ix, iy = self.to_image(x, y)
        self.cursor = (x, y)
        if event in (cv2.EVENT_LBUTTONDOWN, cv2.EVENT_RBUTTONDOWN):
            self.history.append((self.layer, self.masks[self.layer].copy()))
            self.history = self.history[-30:]
            self.drawing = 255 if event == cv2.EVENT_LBUTTONDOWN else 0
            self.stroke(ix, iy, self.drawing)
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing is not None:
            self.stroke(ix, iy, self.drawing)
        elif event in (cv2.EVENT_LBUTTONUP, cv2.EVENT_RBUTTONUP):
            self.drawing = None

    def render(self):
        view = self.image.copy()
        if self.show:
            for name, color in LAYERS.items():
                selected = self.masks[name] > 0
                view[selected] = (0.45 * view[selected] + 0.55 * np.array(color)).astype(np.uint8)
        if self.scale != 1.0:
            view = cv2.resize(view, None, fx=self.scale, fy=self.scale, interpolation=cv2.INTER_AREA)
        if self.cursor:
            cv2.circle(view, self.cursor, max(1, int(self.brush * self.scale)), LAYERS[self.layer], 1)
        text = f"{self.id} | katman: {self.layer} (1 baret, 2 bas) | firca: {self.brush}px | s kaydet, n/p gec, q cik"
        cv2.rectangle(view, (0, 0), (view.shape[1], 26), (0, 0, 0), -1)
        cv2.putText(view, text, (8, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        return view

    def save(self):
        for name, mask in self.masks.items():
            write_mask(mask_path(self.id, name), mask)
        pixels = {name: int(np.count_nonzero(mask)) for name, mask in self.masks.items()}
        print(f"{self.id} kaydedildi: baret={pixels['baret']} px, baş={pixels['bas']} px")


def main(selected):
    records = [r for r in load_dataset() if not selected or r["image_id"] in selected]
    if not records:
        raise SystemExit("Görüntü bulunamadı.")
    window = "Etiket boyama"
    cv2.namedWindow(window, cv2.WINDOW_AUTOSIZE)
    index = 0
    painter = Painter(records[index])
    cv2.setMouseCallback(window, painter.on_mouse)
    while True:
        cv2.imshow(window, painter.render())
        key = cv2.waitKey(20) & 0xFF
        if key in (ord("q"), 27):
            painter.save()
            break
        if key == ord("1"):
            painter.layer = "baret"
        elif key == ord("2"):
            painter.layer = "bas"
        elif key == ord("]"):
            painter.brush += 1
        elif key == ord("[") and painter.brush > 1:
            painter.brush -= 1
        elif key == ord("z") and painter.history:
            layer, previous = painter.history.pop()
            painter.masks[layer] = previous
        elif key == ord("c"):
            painter.history.append((painter.layer, painter.masks[painter.layer].copy()))
            painter.masks[painter.layer][:] = 0
        elif key == ord("m"):
            painter.show = not painter.show
        elif key == ord("s"):
            painter.save()
        elif key in (ord("n"), ord("p")):
            painter.save()
            index = (index + (1 if key == ord("n") else -1)) % len(records)
            painter = Painter(records[index])
            cv2.setMouseCallback(window, painter.on_mouse)
        if cv2.getWindowProperty(window, cv2.WND_PROP_VISIBLE) < 1:
            painter.save()
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main(set(sys.argv[1:]))
