"""Shared demo integration; actual member algorithms must be implemented separately."""

from src import classification, hsv, rgb
from src.common import load_config, load_dataset, load_image, mask_percentages


def run_color_demo(image_id):
    """Return pixels, masks, measured rows and missing-work messages; never export."""
    records = {record["image_id"]: record for record in load_dataset()}
    if image_id not in records:
        raise ValueError(f"Unknown image_id: {image_id}")
    record = records[image_id]
    image = load_image(record["relative_path"])
    experiment = load_config()
    response = {"image": image, "masks": {}, "rows": [], "messages": []}
    if "ground_truth_class" not in record:
        response["messages"].append("Eksik ground truth: önce manuel etiketi kaydedin.")
        return response
    decision = experiment["decision_rule"]
    for method, module in (("rgb", rgb), ("hsv", hsv)):
        config = load_config(f"{method}_config.json")
        if config["lower"] is None or config["upper"] is None:
            response["messages"].append(f"{method.upper()}: geliştirme eşikleri henüz seçilmedi.")
            continue
        if record["split"] == "control" and not (config["frozen"] and decision["frozen"]):
            response["messages"].append(f"{method.upper()}: kontrol öncesi renk ve karar ayarlarını dondurun.")
            continue
        try:
            mask = module.create_mask(image.copy(), config)
            if mask.shape != image.shape[:2]:
                raise ValueError(f"{method}: mask and image dimensions differ.")
            area, overlap = mask_percentages(mask, record.get("head_roi"))
            response["masks"][method] = mask
        except NotImplementedError as error:
            response["messages"].append(str(error))
            continue
        predicted, correct = "N/A", "N/A"
        if decision["status"] != "configured":
            response["messages"].append("Ortak dört sınıflı karar kuralı henüz yapılandırılmadı.")
        else:
            try:
                predicted = classification.classify_mask(mask, record.get("head_roi"), decision)
                if predicted not in experiment["classes"]:
                    raise ValueError(f"Invalid classifier output: {predicted}")
                correct = predicted == record["ground_truth_class"]
            except NotImplementedError as error:
                response["messages"].append(str(error))
        response["rows"].append({
            "experiment_id": "interactive_preview", "image_id": image_id,
            "method": method, "condition": record["condition"], "parameter": "baseline",
            "mask_area_percent": area, "head_overlap_percent": overlap,
            "predicted_class": predicted, "ground_truth_class": record["ground_truth_class"],
            "correct": correct, "tp": "N/A", "fp": "N/A", "fn": "N/A",
            "note": "Interactive preview; not exported as a final experiment.",
        })
    return response
