import logging
from datetime import datetime

from src.core.metrix import ETLMetrics
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
