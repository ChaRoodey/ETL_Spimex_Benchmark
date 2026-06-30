import asyncio
import logging
import random
import httpx
from src.clients.base_spimex_client import BaseSpimexClient

logger = logging.getLogger(__name__)


class AsyncSpimexClient(BaseSpimexClient):
    async def __aenter__(self):
        self.connection = httpx.AsyncClient(
            timeout=60,
            headers=self.HEADERS
        )
        self.sem = asyncio.Semaphore(10)
        logger.info("AsyncSpimexClient started")
        return self

    async def __aexit__(self, *args):
        await self.connection.aclose()
        logger.info("AsyncSpimexClient closed")

    async def _get_url_by_page(self, page: int) -> list[str]:
        url = f'{self.BASE_URL}/markets/oil_products/trades/results/?page=page-{page}'
        logger.debug("Fetching page %s", url)
        async with self.sem:
            try:
                resp = await self.connection.get(url)
                resp.raise_for_status()
            except httpx.HTTPError:
                logger.exception("HTTP error for %s", url)
                raise

        return await asyncio.to_thread(self._parse_html, resp.text, page)

    async def get_file_urls(self, pages: int) -> list[str]:
        logger.info("Fetching started: %d pages", pages)
        tasks = [self._get_url_by_page(page) for page in range(1, pages + 1)]
        results = await asyncio.gather(*tasks)

        return [link for sublist in results for link in sublist]

    async def download_file(self, link: str, retries: int = 3) -> bytes | None:
        logger.debug("Downloading file %s", link)

        for attempt in range(retries):
            try:
                resp = await self.connection.get(link)
                resp.raise_for_status()
                logger.debug("File downloaded %s", link)
                return resp.content

            except httpx.HTTPStatusError as e:
                status = e.response.status_code

                if status in (429, 503, 502, 504):
                    wait = 2 ** attempt + random.uniform(0, 3)
                    logger.warning(
                        "Retry %d for %s (status %s), sleep %ds",
                        attempt + 1, link, status, wait
                    )
                    await asyncio.sleep(wait)
                    continue

                logger.exception("Fatal HTTP error for %s", link)
                raise

        logger.error("Failed after retries: %s", link)
        return None

    # async def download_file(self, link: str) -> bytes | None:
    #     logger.debug("Downloading file %s", link)
    #
    #     try:
    #         resp = await self.connection.get(link)
    #         resp.raise_for_status()
    #         logger.debug("File downloaded %s", link)
    #         return resp.content
    #
    #     except httpx.HTTPStatusError as e:
    #         status = e.response.status_code
    #         logger.error("Failed to download file %s: %s", status, link)
    #         return None

    # async with asyncio.TaskGroup() as tg:
    #     logger.info("Fetching url started: %d pages", len(pages))
    #     for page in pages:
    #         logger.debug("Queue page %s", page)
    #         tg.create_task(self._get_url_by_page(page))
    #
    # return file_links
