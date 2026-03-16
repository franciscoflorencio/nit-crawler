import scrapy
from notices.items import DaadItem


class DaadSpider(scrapy.Spider):
    name = "daad"
    allowed_domains = ["www.daad-brasil.org"]

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }

    def start(self):
        url = "https://www.daad-brasil.org/pt/category/bolsas-de-estudos/"
        yield scrapy.Request(url, meta={"playwright": True}, callback=self.parse)

    async def parse(self, response):
        self.logger.info(f"Parsing page: {response.url}")

        # Seletor CSS mais robusto para encontrar a lista de oportunidades
        opportunities_list = response.css("li.c-list-teaser")

        if not opportunities_list:
            self.logger.warning(
                f"No opportunity elements found on {response.url} with selector 'li.c-list-teaser'."
            )

        for opportunity in opportunities_list:
            daad_item = DaadItem()

            # O card inteiro é um link, então pegamos o href do 'a' principal
            link_url = opportunity.css("a::attr(href)").get()
            daad_item["link"] = response.urljoin(link_url) if link_url else None

            title = opportunity.css("h2.c-list-teaser__title::text").get()
            daad_item["title"] = title.strip() if title else None

            description = opportunity.css("p.u-size-teaser::text").get()
            daad_item["description"] = description.strip() if description else None

            # Simplificando a extração da observação
            all_p_texts = opportunity.css("p:not(.u-size-teaser):not(.u-dateline) ::text").getall()
            observation = " ".join(text.strip() for text in all_p_texts if text.strip())
            daad_item["observation"] = observation if observation else None
            daad_item['country'] = 'Alemanha'

            if daad_item.get("title"):
                yield daad_item

        # Lógica de paginação
        pagination_option_values = response.css(
            "select#pagination option::attr(value)"
        ).getall()

        for next_page_url_value in pagination_option_values:
            if (
                next_page_url_value
                and isinstance(next_page_url_value, str)
                and next_page_url_value != response.url
            ):
                yield response.follow(
                    next_page_url_value, callback=self.parse, meta={"playwright": True}
                )
