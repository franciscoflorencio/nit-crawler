import scrapy
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
        #this is for pagination
        results = response.css('li.resultSearch::text').get()
        parts = results.split()
        total_notices = int(parts[3])
        start_end = parts[1].split('-')
        current_page_start = int(start_end[0])
        items_per_page = int(start_end[1])

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

        current_items_count = len(notices)
        next_page_start = current_page_start + current_items_count

        if next_page_start < total_notices:
            next_page_number = (next_page_start // items_per_page) + 1
            next_page_url = f"http://memoria2.cnpq.br/web/guest/chamadas-publicas?p_p_id=chamada_WAR_chamadasportlet&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&_chamada_WAR_chamadasportlet_keywords=&_chamada_WAR_chamadasportlet_delta={items_per_page}&_chamada_WAR_chamadasportlet_advancedSearch=false&_chamada_WAR_chamadasportlet_andOperator=true&_chamada_WAR_chamadasportlet_resetCur=false&_chamada_WAR_chamadasportlet_cur={next_page_number}"
            
            yield scrapy.Request(next_page_url, callback=self.parse)
