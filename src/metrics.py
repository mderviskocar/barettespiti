"""Kutu düzeyi değerlendirme: IoU, bire bir eşleştirme ve TP/FP/FN sayımı.

Koordinat biçimi ground_truth.json ile aynıdır: [xmin, ymin, xmax, ymax], piksel,
xmax/ymax hariç (exclusive). Bu nedenle genişlik = xmax - xmin (+1 yok).

Kural (görev dağılımı, bölüm 07):
- IoU >= 0.50 olan eşleşme TP,
- hiçbir gerçek kutuyla eşleşmeyen tahmin FP,
- hiçbir tahminle eşleşmeyen gerçek kutu FN,
- bir gerçek kutu en fazla bir kez TP sayılır (bire bir eşleştirme).

Confidence yalnızca eşleştirme sırasını belirler; doğruluk oranı değildir.
"""

ALLOWED_PREDICTION_KEYS = {"box", "class", "confidence"}


def _validate_box(box):
    if box is None or len(box) != 4:
        raise ValueError(f"Kutu dört koordinat içermeli: {box!r}")
    xmin, ymin, xmax, ymax = (float(value) for value in box)
    if xmax <= xmin or ymax <= ymin:
        raise ValueError(f"Kutu boyutu pozitif olmalı: {box!r}")
    return xmin, ymin, xmax, ymax


def box_area(box):
    xmin, ymin, xmax, ymax = _validate_box(box)
    return (xmax - xmin) * (ymax - ymin)


def iou(box_a, box_b):
    """İki kutunun kesişim / birleşim oranı (0-1)."""
    ax1, ay1, ax2, ay2 = _validate_box(box_a)
    bx1, by1, bx2, by2 = _validate_box(box_b)
    inter_w = max(0.0, min(ax2, bx2) - max(ax1, bx1))
    inter_h = max(0.0, min(ay2, by2) - max(ay1, by1))
    intersection = inter_w * inter_h
    union = box_area(box_a) + box_area(box_b) - intersection
    return intersection / union if union > 0 else 0.0


def _normalize_predictions(predictions):
    """Tahminleri {"box", "class", "confidence"} sözlüklerine çevirir."""
    normalized = []
    for index, item in enumerate(predictions):
        if isinstance(item, dict):
            unknown = set(item) - ALLOWED_PREDICTION_KEYS
            if unknown:
                raise ValueError(f"Bilinmeyen tahmin alanı: {sorted(unknown)}")
            box = item["box"]
            confidence = item.get("confidence")
            label = item.get("class", "helmet")
        else:  # yalnızca kutu verilmişse
            box, confidence, label = item, None, "helmet"
        _validate_box(box)
        normalized.append({
            "index": index,
            "box": [float(value) for value in box],
            "class": label,
            "confidence": None if confidence is None else float(confidence),
        })
    return normalized


def evaluate_boxes(predictions, ground_truth, iou_threshold=0.5):
    """Baret tahminlerini elle çizilmiş gerçek baret kutularıyla karşılaştırır.

    predictions: [{"box": [x1,y1,x2,y2], "class": "helmet", "confidence": 0.8}, ...]
                 ya da yalnızca kutu listesi. Hepsi baret sınıfı kabul edilir;
                 baret dışı sınıflar (ör. "head", "no_helmet") çağırmadan önce ayıklanmalıdır.
    ground_truth: [[x1,y1,x2,y2], ...]  (ground_truth.json -> helmet_boxes)

    Eşleştirme: tahminler confidence'a göre büyükten küçüğe sıralanır (confidence
    yoksa verildiği sırayla); her tahmin, henüz eşleşmemiş gerçek kutular arasında
    en yüksek IoU'ya sahip olanla, IoU >= eşik ise eşleşir.
    """
    if not 0.0 < iou_threshold <= 1.0:
        raise ValueError("IoU eşiği (0, 1] aralığında olmalı.")
    preds = _normalize_predictions(predictions)
    gts = [[float(value) for value in _validate_box(box)] for box in ground_truth]

    order = sorted(
        preds,
        key=lambda p: (-(p["confidence"] if p["confidence"] is not None else 0.0), p["index"]),
    )
    gt_used = [False] * len(gts)
    matches, false_positives = [], []
    for pred in order:
        best_iou, best_gt = 0.0, None
        for gt_index, gt_box in enumerate(gts):
            if gt_used[gt_index]:
                continue
            value = iou(pred["box"], gt_box)
            if value > best_iou:
                best_iou, best_gt = value, gt_index
        if best_gt is not None and best_iou >= iou_threshold:
            gt_used[best_gt] = True
            matches.append({"prediction_index": pred["index"], "gt_index": best_gt,
                            "iou": best_iou, "confidence": pred["confidence"]})
        else:
            false_positives.append({"prediction_index": pred["index"], "best_iou": best_iou,
                                    "confidence": pred["confidence"]})
    false_negatives = [index for index, used in enumerate(gt_used) if not used]
    return {
        "tp": len(matches),
        "fp": len(false_positives),
        "fn": len(false_negatives),
        "iou_threshold": iou_threshold,
        "matches": matches,
        "false_positives": false_positives,
        "false_negative_gt_indices": false_negatives,
    }
