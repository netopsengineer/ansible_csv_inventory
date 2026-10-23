"""Offline syntax and security-regression checks. Never contact managed hosts."""
import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class OfflineSafety(unittest.TestCase):
    def test_python_sources_parse_without_execution(self):
        paths = [p for p in ROOT.rglob("*.py") if not any(x.startswith(".") for x in p.relative_to(ROOT).parts)]
        for path in paths:
            with self.subTest(path=str(path.relative_to(ROOT))):
                ast.parse(path.read_text(), filename=str(path))

    def test_supported_controller_python(self):
        self.assertEqual((ROOT / ".python-version").read_text().strip(), "3.12.15")

    def test_ci_has_no_inventory_or_dependency_export(self):
        text = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertIn("persist-credentials: false", text)
        self.assertIn("contents: read", text)
        self.assertNotIn("pip install", text)
        self.assertNotIn("ansible-playbook", text)

    def test_csv_inventory_on_synthetic_data(self):
        import importlib.util
        import tempfile
        spec = importlib.util.spec_from_file_location("csv_inventory", ROOT / "csv_inventory.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "hosts.csv"
            path.write_text("name,group,role\nexample-a,lab,router\nexample-b,lab,switch\n")
            result = module.csv_to_inventory(str(path), "group", "name")
            self.assertEqual(result["lab"]["hosts"], ["example-a", "example-b"])
            self.assertEqual(result["_meta"]["hostvars"]["example-b"]["role"], "switch")

    def test_cli_config_and_list_use_only_synthetic_inventory(self):
        import json
        import os
        import subprocess
        import sys
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            directory = pathlib.Path(tmp)
            source = directory / "synthetic.csv"
            source.write_text("name,group\nexample-only,lab\n")
            env = dict(os.environ, CSV_INVENTORY_CONFIG=str(directory / "test.cfg"))
            script = str(ROOT / "csv_inventory.py")
            subprocess.run([sys.executable, script, "--config", "--file", str(source),
                            "--hostname-col", "name", "--group-by-col", "group"],
                           cwd=directory, env=env, check=True, capture_output=True, text=True)
            result = subprocess.run([sys.executable, script, "--list"], cwd=directory,
                                    env=env, check=True, capture_output=True, text=True)
            self.assertEqual(json.loads(result.stdout)["lab"]["hosts"], ["example-only"])
