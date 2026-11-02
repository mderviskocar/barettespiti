"""Validate the shared project contract without requiring computer-vision dependencies."""

import argparse
import ast
import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common import RESULT_FIELDS  # noqa: E402

SOURCE_FIELDS = (
    "image_id", "split", "relative_path", "width", "height", "condition",
    "source_type", "source_url", "license", "notes",
)
NOTEBOOKS = (
    "nesli_dataset_analysis", "omar_rgb", "dervis_hsv", "ahmet_gaussian_blur",
    "efe_scale", "murathan_detection", "main_demo",
)
RESULT_FILES = (
    "results/results.csv", "results/rgb_results.csv", "results/hsv_results.csv",
    "results/gaussian_blur/blur_results.csv", "results/scale/scale_results.csv",
    "results/detector/detection_results.csv",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def read_csv(relative, fields):
    with (ROOT / relative).open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        require(reader.fieldnames == list(fields), f"Unexpected CSV columns: {relative}")
        rows = list(reader)
    require(all(None not in row and None not in row.values() for row in rows),
            f"Malformed CSV row: {relative}")
    return rows


def validate_box(box, width, height, label):
    require(isinstance(box, list) and len(box) == 4, f"Invalid xyxy box: {label}")
    require(all(type(value) is int for value in box), f"Non-integer box: {label}")
    xmin, ymin, xmax, ymax = box
    require(0 <= xmin < xmax <= width and 0 <= ymin < ymax <= height,
            f"Box outside image: {label}")


def validate(require_data=False):
    project = read_json("configs/experiment.json")
    development = ["G1", "G2"]
    control = ["K1", "K2", "K3", "K4"]
    classes = ["helmet_on_head", "helmet_off_head", "no_helmet", "uncertain"]
    require(project["development_ids"] == development, "Development IDs must be G1/G2.")
    require(project["control_ids"] == control, "Control IDs must be K1-K4.")
    require(project["classes"] == classes, "Four shared class codes must be preserved.")
    expected_ids = set(development + control)

    for method, limits in (("rgb", (255, 255, 255)), ("hsv", (179, 255, 255))):
        config = read_json(f"configs/{method}_config.json")
        lower, upper = config["lower"], config["upper"]
        require(type(config["frozen"]) is bool, f"{method}: frozen must be boolean.")
        require((lower is None) == (upper is None), f"{method}: both bounds are required.")
        if lower is not None:
            require(isinstance(lower, list) and isinstance(upper, list)
                    and len(lower) == len(upper) == 3, f"{method}: expected three channels.")
            require(all(type(a) is int and type(b) is int and 0 <= a <= b <= limit
                        for a, b, limit in zip(lower, upper, limits)),
                    f"{method}: invalid channel range.")
        if config["frozen"]:
            require(lower is not None and config["status"] == "configured",
                    f"{method}: frozen settings must be configured.")

    decision = project["decision_rule"]
    require(type(decision["frozen"]) is bool, "Decision frozen must be boolean.")
    for field in ("min_color_area_percent", "min_head_overlap_percent"):
        value = decision[field]
        require(value is None or (type(value) in (int, float) and math.isfinite(value)
                                  and 0 <= value <= 100), f"Invalid percentage: {field}")
    if decision["frozen"]:
        require(decision["status"] == "configured"
                and decision["min_color_area_percent"] is not None
                and decision["min_head_overlap_percent"] is not None
                and bool(decision["insufficient_evidence_rule"]),
                "Frozen decision rule must be fully configured.")
    blur = read_json("configs/gaussian_blur.json")
    require(all(type(v) in (int, float) and math.isfinite(v) and v > 0
                for v in blur["sigma_values"]), "Invalid blur sigma.")
    require(len(blur["kernel_size"]) == 2
            and all(type(v) is int and v > 0 and v % 2 == 1 for v in blur["kernel_size"]),
            "Blur kernel must have two positive odd dimensions.")
    scale = read_json("configs/scale_config.json")
    require(all(type(v) in (int, float) and math.isfinite(v) and 0 < v <= 1
                for v in scale["scale_factors"]), "Invalid downscale factor.")
    detector = read_json("configs/detector_config.json")
    require(detector["evaluation_iou_threshold"] == 0.5, "Evaluation IoU must be 0.50.")
    if detector["enabled"]:
        require(all(detector.get(field) for field in
                    ("weights_source", "weights_local_path", "class_names", "input_size")),
                "Enabled detector needs model provenance and input settings.")

    sources = read_csv("data/sources.csv", SOURCE_FIELDS)
    by_id = {}
    dimensions = {}
    for row in sources:
        image_id = row["image_id"]
        require(image_id in expected_ids and image_id not in by_id, f"Invalid/duplicate ID: {image_id}")
        split = "development" if image_id in development else "control"
        require(row["split"] == split, f"Wrong split: {image_id}")
        relative = Path(row["relative_path"])
        image_path = (ROOT / relative).resolve()
        require(not relative.is_absolute() and image_path.is_relative_to(ROOT / "data" / split),
                f"Image path must be inside data/{split}: {image_id}")
        require(image_path.is_file(), f"Image missing: {row['relative_path']}")
        width, height = int(row["width"]), int(row["height"])
        require(width > 0 and height > 0, f"Invalid dimensions: {image_id}")
        require(bool(row["condition"] and row["source_type"] and row["license"]),
                f"Missing condition/source/license: {image_id}")
        require(row["source_type"] == "own_photo" or bool(row["source_url"]),
                f"Missing source URL: {image_id}")
        by_id[image_id] = row
        dimensions[image_id] = width, height

    ground_truth = read_json("annotations/ground_truth.json")
    require(ground_truth["coordinate_format"] == "xyxy_pixels_exclusive_max",
            "Unexpected coordinate format.")
    labeled = set()
    for entry in ground_truth["images"]:
        image_id = entry["image_id"]
        require(image_id in by_id and image_id not in labeled, f"Unmatched/duplicate label: {image_id}")
        require(entry["ground_truth_class"] in classes and bool(entry["reason"].strip()),
                f"Missing class/reason: {image_id}")
        width, height = dimensions[image_id]
        if entry["head_roi"] is not None:
            validate_box(entry["head_roi"], width, height, image_id + " head")
        require(isinstance(entry["helmet_boxes"], list), f"Invalid helmet list: {image_id}")
        for box in entry["helmet_boxes"]:
            validate_box(box, width, height, image_id + " helmet")
        labeled.add(image_id)
    if require_data:
        require(set(by_id) == expected_ids and labeled == expected_ids,
                "Full-data validation needs six source images and six manual labels.")

    for filename in RESULT_FILES:
        for row in read_csv(filename, RESULT_FIELDS):
            require(row["image_id"] in by_id, f"Result without a source image: {filename}")
            require(all(value != "" for value in row.values()), f"Use N/A for absent metrics: {filename}")
            for field in ("mask_area_percent", "head_overlap_percent"):
                if row[field] != "N/A":
                    value = float(row[field])
                    require(math.isfinite(value) and 0 <= value <= 100, f"Invalid {field}: {filename}")
            for field in ("tp", "fp", "fn"):
                require(row[field] == "N/A" or (row[field].isdigit() and int(row[field]) >= 0),
                        f"Invalid {field}: {filename}")
            for field in ("predicted_class", "ground_truth_class"):
                require(row[field] in classes + ["N/A"], f"Invalid {field}: {filename}")
            require(row["correct"].lower() in ("true", "false", "n/a"), f"Invalid correct: {filename}")

    for name in NOTEBOOKS:
        notebook = read_json(f"notebooks/{name}.ipynb")
        require(notebook["nbformat"] == 4 and bool(notebook["cells"]), f"Invalid notebook: {name}")
        for cell in notebook["cells"]:
            require(cell["cell_type"] in ("markdown", "code", "raw"), f"Invalid cell: {name}")
            require(isinstance(cell["source"], (list, str)), f"Invalid cell source: {name}")
            if cell["cell_type"] == "code":
                require(isinstance(cell["outputs"], list), f"Invalid outputs: {name}")
    for directory in ("src", "scripts"):
        for module in (ROOT / directory).glob("*.py"):
            ast.parse(module.read_text(encoding="utf-8"), filename=str(module))
    for member in ("nesli", "omar", "dervis", "ahmet", "efe", "murathan"):
        require((ROOT / "individual_notes" / f"{member}.md").is_file(), f"Missing note: {member}")
    print(f"OK: shared configuration, 7 notebooks, 6 result schemas, {len(sources)} source images.")
    if not sources:
        print("Scaffold only: no real images, labels or measurements have been added.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-data", action="store_true", help="Require all six images and manual labels.")
    arguments = parser.parse_args()
    try:
        validate(require_data=arguments.require_data)
    except (ValueError, KeyError, TypeError, OSError, SyntaxError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
