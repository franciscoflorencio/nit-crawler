import scrapy
import re
from datetime import datetime
from notices.items import UkriItem


class UkriSpider(scrapy.Spider):
    name = "ukri"
    custom_settings = {
        "ITEM_PIPELINES": {
            "notices.pipelines.UkriPipeline": 300,
        },
    }
    allowed_domains = ["www.ukri.org"]
    start_urls = ["https://www.ukri.org/opportunity/"]

    def start_requests(self):
        url = "https://www.ukri.org/opportunity/"
        yield scrapy.Request(url, meta={"playwright": True})

    def parse(self, response):
        # lida com paginacao
        for page in response.css("a.page-numbers").get():
            yield response.follow(page, self.parse)

        # pega as oportunidades
        for opportunity in response.css('div[id^="post-"]'):
            ukri_item = UkriItem()

            ukri_item["opportunity_status"] = opportunity.css(
                "span.opportunity-status__flag::text"
            ).get()

            funders = []
            funders_urls = []
            for funder in opportunity.css(
                'div.govuk-table__row:contains("Funders:") a'
            ):
                funders.append(funder.css("::text").get())
                funders_urls.append(funder.css("::attr(href)").get())
            ukri_item["title"] = opportunity.css("h3.entry-title a::text").get().strip()
            ukri_item["link"] = opportunity.css("h3.entry-title a::attr(href)").get()
            ukri_item["funders"] = (
                ", ".join(funders)
                if funders
                else opportunity.css(
                    'div.govuk-table__row:contains("Funders:") dd.govuk-table__cell::text'
                )
                .get("")
                .strip()
            )
            ukri_item["funders_url"] = ", ".join(funders_urls) if funders_urls else None

            ukri_item["funding_type"] = (
                opportunity.css(
                    'div.govuk-table__row:contains("Funding type:") dd.govuk-table__cell::text'
                )
                .get("")
                .strip()
            )

            ukri_item["total_fund"] = (
                opportunity.css(
                    'div.govuk-table__row:contains("Total fund:") dd.govuk-table__cell::text'
                )
                .get("")
                .strip()
            )

            ukri_item["award_range"] = (
                opportunity.css(
                    'div.govuk-table__row:contains("Award range:") dd.govuk-table__cell::text'
                )
                .get("")
                .strip()
            )

            if not ukri_item["award_range"]:
                min_award = (
                    opportunity.css(
                        'div.govuk-table__row:contains("Minimum award:") dd.govuk-table__cell::text'
                    )
                    .get("")
                    .strip()
                )
                max_award = (
                    opportunity.css(
                        'div.govuk-table__row:contains("Maximum award:") dd.govuk-table__cell::text'
                    )
                    .get("")
                    .strip()
                )
                if min_award and max_award:
                    ukri_item["award_range"] = f"{min_award} - {max_award}"
                elif min_award:
                    ukri_item["award_range"] = f"Min: {min_award}"
                elif max_award:
                    ukri_item["award_range"] = f"Max: {max_award}"

            # Extrair datas
            ukri_item["publication_date"] = (
                opportunity.css(
                    'div.govuk-table__row:contains("Publication date:") dd.govuk-table__cell::text'
                )
                .get("")
                .strip()
            )

            # Helper to normalize English date strings to dd/mm/YYYY
            def normalize_date(date_str):
                if not date_str:
                    return None
                s = re.sub(r"<[^>]+>", "", date_str).strip()
                # Try 'MonthName D, YYYY' e.g. 'October 7, 2025' (optionally followed by time)
                m = re.search(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", s)
                if m:
                    month_name, day, year = m.group(1), m.group(2), m.group(3)
                else:
                    # Try 'D MonthName YYYY' e.g. '12 June 2025'
                    m = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", s)
                    if m:
                        day, month_name, year = m.group(1), m.group(2), m.group(3)
                    else:
                        return None
                # Map month name to number
                try:
                    try:
                        month = datetime.strptime(month_name, "%B").month
                    except ValueError:
                        month = datetime.strptime(month_name, "%b").month
                except Exception:
                    months = {
                        'january':1,'jan':1,'february':2,'feb':2,'march':3,'mar':3,'april':4,'apr':4,
                        'may':5,'june':6,'jun':6,'july':7,'jul':7,'august':8,'aug':8,'september':9,'sep':9,
                        'october':10,'oct':10,'november':11,'nov':11,'december':12,'dec':12
                    }
                    month = months.get(month_name.lower())
                    if not month:
                        return None
                try:
                    d = int(day)
                    y = int(year)
                    return f"{d:02d}/{month:02d}/{y}"
                except Exception:
                    return None

            opening_raw = (
                opportunity.css('div.govuk-table__row:contains("Opening date:") time::text').get("")
                or opportunity.css('div.govuk-table__row:contains("Opening date:") dd.govuk-table__cell::text').get("")
            )
            closing_raw = (
                opportunity.css('div.govuk-table__row:contains("Closing date:") time::text').get("")
                or opportunity.css('div.govuk-table__row:contains("Closing date:") dd.govuk-table__cell::text').get("")
            )

            opening_raw = opening_raw.strip() if opening_raw else ""
            closing_raw = closing_raw.strip() if closing_raw else ""

            opening_norm = normalize_date(opening_raw)
            closing_norm = normalize_date(closing_raw)

            ukri_item["opening_date"] = opening_norm if opening_norm else (opening_raw or None)
            ukri_item["closing_date"] = closing_norm if closing_norm else (closing_raw or None)

            yield ukri_item

        current_page = response.css("span.page-numbers.current::text").get()
        if current_page:
            current_page_num = int(current_page)
            next_page_num = current_page_num + 1

            # Find the link that has this next page number
            next_page = response.css(
                f'a.page-numbers:contains("{next_page_num}")::attr(href)'
            ).get()

            if next_page:
                yield scrapy.Request(
                    next_page, callback=self.parse, meta={"playwright": True}
                )
