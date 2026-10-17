"""Actual product supervisor with loopback-only measurement hooks."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from recon_pipeline import capture
from handoff_probe import MeasuredSession
capture.BrowserSession=MeasuredSession
if __name__=='__main__':
    assert '--fixture-only' in sys.argv
    capture.main()
