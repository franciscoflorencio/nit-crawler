import scrapy
from scrapy.http import Response
from typing import Any, Iterable
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

    def parse(self, response: Response, **kwargs: Any) -> Iterable[Any]:
        # Pagination details
        results = response.css('li.resultSearch::text').get()
        if not results:
            return

        parts = results.split()
        if len(parts) < 4:
            return

        total_notices = int(parts[3])
        start_end = parts[1].split('-')
        if len(start_end) < 2:
            return

        current_page_start = int(start_end[0])
        items_per_page = int(start_end[1])

        notices = response.css('div.content')
        bottoms = response.css('div.bottom-content')
        row_fluid = bottoms.css('div.row-fluid')

        for i, notice in enumerate(notices):
            date_selector = response.css('div.inscricao ul.datas li::text')
            if i < len(date_selector):
                date_text = date_selector[i].get() or ""
            else:
                date_text = ""

            dates = date_text.split(' a ') if date_text else []

            item = CnpqItem()
            item['title'] = notice.css('h4::text').get(default='').strip()
            # Get all paragraphs of the current notice
            description_paragraphs = notice.css('p::text').getall()
            item['description'] = [
                desc.strip() for desc in description_paragraphs
            ]
            inscriptions = notice.css('div.inscricao li::text').getall()
            # Join all inscription deadlines if needed
            item['closing_date'] = ' '.join(inscriptions).strip()

            if len(dates) > 0:
                item['opening_date'] = dates[0]
            if len(dates) > 1:
                item['closing_date'] = dates[1]

            btn_selector = row_fluid.css('a.btn')
            if i < len(btn_selector):
                item['link'] = btn_selector[i].attrib.get('href', '')
            else:
                item['link'] = ''

            item['country'] = "Brasil"
            yield item

        current_items_count = len(notices)
        next_page_start = current_page_start + current_items_count

        if next_page_start < total_notices:
            next_page_number = (next_page_start // items_per_page) + 1
            url_params = (
                "?p_p_id=chamada_WAR_chamadasportlet&p_p_lifecycle=0&"
                "p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&"
                "p_p_col_count=1&_chamada_WAR_chamadasportlet_keywords=&"
                f"_chamada_WAR_chamadasportlet_delta={items_per_page}&"
                "_chamada_WAR_chamadasportlet_advancedSearch=false&"
                "_chamada_WAR_chamadasportlet_andOperator=true&"
                "_chamada_WAR_chamadasportlet_resetCur=false&"
                f"_chamada_WAR_chamadasportlet_cur={next_page_number}"
            )
            next_page_url = (
                "http://memoria2.cnpq.br/web/guest/chamadas-publicas"
                f"{url_params}"
            )

            yield scrapy.Request(next_page_url, callback=self.parse)
