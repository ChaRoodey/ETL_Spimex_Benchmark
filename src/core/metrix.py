import time
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass
class StageMetrics:
    time: float = 0.0
    count: int = 0


@dataclass
class ETLMetrics:
    download: StageMetrics = field(default_factory=StageMetrics)
    parse: StageMetrics = field(default_factory=StageMetrics)
    load: StageMetrics = field(default_factory=StageMetrics)

    total_time: float = 0.0
    total_rows: int = 0


@contextmanager
def timer():
    start = time.perf_counter()
    yield lambda: time.perf_counter() - start
