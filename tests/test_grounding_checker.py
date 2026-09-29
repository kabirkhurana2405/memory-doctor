import unittest

from memory_doctor.core.grounding_checker import analyze_summary


class AnalyzeSummaryTests(unittest.TestCase):
    def test_flags_expansion(self):
        result = analyze_summary("SQLite stores five notes.", "SQLite stores five notes across a much larger system.")
        self.assertTrue(result["expanded"])
        self.assertTrue(any(item["check"] == "Length" for item in result["findings"]))

    def test_flags_unsupported_entities_dates_and_numbers(self):
        source = "Project Atlas stores five notes in SQLite."
        summary = (
            "Project Atlas, led by Dr. Elias Thorne and the Memory Innovation Team, "
            "stores eight notes and launches on 2026-10-01."
        )
        result = analyze_summary(source, summary)
        self.assertTrue(any("Elias Thorne" in item["value"] for item in result["unsupported_entities"]))
        self.assertTrue(any("Memory Innovation Team" in item["value"] for item in result["unsupported_entities"]))
        self.assertIn("2026-10-01", result["unsupported_dates"])
        self.assertIn("8", result["unsupported_numbers"])

    def test_does_not_flag_source_supported_project_and_number(self):
        result = analyze_summary(
            "Project Atlas contains five notes.",
            "Project Atlas contains 5 notes.",
        )
        self.assertFalse(result["unsupported_entities"])
        self.assertFalse(result["unsupported_numbers"])

    def test_flags_missing_required_phrase(self):
        result = analyze_summary(
            "The team has not selected a launch date.",
            "The team plans to launch in October.",
            "The team has not selected a launch date.",
        )
        self.assertEqual(
            result["missing_required_phrases"],
            ["The team has not selected a launch date."],
        )

    def test_no_findings_is_not_called_grounded(self):
        result = analyze_summary("SQLite stores notes.", "SQLite stores notes.")
        self.assertEqual(result["status"], "No heuristic flags")
        self.assertTrue(any("does not prove" in item for item in result["limitations"]))

    def test_requires_both_inputs(self):
        with self.assertRaises(ValueError):
            analyze_summary("", "A summary")
        with self.assertRaises(ValueError):
            analyze_summary("A source", " ")

    def test_rejects_oversized_input(self):
        with self.assertRaises(ValueError):
            analyze_summary("a" * 100_001, "summary")


if __name__ == "__main__":
    unittest.main()
