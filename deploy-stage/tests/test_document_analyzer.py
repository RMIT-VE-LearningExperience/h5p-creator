import unittest

from app.services.document_analyzer import analyze_document
from app.services.document_parser import ListItem, ParsedDocument, Section


class DocumentAnalyzerTest(unittest.TestCase):
    def test_analyzer_suggests_question_set_for_question_heavy_docs(self) -> None:
        doc = ParsedDocument(
            title="Quiz",
            raw_text="Question one\nAnswer A\nAnswer B",
            sections=[
                Section(
                    heading="Question 1",
                    level=2,
                    lists=[[ListItem(text="Answer A", is_bold=True), ListItem(text="Answer B")]],
                ),
                Section(
                    heading="Question 2",
                    level=2,
                    lists=[[ListItem(text="Answer C", is_bold=True), ListItem(text="Answer D")]],
                ),
            ],
        )

        analysis = analyze_document(doc)

        self.assertEqual(analysis.suggested_activity_type, "H5P.QuestionSet")
        self.assertEqual(analysis.estimated_question_count, 2)
        self.assertEqual(analysis.question_like_section_count, 2)
        self.assertEqual(analysis.breakdown_strategy, "generate-directly")
        self.assertEqual(len(analysis.breakdown_plans), 1)

    def test_analyzer_flags_large_mixed_docs(self) -> None:
        doc = ParsedDocument(
            title="Module",
            raw_text="x" * 9000,
            sections=[
                Section(heading=f"Topic {i}", level=2, paragraphs=["Paragraph 1", "Paragraph 2"])
                for i in range(12)
            ],
        )

        analysis = analyze_document(doc)

        self.assertTrue(analysis.is_large_document)
        self.assertEqual(analysis.suggested_activity_type, "H5P.CoursePresentation")
        self.assertTrue(any("splitting" in suggestion for suggestion in analysis.suggestions))
        self.assertEqual(analysis.breakdown_strategy, "split-by-major-heading")
        self.assertGreater(len(analysis.breakdown_plans), 1)
        self.assertEqual(analysis.breakdown_plans[0].section_start, 1)
