import scrapy
from notices.items import AnrItem


class AnrSpider(scrapy.Spider):
    name = "anr"
    allowed_domains = ["anr.fr"]
    start_urls = ["https://anr.fr/en/open-calls-and-preannouncements/"]

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "firefox",  # Changed from chromium to firefox
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        }
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_context_kwargs": {
                        "ignore_https_errors": True,
                    },
                },
                callback=self.parse,
            )

    def parse(self, response):
        accordion = response.css('div.accordion.accordion--search')

        for opportunity in accordion.css('div.card.appel'):

            date_div = opportunity.css('div.date.my-2::text').getall()
            compound_date = ''.join([date.strip() for date in date_div if date.strip()])
            split_date = compound_date.split('-')

            if len(split_date) >= 2:
                opening_date = split_date[0].strip()
                closing_date = split_date[1].strip()
            else:
                opening_date = compound_date
                closing_date = None

            anr_item = AnrItem()

            anr_item['observation'] = opportunity.css('span.tag-type::text').get().strip()
            anr_item['opening_date'] = opening_date
            anr_item['closing_date'] = closing_date
            anr_item['title'] = opportunity.css('h2 a::text').get().strip()
            anr_item['description'] = opportunity.css('p::text').get().strip()
            anr_item['link'] = response.urljoin(opportunity.css('h2 a::attr(href)').get())
            anr_item['country'] = "França"
            yield anr_item

        # Handle pagination
        next_page = response.css('ul.pagination li.page-item:not(.active) a.page-link-next::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            self.logger.info(f"Following next page: {next_page_url}")
            yield scrapy.Request(
                next_page_url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_context_kwargs": {
                        "ignore_https_errors": True,
                    },
                },
                callback=self.parse,
            )
