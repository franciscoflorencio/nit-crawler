import scrapy
import re
from notices.items import CnpqItem

class CnpqSpider(scrapy.Spider):
    name = "cnpq"
    custom_settings = {
        'ITEM_PIPELINES': {
            'notices.pipelines.CnpqPipeline': 300,
        },
    }
    allowed_domains = ["memoria2.cnpq.br"]
    start_urls = ["http://memoria2.cnpq.br/web/guest/chamadas-publicas"]

    def parse(self, response):
        notices = response.css('div.content')
        bottoms = response.css('div.bottom-content')
        row_fluid = bottoms.css('div.row-fluid')

        for i, notice in enumerate(notices):
            item = CnpqItem()
            item['title'] = notice.css('h4::text').get(default='').strip()
            # Get all paragraphs of the current notice
            description_paragraphs = notice.css('p::text').getall()
            item['description'] = [desc.strip() for desc in description_paragraphs]
            inscriptions = notice.css('div.inscricao li::text').getall()
            # Join all inscription deadlines if needed
            item['deadline'] = ' '.join(inscriptions).strip()
            # Get link (same approach)
            item['link'] = row_fluid.css('a.btn')[i].attrib['href'] if i < len(row_fluid.css('a.btn')) else ''
            yield item
