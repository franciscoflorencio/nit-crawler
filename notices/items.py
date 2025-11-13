# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CnpqItem(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
    opening_date = scrapy.Field()
    closing_date = scrapy.Field()
    link = scrapy.Field()
    country = scrapy.Field()


class EacItem(scrapy.Item):
    title = scrapy.Field()
    closing_date = scrapy.Field()
    closing_time = scrapy.Field()
    link = scrapy.Field()
    country = scrapy.Field()


class FaperjItem(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
    link = scrapy.Field()
    opening_date = scrapy.Field()
    closing_date = scrapy.Field()
    country = scrapy.Field()


class UkriItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    opportunity_status = scrapy.Field()
    funders = scrapy.Field()
    funders_url = scrapy.Field()
    funding_type = scrapy.Field()
    total_fund = scrapy.Field()
    award_range = scrapy.Field()
    publication_date = scrapy.Field()
    opening_date = scrapy.Field()
    closing_date = scrapy.Field()
    country = scrapy.Field()


class DaadItem(scrapy.Item):
    title = scrapy.Field()
    observation = scrapy.Field()
    description = scrapy.Field()
    link = scrapy.Field()
    country = scrapy.Field()


class FinepItem(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
    link = scrapy.Field()
    closing_date = scrapy.Field()
    opening_date = scrapy.Field()
    country = scrapy.Field()


class EuraexxItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    description = scrapy.Field()
    closing_date = scrapy.Field()
    opening_date = scrapy.Field()
    date = scrapy.Field()
    country = scrapy.Field()


class FapespItem(scrapy.Item):
    title = scrapy.Field()
    institution = scrapy.Field()
    city = scrapy.Field()
    closing_date = scrapy.Field()
    description = scrapy.Field()
    link = scrapy.Field()
    country = scrapy.Field()


class AnrItem(scrapy.Item):
    title = scrapy.Field()
    observation = scrapy.Field()
    opening_date = scrapy.Field()
    closing_date = scrapy.Field()
    link = scrapy.Field()
    description = scrapy.Field()
    country = scrapy.Field()


class EurekaItem(scrapy.Item):
    title = scrapy.Field()
    closing_date = scrapy.Field()
    opening_date = scrapy.Field()
    link = scrapy.Field()
    image_url = scrapy.Field()
    countries = scrapy.Field()
    description = scrapy.Field()
    scope = scrapy.Field()
    timeframe = scrapy.Field()
    funding_details = scrapy.Field()
    status = scrapy.Field()
    country = scrapy.Field()
