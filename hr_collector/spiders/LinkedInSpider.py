# -*- coding: utf-8 -*-
import logging

from scrapy import Spider
from ..selenium.LinkedIn import LinkedIn


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

        for url in self.start_urls:
            self.parse(self.lk.request_page(url))

    def start_requests(self):
        """
        Dumb placeholder function
        :return: empty list
        """
        return []  # return nothing for build-in parsing

    def parse(self, response):
        pass

    def parse_html(self, html):
        return None