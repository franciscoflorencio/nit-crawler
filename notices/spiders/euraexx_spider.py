import scrapy
from notices.items import EuraexxItem  # Import the EuraexxItem

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
        self.logger.info(f"Found {len(results)} results")

        for result in results:
            # Extract title
            title = result.xpath(".//h3[@class='ecl-content-block__title']/a/text()").get(default="No title").strip()

            # Extract link
            link = result.xpath(".//h3[@class='ecl-content-block__title']/a/@href").get(default="").strip()

            # Extract description
            description = result.xpath(".//div[@class='ecl-content-block__description']/p/text()").get(default="No description").strip()

            # Extract opening and closing dates
            opening_date = result.xpath(".//li[contains(@class, 'ecl-content-block__primary-meta-item') and contains(text(), 'Posted on:')]/text()").get(default="").replace("Posted on:", "").strip()
            closing_date = result.xpath(".//div[contains(@class, 'id-Deadline')]//div[@class='ecl-text-standard ecl-u-d-flex ecl-u-flex-column']/text()").get(default="").strip()

            # Create and yield the item
            item = EuraexxItem(
                title=title,
                link=link,
                description=description,
                opening_date=opening_date,
                closing_date=closing_date,
            )
            yield item