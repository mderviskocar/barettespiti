"""Gaussian Blur experiment; no measurements are written on import or execution."""

import math

from src.common import PROJECT_ROOT, load_config, load_dataset, load_image, mask_percentages


def _settings():
    settings = load_config("gaussian_blur.json")
    kernel = settings["kernel_size"]
    sigmas = settings["sigma_values"]
    if (len(kernel) != 2 or any(type(n) is not int or n <= 0 or n % 2 == 0 for n in kernel)
            or settings["include_unfiltered_reference"] is not True
            or settings["reference_sigma"] != 0
            or not sigmas or any(type(s) not in (int, float) or not math.isfinite(s) or s <= 0
                                  for s in sigmas) or len(set(sigmas)) != len(sigmas)
            or settings["fixed_scale"] != 1):
        raise ValueError("Invalid Gaussian Blur settings.")
    return settings


def apply_blur(image_bgr, sigma, kernel_size):
    """Return BGR pixels at the original size; sigma=0 is an unfiltered copy."""
    import cv2
    import numpy as np

    image = np.asarray(image_bgr)
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3 or 0 in image.shape:
        raise ValueError("Expected a non-empty uint8 BGR image with three channels.")
    if type(sigma) not in (int, float) or not math.isfinite(sigma) or sigma < 0:
        raise ValueError("Sigma must be finite and non-negative.")
    if (len(kernel_size) != 2 or any(type(n) is not int or n <= 0 or n % 2 == 0
                                     for n in kernel_size)):
        raise ValueError("Kernel dimensions must be positive odd integers.")
    if sigma == 0:
        return image.copy()
    return cv2.GaussianBlur(image, tuple(kernel_size), sigmaX=float(sigma), sigmaY=float(sigma))


def readiness_issues():
    """Explain why the final control experiment cannot run yet."""
    issues = []
    settings = _settings()
    for method in ("rgb", "hsv"):
        config = load_config(f"{method}_config.json")
        if (config.get("status") != "configured" or config.get("frozen") is not True
                or config.get("lower") is None or config.get("upper") is None):
            issues.append(f"{method.upper()} thresholds are not configured and frozen.")
    decision = load_config()["decision_rule"]
    if (decision.get("status") != "configured" or decision.get("frozen") is not True
            or decision.get("min_color_area_percent") is None
            or decision.get("min_head_overlap_percent") is None
            or not decision.get("insufficient_evidence_rule")):
        issues.append("Shared classification rule is not configured and frozen.")
    records = load_dataset()
    expected = {"G1", "G2", "K1", "K2", "K3", "K4"}
    if len(records) != 6 or {row["image_id"] for row in records} != expected or any(
            "ground_truth_class" not in row or "head_roi" not in row
            or not (PROJECT_ROOT / row["relative_path"]).is_file() for row in records):
        issues.append("Six source images and manual labels are required.")
    return issues


def run_experiment():
    """Measure K1-K4 with fixed RGB/HSV rules; return rows without exporting them.

    Call only after the dataset, color thresholds and shared decision rule are frozen.
    The caller explicitly exports returned rows after reviewing them.
    """
    issues = readiness_issues()
    if issues:
        raise RuntimeError("Gaussian Blur experiment is not ready: " + " ".join(issues))

    from src import classification, hsv, rgb

    settings = _settings()
    decision = load_config()["decision_rule"]
    methods = (("rgb", rgb.create_mask), ("hsv", hsv.create_mask))
    records = load_dataset(split="control")
    rows = []
    for record in records:
        image = load_image(record["relative_path"])
        for sigma in (settings["reference_sigma"], *settings["sigma_values"]):
            filtered = apply_blur(image, sigma, settings["kernel_size"])
            for method, create_mask in methods:
                mask = create_mask(filtered, load_config(f"{method}_config.json"))
                area, overlap = mask_percentages(mask, record["head_roi"])
                predicted = classification.classify_mask(mask, record["head_roi"], decision)
                rows.append({
                    "experiment_id": "gaussian_blur",
                    "image_id": record["image_id"],
                    "method": method,
                    "condition": record["condition"],
                    "parameter": f"sigma={sigma:g};kernel={settings['kernel_size'][0]}x{settings['kernel_size'][1]};scale=1",
                    "mask_area_percent": area,
                    "head_overlap_percent": overlap,
                    "predicted_class": predicted,
                    "ground_truth_class": record["ground_truth_class"],
                    "correct": str(predicted == record["ground_truth_class"]).lower(),
                    "tp": "N/A", "fp": "N/A", "fn": "N/A",
                    "note": "Unfiltered reference" if sigma == 0 else "Gaussian Blur",
                })
    return rows
