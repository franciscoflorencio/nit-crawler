import scrapy
from scrapy.http import Response
from typing import Any, Iterable, AsyncIterable
from notices.items import FinepItem


class FinepSpider(scrapy.Spider):
    name = "finep"
    custom_settings = {
        'ITEM_PIPELINES': {
            'notices.pipelines.FinepPipeline': 303,
        },
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",  # noqa: E501
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",  # noqa: E501
        },
    }
    allowed_domains = ["finep.gov.br"]
    start_urls = [
        "https://www.finep.gov.br/oportunidades"
    ]

    def start_requests(self) -> Iterable[scrapy.Request]:
        for url in self.start_urls:
            # Ativa o Playwright para interagir com o portal da Finep
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True
                }
            )

    async def parse(
        self, response: Response, **kwargs: Any
    ) -> AsyncIterable[Any]:
        page = response.meta["playwright_page"]

        try:
            # 1. Clicar nos filtros
            try:
                # Clica no filtro "ICT" (Público Alvo) através da label
                await page.locator('label[for="publico-ict"]').click()
                await page.wait_for_timeout(2000)  # Espera o site processar
                # Clica no filtro "Aberta" (Inscrição) através da label
                await page.locator('label[for="situacao-aberta"]').click()
                await page.wait_for_timeout(3000)  # Espera carregar a lista
            except Exception as e:
                self.logger.warning(f"Aviso ao clicar nos filtros: {e}")

            # 2. Loop de paginação do Playwright
            while True:
                content = await page.content()
                sel = scrapy.Selector(text=content)

                # Busca a tag <a> que contém o título
                opportunity_links = sel.xpath(
                    '//a[h2[contains(@class, "card-title-chamadas")]]'
                )

                for opp in opportunity_links:
                    link = opp.xpath('./@href').get()
                    title = opp.xpath('.//h2/text()').get()

                    # Seleciona o elemento pai (container) do link
                    container = opp.xpath('..')

                    # Busca o prazo e trata possíveis espaços e tags aninhadas
                    closing_date_parts = container.xpath(
                        './/div[contains(@class, "bloco-data")]'
                        '[.//strong[contains(text(), "Prazo:")]]'
                        '//span//text()'
                    ).getall()
                    closing_date = (
                        "".join(closing_date_parts).strip()
                        if closing_date_parts
                        else None
                    )

                    # Busca a descrição na própria lista de resultados
                    desc_parts = container.xpath(
                        './/p[contains(@class, "card-text")]//text()'
                    ).getall()
                    description = " ".join(
                        d.strip() for d in desc_parts if d.strip()
                    )

                    if link:
                        full_url = response.urljoin(link)
                        yield FinepItem(
                            title=title.strip() if title else "",
                            description=description,
                            opening_date=None,
                            closing_date=closing_date,
                            link=full_url,
                            country="Brasil"
                        )

                # Verifica o botão de próxima página
                next_btn_li = sel.xpath(
                    '//li[contains(@class, "page-item")]'
                    '[button[svg[contains(@class,'
                    '"lexicon-icon-angle-right")]]]'
                )

                if not next_btn_li or "disabled" in next_btn_li.xpath(
                    './@class'
                ).get(default=""):
                    self.logger.info("Fim da paginação alcançado.")
                    break

                # Clica na setinha para ir à próxima página
                await page.locator(
                    'button.page-link:has(svg.lexicon-icon-angle-right)'
                ).first.click()
                await page.wait_for_timeout(3000)

        finally:
            await page.close()
