import unittest
from unittest.mock import patch

from app.api.routes.canvas import VideoSlotSuggestionRequest
from app.services import canvas_lms


class _Response:
    def __init__(self, payload, next_url=""):
        self.status_code = 200
        self._payload = payload
        self.headers = {
            "link": f'<{next_url}>; rel="next"' if next_url else ""
        }

    def json(self):
        return self._payload


class _Client:
    def __init__(self, responses):
        self.responses = responses

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    async def get(self, _url, params=None):
        return self.responses.pop(0)


class CanvasContentRequestTests(unittest.TestCase):
    def test_video_slot_request_accepts_more_than_ten_pages(self):
        urls = [f"page-{index}" for index in range(75)]

        request = VideoSlotSuggestionRequest(course_id=1, page_urls=urls)

        self.assertEqual(request.page_urls, urls)


class CanvasPaginationTests(unittest.IsolatedAsyncioTestCase):
    async def test_unbounded_pagination_reads_every_canvas_page(self):
        first_page = [{"id": index} for index in range(100)]
        second_page = [{"id": index} for index in range(100, 175)]
        responses = [
            _Response(first_page, "https://canvas.example.edu/api/v1/courses/1/pages?page=2"),
            _Response(second_page),
        ]
        credentials = canvas_lms.CanvasCredentials(
            base_url="https://canvas.example.edu",
            api_token="test-token",
            source="user",
        )
        context_token = canvas_lms.bind_request_credentials(credentials)
        try:
            with patch.object(
                canvas_lms.httpx,
                "AsyncClient",
                return_value=_Client(responses),
            ):
                pages = await canvas_lms._get_paginated(
                    "courses/1/pages", limit=None
                )
        finally:
            canvas_lms.reset_request_credentials(context_token)

        self.assertEqual(len(pages), 175)
        self.assertEqual(pages[-1]["id"], 174)


if __name__ == "__main__":
    unittest.main()
