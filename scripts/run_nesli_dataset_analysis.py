"""Run Nesli's frozen RGB/HSV baseline on the four control images.

This is a small color-segmentation baseline, not a trained helmet detector.
Thresholds and the class rule are calibrated on G1/G2 only.
"""

import csv
import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_ID = "nesli_rgb_hsv_baseline"
CLASSES = ("helmet_on_head", "helmet_off_head", "no_helmet", "uncertain")
RESULT_FIELDS = (
    "experiment_id", "image_id", "method", "condition", "parameter",
    "mask_area_percent", "head_overlap_percent", "predicted_class",
    "ground_truth_class", "correct", "tp", "fp", "fn", "note",
)


def _json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _csv(path):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _mask(image_bgr, method, config):
    lower = np.asarray(config["lower"], dtype=np.uint8)
    upper = np.asarray(config["upper"], dtype=np.uint8)
    if method == "rgb":
        pixels = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    elif method == "hsv":
        pixels = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    else:
        raise ValueError(f"Unsupported color method: {method}")
    return cv2.inRange(pixels, lower, upper)


def _measure(mask, head_roi):
    selected = mask != 0
    area_percent = 100.0 * np.count_nonzero(selected) / selected.size
    if head_roi is None:
        return area_percent, "N/A"
    xmin, ymin, xmax, ymax = head_roi
    roi = selected[ymin:ymax, xmin:xmax]
    overlap_percent = 100.0 * np.count_nonzero(roi) / roi.size
    return area_percent, overlap_percent


def _classify(area_percent, overlap_percent, head_roi, decision):
    if head_roi is None:
        return "uncertain"
    if area_percent < decision["min_color_area_percent"]:
        return "no_helmet"
    if overlap_percent >= decision["min_head_overlap_percent"]:
        return "helmet_on_head"
    return "helmet_off_head"


def _format_parameter(method, config, decision):
    return (
        f"baseline; {method.upper()} lower={config['lower']} upper={config['upper']}; "
        f"min_color_area_percent={decision['min_color_area_percent']}; "
        f"min_head_overlap_percent={decision['min_head_overlap_percent']}"
    )


