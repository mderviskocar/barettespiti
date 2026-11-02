"""Renk maskesi kutu değerlendirmesi (hazır dedektör KULLANILMAZ).

Yöntem: RGB veya HSV renk aralığıyla sarı pikseller seçilir (cv2.inRange), küçük
gürültü 3x3 açma/kapama ile temizlenir, birbirine bağlı her sarı leke
(connected component) bir aday kutuya dönüştürülür. Kutular Nesli'nin elle
çizdiği gerçek baret kutularıyla src/metrics.py içinde IoU >= 0.50 kuralına göre
eşleştirilir.

Bu bir nesne dedektörü değildir: kutu yalnızca "sarı renkli bölge" demektir.
Baret ile aynı renkteki yelek, kova, testere de kutu üretir (FP); renk aralığı
dışında kalan karanlık baret kutu üretmez (FN). Confidence değeri yoktur.
"""

import cv2
import numpy as np


def color_mask(image_bgr, color_config):
    """Dondurulmuş RGB/HSV aralığıyla 0/255 maske üretir."""
    space = color_config["color_space"]
    if space == "RGB":
        pixels = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    elif space == "HSV_OPENCV_8BIT":
        pixels = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)  # H 0-179, S/V 0-255
    else:
        raise ValueError(f"Bilinmeyen renk uzayı: {space}")
    lower = np.array(color_config["lower"], dtype=np.uint8)
    upper = np.array(color_config["upper"], dtype=np.uint8)
    return cv2.inRange(pixels, lower, upper)


def clean_mask(mask, kernel_size):
    """Tek piksellik gürültüyü açma, küçük delikleri kapama ile temizler."""
    if not kernel_size:
        return mask
    kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)


def mask_to_boxes(mask, min_component_area_px):
    """Her bağlı bileşeni [xmin, ymin, xmax, ymax] (xmax/ymax hariç) kutusuna çevirir."""
    count, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    boxes = []
    for index in range(1, count):  # 0 = arka plan
        x, y, w, h, area = (int(v) for v in stats[index])
        if area >= min_component_area_px:
            boxes.append({"box": [x, y, x + w, y + h], "area_px": area})
    return sorted(boxes, key=lambda b: -b["area_px"])


def predict_boxes(image_bgr, color_config, box_config):
    """Maske -> temizlik -> bileşen kutuları. metrics.evaluate_boxes için liste döndürür."""
    mask = clean_mask(color_mask(image_bgr, color_config), box_config["morph_kernel_size"])
    components = mask_to_boxes(mask, box_config["min_component_area_px"])
    return mask, components


def draw_boxes(image_bgr, components, gt_boxes, evaluation, head_roi=None):
    """Gerçek kutu yeşil, TP mavi, FP kırmızı, baş ROI gri."""
    canvas = image_bgr.copy()
    thickness = max(1, round(max(canvas.shape[:2]) / 400))
    if head_roi is not None:
        x1, y1, x2, y2 = head_roi
        cv2.rectangle(canvas, (x1, y1), (x2 - 1, y2 - 1), (180, 180, 180), thickness)
    for box in gt_boxes:
        x1, y1, x2, y2 = box
        cv2.rectangle(canvas, (x1, y1), (x2 - 1, y2 - 1), (0, 200, 0), thickness + 1)
    tp_ids = {m["prediction_index"] for m in evaluation["matches"]}
    for index, comp in enumerate(components):
        x1, y1, x2, y2 = comp["box"]
        color = (255, 120, 0) if index in tp_ids else (0, 0, 255)
        cv2.rectangle(canvas, (x1, y1), (x2 - 1, y2 - 1), color, thickness)
    return canvas
