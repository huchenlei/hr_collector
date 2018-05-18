import json
import time
import logging
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class url_changed(object):
    """
    An expectation checking that the url of current page has changed
    since the object is created
    """

    def __init__(self, url):
        self.url = url

    def __call__(self, driver, *args, **kwargs):
        return driver.current_url != self.url


class LinkedIn(object):
    url = "https://linkedin.com"

    def __init__(self, headless=True, cache_path='../../cached_cookies', wait=10):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-extensions")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")

        self.driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=options)
        self.driver.implicitly_wait(wait)
        self.default_wait = WebDriverWait(self.driver, wait)
        self.driver.maximize_window()

        self.cache_path = cache_path

        # init logger
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.logger = logging.getLogger("_LinkedIn")
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(ch)

    def _cookie_file(self, username):
        return self.cache_path + '/' + username + ".cookie"

    def new_login(self, username, password, cache_cookie=True):
        """
        First time login with username and password
        :param username: username(email)
        :param password: password
        :param cache_cookie: whether to cache cookie or not
        :return: void
        """
        self.driver.delete_all_cookies()
        self.driver.get(self.url)
        self.driver.find_element_by_id("login-email").send_keys(username)
        self.driver.find_element_by_id("login-password").send_keys(password)
        self.driver.find_element_by_id("login-submit").click()

        if cache_cookie:
            with open(self._cookie_file(username), "w") as f:
                json.dump(self.driver.get_cookies(), f)

    def cookie_login(self, username):
        """
        Try to login with cached cookie
        Will raise exception if the cached cookie file is not found
        :param username: used to identify cached cookie file
        :return: void
        """
        self.driver.get(self.url)
        with open(self._cookie_file(username), "r") as f:
            cookies = json.load(f)
            for cookie in cookies:
                self.driver.add_cookie(cookie)

        self.driver.refresh()

    @staticmethod
    def _extract_search_results(html):
        root = etree.HTML(html)
        return root.xpath("//li[contains(@class, 'search-result')]//a[contains(@href, '/in')]/@href")

    def _get_height(self):
        height = self.driver.execute_script("return document.body.scrollHeight")
        self.logger.debug("current page height {}".format(height))
        return height

    def _scrape_single_page(self, extract_data):
        """
        Scrape a single page(scroll down to bottom) and click the next button
        :param: extract_data function object to process page html
        :return: scraped result, whether the page is the last page
        """
        ret = set()
        last_height = self._get_height()

        while True:
            ret.update(extract_data(self.driver.page_source))
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

            # wait to load page TODO need other indicator other than fixed sleep
            time.sleep(0.5)

            new_height = self._get_height()
            if new_height == last_height:
                break
            last_height = new_height

        has_next = False
        next_xpath = "//button[@class='next']"
        nexts = self.driver.find_elements_by_xpath(next_xpath)
        if nexts:
            self.default_wait.until(EC.element_to_be_clickable((By.XPATH, next_xpath)))
            nexts[0].click()
            self.default_wait.until(url_changed(self.driver.current_url))
            has_next = True

        return ret, has_next

    def search(self, keyword, options=None, max_req=1000):
        """
        perform a search action on linkedin website top search bar and return the result
        links an list

        :param keyword: search keyword entered in search-box
        :param options: dictionary used to specify filter
        :param max_req: max number of request made
        :return: list
        """
        # TODO add filter options
        search_box = self.driver.find_element_by_xpath(
            "//form[@id='extended-nav-search']//input[@placeholder='Search']")
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)
        self.default_wait.until(url_changed(self.driver.current_url))

        self.logger.info("Searching keyword {} \nwith options {}".format(keyword, options))

        req_count = 0
        ret = []
        has_next = True
        while has_next and req_count < max_req:
            req_count += 1
            self.logger.info("Request #{} to url {}".format(req_count, self.driver.current_url))
            page_info, has_next = self._scrape_single_page(self._extract_search_results)
            ret.extend(page_info)

        return ret


if __name__ == '__main__':
    login = json.load(open("../../login_config.json"))
    login_email = login["username"]
    login_pass = login["password"]

    lk = LinkedIn(False)
    # lk.new_login(login_email, login_pass)
    lk.cookie_login(login_email)

    r = lk.search("Google Canada", max_req=3)

    print(r)

    lk.driver.close()
