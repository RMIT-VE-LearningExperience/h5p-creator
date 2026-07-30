import unittest

from app.api.routes.canvas import _page_context_summary


class CanvasPageContextTests(unittest.TestCase):
    def test_summary_omits_template_video_instructions(self):
        summary = _page_context_summary(
            "Production room safety",
            """
            Production room safety
            This page explains PPE, machine guards, and safe shutdown procedures.
            Watch this (X:XX mins) video to learn about safety.
            *Embed your YouTube video here [Suggested search: "machine safety"]
            """,
        )

        self.assertEqual(
            summary,
            "This page explains PPE, machine guards, and safe shutdown procedures.",
        )

    def test_summary_has_a_title_fallback(self):
        self.assertEqual(
            _page_context_summary("Flatlock seams", ""),
            "This page covers Flatlock seams.",
        )


if __name__ == "__main__":
    unittest.main()
