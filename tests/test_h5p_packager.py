import json
import unittest
import zipfile
from io import BytesIO

from app.schemas.h5p_types import H5PResult
from app.services.h5p_packager import pack


class H5PPackagerTest(unittest.TestCase):
    def test_pack_creates_h5p_archive(self) -> None:
        result = H5PResult(
            content_type="H5P.QuestionSet",
            title="Sample Quiz",
            content={"questions": []},
        )

        archive = pack(result)

        with zipfile.ZipFile(BytesIO(archive)) as zf:
            self.assertEqual(sorted(zf.namelist()), ["content/content.json", "h5p.json"])
            metadata = json.loads(zf.read("h5p.json"))
            content = json.loads(zf.read("content/content.json"))

        self.assertEqual(metadata["mainLibrary"], "H5P.QuestionSet")
        self.assertEqual(metadata["title"], "Sample Quiz")
        self.assertEqual(content, {"questions": []})

    def test_pack_uses_current_multichoice_dependency_versions(self) -> None:
        result = H5PResult(
            content_type="H5P.MultiChoice",
            title="Sample Question",
            content={"question": "<p>Q</p>", "answers": []},
        )

        archive = pack(result)

        with zipfile.ZipFile(BytesIO(archive)) as zf:
            metadata = json.loads(zf.read("h5p.json"))

        self.assertIn(
            {"machineName": "H5P.JoubelUI", "majorVersion": 1, "minorVersion": 3},
            metadata["preloadedDependencies"],
        )
