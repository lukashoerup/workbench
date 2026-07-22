import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "bin"))


@pytest.fixture
def fake_home(tmp_path, monkeypatch):
    """An isolated HOME so tests never touch the real ~/.secrets or ~/logs.

    Both notify.py and watchdog-check.sh derive every path from HOME, so this is
    the whole isolation story for both.
    """
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    (tmp_path / "logs").mkdir()
    (tmp_path / ".secrets").mkdir(mode=0o700)
    return tmp_path


@pytest.fixture
def notify_mod(fake_home):
    """notify.py bound to fake_home. Reimported per test so module-level
    Path.home() constants pick up the patched HOME."""
    for name in ("notify",):
        sys.modules.pop(name, None)
    import notify

    return notify
