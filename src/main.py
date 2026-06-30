import time
import asyncio
import logging
import typer
from rich.console import Console
from rich.table import Table

from src.core.metrix import ETLMetrics, timer
from src.db.async_session import create_tables
from src.services.async_bulletin_service import AsyncBulletinService
from src.services.sync_bulletin_service import SyncBulletinService

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

for lib in ["httpx", "httpcore", "pdfplumber", "pandas", "urllib3", "pdfminer"]:
    logging.getLogger(lib).setLevel(logging.ERROR)

app = typer.Typer()
console = Console()


def display_metrics(metrics: ETLMetrics, total_time: float) -> None:
    table = Table(title="ETL Metrics")

    table.add_column("Metric", justify="center")
    table.add_column("Count", justify="center")
    table.add_column("Time", justify="center")

    table.add_row(
        "Download files",
        str(metrics.download.count),
        f"{metrics.download.time:.2f}"
    )

    table.add_row(
        "Parse files",
        str(metrics.parse.count),
        f"{metrics.parse.time:.2f}"
    )

    table.add_row(
        "Load to DB",
        str(metrics.load.count),
        f"{metrics.load.time:.2f}"
    )

    table.add_section()

    table.add_row(
        "Total",
        "-",
        f"{total_time:.2f}",
        style="bold green",
    )

    console.print(table)


def display_benchmark_metrics(
        sync_metrics: ETLMetrics,
        sync_total_time: float,
        async_metrics: ETLMetrics,
        async_total_time: float,
) -> None:
    def speedup(sync: float, async_: float) -> str:
        if async_ == 0:
            return "∞"
        return f"{sync / async_:.2f}x"

    table = Table(title="Sync vs Async Benchmark")

    table.add_column("Metric", style="cyan")
    table.add_column("Sync", justify="right")
    table.add_column("Async", justify="right")
    table.add_column("Speedup", justify="right", style="green")

    table.add_row(
        "Download files",
        f"{sync_metrics.download.time:.2f}s",
        f"{async_metrics.download.time:.2f}s",
        speedup(sync_metrics.download.time, async_metrics.download.time),
    )

    table.add_row(
        "Parse data",
        f"{sync_metrics.parse.time:.2f}s",
        f"{async_metrics.parse.time:.2f}s",
        speedup(sync_metrics.parse.time, async_metrics.parse.time),
    )

    table.add_row(
        "Load to DB",
        f"{sync_metrics.load.time:.2f}s",
        f"{async_metrics.load.time:.2f}s",
        speedup(sync_metrics.load.time, async_metrics.load.time),
    )

    table.add_section()

    table.add_row(
        "Total",
        f"{sync_total_time:.2f}s",
        f"{async_total_time:.2f}s",
        speedup(sync_total_time, async_total_time),
        style="bold green",
    )

    console.print(table)


def execute_sync(pages) -> tuple[ETLMetrics, float]:
    with timer() as t:
        sync_service = SyncBulletinService(pages)
        metrix = sync_service.run()

    return metrix, t()


async def execute_async(pages) -> tuple[ETLMetrics, float]:
    with timer() as t:
        async_service = AsyncBulletinService(pages)
        metrix = await async_service.run()

    return metrix, t()


@app.command()
async def init_db() -> None:
    await create_tables()


@app.command()
def run_sync(pages: int = typer.Option(1, help="Number of pages to run")) -> None:
    metrix, total_time = execute_sync(pages)
    display_metrics(metrix, total_time)


@app.command()
def run_async(pages: int = typer.Option(1, help="Number of pages to run")) -> None:
    metrix, total_time = asyncio.run(execute_async(pages))
    display_metrics(metrix, total_time)


@app.command()
def benchmark(pages: int = typer.Option(1, help="Number of pages to run")) -> None:
    sync_metrix, sync_total_time = execute_sync(pages)
    async_metrix, async_total_time = asyncio.run(execute_async(pages))
    display_benchmark_metrics(sync_metrix, sync_total_time, async_metrix, async_total_time)


if __name__ == '__main__':
    app()
    # asyncio.run(create_tables())  # Раскомментировать при инициализации

    # service = AsyncBulletinService(2)  # 85
    # start = time.perf_counter()
    #
    # asyncio.run(service.run())
    # end = time.perf_counter()
    #
    # print(f"""
    # ETL finished:
    # - Time: {end - start:.2f} sec
    # - Download: {service.metrix.download.count} for {service.metrix.download.time} s
    # - Parse: {service.metrix.parse.count} for {service.metrix.parse.time} s
    # - Load: {service.metrix.load.count} for {service.metrix.load.time} s
    # """)
