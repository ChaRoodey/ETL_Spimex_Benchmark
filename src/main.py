import time
import asyncio
import logging

from src.db.session import create_tables
from src.services.biluten_service import BilutenService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

for lib in ["httpx", "httpcore", "pdfplumber", "pandas", "urllib3", "pdfminer"]:
    logging.getLogger(lib).setLevel(logging.ERROR)

if __name__ == '__main__':
    # asyncio.run(create_tables()) # Раскомментировать при инициализации

    service = BilutenService(85)
    start = time.perf_counter()

    asyncio.run(service.collect_data())
    end = time.perf_counter()

    print(f"""
    ETL finished:
    - Time: {end - start:.2f} sec
    - PDF files processed: {service.total_pdf_files}
    - Excel files processed: {service.total_excel_files}
    - Failed to download: {service.failed_to_download_files}
    - Rows inserted: {service.total_rows}
    """)
