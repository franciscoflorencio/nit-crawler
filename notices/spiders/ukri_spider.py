import scrapy
from notices.items import UkriItem

class UkriSpider(scrapy.Spider):
    name = "ukri"
    allowed_domains = ["www.ukri.org"]
    start_urls = ["https://www.ukri.org/opportunity/"]

    def start_requests(self):
        url = "https://www.ukri.org/opportunity/"
        yield scrapy.Request(url, meta={"playwright": True})

    def parse(self, response):
        #lida com paginacao
        for page in response.css('a.page-numbers').get():
            yield response.follow(page, self.parse)


        for opportunity in response.css('div[id^="post-"]'):
            ukri_item = UkriItem()
            
            ukri_item['opportunity_status'] = opportunity.css('span.opportunity-status__flag::text').get()
            
            funders = []
            funders_urls = []
            for funder in opportunity.css('div.govuk-table__row:contains("Funders:") a'):
                funders.append(funder.css('::text').get())
                funders_urls.append(funder.css('::attr(href)').get())
            ukri_item['title'] = opportunity.css('h3.entry-title a::text').get().strip()
            ukri_item['opportunity_link'] = opportunity.css('h3.entry-title a::attr(href)').get()
            ukri_item['funders'] = ', '.join(funders) if funders else opportunity.css('div.govuk-table__row:contains("Funders:") dd.govuk-table__cell::text').get('').strip()
            ukri_item['funders_url'] = ', '.join(funders_urls) if funders_urls else None
            
            ukri_item['funding_type'] = opportunity.css('div.govuk-table__row:contains("Funding type:") dd.govuk-table__cell::text').get('').strip()
            
            ukri_item['total_fund'] = opportunity.css('div.govuk-table__row:contains("Total fund:") dd.govuk-table__cell::text').get('').strip()
            
            ukri_item['award_range'] = opportunity.css('div.govuk-table__row:contains("Award range:") dd.govuk-table__cell::text').get('').strip()
            
            if not ukri_item['award_range']:
                min_award = opportunity.css('div.govuk-table__row:contains("Minimum award:") dd.govuk-table__cell::text').get('').strip()
                max_award = opportunity.css('div.govuk-table__row:contains("Maximum award:") dd.govuk-table__cell::text').get('').strip()
                if min_award and max_award:
                    ukri_item['award_range'] = f"{min_award} - {max_award}"
                elif min_award:
                    ukri_item['award_range'] = f"Min: {min_award}"
                elif max_award:
                    ukri_item['award_range'] = f"Max: {max_award}"
            
            # Extrair datas
            ukri_item['publication_date'] = opportunity.css('div.govuk-table__row:contains("Publication date:") dd.govuk-table__cell::text').get('').strip()
            ukri_item['opening_date'] = opportunity.css('div.govuk-table__row:contains("Opening date:") time::text').get('').strip() or \
                                        opportunity.css('div.govuk-table__row:contains("Opening date:") dd.govuk-table__cell::text').get('').strip()
            ukri_item['closing_date'] = opportunity.css('div.govuk-table__row:contains("Closing date:") time::text').get('').strip() or \
                                       opportunity.css('div.govuk-table__row:contains("Closing date:") dd.govuk-table__cell::text').get('').strip()
            
            yield ukri_item
        

        current_page = response.css('span.page-numbers.current::text').get()
        if current_page:
            current_page_num = int(current_page)
            next_page_num = current_page_num + 1
            
            # Find the link that has this next page number
            next_page = response.css(f'a.page-numbers:contains("{next_page_num}")::attr(href)').get()
            
            if next_page:
                yield scrapy.Request(
                    next_page,
                    callback=self.parse,
                    meta={"playwright": True}
                )

