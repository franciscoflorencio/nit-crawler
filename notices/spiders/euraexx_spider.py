import scrapy

class EuraexxSpider(scrapy.Spider):
    name = "euraexx"
    custom_settings = {
        'ITEM_PIPELINES': {
            'notices.pipelines.EuraexxPipeline': 305
        },
        'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
        'DOWNLOAD_HANDLERS': {
            'http': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
            'https': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
        },
        'ROBOTSTXT_OBEY': False, 
    }
    allowed_domains = ["euraxess.ec.europa.eu"]
    start_urls = ["https://euraxess.ec.europa.eu/jobs/search"]

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
        # Extract and list all titles from the results
        results = response.xpath("//article[@class='ecl-content-item']")
        self.logger.info(f"Found {len(results)} results")
        for result in results:
            # Extract title from the <span> inside <a> within <h3>
            title = result.xpath(".//h3[@class='ecl-content-block__title']/a/span/text()").get(default="No title").strip()
            self.logger.info(f"Title: {title}")
            yield {"title": title}