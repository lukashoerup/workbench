"""docs/roles.md is the single record of which model builds and which reviews.

The direction work of 2026-09-12 asks for the role assignment to live apart from
project rules so it can change with subscriptions. A record that can change is a
record that can rot: a row goes blank, a paid fallback slips in, the date stops
moving. These checks keep the file usable by the next session without reading
minds.
"""
import re
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ROLES = REPO / "docs" / "roles.md"


def rows():
    """Table rows as {role: (provider, paid_for_by, cadence)}."""
    out = {}
    for line in ROLES.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or set(line.strip("| ")) <= {"-", "|", " "}:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 4 and cells[0] not in ("Role",):
            out[cells[0]] = tuple(cells[1:])
    return out


def test_builder_and_reviewer_are_both_named():
    r = rows()
    for role in ("Builder", "Reviewer"):
        assert role in r, f"{role} row missing from docs/roles.md"
        provider, paid, cadence = r[role]
        assert provider and paid and cadence, f"{role} row has an empty cell"


def test_no_paid_fallback_can_slip_in():
    """Lukas's standing rule: no API keys, overage or credits for either provider.
    The Fallback row exists so that anyone tempted to add one has to change a
    line this test reads."""
    r = rows()
    assert r["Fallback"][0] == "none"
    for role, (provider, paid, _) in r.items():
        assert not re.search(r"api key|overage|credits on|credit purchase", paid, re.I), (
            f"{role} row names a paid route: {paid!r}"
        )
    assert "credits off" in r["Builder"][1]


def test_changed_date_is_real_and_not_in_the_future():
    m = re.search(r"^Changed: (\d{4}-\d{2}-\d{2})", ROLES.read_text(encoding="utf-8"), re.M)
    assert m, "docs/roles.md needs a 'Changed: YYYY-MM-DD' line"
    assert date.fromisoformat(m.group(1)) <= date.today()
