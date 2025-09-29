import scrapy
from notices.items import FaperjItem
import re


class FaperjSpider(scrapy.Spider):
    name = "faperj"
    custom_settings = {
        "ITEM_PIPELINES": {
            "notices.pipelines.FaperjPipeline": 301,
        },
    }
    allowed_domains = ["faperj.br"]
    start_urls = ["https://www.faperj.br/?id=28.5.7"]

    def parse(self, response):
        # Seleciona todos os <p> que estão antes do <h2> com o texto "OUTROS PROGRAMAS E CHAMADAS"
        notices = response.xpath(
            '//h2[strong[contains(text(), "OUTROS PROGRAMAS E CHAMADAS")]]/preceding-sibling::p'
        )
        self.logger.info(f"Found {len(notices)} notices before 'OUTROS PROGRAMAS'")

        # Regex para encontrar datas no formato dd/mm/yyyy
        date_pattern = re.compile(r"\d{2}/\d{2}/\d{4}")

        for notice in notices:
            # Extract the first link (title and URL)
            title = notice.css("strong a::text").get()
            link = notice.css("strong a::attr(href)").get()

            # Pula parágrafos que não contêm um link de edital no início
            if not title or not link:
                continue

            # Extrai o HTML interno do parágrafo para limpar os textos riscados
            notice_html = notice.get()
            # Remove tags de texto riscado para não capturar datas antigas
            cleaned_html = re.sub(r'<span style="text-decoration: line-through;">.*?</span>', '', notice_html, flags=re.DOTALL)
            temp_selector = scrapy.Selector(text=cleaned_html)
            
            # Extrai todo o texto do parágrafo (já limpo)
            all_text = " ".join(temp_selector.css("::text").getall())

            # Procura pela linha de submissão
            submission_match = re.search(r"Submissão de propostas on-line:? de (.*?)(?=<br>|Lançamento|$)", all_text, re.IGNORECASE)
            
            opening_date = None
            closing_date = None

            if submission_match:
                # Pega todas as datas encontradas na linha de submissão
                dates = date_pattern.findall(submission_match.group(1))
                if len(dates) >= 2:
                    opening_date = dates[0]
                    closing_date = dates[-1] # Pega a última data como data de fechamento
                elif len(dates) == 1:
                    opening_date = dates[0]

            # Populate the item with title, description, and link
            item = FaperjItem()
            item["title"] = title.strip()
            # A descrição pode ser o texto completo ou uma versão resumida
            item["description"] = " ".join(all_text.split())
            item["link"] = response.urljoin(link)  # Convert relative URLs to absolute
            item["opening_date"] = opening_date
            item["closing_date"] = closing_date

            yield item
