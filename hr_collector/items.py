# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class LinkedInItem(Item):
    # data items
    name = Field()
    short_description = Field()
    long_description = Field()
    location = Field()

    contact_info = Field()
    experience = Field()

    education = Field()
    skills = Field()
    recommendations = Field()
    accomplishments = Field()
    interests = Field()

    following = Field()

    # house keeping fields
    url = Field()
