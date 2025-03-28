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

        # Select all <p> tags within the section
        notices = section.css('p')
        self.logger.info(f"Found {len(notices)} notices")

        for notice in notices:
            # Extract the first link (title and URL)
            title = notice.css('a::text').get()
            link = notice.css('a::attr(href)').get()

            # Extract the description (all text after the title within the <p> tag)
            description_parts = notice.css('::text').getall()
            description = ' '.join([part.strip() for part in description_parts if part.strip() and part != title])

            # Skip if no title or link is found
            if not title or not link:
                continue

            # Populate the item with title, description, and link
            item = FaperjItem()
            item['title'] = title.strip()
            item['description'] = description.strip()
            item['link'] = response.urljoin(link)  # Convert relative URLs to absolute
            yield item