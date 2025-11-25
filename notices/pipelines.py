from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from datetime import datetime


class EacPipeline:
    def process_item(self, item, spider):
        if isinstance(item, str):
            spider.logger.warning(f"Unexpected string item: {item}")
            return item

        adapter = ItemAdapter(item)

        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name == "closing_date":
                day_deadline = adapter["closing_date"]
                if not day_deadline:
                    adapter["closing_date"] = "No deadline day"
                else:
                    try:
                        date_obj = datetime.strptime(day_deadline, "%d %B %Y")
                        adapter["closing_date"] = date_obj.strftime("%d/%m/%Y")
                    except ValueError as e:
                        spider.logger.error(f"Error converting date: {e}")
                        adapter["closing_date"] = "No deadline day"
        return item


class CnpqPipeline:
    def process_item(self, item, spider):
        if isinstance(item, str):
            spider.logger.warning(f"Unexpected string item: {item}")
            return item

        adapter = ItemAdapter(item)

        if "description" in adapter.field_names():
            description = adapter["description"]
            if isinstance(description, list):
                adapter["description"] = " ".join(
                    desc.strip() for desc in description if desc.strip()
                )  # Merge list into a single string

        return item


class FaperjPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Parse the current date
        current_date = datetime.now().date()

        # Ensure the title field exists
        if "title" not in adapter.field_names():
            spider.logger.warning(f"Item dropped due to missing title: {item}")
            raise DropItem(f"Item dropped because it does not contain a title: {item}")

        # Validate the title starts with "Edital"
        title = adapter["title"]
        if not title.startswith("Edital"):
            spider.logger.info(f"Item dropped due to title: {title}")
            raise DropItem(
                f"Item dropped because title does not start with 'Edital': {title}"
            )

        # Validate the link is a valid URL
        link = adapter["link"]
        if not link.startswith("http"):
            spider.logger.info(f"Item dropped due to invalid link: {link}")
            raise DropItem(f"Item dropped because link is not a valid URL: {link}")

        # Check if the 'deadline' field exists and is still valid
        if "closing_date" in item and item["closing_date"]:
            closing_date = datetime.strptime(item["closing_date"], "%d/%m/%Y")
            if closing_date < current_date:  # Deadline has passed
                print("pipeline error!!")

        # Return the item if it passes validation
        return item


class FinepPipeline:
    def process_item(self, item, spider):
        # Parse the current date
        current_year = datetime.now().year
        current_date = datetime.now().date()

        # Check if the 'date' field is more than 2 years old
        if "date" in item and item["date"]:
            item_year = int(
                item["date"].split("/")[-1]
            )  # Extract the year from the date
            if item_year < current_year - 2:
                # Stop the spider if the date is more than 2 years old
                spider.crawler.engine.close_spider(
                    spider,
                    f"Stopping spider: Item date is more than 2 years old ({item['date']})",
                )

        # Check if the 'deadline' field exists and is still valid
        if "closing_date" in item and item["closing_date"]:
            closing_date = datetime.strptime(item["closing_date"], "%d/%m/%Y")
            if closing_date < current_date:  # Deadline has passed
                print("pipeline error!!")

        # If the item passes the check, return it for saving
        return item


class EuraexxPipeline:
    def process_item(self, item, spider):
        if item.get("link") and not item["link"].startswith("http"):
            item["link"] = "https://euraxess.ec.europa.eu" + item["link"]
        return item


class UkriPipeline:
    def process_item(self, item, spider):
        if isinstance(item, str):
            spider.logger.warning(f"Unexpected string item: {item}")
            return item

        adapter = ItemAdapter(item)

        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name == "publication_date":
                day_deadline = adapter["publication_date"]
                if not day_deadline:
                    adapter["publication_date"] = "No deadline day"
                else:
                    try:
                        date_obj = datetime.strptime(day_deadline, "%d %B %Y")
                        adapter["publication_date"] = date_obj.strftime("%d/%m/%Y")
                    except ValueError as e:
                        spider.logger.error(f"Error converting date: {e}")
                        adapter["publication_date"] = "No publication date"
        return item


class FapespPipeline:
    def process_item(self, item, spider):
        if item.get("link") and not item["link"].startswith("http"):
            item["link"] = "https://fapesp.br" + item["link"]
        return item


class EurekaPipeline:
    def process_item(self, item, spider):
        if isinstance(item, str):
            spider.logger.warning(f"Unexpected string item: {item}")
            return item

        adapter = ItemAdapter(item)

        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name == "closing_date":
                day_deadline = adapter["closing_date"]
                if not day_deadline:
                    pass
                else:
                    try:
                        date_obj = datetime.strptime(day_deadline, "%d %B %Y")
                        adapter["closing_date"] = date_obj.strftime("%d/%m/%Y")
                    except ValueError as e:
                        spider.logger.error(f"Error converting date: {e}")

            elif field_name == "opening_date":
                day_deadline = adapter["opening_date"]
                if not day_deadline:
                    pass
                else:
                    try:
                        date_obj = datetime.strptime(day_deadline, "%d %B %Y")
                        adapter["opening_date"] = date_obj.strftime("%d/%m/%Y")
                    except ValueError as e:
                        spider.logger.error(f"Error converting date: {e}")
        return item
