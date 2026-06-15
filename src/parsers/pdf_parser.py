import logging
from io import BytesIO
import pdfplumber

logger = logging.getLogger(__name__)


class PdfParser:
    @staticmethod
    def _find_metric_ton_y(page):
        try:
            words = page.extract_words()
            line_words = []
            current_top = None

            for word in words:
                top = round(word["top"], 1)

                if current_top is None:
                    current_top = top

                if abs(top - current_top) > 2:
                    line_text = " ".join(line_words)

                    if "Единица измерения: Метрическая тонна" in line_text:
                        return current_top

                    line_words = [word["text"]]
                    current_top = top
                else:
                    line_words.append(word["text"])

            line_text = " ".join(line_words)

            if "Единица измерения: Метрическая тонна" in line_text:
                return current_top

            return None

        except Exception:
            logger.exception("Failed to locate metric section in PDF page")
            return None

    def parse(self, pdf_bytes) -> list[list[str | None]]:
        result_rows = []
        try:
            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                metric_section_started = False

                for page in pdf.pages:
                    if not metric_section_started:
                        metric_y = self._find_metric_ton_y(page)

                        if metric_y is None:
                            continue

                        metric_section_started = True
                        tables = page.find_tables()

                        for table in tables:
                            _, table_top, _, _ = table.bbox

                            if table_top > metric_y:
                                rows = table.extract()

                                if rows:
                                    result_rows.extend(rows)
                                break
                        continue

                    text = page.extract_text() or ""

                    if (
                            "Единица измерения: Кубический метр" in text
                            or "Единица измерения: Килограмм" in text
                    ):
                        break

                    tables = page.find_tables()

                    if not tables:
                        continue

                    rows = tables[0].extract()

                    if rows:
                        result_rows.extend(rows)
        except Exception:
            logger.exception("Failed to parse PDF document")
            return []

        return result_rows[2:]
