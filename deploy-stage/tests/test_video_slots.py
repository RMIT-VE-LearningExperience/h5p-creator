import unittest

from app.services import video_slots


PLACEHOLDER_HTML = """
<div class="emble-columns-container">
  <div class="emble-columns-child">
    <p>Watch this (X:XX mins) video to learn about safe machine operation.</p>
  </div>
  <div class="emble-columns-child">
    <p>*Embed your YouTube video here [Suggested search: "industrial sewing safety"]</p>
  </div>
</div>
"""


class VideoSlotsTests(unittest.TestCase):
    def test_placeholder_has_a_deterministic_slot_id(self):
        first = video_slots.find_video_slots(PLACEHOLDER_HTML)
        second = video_slots.find_video_slots(PLACEHOLDER_HTML)

        self.assertEqual(len(first), 1)
        self.assertEqual(first[0].slot_id, second[0].slot_id)
        self.assertFalse(first[0].already_filled)

    def test_applied_video_is_found_again_with_the_same_slot_id(self):
        slot = video_slots.find_video_slots(PLACEHOLDER_HTML)[0]
        rendered = video_slots.render_slot_html(
            slot,
            [{"id": "video-123", "title": "Machine safety"}],
            ["Watch this (2:30 mins) video to learn about machine safety."],
        )

        updated = video_slots.apply_slot(
            PLACEHOLDER_HTML, slot.index, rendered, slot_id=slot.slot_id
        )
        found = video_slots.find_video_slots(updated)

        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].slot_id, slot.slot_id)
        self.assertTrue(found[0].already_filled)
        self.assertIn('data-video-finder-slot-id="' + slot.slot_id + '"', updated)
        self.assertIn("youtube.com/embed/video-123", updated)

    def test_legacy_applied_video_is_still_replaceable(self):
        legacy_html = """
        <div>
          <p>Watch this (1:29 mins) video to learn about flatlock seams.</p>
          <p><iframe src="https://www.youtube.com/embed/old-video"></iframe></p>
        </div>
        """

        slots = video_slots.find_video_slots(legacy_html)

        self.assertEqual(len(slots), 1)
        self.assertTrue(slots[0].already_filled)
        self.assertEqual(
            slots[0].embed_tag.find("iframe").get("src"),
            "https://www.youtube.com/embed/old-video",
        )

    def test_legacy_video_is_not_consumed_by_a_later_placeholder(self):
        mixed_html = """
        <div>
          <p>Watch this (1:29 mins) video to learn about flatlock seams.</p>
          <p><iframe src="https://www.youtube.com/embed/old-video"></iframe></p>
          <p>Watch this (X:XX mins) video to learn about overlockers.</p>
          <p>*Embed your YouTube video here [Suggested search: "overlocker basics"]</p>
        </div>
        """

        slots = video_slots.find_video_slots(mixed_html)

        self.assertEqual(len(slots), 2)
        self.assertTrue(slots[0].already_filled)
        self.assertFalse(slots[1].already_filled)
        self.assertEqual(slots[1].suggested_search, "overlocker basics")

    def test_slot_id_does_not_fall_back_to_a_different_index(self):
        self.assertIsNone(
            video_slots.find_video_slot(
                PLACEHOLDER_HTML, slot_id="vf-missing", slot_index=0
            )
        )

    def test_before_preview_contains_the_current_video(self):
        legacy_html = """
        <p>Watch this (1:29 mins) video to learn about flatlock seams.</p>
        <p><iframe src="https://www.youtube.com/embed/current-video"></iframe></p>
        """
        slot = video_slots.find_video_slots(legacy_html)[0]

        preview = video_slots.wrap_for_preview(
            video_slots.render_current_slot_html(slot)
        )

        self.assertIn("youtube.com/embed/current-video", preview)
        self.assertIn("flatlock seams", preview)

    def test_page_without_video_section_gets_an_append_slot(self):
        html = "<h2>Machine safety</h2><p>Wear PPE before operating equipment.</p>"
        slot = video_slots.make_append_slot(html)
        resolved = video_slots.find_video_slot(
            html, slot_id=slot.slot_id, slot_index=slot.index
        )

        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.insertion_mode, "append")

    def test_append_slot_becomes_a_replaceable_filled_slot(self):
        html = "<h2>Machine safety</h2><p>Wear PPE before operating equipment.</p>"
        slot = video_slots.make_append_slot(html)
        rendered = video_slots.render_slot_html(
            slot,
            [{"id": "safety-video", "title": "Machine safety"}],
            ["Watch this (3:00 mins) video to learn about machine safety."],
        )

        updated = video_slots.apply_slot(
            html, slot.index, rendered, slot_id=slot.slot_id
        )
        found = video_slots.find_video_slots(updated)

        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].slot_id, slot.slot_id)
        self.assertTrue(found[0].already_filled)
        self.assertIn("Wear PPE before operating equipment.", updated)
        self.assertIn("youtube.com/embed/safety-video", updated)


if __name__ == "__main__":
    unittest.main()
