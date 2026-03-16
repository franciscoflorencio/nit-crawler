import scrapy
from notices.items import FaperjItem
import re


class FaperjSpider(scrapy.Spider):
	name = "faperj"
	custom_settings = {
		"ITEM_PIPELINES": {
			"notices.pipelines.FaperjPipeline": 301,
		},
		"DOWNLOAD_HANDLERS": {
			"http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
			"https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
		},
		"TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
	}
	allowed_domains = ["faperj.br"]
	start_urls = ["https://www.faperj.br/?id=28.5.7"]

	def start_requests(self):
		for url in self.start_urls:
			yield scrapy.Request(url, meta={"playwright": True})

	def parse(self, response):
		# Regex to find dates in dd/mm/yyyy format
		date_pattern = re.compile(r"d{2}/d{2}/d{4}")

		# Select all paragraphs within the main content area
		paragraphs = response.css("section.corpo-interna p")
		self.logger.info(f"Found {len(paragraphs)} paragraphs to process.")

		for p in paragraphs:
			# Remove strikethrough text to avoid capturing old dates
			p_html = p.get()
			cleaned_html = re.sub(
				r'<span style="text-decoration: line-through;">.*?</span>',
				"",
				p_html,
				flags=re.DOTALL,
			)

			# A paragraph may contain multiple notices, so search for all bold links
			notice_links = scrapy.Selector(text=cleaned_html).css(
				'strong > a[href*="downloads/Edital"]'
			)

			if not notice_links:
				continue

			# Full cleaned paragraph text is used to find dates
			all_text = " ".join(
				scrapy.Selector(text=cleaned_html).xpath(".//text()").getall()
			)

			for notice_link in notice_links:
				title = notice_link.css("::text").get()
				link = notice_link.css("::attr(href)").get()

				if not title or not link:
					continue

				# Extract opening date
				opening_match = re.search(
					r"Lan[çc]amento (?:do programa|do edital|da chamada|do Edital)[:]?s*(d{2}/d{2}/d{4})",
					all_text,
					re.IGNORECASE,
				)
				opening_date = opening_match.group(1) if opening_match else None

				# Extract closing date
				submission_regex = (
					r"Submiss[aã]o (?:de|das)? propostas? on-line:?[^d]*(.*)"
				)
				submission_match = re.search(
					submission_regex, all_text, re.IGNORECASE
				)
				closing_date = None
				if submission_match:
					submission_text = submission_match.group(1)
					dates = date_pattern.findall(submission_text)
					if dates:
						closing_date = dates[-1]

				item = FaperjItem()
				item["title"] = title.strip()
				item["description"] = " ".join(all_text.split())
				item["link"] = response.urljoin(link)
				item["opening_date"] = opening_date
				item["closing_date"] = closing_date
				item["country"] = "Brasil"

				yield item
