import scrapy
from notices.items import FapespItem

class FapespSpider(scrapy.Spider):
    name = "fapesp"
    allowed_domains = ["fapesp.br"]
    start_urls = ["https://fapesp.br/oportunidades/"]

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "ROBOTSTXT_OBEY": False
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
                    deadline = opportunity.xpath('.//span[@class="text-principal"]/strong[contains(text(), "Inscrições até") or contains(text(), "Deadline")]/following-sibling::text()[1]').get().strip(),
                    description = opportunity.css('span.text-resumo p::text').get().strip(),
                    link = opportunity.css('a.link_col::attr(href)').get()
            )


