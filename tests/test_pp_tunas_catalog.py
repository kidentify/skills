import importlib.util
import json
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "skills/pp-tunas-risk-assessment"
CATALOG = SKILL / "references/kepmen142_parameters.json"
BUILDER = SKILL / "scripts/build_self_assessment.py"
ROUNDING_TOLERANCE = 0.02
KEPMEN_219_GF_ROWS = {
    "GF01": (23.53, "YES"),
    "GF02": (20.59, "NO"),
}
KEPMEN_219_GF_SCORES = {
    ("GF01", "FOUND"): 23.53,
    ("GF01", "NOT_FOUND"): 0.0,
    ("GF02", "FOUND"): 0.0,
    ("GF02", "NOT_FOUND"): 20.59,
}


def load_aspects():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    return {a["key"]: a for a in catalog["aspects"]}


def load_builder():
    spec = importlib.util.spec_from_file_location("build_self_assessment", BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class KepmenCatalogTest(unittest.TestCase):
    def test_each_aspect_weights_sum_to_100(self):
        for key, aspect in load_aspects().items():
            total = sum(p["weight"] for p in aspect["parameters"])
            with self.subTest(aspect=key):
                self.assertAlmostEqual(total, 100.0, delta=ROUNDING_TOLERANCE)

    def test_gf_rows_match_kepmen_219(self):
        by_code = {p["code"]: p for p in load_aspects()["g"]["parameters"]}
        for code, (weight, column) in KEPMEN_219_GF_ROWS.items():
            with self.subTest(code=code):
                self.assertEqual(by_code[code]["weight"], weight)
                self.assertEqual(by_code[code]["weight_column"], column)

    def test_gf_rows_score_by_answer(self):
        builder = load_builder()
        aspect = load_aspects()["g"]
        for (code, status), expected in KEPMEN_219_GF_SCORES.items():
            rows, _, _ = builder._score_aspect(aspect, {code: {"status": status}})
            score = next(row["score"] for row in rows if row["p"]["code"] == code)
            with self.subTest(code=code, status=status):
                self.assertEqual(score, expected)


if __name__ == "__main__":
    unittest.main()
