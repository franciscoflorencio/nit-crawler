import scrapy
from notices.items import DaadItem


class DaadSpider(scrapy.Spider):
    name = "daad"
    allowed_domains = ["www.daad-brasil.org"]

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "DEFAULT_REQUEST_HEADERS": {
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        },
        "PLAYWRIGHT_CONTEXTS": {
            "default": {
                "locale": "pt-BR",
                "timezone_id": "America/Sao_Paulo",
            }
        },
    }

    async def start(self):
        url = "https://www.daad-brasil.org/pt/bolsas/busca/?language=pt"
        yield scrapy.Request(url, meta={"playwright": True}, callback=self.parse)

    async def parse(self, response):
        self.logger.info(f"Parsing page: {response.url}")

        # Select all items from the scholarship list
        opportunities_list = response.css("li.c-scholarship-list__item")

        if not opportunities_list:
            self.logger.warning(
                f"No opportunity elements found on {response.url}."
            )

        for opportunity in opportunities_list:
            daad_item = DaadItem()

            # Extract title and link
            title = opportunity.css("h3 a::text").get()
            link_url = opportunity.css("h3 a::attr(href)").get()

            daad_item["title"] = title.strip() if title else None
            daad_item["link"] = response.urljoin(link_url) if link_url else None

            # Extract description
            description = opportunity.css("p.u-size-teaser::text").get()
            daad_item["description"] = description.strip() if description else None

            # Extract deadline and status to compose observation
            deadline_texts = opportunity.xpath('.//dt[contains(., "Prazo de inscrição:")]/following-sibling::dd[1]//text()').getall()
            deadline = " ".join([t.strip() for t in deadline_texts if t.strip()])

            status_texts = opportunity.xpath('.//dt[contains(., "Status:")]/following-sibling::dd[1]//text()').getall()
            status = ", ".join([t.strip() for t in status_texts if t.strip()])

            observations = []
            if deadline: observations.append(f"Prazo: {deadline}")
            if status: observations.append(f"Status alvo: {status}")

            daad_item["observation"] = " | ".join(observations) if observations else None
            daad_item["country"] = "Alemanha"

            if daad_item.get("title"):
                yield daad_item

        # Handle pagination (Next page arrow)
        next_page = response.css('a[aria-label="Próxima página"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse, meta={"playwright": True})
