import scrapy
import re
from datetime import datetime
from notices.items import EuraexxItem

class EuraexxSpider(scrapy.Spider):
    name = "euraexx"
    custom_settings = {
        'ITEM_PIPELINES': {
            'notices.pipelines.EuraexxPipeline': 305
        },
        'PLAYWRIGHT_BROWSER_TYPE': 'firefox',
        'USER_AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_HANDLERS': {
            'http': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
            'https': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
        },
    }
    allowed_domains = ["euraxess.ec.europa.eu"]
    start_urls = ["https://euraxess.ec.europa.eu/jobs/search?f%5B0%5D=offer_type%3Afunding"]

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls[0],
            meta={
                "playwright": True,
                "playwright_context": "default",
            },
            callback=self.parse
        )

    def parse(self, response):
        # Extract all job postings
        results = response.xpath("//article[@class='ecl-content-item']")
        self.logger.info(f"Found {len(results)} results on this page")

        for result in results:
            # Extract title
            title = result.xpath(".//h3[@class='ecl-content-block__title']/a/text()").get(default="No title").strip()

            # Extract link
            link = result.xpath(".//h3[@class='ecl-content-block__title']/a/@href").get(default="").strip()

            # Extract description
            description = result.xpath(".//div[@class='ecl-content-block__description']/p/text()").get(default="No description").strip()

            # Extract opening and closing dates by scanning the text inside the result
            text_blob = " ".join([t.strip() for t in result.xpath('.//text()').getall() if t.strip()])

            def normalize_date(date_str):
                """Normalize English dates like 'October 7, 2025' or '12 June 2025, 12:00 AM CEST' to 'dd/mm/YYYY'. Returns None if not parseable."""
                if not date_str:
                    return None
                s = re.sub(r'<[^>]+>', '', date_str).strip()
                # Try 'MonthName D, YYYY' e.g. 'October 7, 2025'
                m = re.search(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", s)
                if m:
                    month_name, day, year = m.group(1), m.group(2), m.group(3)
                else:
                    # Try 'D MonthName YYYY' e.g. '12 June 2025'
                    m = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", s)
                    if m:
                        day, month_name, year = m.group(1), m.group(2), m.group(3)
                    else:
                        return None
                # Map month name to number (support abbreviated names)
                try:
                    try:
                        month = datetime.strptime(month_name, '%B').month
                    except ValueError:
                        month = datetime.strptime(month_name, '%b').month
                except Exception:
                    months = {
                        'january':1,'jan':1,'february':2,'feb':2,'march':3,'mar':3,'april':4,'apr':4,
                        'may':5,'june':6,'jun':6,'july':7,'jul':7,'august':8,'aug':8,'september':9,'sep':9,
                        'october':10,'oct':10,'november':11,'nov':11,'december':12,'dec':12
                    }
                    month = months.get(month_name.lower())
                    if not month:
                        return None
                try:
                    d = int(day)
                    y = int(year)
                    return f"{d:02d}/{month:02d}/{y}"
                except Exception:
                    return None

            # Prefer explicit 'Posted on' text for opening_date, else pick first date in text
            opening_raw = result.xpath(".//li[contains(@class, 'ecl-content-block__primary-meta-item') and contains(text(), 'Posted on:')]/text()").get(default="").replace("Posted on:", "").strip()
            opening_date = normalize_date(opening_raw) if opening_raw else None
            if not opening_date:
                # fallback: take first date-looking substring in the text blob
                first_date = re.search(r"[A-Za-z]+\s+\d{1,2},\s*\d{4}|\d{1,2}\s+[A-Za-z]+\s+\d{4}", text_blob)
                opening_date = normalize_date(first_date.group(0)) if first_date else None

            # For closing date, try to find a date near keywords like 'Deadline' or 'Application deadline', else take last date in the block
            closing_date = None
            # Search for keyword + date
            keyword_date = re.search(r"(?:Deadline|Application deadline|Deadline:)[:\s\-]*([A-Za-z]+\s+\d{1,2},\s*\d{4}|\d{1,2}\s+[A-Za-z]+\s+\d{4})", text_blob, re.IGNORECASE)
            if keyword_date:
                closing_date = normalize_date(keyword_date.group(1))
            else:
                # take last date in the text blob
                all_dates = re.findall(r"[A-Za-z]+\s+\d{1,2},\s*\d{4}|\d{1,2}\s+[A-Za-z]+\s+\d{4}", text_blob)
                if all_dates:
                    closing_date = normalize_date(all_dates[-1])

            # Make link absolute
            link_abs = response.urljoin(link)

            # Create and yield each part of the item
            item = EuraexxItem(
                title=title,
                link=link_abs,
                description=description,
                opening_date=opening_date,
                closing_date=closing_date,
            )
            item['country'] = 'União Europeia'
            yield item

        # Pagination: follow the actual 'next' link href to avoid constructing URLs that may loop
        next_href = response.xpath("//li[contains(@class,'ecl-pagination__item--next')]//a/@href").get()
        if next_href:
            next_page_url = response.urljoin(next_href)
            self.logger.info(f"Navigating to next page: {next_page_url}")
            yield scrapy.Request(next_page_url, callback=self.parse)
