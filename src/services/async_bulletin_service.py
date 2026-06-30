import asyncio
import logging

from src.clients.async_spimex_client import AsyncSpimexClient
from src.core.config import settings
from src.core.metrix import timer, ETLMetrics
from src.db.async_bulletin_repository import AsyncBulletinRepository
from src.db.models import BulletinModel
from src.db.async_session import AsyncSessionLocal
from src.services.base_bulletin_service import BaseBulletinService

logger = logging.getLogger(__name__)


class AsyncBulletinService(BaseBulletinService):
    def __init__(self, page_amount):
        self.sem = asyncio.Semaphore(settings.DOWNLOAD_CONCURRENCY)
        super().__init__(page_amount)

    async def run(self) -> ETLMetrics:
        logger.info("Async ETL started")
        with timer() as t:
            files = await self.collect_data()
            self.metrix.download.time = t()
            self.metrix.download.count = len(files)

        bulletins = self.parse(files)

        with timer() as t:
            await self._save_bulletin(bulletins)
            self.metrix.load.time = t()
            self.metrix.load.count = len(bulletins)

        logger.info("Async ETL finished")
        return self.metrix

    async def collect_data(self) -> list[tuple[str, bytes]]:
        async with AsyncSpimexClient() as client:
            file_urls = await client.get_file_urls(self.page_amount)
            logger.info("Processing started: %d files", len(file_urls))

            tasks = [
                self.process_link(link, client)
                for link in file_urls
            ]

            results = await asyncio.gather(*tasks)

            return [res for res in results if res is not None]

    async def process_link(self, link: str, client: AsyncSpimexClient) -> tuple[str, bytes] | None:
        logger.info("Processing %s", link)
        try:
            async with self.sem:
                file = await client.download_file(link)
                if file:
                    return link, file
        except Exception:
            logger.exception('Exception occurred while processing file: %s', link)
            return None

    async def _save_bulletin(self, bulletins: list[BulletinModel]) -> None:
        if not bulletins:
            return

        async with AsyncSessionLocal() as session:
            repo = AsyncBulletinRepository(session)

            await repo.add_many(bulletins)

            # self.total_rows += len(bulletins)
            logger.debug("Saved bulletins: %d", len(bulletins))

            # async with asyncio.TaskGroup() as tg:
            #     for link in file_urls:
            #         logger.debug("Queue link %s", link)
            #         tasks.append(tg.create_task(self.process_link(link, client)))
            bulletins = []
            # for file_data in files:
            #     bulletin = await self.process_file(file_data[0], file_data[1])
            #
            #     if bulletin is not None:
            #         bulletins.extend(bulletin)
