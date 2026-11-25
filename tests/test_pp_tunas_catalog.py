import json
import unittest
from pathlib import Path

CATALOG = (
    Path(__file__).resolve().parent.parent
    / "skills/pp-tunas-risk-assessment/references/kepmen142_parameters.json"
)
ROUNDING_TOLERANCE = 0.02
KEPMEN_219_GF_ROWS = {
    "GF01": (23.53, "YES"),
    "GF02": (20.59, "NO"),
}


def load_parameters():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    return {a["key"]: a["parameters"] for a in catalog["aspects"]}


class KepmenCatalogTest(unittest.TestCase):
    def test_each_aspect_weights_sum_to_100(self):
        for key, parameters in load_parameters().items():
            total = sum(p["weight"] for p in parameters)
            with self.subTest(aspect=key):
                self.assertAlmostEqual(total, 100.0, delta=ROUNDING_TOLERANCE)

    def test_gf_rows_match_kepmen_219(self):
        by_code = {p["code"]: p for p in load_parameters()["g"]}
        for code, (weight, column) in KEPMEN_219_GF_ROWS.items():
            with self.subTest(code=code):
                self.assertEqual(by_code[code]["weight"], weight)
                self.assertEqual(by_code[code]["weight_column"], column)


if __name__ == "__main__":
    unittest.main()
