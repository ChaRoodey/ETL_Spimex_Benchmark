import logging
from io import BytesIO
import pandas as pd

logger = logging.getLogger(__name__)


class ExcelParser:
    @staticmethod
    def parse(excel_bytes: bytes) -> list[str]:
        try:
            df = pd.read_excel(BytesIO(excel_bytes), header=None)

            mask = df.astype(str).apply(
                lambda col: col.str.contains("Единица измерения", na=False)
            )
            marker_rows = df.index[mask.any(axis=1)][-1]

            block = df.iloc[marker_rows + 3:-3].reset_index(drop=True)
            block = block.dropna(axis=1, how='all')

            return block.values.tolist()
        except Exception:
            logger.exception("Failed to parse Excel file")
            return []
