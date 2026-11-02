"""metrics.py için küçük birim testleri: python tests/test_metrics.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.metrics import evaluate_boxes, iou  # noqa: E402

K2_GT = [981, 94, 1070, 165]          # ground_truth.json -> K2 helmet_boxes[0]
K3_GT = [[1094, 859, 1135, 908], [1633, 963, 1658, 1005]]


def test_iou_basics():
    assert iou([0, 0, 10, 10], [0, 0, 10, 10]) == 1.0
    assert iou([0, 0, 10, 10], [20, 20, 30, 30]) == 0.0
    # 10x10 ve 5 piksel kaydırılmış: kesişim 50, birleşim 150
    assert abs(iou([0, 0, 10, 10], [5, 0, 15, 10]) - 1 / 3) < 1e-9


def test_exact_match_is_tp():
    result = evaluate_boxes([{"box": K2_GT, "confidence": 0.9}], [K2_GT])
    assert (result["tp"], result["fp"], result["fn"]) == (1, 0, 0)


def test_one_gt_counted_once():
    # Aynı baret için iki kutu: biri TP, diğeri FP olmalı (çift sayım yok)
    preds = [{"box": K2_GT, "confidence": 0.9}, {"box": [982, 95, 1071, 166], "confidence": 0.6}]
    result = evaluate_boxes(preds, [K2_GT])
    assert (result["tp"], result["fp"], result["fn"]) == (1, 1, 0)
    assert result["matches"][0]["prediction_index"] == 0  # yüksek confidence önce eşleşir


def test_low_iou_is_fp_and_fn():
    shifted = [1030, 94, 1119, 165]  # yarım kutu kaydırma -> IoU < 0.5
    result = evaluate_boxes([shifted], [K2_GT])
    assert (result["tp"], result["fp"], result["fn"]) == (0, 1, 1)


def test_missed_small_helmet_is_fn():
    result = evaluate_boxes([{"box": K3_GT[0], "confidence": 0.7}], K3_GT)
    assert (result["tp"], result["fp"], result["fn"]) == (1, 0, 1)
    assert result["false_negative_gt_indices"] == [1]


def test_no_gt_any_prediction_is_fp():
    result = evaluate_boxes([[10, 10, 50, 50]], [])
    assert (result["tp"], result["fp"], result["fn"]) == (0, 1, 0)
    assert evaluate_boxes([], [])["tp"] == 0


if __name__ == "__main__":
    for name, func in list(globals().items()):
        if name.startswith("test_"):
            func()
            print("OK", name)
