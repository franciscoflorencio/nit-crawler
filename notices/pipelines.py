# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
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
            if field_name == 'day_deadline':
                day_deadline = adapter['day_deadline']
                if not day_deadline:
                    adapter['day_deadline'] = 'No deadline day'
                else:
                    try:
                        date_obj = datetime.strptime(day_deadline, '%d %B %Y')
                        adapter['day_deadline'] = date_obj.strftime('%d/%m/%Y')
                    except ValueError as e:
                        spider.logger.error(f"Error converting date: {e}")
                        adapter['day_deadline'] = 'No deadline day'
        return item


class CnpqPipeline:
    def process_item(self, item, spider):
        
        if isinstance(item, str):
            spider.logger.warning(f"Unexpected string item: {item}")
            return item

        adapter = ItemAdapter(item)
        
        if 'description' in adapter.field_names():
            description = adapter['description']
            if isinstance(description, list):  
                adapter['description'] = " ".join(desc.strip() for desc in description if desc.strip())  # Merge list into a single string
        
        return item    

class FaperjPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Ensure the title field exists
        if 'title' not in adapter.field_names():
            spider.logger.warning(f"Item dropped due to missing title: {item}")
            raise DropItem(f"Item dropped because it does not contain a title: {item}")

        # Validate the title starts with "Edital"
        title = adapter['title']
        if not title.startswith('Edital'):
            spider.logger.info(f"Item dropped due to title: {title}")
            raise DropItem(f"Item dropped because title does not start with 'Edital': {title}")

        # Validate the link is a valid URL
        link = adapter['link']
        if not link.startswith('http'):
            spider.logger.info(f"Item dropped due to invalid link: {link}")
            raise DropItem(f"Item dropped because link is not a valid URL: {link}")

        # Return the item if it passes validation
        return item

class FinepPipeline:
    def process_item(self, item, spider):
        return item