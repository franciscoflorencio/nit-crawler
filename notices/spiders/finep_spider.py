import scrapy
from notices.items import FinepItem

class FinepSpider(scrapy.Spider):
    name = "finep"
    """
    custom_settings = {
        'ITEM_PIPELINES': {
            'notices.pipelines.FinepPipeline': 303,
        },
    }
    """
    allowed_domains = ["finep.gov.br"]
    start_urls = ["http://www.finep.gov.br/chamadas-publicas/chamadaspublicas?situacao=aberta"]

    def parse(self, response):
        # Extract links to individual pages
        links = response.css("div.item h3 a::attr(href)").getall()
        for link in links:
            full_url = response.urljoin(link)
            yield scrapy.Request(url=full_url, callback=self.parse_details)

         # Handle pagination
        next_page = response.css("li.pagination-next a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse)
            
    def parse_details(self, response):
        # Extract data from the individual page
        title = response.css("h2.tit_pag a::text").get()
        description = " ".join(response.css("div.group.desc div.text p::text").getall()).strip()
        date = response.xpath("//div[contains(., 'Data de Publicação:')]/following-sibling::div[@class='text']/text()").get()
        closing_date = response.xpath("//div[contains(., 'Prazo para envio de propostas até:')]/following-sibling::div[@class='text']/text()").get()

        # Create and yield the item
        yield FinepItem(
            title=title,
            description=description,
            date=date,
            closing_date=closing_date,
            link=response.url
        )
