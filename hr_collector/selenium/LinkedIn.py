import json
from selenium import webdriver


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


if __name__ == '__main__':
    login = json.load(open("../../login_config.json"))
    login_email = login["username"]
    login_pass = login["password"]

    lk = LinkedIn(False)
    # lk.new_login(login_email, login_pass)
    lk.cookie_login(login_email)

    lk.driver.close()
