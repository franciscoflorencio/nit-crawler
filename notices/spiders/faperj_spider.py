import scrapy
from notices.items import FaperjItem

class FaperjSpider(scrapy.Spider):
    name = "faperj"
    custom_settings = {
        'ITEM_PIPELINES': {
            'notices.pipelines.FaperjPipeline': 301,
        },
    }
    allowed_domains = ["faperj.br"]
    start_urls = ["https://www.faperj.br/?id=28.5.7"]

    def parse(self, response):
        # Select the section containing the editais
        section = response.css('div.tamanho-fonte')
        if not section:
            self.logger.warning("No section with class 'tamanho-fonte' found.")
            return

        # Select all <p> tags within the section
        notices = section.css('p')
        self.logger.info(f"Found {len(notices)} notices")

        for notice in notices:
            # Extract the first link (title)
            title = notice.css('a::text').get()

            # Skip if no title is found
            if not title:
                continue

            # Populate the item with only the title
            item = FaperjItem()
            item['title'] = title.strip()
            yield item