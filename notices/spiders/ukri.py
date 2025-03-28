import scrapy


class UkriSpider(scrapy.Spider):
    name = "ukri"
    allowed_domains = ["www.ukri.org"]
    start_urls = ["https://www.ukri.org/opportunity/"]

    def parse(self, response):
        pass
