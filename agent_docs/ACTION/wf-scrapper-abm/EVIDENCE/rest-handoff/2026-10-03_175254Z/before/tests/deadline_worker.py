"""Loopback timing fixture: actual product supervisor/worker, delayed CDP setup.

Only scheduling latency is injected. No transport, response, timeout result or
protocol error is substituted. Spawned workers execute this same module setup.
"""
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from recon_pipeline import capture


class SetupLatency(capture.BrowserSession):
    async def correlated_read(self, expression):
        self.event('fixture_setup_delay', seconds=0.6)
        await asyncio.sleep(0.6)
        return await super().correlated_read(expression)


capture.BrowserSession=SetupLatency

if __name__=='__main__':
    assert '--fixture-only' in sys.argv, 'This helper is exclusively for loopback fixtures'
    capture.main()
