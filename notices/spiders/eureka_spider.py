import scrapy
from scrapy_playwright.page import PageMethod
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

    def _get_playwright_meta(self):
        """Returns the base metadata for a Playwright request."""
        return {
            "playwright": True,
            "playwright_include_page": True,
            "playwright_page_coroutines": [
                PageMethod("set_default_timeout", 30 * 1000),
                PageMethod(
                    "route",
                    "**/*",
                    lambda route: (
                        route.abort()
                        if route.request.resource_type in ("image", "font", "stylesheet")
                        else route.continue_()
                    ),
                ),
            ],
        }

    async def start(self):
        url = self.start_urls[0]
        meta = self._get_playwright_meta()
        yield scrapy.Request(url, callback=self.parse, meta=meta)

    async def parse(self, response):
        page = response.meta["playwright_page"]

        # Process all items on the current page
        cards = await page.query_selector_all("div.relative.rounded-lg.overflow-hidden.shadow-lg.group")
        for card in cards:
            link = await card.query_selector("a.absolute.inset-0.z-30")
            link_url = await link.get_attribute("href") if link else None

            if link_url:
                title_el = await card.query_selector("h3.text-white")
                title = await title_el.inner_text() if title_el else ""

                deadline_el = await card.query_selector("div.absolute.top-4 div.text-lg")
                deadline_text = await deadline_el.inner_html() if deadline_el else ""
                # Remove tags HTML e espaços extras
                import re
                deadline_text_clean = re.sub(r'<[^>]+>', '', deadline_text)
                closing_date_match = scrapy.Selector(text=deadline_text_clean).re_first(r"Deadline:\s*([\w\s,]+\d{4})")
                if closing_date_match:
                    closing_date_clean = closing_date_match.strip()
                else:
                    closing_date_clean = ""

                img_el = await card.query_selector("img")
                image_url = await img_el.get_attribute("src") if img_el else ""

                item = EurekaItem(
                    title=title.strip(),
                    closing_date=closing_date_clean,
                    link=response.urljoin(link_url),
                    image_url=image_url,
                )
                meta = self._get_playwright_meta()
                meta["item"] = item
                yield response.follow(link_url, callback=self.parse_opportunity, meta=meta)

        # Pagination
        next_page_link = await page.query_selector("a.next.page-numbers")
        if next_page_link:
            next_page_url = await next_page_link.get_attribute("href")
            await page.close()  # Explicitly close the current page
            yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse, meta=self._get_playwright_meta())

    def parse_opportunity(self, response):
        item = response.meta["item"]

        title = response.css("h1.heading-xl::text").get()
        if title:
            item["title"] = title.strip()


        # Extrai opening_date do bloco 'Start Date'
        opening_date_html = response.css("div.inconsolata-200:contains('Start Date')").get()
        import re
        opening_date_match = None
        if opening_date_html:
            opening_date_match = re.search(r'Start Date:</span>\s*([^<]+)', opening_date_html)
        item["opening_date"] = opening_date_match.group(1).strip() if opening_date_match else None

        # Extrai description do bloco 'div.space-y-4.text-lg#about'
        about_html = response.css("div.space-y-4.text-lg#about").get()
        if about_html:
            # Remove tags HTML e pega só o texto
            about_text = re.sub(r'<[^>]+>', '', about_html)
            item["description"] = about_text.strip()
        else:
            item["description"] = None

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
        item['country'] = 'mundo'

        yield item
