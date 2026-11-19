import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.check_release import verify_receipt


class ReleaseReceiptTests(unittest.TestCase):
    def setUp(self):
        self.receipt = json.loads((ROOT / "examples/release.json").read_text(encoding="utf-8"))

    def test_verifies_scoped_paths(self):
        verify_receipt(self.receipt, ["src/app.py", "tests/test_app.py"])

    def test_rejects_out_of_scope(self):
        with self.assertRaisesRegex(ValueError, "Out-of-scope"):
            verify_receipt(self.receipt, ["vendor/private.txt"])

    def test_rejects_stale_review(self):
        self.receipt["review"]["candidate"] = self.receipt["base"]
        with self.assertRaisesRegex(ValueError, "exact candidate"):
            verify_receipt(self.receipt, ["src/app.py"])

    def test_rejects_the_authors_own_review(self):
        self.receipt["review"]["reviewer"] = self.receipt["author"]
        with self.assertRaisesRegex(ValueError, "independent"):
            verify_receipt(self.receipt, ["src/app.py"])

    def test_rejects_failed_checks(self):
        self.receipt["checks"]["tests"] = False
        with self.assertRaisesRegex(ValueError, "must have passed"):
            verify_receipt(self.receipt, ["src/app.py"])


if __name__ == "__main__":
    unittest.main()
