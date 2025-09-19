import scrapy
from notices.items import EurekaItem


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

    async def start(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={"playwright": True, "playwright_include_page": True},
                callback=self.parse,
            )

    def parse(self, response):
        for card in response.css("div.bg-white.group"):
            link = card.css("a.h-full.flex.flex-col::attr(href)").get()
            title = card.css("h2.heading-md.mt-3::text").get()
            closing_date = card.css(
                "div.flex.items-center.justify-end.font-inconsolata.text-xs.font-bold::text"
            ).re_first(r"Deadline\s*(.*)")
            image_url = card.css("img::attr(src)").get()
            item = EurekaItem(
                title=title.strip() if title else "",
                closing_date=closing_date.strip() if closing_date else "",
                link=response.urljoin(link) if link else "",
                image_url=image_url if image_url else "",
            )
            if link:
                yield response.follow(
                    link,
                    callback=self.parse_opportunity,
                    meta={
                        "item": item,
                        "playwright": True,
                        "playwright_include_page": True,
                    },
                )
            else:
                yield item

        # Pagination
        next_page = response.css("a.next.page-numbers::attr(href)").get()
        if next_page:
            yield scrapy.Request(next_page, callback=self.parse)
            yield scrapy.Request(
                response.urljoin(next_page), callback=self.parse, meta={"playwright": True}
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
        item["closing_date"] = apply_until.strip() if apply_until else None

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