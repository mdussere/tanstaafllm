"""Every workline record says how fresh it is (Professor Step 13)."""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_every_record_has_a_freshness_banner():
    run = subprocess.run([sys.executable, str(ROOT / "scripts" / "doc_freshness.py"), "--check"],
                         cwd=ROOT, capture_output=True, text=True)
    assert run.returncode == 0, run.stdout
