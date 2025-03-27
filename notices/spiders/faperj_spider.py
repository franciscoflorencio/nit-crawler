import scrapy
from scrapy_playwright.page import PageMethod

class FaperjEditalSpider(scrapy.Spider):
    name = "faperj"
    custom_settings = {
        'ITEM_PIPELINES': {
            'notices.pipelines.FaperjPipeline': 300,
        },
    }
    allowed_domains = ["faperj.br"]
    start_urls = ["https://www.faperj.br/?id=415.6.5"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.tamanho-fonte"),
                    ],
                },
            )

    async def parse(self, response):
        # Extrair o conteúdo da página carregada pelo Playwright
        for p in response.xpath('//div[@class="tamanho-fonte"]//p[.//strong/a]'):
            title = p.xpath('.//strong/a/text()').get()
            if not title:
                continue
            title = title.strip()

            link = p.xpath('.//strong/a/@href').get()
            link = response.urljoin(link) if link else 'No link'

            # Extrair a descrição (todos os textos dentro do <p>, exceto o título)
            description_nodes = p.xpath('.//text()[not(ancestor::strong)]').getall()
            description = ' '.join([text.strip() for text in description_nodes if text.strip()])

            yield {
                'title': title,
                'link': link,
                'description': description.strip()
            }