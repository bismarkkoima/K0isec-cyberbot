import json
import unittest
from pathlib import Path

from guardian.scam_checker import analyze

DATA = Path(__file__).resolve().parent.parent / "evaluation" / "messages.json"


class EvaluationDatasetTests(unittest.TestCase):
    def setUp(self):
        self.messages = json.loads(DATA.read_text(encoding="utf-8"))

    def test_dataset_is_well_formed_and_balanced(self):
        labels = [m["label"] for m in self.messages]
        self.assertEqual(set(labels), {"scam", "genuine"})
        self.assertEqual(labels.count("scam"), labels.count("genuine"))
        for m in self.messages:
            self.assertTrue(m["text"].strip())

    def test_accuracy_does_not_regress(self):
        correct = sum((analyze(m["text"])["level"] != "low") == (m["label"] == "scam")
                      for m in self.messages)
        self.assertGreaterEqual(correct / len(self.messages), 0.85)


if __name__ == "__main__":
    unittest.main()
