import scrapy
from notices.items import DaadItem

class DaadSpider(scrapy.Spider):
    name = "daad"
    allowed_domains = ["www.daad.org.br"]
    start_urls = ["https://www.daad.org.br/pt/category/bolsas-de-estudos/"]

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }
    def start_requests(self):
        url = "https://www.daad.org.br/pt/category/bolsas-de-estudos/"
        yield scrapy.Request(url, meta={"playwright": True})

    def parse(self, response):
        main = response.css('main')
        section = main.css('section')
        ul = section.css('ul')


        for opportunity in ul.css('li'):

            if not opportunity.css('h3::text').get():
                continue

            daad_item = DaadItem()

            daad_item['title'] = opportunity.css('h3::text').get().strip()
            daad_item['link'] = opportunity.css('a::attr(href)').get()
            daad_item['description'] = opportunity.css('p.u-size-teaser::text').get()
            daad_item['observation'] = opportunity.css('p::text').get()
            
            yield daad_item
