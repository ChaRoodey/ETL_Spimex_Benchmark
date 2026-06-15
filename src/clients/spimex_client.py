import asyncio
import logging
import random

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class SpimexClient:
    BASE_URL = 'https://spimex.com'

    async def __aenter__(self):
        self.connection = httpx.AsyncClient(
            timeout=60,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/137.0.0.0 Safari/537.36"
                )
            }
        )
        self.sem = asyncio.Semaphore(10)
        logger.info("SpimexClient started")
        return self

    async def __aexit__(self, *args):
        await self.connection.aclose()
        logger.info("SpimexClient closed")

    def _parse_html(self, html: str, page: int) -> list[str]:
        page_urls = []
        soup = BeautifulSoup(html, 'html.parser')

        for a in soup.find_all('a', class_='accordeon-inner__item-title'):
            href = a.get('href')

            if href and a['href'].startswith('/files/trades/result/'):
                page_urls.append(self.BASE_URL + a['href'])

        logger.debug("Fetched %d links from page %d", len(page_urls), page)
        return page_urls

    async def _get_url_by_page(self, page: int) -> list[str]:
        url = f'{self.BASE_URL}/markets/oil_products/trades/results/?page=page-{page}'
        logger.debug("Fetching page %s", url)
        async with self.sem:
            try:
                resp = await self.connection.get(url)
                resp.raise_for_status()
            except httpx.HTTPError as e:
                logger.exception("HTTP error for %s", url)
                raise

        return await asyncio.to_thread(self._parse_html, resp.text, page)

    async def get_file_urls(self, pages: int) -> list[str]:
        logger.info("Fetching started: %d pages", pages)
        tasks = [self._get_url_by_page(page) for page in range(1, pages + 1)]
        results = await asyncio.gather(*tasks)

        return [link for sublist in results for link in sublist]

    async def download_file(self, link: str) -> bytes | None:
        logger.debug("Downloading file %s", link)

        try:
            resp = await self.connection.get(link)
            resp.raise_for_status()
            logger.debug("File downloaded %s", link)
            return resp.content

        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            logger.error("Failed to download file %s: %s", status, link)
            return None

    # async def download_file(self, link: str, retries: int = 3) -> bytes | None:
    #     logger.debug("Downloading file %s", link)
    #
    #     for attempt in range(retries):
    #         try:
    #             resp = await self.connection.get(link)
    #             resp.raise_for_status()
    #             logger.debug("File downloaded %s", link)
    #             return resp.content
    #
    #         except httpx.HTTPStatusError as e:
    #             status = e.response.status_code
    #
    #             if status in (429, 503, 502, 504):
    #                 wait = 2 ** attempt + random.uniform(0, 3)
    #                 logger.warning(
    #                     "Retry %d for %s (status %s), sleep %ds",
    #                     attempt + 1, link, status, wait
    #                 )
    #                 await asyncio.sleep(wait)
    #                 continue
    #
    #             logger.exception("Fatal HTTP error for %s", link)
    #             raise
    #
    #     logger.error("Failed after retries: %s", link)
    #     return None

    # async with asyncio.TaskGroup() as tg:
    #     logger.info("Fetching url started: %d pages", len(pages))
    #     for page in pages:
    #         logger.debug("Queue page %s", page)
    #         tg.create_task(self._get_url_by_page(page))
    #
    # return file_links
