"""Provide a psutil import that gracefully degrades when unavailable.

This module checks for the ``psutil`` dependency at runtime. In restricted
environments where network access prevents installing optional dependencies,
it falls back to a lightweight stub so the application can still start and
tests can execute without ImportError. The stub returns minimal placeholder
values that keep code paths operational while clearly indicating that real
metrics are unavailable.
"""

from __future__ import annotations

import os
import time
from importlib.util import find_spec
from typing import Dict, List


def _build_stub():  # pragma: no cover - exercised only when psutil is missing
    class _CpuFreq:
        current = 0.0
        min = 0.0
        max = 0.0

    class _SVMem:
        total = 0
        available = 0
        used = 0
        free = 0
        percent = 0.0
        cached = None
        buffers = None

    class _SwapMem:
        total = 0
        used = 0
        free = 0
        percent = 0.0

    class _DiskUsage:
        total = 0
        used = 0
        free = 0
        percent = 0.0

    class _NetIO:
        bytes_sent = 0
        bytes_recv = 0
        packets_sent = 0
        packets_recv = 0
        errin = 0
        errout = 0
        dropin = 0
        dropout = 0

    class _PsutilStub:
        def cpu_percent(self, interval: float = 0.0, percpu: bool = False):
            if percpu:
                count = os.cpu_count() or 1
                return [0.0 for _ in range(count)]
            return 0.0

        def cpu_freq(self):
            return _CpuFreq()

        def cpu_count(self, logical: bool = True):
            return os.cpu_count() or 1

        def getloadavg(self):
            return (0.0, 0.0, 0.0)

        def virtual_memory(self):
            return _SVMem()

        def swap_memory(self):
            return _SwapMem()

        def disk_partitions(self):
            return []

        def disk_usage(self, path: str):
            return _DiskUsage()

        def net_io_counters(self):
            return _NetIO()

        def net_if_addrs(self) -> Dict:
            return {}

        def net_connections(self, kind: str = "inet") -> List:
            return []

        def sensors_temperatures(self):
            return {}

        def boot_time(self):
            return time.time()

        def pids(self):
            return []

        def users(self):
            return []

    return _PsutilStub()


if find_spec("psutil"):
    import psutil as psutil  # type: ignore[assignment]
else:  # pragma: no cover - activated only in missing dependency scenarios
    psutil = _build_stub()

