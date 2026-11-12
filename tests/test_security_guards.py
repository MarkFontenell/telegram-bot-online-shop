import ast
from pathlib import Path
import unittest
import subprocess
ROOT = Path(__file__).resolve().parents[1]
class TestSecurity(unittest.TestCase):
    def test_admin_order_callbacks(self):
        src = (ROOT / "handlers/admin_hand.py").read_text(encoding="utf-8")
        methods = {n.name: n for n in ast.parse(src).body if isinstance(n, ast.AsyncFunctionDef)}
        for name in ("open_orders_page", "view_order", "confirm_payment", "confirm_issue"):
            self.assertIn("callback.from_user.id not in config.admin_ids", ast.get_source_segment(src, methods[name]))
    def test_private_files_not_tracked(self):
        tracked = subprocess.check_output(
            ["git", "ls-files"], cwd=ROOT
        ).decode("utf-8").splitlines()
        for path in tracked:
            self.assertNotEqual(path, ".env")
            self.assertFalse(path.endswith(".db"), path)
            self.assertFalse("/__pycache__/" in "/" + path, path)
            self.assertFalse(path.startswith(".idea/"), path)
if __name__ == "__main__":
    unittest.main()
