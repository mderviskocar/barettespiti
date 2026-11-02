"""Renk maskesi kutu değerlendirmesi: RGB ve HSV maskelerinden kutu -> TP/FP/FN.

Kullanım:  python scripts/evaluate_color_mask_boxes.py            (K1-K4 kontrol)
           python scripts/evaluate_color_mask_boxes.py development (G1-G2, yalnız ayar kontrolü)
Kontrol çıktıları:
    results/detector/detection_results.csv   (ortak sonuç şeması, 8 satır)
    results/detector/raw_mask_boxes.json      (tüm kutular, IoU ve eşleşmeler)
    results/detector/<ID>_<rgb|hsv>_boxes.png  (görseller)
Ayarlar configs/detector_config.json (mask_box) ve configs/{rgb,hsv}_config.json içinde
dondurulmuştur; kontrol görüntülerinde değiştirilmez.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import cv2  # noqa: E402

from src.common import load_config, load_dataset, load_image, write_results  # noqa: E402
from src.detection import draw_boxes, predict_boxes  # noqa: E402
from src.metrics import evaluate_boxes  # noqa: E402

EXPERIMENT_ID = "color_mask_box_eval"
OUT_DIR = Path("results/detector")


def run(split="control", write_outputs=True):
    settings = load_config("detector_config.json")
    box_config = settings["mask_box"]
    if not box_config.get("frozen"):
        raise SystemExit("mask_box ayarları dondurulmamış.")
    threshold = settings["evaluation_iou_threshold"]
    rows, raw = [], {}
    for record in load_dataset(split):
        image = load_image(record["relative_path"])
        gt_boxes = record["helmet_boxes"]
        raw[record["image_id"]] = {"gt_helmet_boxes": gt_boxes}
        for color_file in box_config["color_configs"]:
            color_config = load_config(color_file)
            method = "rgb" if color_config["color_space"] == "RGB" else "hsv"
            if not color_config.get("frozen"):
                raise SystemExit(f"{color_file} dondurulmamış.")
            _, components = predict_boxes(image, color_config, box_config)
            evaluation = evaluate_boxes(components and [{"box": c["box"]} for c in components],
                                        gt_boxes, threshold)
            ious = ", ".join(f"{m['iou']:.2f}" for m in evaluation["matches"]) or "-"
            parameter = (f"{method.upper()} lower={color_config['lower']} upper={color_config['upper']}; "
                         f"morph={box_config['morph_kernel_size']}x{box_config['morph_kernel_size']}; "
                         f"min_area={box_config['min_component_area_px']}px; eval_iou={threshold}")
            rows.append({
                "experiment_id": EXPERIMENT_ID,
                "image_id": record["image_id"],
                "method": f"{method}_mask_boxes",
                "condition": record["condition"],
                "parameter": parameter,
                "mask_area_percent": "N/A",
                "head_overlap_percent": "N/A",
                "predicted_class": "N/A",
                "ground_truth_class": record["ground_truth_class"],
                "correct": "N/A",
                "tp": evaluation["tp"],
                "fp": evaluation["fp"],
                "fn": evaluation["fn"],
                "note": (f"GT baret kutusu={len(gt_boxes)}; maske kutusu={len(components)}; "
                         f"eşleşen IoU: {ious}. Renk maskesi kutu değerlendirmesi; hazır dedektör "
                         "sonucu değildir. Kutu düzeyi sayım, dört sınıflı karar ayrıdır."),
            })
            raw[record["image_id"]][method] = {"components": components, "evaluation": evaluation}
            print(f"{record['image_id']} {method.upper()}: kutu={len(components):3d} "
                  f"TP={evaluation['tp']} FP={evaluation['fp']} FN={evaluation['fn']} IoU={ious}")
            if write_outputs:
                canvas = draw_boxes(image, components, gt_boxes, evaluation, record.get("head_roi"))
                (ROOT / OUT_DIR).mkdir(parents=True, exist_ok=True)
                ok, encoded = cv2.imencode(".png", canvas)
                name = f"{record['image_id']}_{method}_boxes.png"
                (ROOT / OUT_DIR / name).write_bytes(encoded.tobytes())
    for method in ("rgb", "hsv"):
        subset = [r for r in rows if r["method"] == f"{method}_mask_boxes"]
        print(f"TOPLAM {method.upper()}: TP={sum(r['tp'] for r in subset)} "
              f"FP={sum(r['fp'] for r in subset)} FN={sum(r['fn'] for r in subset)}")
    if write_outputs and split == "control":
        write_results(rows, OUT_DIR / "detection_results.csv")
        (ROOT / OUT_DIR / "raw_mask_boxes.json").write_text(
            json.dumps({"settings": settings, "images": raw}, indent=2, ensure_ascii=False),
            encoding="utf-8")
    return rows, raw


if __name__ == "__main__":
    chosen = sys.argv[1] if len(sys.argv) > 1 else "control"
    run(chosen, write_outputs=(chosen == "control"))
