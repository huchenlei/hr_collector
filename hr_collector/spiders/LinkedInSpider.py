# -*- coding: utf-8 -*-
import logging

from lxml import etree
from scrapy import Spider

from ..common.xpath import attr_contains
from ..items import LinkedInItem
from ..selenium.LinkedIn import LinkedIn
from ..pipelines import MongoPipeline
from ..settings import MONGO_URI, MONGO_DATABASE


class LinkedInSpider(Spider):
    name = 'LinkedInSpider'
    allowed_domains = ['linkedin.com']

    def __init__(self, keyword, **kwargs):
        # basic configs
        super().__init__(**kwargs)
        max_req = int(kwargs["max_req"]) if "max_req" in kwargs else 1000
        if "log_level" in kwargs:
            self.logger.setLevel(kwargs["log_level"])
        else:
            self.logger.setLevel(logging.INFO)

        # get urls and cookie through selenium session
        self.lk = LinkedIn(headless=True, **kwargs)  # keep other settings default if not provided by kwargs
        self.lk.login()
        self.start_urls = self.lk.search(keyword, options=kwargs, max_req=max_req)
        self.cookies = {c["name"]: c["value"] for c in self.lk.driver.get_cookies()}

        self.logger.info("{} results found".format(len(self.start_urls)))

        # create pipeline instance
        self.mongo = MongoPipeline(
            MONGO_URI,
            MONGO_DATABASE
        )
        self.mongo.open_spider(self)

    def start_requests(self):
        """
        Dumb placeholder function
        :return: empty list
        """
        for url in self.start_urls:
            lki = self.parse_html(self.lk.request_page(url))
            lki["url"] = url
            self.mongo.process_item(lki, self)

        return []  # return nothing for build-in parsing

    def parse(self, response):
        pass

    @staticmethod
    def parse_html(html):
        document = etree.HTML(html)
        lki = LinkedInItem()

        info_box = document.xpath("//section[{classes}]".format(
            classes=attr_contains("class", *["pv-profile-section", "pv-top-card-section", "ember-view"])))
        assert len(info_box) == 1
        info_box = info_box[0]

        field_table = {
            "name": ".//h1/text()",
            "short_description": ".//h2/text()",
            # TODO need to deal with contents dynamically loaded
            # "long_description": ".//p[{classes}]".format(classes=attr_contains("class", "summary-text", "ember-view")),
            "location": ".//h3/text()",
        }

        for field, xpath in field_table.items():
            data = info_box.xpath(xpath)
            assert len(data) == 1
            lki[field] = data[0].strip()

        return lki

    # called on close
    def closed(self, reason):
        self.mongo.close_spider(self)
