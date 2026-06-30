import logging
from datetime import datetime

from src.core.metrix import ETLMetrics, timer
from src.db.models import BulletinModel
from src.parsers.excel_parser import ExcelParser
from src.parsers.pdf_parser import PdfParser
from src.schemas.bulletin import BulletinAddSchema

logger = logging.getLogger(__name__)


class BaseBulletinService:
    def __init__(self, page_amount):
        self.pdf_parser = PdfParser()
        self.excel_parser = ExcelParser()
        self.page_amount = page_amount

        self.metrix = ETLMetrics()

    def parse(self, files: list[tuple[str, bytes]]) -> list[BulletinModel]:
        with timer() as t:
            bulletins = []

            for file_data in files:
                bulletin = self.process_file(file_data[0], file_data[1])

                if bulletin is not None:
                    bulletins.extend(bulletin)

            self.metrix.parse.time = t()
            self.metrix.parse.count = len(bulletins)

        return bulletins

    def process_file(self, link: str, file: bytes) -> list[BulletinModel]:
        bulletins = []
        ext, date = self._extract_data_from_link(link)

        if not ext or not date:
            logger.info('Failed to extract extension from link %s', link)
            return []

        if date.year < 2023:
            return []

        rows = []

        if ext in ("xlsx", "xls"):
            logger.debug("Parsing Excel file: %s", link)

            rows = self.excel_parser.parse(file)
            # time.sleep(1.5)
            curr_file_ext = 'excel'

            logger.debug("Done parsing Excel file: %s", link)
        elif ext == "pdf":
            logger.debug("Parsing PDF file: %s", link)

            rows = self.pdf_parser.parse(file)
            curr_file_ext = 'pdf'

            logger.debug("Done parsing PDF file: %s", link)

        if not rows:
            logger.debug("No rows parsed from %s", link)
            return []

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

        # if curr_file_ext == 'pdf':
        #     self.total_pdf_files += 1
        # elif curr_file_ext == 'excel':
        #     self.total_excel_files += 1

        return bulletins

    @staticmethod
    def create_bulletin_obj(row: list[str | None], date: datetime) -> BulletinModel | None:
        try:
            bulletin_schema = BulletinAddSchema(
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
            return BulletinModel(**bulletin_schema.model_dump())
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
