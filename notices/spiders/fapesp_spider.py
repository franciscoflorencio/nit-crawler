import scrapy
from notices.items import FapespItem

class FapespSpider(scrapy.Spider):
    name = "fapesp"
    allowed_domains = ["fapesp.br"]
    start_urls = ["https://fapesp.br/oportunidades/"]

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_IGNORE_HTTPS_ERRORS": True,
        "PLAYWRIGHT_CONTEXT_ARGS": {
            "ignore_https_errors": True,
            "viewport": {"width": 1280, "height": 720},
        },
        "PLAYWRIGHT_PAGE_GOTO_KWARGS": {
            "wait_until": "domcontentloaded",
            "timeout": 60_000,
        },
        "DOWNLOAD_DELAY": 5.0,
        "ROBOTSTXT_OBEY": False,

        'ITEM_PIPELINES': {
            'notices.pipelines.FapespPipeline': 300,
        },
    }

    def start_requests(self):
        url = "https://fapesp.br/oportunidades/"
        yield scrapy.Request(url, meta={"playwright": True})

    def parse(self, response):
        for opportunity in response.css('ul.list li.box_col:not([style*="display: none"])'):
            yield FapespItem(
                    title = opportunity.css('strong.title::text').get().strip(),
                    institution = opportunity.xpath('.//span[@class="text-principal"]/strong[contains(text(), "Instituição")]/following-sibling::text()[1]').get().strip(),
                    city = opportunity.xpath('.//span[@class="text-principal"]/strong[contains(text(), "Cidade")]/following-sibling::text()[1]').get().strip(),
                    closing_date = opportunity.xpath('.//span[@class="text-principal"]/strong[contains(text(), "Inscrições até") or contains(text(), "Deadline")]/following-sibling::text()[1]').get().strip(),
                    description = opportunity.css('span.text-resumo p::text').get().strip(),
                    link = opportunity.css('a.link_col::attr(href)').get(),
                    country = "Brasil"
            )
