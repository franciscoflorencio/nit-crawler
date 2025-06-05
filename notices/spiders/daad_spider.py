import scrapy
from notices.items import DaadItem  # Ensure DaadItem is defined in notices.items


class DaadSpider(scrapy.Spider):
    name = "daad"
    allowed_domains = ["www.daad.org.br"]

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }

    def start_requests(self):
        url = "https://www.daad.org.br/pt/category/bolsas-de-estudos/"
        yield scrapy.Request(url, meta={"playwright": True}, callback=self.parse)

    def parse(self, response):
        self.logger.info(f"Parsing page: {response.url}")

        # This XPath was confirmed to find 10 opportunities in your logs
        opportunities_xpath_original = (
            "/html/body/div[2]/div[1]/div/main/section[1]/ul/li"
        )

        opportunities_list = response.xpath(opportunities_xpath_original)
        self.logger.info(
            f"Using original XPath ('{opportunities_xpath_original}'): Found {len(opportunities_list)} opportunities."
        )

        if not opportunities_list:
            # Fallback if the original XPath fails in the future
            opportunities_xpath_general = "//main//section//ul/li"
            self.logger.info(
                "Original XPath found 0 opportunities. Trying general XPath."
            )
            opportunities_list = response.xpath(opportunities_xpath_general)
            self.logger.info(
                f"Using general XPath ('{opportunities_xpath_general}'): Found {len(opportunities_list)} opportunities."
            )

        if not opportunities_list:
            self.logger.warning(
                f"No 'li' opportunity elements found on {response.url} with any attempted selector."
            )
            self.logger.warning(
                "Consider inspecting the page structure manually or using 'scrapy shell' with Playwright to test selectors."
            )
            # You can uncomment the following lines to save the page HTML for offline debugging if needed
            # body = response.body.decode(response.encoding)
            # with open(f"debug_page_{response.url.split('/')[-2] or 'index'}.html", "w", encoding=response.encoding) as f:
            #    f.write(body)
            # self.logger.info(f"Saved debug HTML for {response.url}")

        for i, opportunity in enumerate(opportunities_list):
            # Log the HTML of the first item to help debug its internal selectors
            if i == 0:
                self.logger.info(
                    f"Processing first opportunity element. HTML snippet: {opportunity.get()[:500]}"
                )

            # Corrected: Target h2 for title based on your log's HTML snippet
            title_text_h2_a = opportunity.css("h2 a::text").get()
            title_text_h2_direct = opportunity.css("h2::text").get()

            title_text = None
            if title_text_h2_a and title_text_h2_a.strip():
                title_text = title_text_h2_a.strip()
            elif title_text_h2_direct and title_text_h2_direct.strip():
                title_text = title_text_h2_direct.strip()

            if i == 0:  # More logging for the first item's title extraction
                self.logger.info(
                    f"First item - title from 'h2 a::text': '{title_text_h2_a}'"
                )
                self.logger.info(
                    f"First item - title from 'h2::text' (direct): '{title_text_h2_direct}'"
                )
                self.logger.info(f"First item - selected title_text: '{title_text}'")

            if (
                not title_text
            ):  # Check if title_text is None or empty string after stripping
                if i == 0:
                    self.logger.warning(
                        "Skipping first opportunity because no valid title was extracted (using h2 selectors). Check its HTML and title selectors."
                    )
                continue

            daad_item = DaadItem()
            daad_item["title"] = title_text

            # Link extraction:
            # Often, the entire teaser item or its h2 is wrapped in an <a> tag.
            link_url = None
            # Try to get link from an <a> tag that is a direct child of the opportunity <li> itself
            # or from an <a> tag that is a child of the .c-list-teaser div
            # This handles cases where the whole block is clickable.
            possible_wrapper_link = opportunity.css(
                "a::attr(href)"
            ).get()  # Most direct child a
            link_from_teaser_div = opportunity.css(
                ".c-list-teaser > a::attr(href)"
            ).get()

            if (
                possible_wrapper_link
            ):  # Check if the <li> itself might be wrapped or contain a primary link
                # Check if this link is directly associated with the h2 or is a general wrapper
                h2_link_test = opportunity.xpath(
                    "./a[h2]/@href"
                ).get()  # <a> that has an <h2> child
                if h2_link_test:
                    link_url = h2_link_test
                elif opportunity.xpath(
                    "./a[.//h2]/@href"
                ).get():  # <a> that has an <h2> descendant
                    link_url = opportunity.xpath("./a[.//h2]/@href").get()
                else:  # If not specifically for h2, check if it's a simple wrapper
                    link_url = possible_wrapper_link

            if not link_url and link_from_teaser_div:
                link_url = link_from_teaser_div

            if not link_url:  # Fallback to link specifically inside h2
                link_url = opportunity.css("h2 a::attr(href)").get()

            daad_item["link"] = response.urljoin(link_url) if link_url else None

            description_text = opportunity.css("p.u-size-teaser::text").get()
            daad_item["description"] = (
                description_text.strip() if description_text else None
            )

            observation_text = None
            all_paragraphs = opportunity.css("p")
            for p_element in all_paragraphs:
                p_class_attr = p_element.attrib.get("class", "")
                # Ensure it's not 'u-size-teaser' (already captured) and also not 'u-dateline' (usually metadata)
                if (
                    "u-size-teaser" not in p_class_attr.split()
                    and "u-dateline" not in p_class_attr.split()
                ):
                    current_p_text_list = p_element.css("::text").getall()
                    current_p_text = "".join(current_p_text_list).strip()
                    if current_p_text:
                        # Basic check to ensure it's not the same as description if description was found
                        if (
                            daad_item["description"]
                            and current_p_text == daad_item["description"]
                        ):
                            continue
                        observation_text = current_p_text
                        break  # Take the first such paragraph as observation
            daad_item["observation"] = observation_text

            self.logger.info(f"Yielding item: {daad_item}")
            yield daad_item

        # Pagination
        pagination_option_values = response.css(
            "select#pagination option::attr(value)"
        ).getall()
        if pagination_option_values:
            self.logger.info(f"Found pagination options: {pagination_option_values}")
        else:
            self.logger.info(
                "No pagination options found with 'select#pagination option::attr(value)'."
            )

        for next_page_url_value in pagination_option_values:
            if (
                next_page_url_value
                and isinstance(next_page_url_value, str)
                and next_page_url_value != response.url
            ):
                yield response.follow(
                    next_page_url_value, callback=self.parse, meta={"playwright": True}
                )
