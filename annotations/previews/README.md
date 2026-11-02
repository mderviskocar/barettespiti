# Ground truth previews

These six PNGs are visualization derivatives of the original dataset images, not independent samples. Blue boxes show the manually labeled `head_roi`; green boxes show `helmet_boxes`. K1 has no head box because the heads are cropped out. Box coordinates remain in original-image pixel coordinates in `../ground_truth.json`.

Regenerate the previews by running `notebooks/nesli_dataset_analysis.ipynb` or `python scripts/run_nesli_dataset_analysis.py` after installing the project requirements.
