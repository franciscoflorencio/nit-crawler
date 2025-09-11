
import scrapy
from notices.items import EurekaItem
from scrapy_playwright.page import PageMethod


class EurekaSpider(scrapy.Spider):
    name = "eureka"
    allowed_domains = ["eurekanetwork.org"]
    start_urls = ["https://eurekanetwork.org/programmes-and-calls/"]

    custom_settings = {
        "ITEM_PIPELINES": {
            "notices.pipelines.EurekaPipeline": 300,
        },
        "PLAYWRIGHT_BROWSER_TYPE": "firefox",
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
    }

    def start_requests(self):
        from scrapy_playwright.page import PageMethod
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_context_kwargs": {"ignore_https_errors": True},
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.shadow-lg.group", timeout=10000),
                    ],
                },
                callback=self.parse,
            )

    def parse(self, response):
        for card in response.css("div.shadow-lg.group"):
            link = card.css("a[aria-label]::attr(href)").get()
            title = card.css("a[aria-label]::attr(aria-label)").get()
            closing_date = None  # Adjust if you find a selector for deadline
            image_url = card.css("img::attr(src)").get()
            item = EurekaItem(
                title=title.strip() if title else "",
                closing_date=closing_date.strip() if closing_date else "",
                link=response.urljoin(link) if link else "",
                image_url=image_url if image_url else "",
            )
            if link:
                yield response.follow(
                    response.urljoin(link),
                    callback=self.parse_opportunity,
                    meta={
                        "item": item,
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_context_kwargs": {"ignore_https_errors": True},
                        "playwright_page_methods": [
                            PageMethod("wait_for_selector", "h1.heading-xl", timeout=10000),
                        ],
                    },
                )
            else:
                yield item

        # Pagination
        next_page = response.css("a.pagination__next::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            from scrapy_playwright.page import PageMethod
            yield scrapy.Request(
                next_page_url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_context_kwargs": {"ignore_https_errors": True},
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.shadow-lg.group", timeout=10000),
                    ],
                },
                callback=self.parse,
            )

    def parse_opportunity(self, response):
        item = response.meta["item"]

        title = response.css("h1.heading-xl::text").get()
        if title:
            item["title"] = title.strip()

        apply_from = response.xpath(
            "//p[contains(text(), 'Apply from')]/following-sibling::p[1]/text()"
        ).get()
        apply_until = response.xpath(
            "//p[contains(text(), 'Until')]/following-sibling::p[1]/text()"
        ).get()
        if not apply_from:
            # fallback for structure seen in screenshot
            apply_from = response.xpath(
                "//div[contains(@class,'bg-white')]//div[contains(@class,'flex')][1]//p[contains(@class,'ml-2')]/text()"
            ).get()
        if not apply_until:
            apply_until = response.xpath(
                "//div[contains(@class,'bg-white')]//div[contains(@class,'flex')][2]//p[contains(@class,'ml-2')]/text()"
            ).get()
        item["opening_date"] = apply_from.strip() if apply_from else None

        # Description (first block after the title)
        description = response.css("div.font-inconsolata.mt-6").xpath("string()").get()
        item["description"] = description.strip() if description else None

        # Countries
        countries = response.css(
            "div.grid.grid-cols-2.lg\\:grid-cols-3.xl\\:grid-cols-4 span.paragraph-base.break-words::text"
        ).getall()
        item["countries"] = [c.strip() for c in countries if c.strip()]

        # Sections: scope, timeframe, funding-details, eligibility, apply, evaluation, downloadables
        def get_section(id_):
            return (
                response.xpath(
                    f'//h2[@id="{id_}"]/following-sibling::div[contains(@class, "wysiwyg")][1]'
                )
                .xpath("string()")
                .get()
            )

        item["scope"] = get_section("scope")
        item["timeframe"] = get_section("timeframe")
        item["funding_details"] = get_section("funding-details")

        yield item