def _render_annotation_previews(images, labels):
    destination = ROOT / "annotations" / "previews"
    destination.mkdir(parents=True, exist_ok=True)
    by_id = {item["image_id"]: item for item in labels}
    outputs = []
    for source in images:
        image_id = source["image_id"]
        image = cv2.imread(str(ROOT / source["relative_path"]), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"Cannot decode {source['relative_path']}")
        header = 56
        canvas = cv2.copyMakeBorder(
            image, header, 0, 0, 0, cv2.BORDER_CONSTANT, value=(248, 248, 248)
        )
        label = by_id[image_id]
        cv2.putText(
            canvas,
            f"{image_id} | GT: {label['ground_truth_class']}",
            (12, 23),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (20, 20, 20),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            canvas,
            "Blue: head ROI   Green: visible hard hat",
            (12, 46),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (50, 50, 50),
            1,
            cv2.LINE_AA,
        )
        roi = label["head_roi"]
        if roi is None:
            cv2.putText(
                canvas,
                "Head not visible; no head box assigned",
                (12, header + 24),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 180, 0),
                2,
                cv2.LINE_AA,
            )
        else:
            x1, y1, x2, y2 = roi
            cv2.rectangle(canvas, (x1, y1 + header), (x2 - 1, y2 + header - 1),
                          (255, 180, 0), 3)
            cv2.putText(canvas, "HEAD ROI", (x1, max(header + 18, y1 + header - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 180, 0), 2, cv2.LINE_AA)
        for index, box in enumerate(label["helmet_boxes"], start=1):
            x1, y1, x2, y2 = box
            cv2.rectangle(canvas, (x1, y1 + header), (x2 - 1, y2 + header - 1),
                          (0, 190, 0), 3)
            cv2.putText(canvas, f"H{index}", (x1 + 3, y2 + header - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 150, 0), 1, cv2.LINE_AA)
        output = destination / f"{image_id}_ground_truth.png"
        if not cv2.imwrite(str(output), canvas):
            raise OSError(f"Could not write {output}")
        outputs.append(output.relative_to(ROOT).as_posix())
    return outputs


def _merge_result_file(path, new_rows):
    old_rows = []
    if path.exists():
        with path.open(encoding="utf-8-sig", newline="") as handle:
            old_rows = list(csv.DictReader(handle))
    old_rows = [row for row in old_rows
                if row.get("experiment_id") != EXPERIMENT_ID]
    combined = old_rows + new_rows
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        writer.writerows(combined)


def run_analysis(write_outputs=True):
    sources = _csv(ROOT / "data" / "sources.csv")
    labels = _json("annotations/ground_truth.json")["images"]
    source_by_id = {item["image_id"]: item for item in sources}
    label_by_id = {item["image_id"]: item for item in labels}
    configs = {
        method: _json(f"configs/{method}_config.json")
        for method in ("rgb", "hsv")
    }
    decision = _json("configs/experiment.json")["decision_rule"]
    if not all(config["frozen"] and config["status"] == "configured"
               for config in configs.values()):
        raise ValueError("RGB and HSV configs must be frozen before analysis.")
    if not decision["frozen"] or decision["status"] != "configured":
        raise ValueError("The shared class decision rule must be frozen.")

    calibration = []
    for image_id in ("G1", "G2"):
        image = cv2.imread(str(ROOT / source_by_id[image_id]["relative_path"]))
        if image is None:
            raise ValueError(f"Cannot decode development image {image_id}")
        annotation = label_by_id[image_id]
        for method, config in configs.items():
            mask = _mask(image, method, config)
            area, overlap = _measure(mask, annotation["head_roi"])
            calibration.append({
                "image_id": image_id,
                "method": method,
                "mask_area_percent": area,
                "head_overlap_percent": overlap,
                "ground_truth_class": annotation["ground_truth_class"],
            })

    for method in configs:
        development_by_id = {
            item["image_id"]: item for item in calibration if item["method"] == method
        }
        negative = development_by_id["G1"]
        positive = development_by_id["G2"]
        if not (
            negative["mask_area_percent"] < decision["min_color_area_percent"]
            <= positive["mask_area_percent"]
            and negative["head_overlap_percent"] < decision["min_head_overlap_percent"]
            <= positive["head_overlap_percent"]
        ):
            raise ValueError(
                f"{method.upper()} frozen class thresholds do not separate G1/G2 "
                "development examples."
            )

    rows_by_method = {"rgb": [], "hsv": []}
    control_measurements = []
    for image_id in ("K1", "K2", "K3", "K4"):
        source = source_by_id[image_id]
        annotation = label_by_id[image_id]
        image = cv2.imread(str(ROOT / source["relative_path"]))
        if image is None:
            raise ValueError(f"Cannot decode control image {image_id}")
        height, width = image.shape[:2]
        if (width, height) != (int(source["width"]), int(source["height"])):
            raise ValueError(f"CSV dimensions do not match image {image_id}")
        for method, config in configs.items():
            mask = _mask(image, method, config)
            area, overlap = _measure(mask, annotation["head_roi"])
            predicted = _classify(area, overlap, annotation["head_roi"], decision)
            overlap_value = None if overlap == "N/A" else overlap
            row = {
                "experiment_id": EXPERIMENT_ID,
                "image_id": image_id,
                "method": f"{method}_color_mask",
                "condition": source["condition"],
                "parameter": _format_parameter(method, config, decision),
                "mask_area_percent": f"{area:.4f}",
                "head_overlap_percent": "N/A" if overlap == "N/A" else f"{overlap:.4f}",
                "predicted_class": predicted,
                "ground_truth_class": annotation["ground_truth_class"],
                "correct": str(predicted == annotation["ground_truth_class"]).lower(),
                "tp": "N/A",
                "fp": "N/A",
                "fn": "N/A",
                "note": "Class prediction uses the frozen color-area/head-overlap rule; box-level detection was not evaluated.",
            }
            rows_by_method[method].append(row)
            control_measurements.append({
                "image_id": image_id,
                "method": method,
                "condition": source["condition"],
                "mask_area_percent": area,
                "head_overlap_percent": overlap,
                "predicted_class": predicted,
                "ground_truth_class": annotation["ground_truth_class"],
                "correct": predicted == annotation["ground_truth_class"],
                "mask": mask,
            })
            if write_outputs:
                mask_path = ROOT / "results" / "masks" / method / f"{image_id}_{method}_baseline.png"
                mask_path.parent.mkdir(parents=True, exist_ok=True)
                if not cv2.imwrite(str(mask_path), mask):
                    raise OSError(f"Could not write {mask_path}")

    previews = _render_annotation_previews(sources, labels) if write_outputs else []
    if write_outputs:
        for method, rows in rows_by_method.items():
            _merge_result_file(ROOT / "results" / f"{method}_results.csv", rows)
        _merge_result_file(
            ROOT / "results" / "results.csv",
            rows_by_method["rgb"] + rows_by_method["hsv"],
        )

    correct_by_method = {}
    for method, rows in rows_by_method.items():
        correct_by_method[method] = sum(row["correct"] == "true" for row in rows)

    summary = {
        "calibration": calibration,
        "control_measurements": control_measurements,
        "correct_by_method": correct_by_method,
        "previews": previews,
        "control_count": 4,
        "rows_written": 8 if write_outputs else 0,
    }
    return summary


def format_summary(summary):
    lines = ["DEVELOPMENT CALIBRATION (G1/G2; thresholds fixed before controls)"]
    lines.append("image method area_percent head_overlap_percent ground_truth")
    for item in summary["calibration"]:
        lines.append(
            f"{item['image_id']} {item['method']} "
            f"{item['mask_area_percent']:.4f} "
            f"{item['head_overlap_percent']:.4f} {item['ground_truth_class']}"
        )
    lines.append("")
    lines.append("CONTROL RESULTS (K1-K4)")
    lines.append("image method condition area_percent head_overlap_percent prediction ground_truth correct")
    for item in summary["control_measurements"]:
        overlap = item["head_overlap_percent"]
        overlap_text = "N/A" if overlap == "N/A" else f"{overlap:.4f}"
        lines.append(
            f"{item['image_id']} {item['method']} {item['condition']} "
            f"{item['mask_area_percent']:.4f} {overlap_text} "
            f"{item['predicted_class']} {item['ground_truth_class']} "
            f"{str(item['correct']).lower()}"
        )
    lines.append("")
    lines.append(
        "CLASS ACCURACY: "
        + ", ".join(f"{method.upper()} {correct}/4"
                    for method, correct in summary["correct_by_method"].items())
    )
    lines.append(
        "BOX METRICS: tp/fp/fn are N/A; no box-level detector evaluation was run."
    )
    if summary["previews"]:
        lines.append("ANNOTATION PREVIEWS: " + ", ".join(summary["previews"]))
    return "\n".join(lines)


if __name__ == "__main__":
    result = run_analysis(write_outputs=True)
    print(format_summary(result))
