"""Temporary synthetic-image checks; these never create experiment results."""

import unittest
from unittest.mock import patch

import numpy as np

from src.gaussian_blur import apply_blur, readiness_issues, run_experiment


class GaussianBlurTests(unittest.TestCase):
    def setUp(self):
        self.image = np.zeros((31, 31, 3), dtype=np.uint8)
        self.image[15, 15] = (255, 120, 30)

    def test_unfiltered_reference_is_independent_copy(self):
        result = apply_blur(self.image, 0, (15, 15))
        np.testing.assert_array_equal(result, self.image)
        self.assertIsNot(result, self.image)

    def test_positive_sigmas_preserve_size_and_reduce_impulse(self):
        center_values = []
        for sigma in (0.5, 1.5, 3.0):
            result = apply_blur(self.image, sigma, (15, 15))
            self.assertEqual(result.shape, self.image.shape)
            self.assertEqual(result.dtype, self.image.dtype)
            self.assertLess(int(result[15, 15, 0]), 255)
            center_values.append(int(result[15, 15, 0]))
        self.assertEqual(center_values, sorted(center_values, reverse=True))
        np.testing.assert_array_equal(self.image[15, 15], (255, 120, 30))

    def test_rejects_invalid_inputs(self):
        for sigma in (-1, float("nan"), float("inf")):
            with self.subTest(sigma=sigma), self.assertRaises(ValueError):
                apply_blur(self.image, sigma, (15, 15))
        with self.assertRaises(ValueError):
            apply_blur(self.image, 1.5, (14, 15))
        with self.assertRaises(ValueError):
            apply_blur(self.image[:, :, 0], 1.5, (15, 15))

    def test_unready_project_produces_no_classification(self):
        issues = readiness_issues()
        self.assertTrue(issues)
        with self.assertRaisesRegex(RuntimeError, "not ready"):
            run_experiment()

    def test_synthetic_pipeline_returns_rows_without_export(self):
        records = [
            {"image_id": f"K{n}", "relative_path": f"synthetic/{n}.jpg",
             "condition": "synthetic", "head_roi": [10, 10, 20, 20],
             "ground_truth_class": "no_helmet"}
            for n in range(1, 5)
        ]
        mask = np.zeros(self.image.shape[:2], dtype=np.uint8)
        with (patch("src.gaussian_blur.readiness_issues", return_value=[]),
              patch("src.gaussian_blur.load_dataset", return_value=records),
              patch("src.gaussian_blur.load_image", return_value=self.image),
              patch("src.rgb.create_mask", return_value=mask),
              patch("src.hsv.create_mask", return_value=mask),
              patch("src.classification.classify_mask", return_value="no_helmet")):
            rows = run_experiment()
        self.assertEqual(len(rows), 32)
        self.assertEqual({row["image_id"] for row in rows}, {"K1", "K2", "K3", "K4"})
        self.assertEqual({row["method"] for row in rows}, {"rgb", "hsv"})
        self.assertEqual({row["parameter"].split(";")[0] for row in rows},
                         {"sigma=0", "sigma=0.5", "sigma=1.5", "sigma=3"})
        self.assertTrue(all(row["head_overlap_percent"] == 0 for row in rows))


if __name__ == "__main__":
    unittest.main()
