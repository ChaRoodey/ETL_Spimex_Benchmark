import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class BaseSpimexClient:
    BASE_URL = "https://spimex.com"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/137.0.0.0 Safari/537.36"
        )
    }

    def _parse_html(self, html: str, page: int) -> list[str]:
        page_urls = []
        soup = BeautifulSoup(html, 'html.parser')

        for a in soup.find_all('a', class_='accordeon-inner__item-title'):
            href = a.get('href')

            if href and a['href'].startswith('/files/trades/result/'):
                page_urls.append(self.BASE_URL + a['href'])

        logger.debug("Fetched %d links from page %d", len(page_urls), page)
        return page_urls
