"""Unit tests for workbench-status.py collectors (the dash in the filename
means we load it via importlib rather than a plain import)."""
import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def load_status_mod():
    spec = importlib.util.spec_from_file_location(
        "workbench_status", REPO / "bin" / "workbench-status.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_repo_without_tests_dir_reports_none(tmp_path):
    mod = load_status_mod()
    assert mod.collect_tests(tmp_path) == {"state": "none"}


def test_node_repo_is_external_not_a_bogus_pytest_run(tmp_path):
    """A package.json repo (erhvervsklubben) must never have pytest run against
    it by the status timer — its suite needs npm + the Docker Supabase stack."""
    (tmp_path / "tests").mkdir()
    (tmp_path / "package.json").write_text("{}")
    mod = load_status_mod()
    assert mod.collect_tests(tmp_path) == {"state": "external"}


def test_erhvervsklubben_is_watched():
    mod = load_status_mod()
    assert any(r.name == "erhvervsklubben" for r in mod.REPOS)
