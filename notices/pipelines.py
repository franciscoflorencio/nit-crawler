# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

class CnpqPipeline:
    def process_item(self, item, spider):
        if isinstance(item, str):
            # Log or handle the unexpected string item
            spider.logger.warning(f"Unexpected string item: {item}")
            return item

        adapter = ItemAdapter(item)
        
        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name == 'description':
                description = adapter['description']
                transformed_description = []
                for desc_item in description:
                    if desc_item.startswith('\n') and transformed_description:
                        transformed_description[-1] += desc_item.strip()
                    else:
                        transformed_description.append(desc_item)
                adapter['description'] = transformed_description
        return item
    
class FaperjPipeline:
    def process_item(self, item, spider):
        if isinstance(item, str):
            spider.logger.warning(f"Unexpected string item: {item}")
            return item
        
        adapter = ItemAdapter(item)
        
        if 'title' in adapter.field_names():
            title = adapter['title']
            if not title.startswith('Edital'):
                spider.logger.info(f"Item dropped due to title: {title}")
                raise DropItem(f"Item dropped because title does not start with 'Edital': {title}")
        
        if 'description' in adapter.field_names():
            description = adapter['description']
            if not description.startswith('Lançamento') or not description.startswith('Publicado'):
                spider.logger.info(f"Item dropped due to description: {description}")
                raise DropItem(f"Item dropped because description does not start with 'Lançamento' or 'Publicado': {description}")
        
        return item