"""Put the repo root on sys.path so tests can import the two scripts."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# The reference package this toolkit was reverse-engineered against. Tests that
# need it skip cleanly when it is absent, so the suite still runs in a clean
# checkout (the .oap is deliberately not committed - it may hold customer model
# data).
OAP = ROOT / "Test Application.oap"
