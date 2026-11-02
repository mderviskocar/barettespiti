"""Shared data paths and result schema; importing does not generate measurements."""

import csv
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULT_FIELDS = (
    "experiment_id", "image_id", "method", "condition", "parameter",
    "mask_area_percent", "head_overlap_percent", "predicted_class",
    "ground_truth_class", "correct", "tp", "fp", "fn", "note",
)


def load_config(filename="experiment.json"):
    return json.loads((PROJECT_ROOT / "configs" / filename).read_text(encoding="utf-8"))


def load_dataset(split=None):
    """Join sources and manual labels; an empty scaffold returns an empty list."""
    with (PROJECT_ROOT / "data/sources.csv").open(encoding="utf-8", newline="") as handle:
        sources = list(csv.DictReader(handle))
    labels = json.loads((PROJECT_ROOT / "annotations/ground_truth.json").read_text(encoding="utf-8"))
    annotations = {item["image_id"]: item for item in labels["images"]}
    return [
        {**source, **annotations.get(source["image_id"], {})}
        for source in sources if split is None or source["split"] == split
    ]


def load_image(relative_path):
    """Decode BGR pixels even when a Windows path contains Turkish characters."""
    import cv2
    import numpy as np

    pixels = np.frombuffer((PROJECT_ROOT / relative_path).read_bytes(), dtype=np.uint8)
    image = cv2.imdecode(pixels, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Cannot decode image: {relative_path}")
    return image


def mask_percentages(mask, head_roi):
    """Return image area and head overlap as 0-100 percentages; missing ROI is N/A."""
    import numpy as np

    selected = np.asarray(mask) != 0
    if selected.ndim != 2 or selected.size == 0:
        raise ValueError("Mask must be non-empty and two-dimensional.")
    area = 100.0 * np.count_nonzero(selected) / selected.size
    if head_roi is None:
        return area, "N/A"
    if len(head_roi) != 4 or not all(isinstance(value, int) for value in head_roi):
        raise ValueError("Head ROI must contain four integer pixel coordinates.")
    xmin, ymin, xmax, ymax = head_roi
    height, width = selected.shape
    if not (0 <= xmin < xmax <= width and 0 <= ymin < ymax <= height):
        raise ValueError("Head ROI is outside the mask.")
    region = selected[ymin:ymax, xmin:xmax]
    return area, 100.0 * np.count_nonzero(region) / region.size


def write_results(rows, relative_path):
    """Explicit export; absent metrics are N/A, never fabricated zeros."""
    destination = PROJECT_ROOT / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "N/A") for field in RESULT_FIELDS})
