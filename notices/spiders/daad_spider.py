import scrapy


class DaadSpider(scrapy.Spider):
    name = "daad"
    allowed_domains = ["www.daad.org.br"]
    start_urls = ["https://www.daad.org.br/pt/category/bolsas-de-estudos/"]

    def parse(self, response):
        pass
