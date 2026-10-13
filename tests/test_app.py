import unittest

from app import analyse, draft_review


class AnalysisTests(unittest.TestCase):
    def test_sustained_improvement_reports_delta(self):
        reading = next(x for x in analyse()["patterns"] if x["area"] == "Reading")
        self.assertEqual((reading["direction"], reading["change"]), ("increased", 20))

    def test_finding_cites_source_records(self):
        reading = next(x for x in analyse()["patterns"] if x["area"] == "Reading")
        self.assertEqual(reading["sources"], ["ASM-2401", "ASM-2402", "ASM-2502"])

    def test_single_poor_result_does_not_become_trend(self):
        result = analyse([{"term": "T1", "reading": 20, "maths": None, "absences": None, "sources": ["S1"]}])
        self.assertEqual(result["patterns"], [])

    def test_missing_assessment_is_visible(self):
        result = analyse()
        self.assertIn({"term": "2025 · Term 1", "field": "reading"}, result["missing_data"])

    def test_conflicting_observations_are_preserved(self):
        result = analyse()
        text = " ".join(x["text"] for x in result["observations"])
        self.assertIn("Teacher A", text)
        self.assertIn("Teacher B", text)

    def test_draft_does_not_diagnose(self):
        text = draft_review()["text"].lower()
        self.assertIn("not a diagnosis", text)

    def test_draft_asks_about_missing_evidence(self):
        self.assertIn("missing 2025 Term 1", draft_review()["text"])

    def test_draft_contains_source_ids(self):
        self.assertIn("ASM-2401", draft_review()["text"])


if __name__ == "__main__":
    unittest.main()
