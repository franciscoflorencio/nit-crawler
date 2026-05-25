import scrapy
from scrapy.http import Response
from typing import Any, Iterable
from notices.items import AnrItem


class AnrSpider(scrapy.Spider):
    name = "anr"
    allowed_domains = ["anr.fr"]
    start_urls = ["https://anr.fr/en/open-calls-and-preannouncements/"]

    def parse(self, response: Response, **kwargs: Any) -> Iterable[Any]:
        for opportunity in response.css('div.card.appel'):
            anr_item = AnrItem()

            title_raw = opportunity.css('h2 a::text').get()
            anr_item['title'] = title_raw.strip() if title_raw else None

            link_raw = opportunity.css('h2 a::attr(href)').get()
            anr_item['link'] = response.urljoin(link_raw) if link_raw else None

            date_raw = opportunity.css('div.date::text').getall()
            date_text = " ".join([d.strip() for d in date_raw if d.strip()])
            if date_text:
                if '-' in date_text:
                    split_date = date_text.split('-')
                    anr_item['opening_date'] = split_date[0].strip()
                    anr_item['closing_date'] = split_date[1].strip()
                else:
                    anr_item['opening_date'] = date_text.strip()
                    anr_item['closing_date'] = None

            anr_item['country'] = "França"

            if anr_item.get('title') and anr_item.get('link'):
                yield anr_item

        next_page = response.css('a.page-link-next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
