import logging

from src.clients.sync_spimex_client import SyncSpimexClient
from src.core.metrix import timer, ETLMetrics
from src.db.models import BulletinModel
from src.db.sync_bulletin_repository import SyncBulletinRepository
from src.db.sync_session import SyncSessionLocal
from src.services.base_bulletin_service import BaseBulletinService

logger = logging.getLogger(__name__)


class SyncBulletinService(BaseBulletinService):
    def __init__(self, page_amount):
        super().__init__(page_amount)

    def run(self) -> ETLMetrics:
        logger.info("Sync ETL started")
        with timer() as t:
            files = self.collect_data()
            self.metrix.download.time = t()
            self.metrix.download.count = len(files)

        bulletins = self.parse(files)

        with timer() as t:
            self._save_bulletin(bulletins)
            self.metrix.load.time = t()
            self.metrix.load.count = len(bulletins)

        logger.info("Sync ETL finished")
        return self.metrix

    def collect_data(self) -> list[tuple[str, bytes]]:
        with SyncSpimexClient() as client:
            file_urls = client.get_file_urls(self.page_amount)
            logger.info("Processing started: %d files", len(file_urls))
            results = []

            for link in file_urls:
                res = self.process_link(link, client)
                if res is not None:
                    results.append(res)

            return results

    def process_link(self, link: str, client: SyncSpimexClient) -> tuple[str, bytes] | None:
        logger.info("Processing %s", link)
        try:
            file = client.download_file(link)
            if file:
                return link, file
        except Exception:
            logger.exception('Exception occurred while processing file: %s', link)
            return None

    def _save_bulletin(self, bulletins: list[BulletinModel]) -> None:
        if not bulletins:
            return

        with SyncSessionLocal() as session:
            repo = SyncBulletinRepository(session)
            try:
                repo.add_many(bulletins)
                session.commit()
            except Exception:
                logger.error("Error saving bulletins")
                session.rollback()

            # self.total_rows += len(bulletins)
            logger.debug("Saved bulletins: %d", len(bulletins))
