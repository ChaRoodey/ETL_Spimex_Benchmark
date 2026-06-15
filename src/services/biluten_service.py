import asyncio
import logging
from datetime import datetime

from src.clients.spimex_client import SpimexClient
from src.db.bulletin_repository import BulletinRepository
from src.db.models import BulletinModel
from src.db.session import SessionLocal
from src.parsers.pdf_parser import PdfParser
from src.parsers.excel_parser import ExcelParser

logger = logging.getLogger(__name__)


class BilutenService:
    def __init__(self, page_amount):
        self.pdf_parser = PdfParser()
        self.excel_parser = ExcelParser()
        self.sem = asyncio.Semaphore(10)
        self.page_amount = page_amount

        self.total_rows = 0
        self.total_pdf_files = 0
        self.total_excel_files = 0
        self.failed_to_download_files = 0

    async def collect_data(self) -> None:
        async with SpimexClient() as client:
            file_urls = await client.get_file_urls(self.page_amount)

            async with asyncio.TaskGroup() as tg:
                logger.info("Processing started: %d files", len(file_urls))
                for link in file_urls:
                    logger.debug("Queue link %s", link)
                    tg.create_task(self.process_link(link, client))

            logger.info("ETL finished")

    async def process_link(self, link: str, client: SpimexClient) -> None:
        logger.info("Processing %s", link)
        try:
            async with self.sem:
                file = await client.download_file(link)
                if file:
                    await self.process_file(link, file)
                else:
                    self.failed_to_download_files += 1
        except Exception:
            logger.exception('Exception occurred while processing file: %s', link)

    async def process_file(self, link: str, file: bytes) -> None:
        bulletins = []
        curr_file_ext = ''
        ext, date = self._extract_data_from_link(link)

        if not ext or not date:
            logger.info('Failed to extract extension from link %s', link)
            return

        if date.year < 2023:
            return

        rows = []

        if ext in ("xlsx", "xls"):
            logger.debug("Parsing Excel file: %s", link)

            rows = await asyncio.to_thread(self.excel_parser.parse, file)
            await asyncio.sleep(1.5)
            curr_file_ext = 'excel'

            logger.debug("Done parsing Excel file: %s", link)
        elif ext == "pdf":
            logger.debug("Parsing PDF file: %s", link)

            rows = await asyncio.to_thread(self.pdf_parser.parse, file)
            curr_file_ext = 'pdf'

            logger.debug("Done parsing PDF file: %s", link)

        if not rows:
            logger.debug("No rows parsed from %s", link)
            return

        for row in rows:
            if str(row[0]).startswith("Итого") or not row:
                continue

            try:
                dog_count = int(row[-1])
            except (TypeError, ValueError):
                continue

            if dog_count > 0:
                obj = self.create_bulletin_obj(row, date)
                if obj:
                    bulletins.append(obj)

        if curr_file_ext == 'pdf':
            self.total_pdf_files += 1
        elif curr_file_ext == 'excel':
            self.total_excel_files += 1

        await self._save_bulletin(bulletins)

    async def _save_bulletin(self, bulletins: list[BulletinModel]) -> None:
        if not bulletins:
            return

        async with SessionLocal() as session:
            repo = BulletinRepository(session)

            await repo.add_many(bulletins)
            await session.commit()

            self.total_rows += len(bulletins)
            logger.debug("Saved bulletins: %d", len(bulletins))

    @staticmethod
    def create_bulletin_obj(row: list[str | None], date: datetime) -> BulletinModel | None:
        try:
            return BulletinModel(
                exchange_product_id=row[0],
                exchange_product_name=row[1],
                oil_id=row[0][:4],
                delivery_basis_id=row[0][4:7],
                delivery_basis_name=row[2],
                delivery_type_id=row[0][-1],
                volume=int(row[3]),
                total=int(row[4]),
                count=int(row[-1]),
                date=date,
            )
        except ValueError as e:
            logger.error('Skipping row: %s due to parse error: %s', row, e)
            return None

    @staticmethod
    def _extract_data_from_link(link: str) -> (str | None, datetime | None):
        filename = link.split('/')[-1]
        extension = filename.split('.')[1].split('?')[0]
        date_str = filename.split('_')[-1].split('.')[0]

        if not date_str:
            logger.error('Failed to extract date from link $s', link)
            return None, None

        return extension, datetime.strptime(date_str, '%Y%m%d%H%M%S')
