import json
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class LinkedIn(object):
    url = "https://linkedin.com"

    def __init__(self, headless=True, cache_path='../../cached_cookies'):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-extensions")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")

        self.driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=options)
        self.cache_path = cache_path

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

    def search(self, keyword, options=None, max_req=1000):
        # TODO add filter options
        search_box = self.driver.find_element_by_xpath(
            "//form[@id='extended-nav-search']//input[@placeholder='Search']")
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)

        self.driver.implicitly_wait(3000)

        req_count = 0
        ret = []
        next_xpath = "//button[@class='next']"
        while len(self.driver.find_elements_by_xpath(next_xpath)) > 0 and req_count < max_req:
            ret.extend(self._extract_search_results(self.driver.page_source))
            self.driver.find_element_by_xpath(next_xpath).click()
            req_count += 1

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

    r = ['/in/amanda-hsueh-685a9225/', '/in/amanda-hsueh-685a9225/', '/in/elfreda-l-878796/', '/in/elfreda-l-878796/',
         '/in/nancy-mcconnell-43260116/', '/in/nancy-mcconnell-43260116/', '/in/mladenraickovic/',
         '/in/mladenraickovic/', '/in/riley-nelko-bb2b0846/', '/in/riley-nelko-bb2b0846/', '/in/cuhoward/',
         '/in/cuhoward/', '/in/andrew-rapsey-593b671/', '/in/andrew-rapsey-593b671/', '/in/nathan-stone-a9109a49/',
         '/in/nathan-stone-a9109a49/', '/in/amanda-hsueh-685a9225/', '/in/amanda-hsueh-685a9225/',
         '/in/elfreda-l-878796/', '/in/elfreda-l-878796/', '/in/nancy-mcconnell-43260116/',
         '/in/nancy-mcconnell-43260116/', '/in/mladenraickovic/', '/in/mladenraickovic/', '/in/riley-nelko-bb2b0846/',
         '/in/riley-nelko-bb2b0846/', '/in/cuhoward/', '/in/cuhoward/', '/in/andrew-rapsey-593b671/',
         '/in/andrew-rapsey-593b671/', '/in/nathan-stone-a9109a49/', '/in/nathan-stone-a9109a49/', '/in/rehanqureshi1/',
         '/in/rehanqureshi1/', '/in/artidavdapatel/', '/in/artidavdapatel/', '/in/amanda-hsueh-685a9225/',
         '/in/amanda-hsueh-685a9225/', '/in/elfreda-l-878796/', '/in/elfreda-l-878796/',
         '/in/nancy-mcconnell-43260116/', '/in/nancy-mcconnell-43260116/', '/in/mladenraickovic/',
         '/in/mladenraickovic/', '/in/riley-nelko-bb2b0846/', '/in/riley-nelko-bb2b0846/', '/in/cuhoward/',
         '/in/cuhoward/', '/in/andrew-rapsey-593b671/', '/in/andrew-rapsey-593b671/', '/in/nathan-stone-a9109a49/',
         '/in/nathan-stone-a9109a49/', '/in/rehanqureshi1/', '/in/rehanqureshi1/', '/in/artidavdapatel/',
         '/in/artidavdapatel/']


    lk.driver.close()
