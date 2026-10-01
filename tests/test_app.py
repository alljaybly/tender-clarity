"""Home-screen smoke test for the first analysis slice."""
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class StreamlitHomeTests(unittest.TestCase):
    def test_home_screen_renders_upload_and_privacy_warning(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.file_uploader), 1)
        self.assertEqual(len(app.button), 0)
        self.assertTrue(app.warning)
        self.assertTrue(any("Tender Clarity" in (item.value or "") for item in app.markdown))


if __name__ == "__main__":
    unittest.main()
