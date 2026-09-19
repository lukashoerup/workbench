"""`docs/roles.md` is the only place the builder/reviewer assignment lives, and it
is read at the start of every session — so it must stay short and must always
name both Claude models, or a session cannot route work by cost."""
from pathlib import Path

ROLES = Path(__file__).resolve().parent.parent / "docs" / "roles.md"


def test_roles_file_exists_and_stays_short():
    lines = ROLES.read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 30, f"docs/roles.md is {len(lines)} lines, cap is 30"


def test_roles_file_names_both_models_and_the_reviewer():
    text = ROLES.read_text(encoding="utf-8").lower()
    for needle in ("opus", "fable", "astra", "allowed_warning"):
        assert needle in text, f"docs/roles.md no longer mentions {needle!r}"
