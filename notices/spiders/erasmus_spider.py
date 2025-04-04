import scrapy
import json
from notices.items import EacItem


class EramusSpider(scrapy.Spider):
    name = "erasmus"
    custom_settings = {
            'ITEM_PIPELINES': {
                'notices.pipelines.EacPipeline': 100
            },
            'DOWNLOAD_DELAY': 7,
            'CONCURRENT_REQUESTS': 7,
            'RETRY_TIMES': 35,
            'RETRY_HTTP_CODES': [500, 502, 503, 504, 400, 403, 404, 408],
    }
    allowed_domains = ["erasmus-plus.ec.europa.eu"]

    api_url = "https://erasmus-plus.ec.europa.eu/eac-api/content?language=en&page%5Boffset%5D={offset}&page%5Blimit%5D=10&sortonly=false&type=calls"

    def start_requests(self):
        # Start from first page (offset 0)
        yield scrapy.Request(url=self.api_url.format(offset=0), callback=self.parse_api, meta={'offset': 0})

    def parse_api(self, response):
        data = json.loads(response.text)
        fundings = data.get('data', [])

        # Yield items
        for funding in fundings:
            item = EacItem()
            item['title'] = funding.get('title', 'No title')
            item['closing_date'] = funding.get('deadlineDate', 'No deadline day')
            item['closing_time'] = funding.get('deadlineTime', 'No deadline time')
            item['link'] = response.urljoin(funding.get('url', 'No link'))
            yield item

        # Pagination handling
        if len(fundings) > 0:
            current_offset = response.meta['offset']
            next_offset = current_offset + 1
            next_page_url = self.api_url.format(offset=next_offset)
            yield scrapy.Request(url=next_page_url, callback=self.parse_api, meta={'offset': next_offset})
