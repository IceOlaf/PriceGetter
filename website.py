import requests
from bs4 import BeautifulSoup
import proxy
from price_getter import split
import threading

# TODO generilaze this class for to be used with other websites
class Site():
    def __init__(self, url, proxy_enabled=0, thread_no=1):
        self.url = url
        self.categories = []
        self.proxies = {}
        self.thread_no = thread_no # DO NOT set it as 0
        if proxy_enabled:
            self.proxies = proxy.working_proxies(url)

    def fetch_categories(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.text, 'html.parser')
        cats = soup.find_all("div", {"class":"cat-name"})
        for cat in cats:
            cat_name = cat.find("a")["href"]
            category = Category(self.url + cat_name, cat_name, proxies)
            self.categories.append(category)

    def fetch_items_in_category(self, category):
        print("Fetching Category: {}".format(category.category))
        category.create_pages()
        category.parse_pages()

    def _fetch_all_helper(self, categories):
        for category in categories:
            self.fetch_items_in_category(category)

    def fetch_all(self):
        threads = []
        list_of_categories = split(self.categories, self.thread_no)
        for category_list in list_of_categories:
            print(len(category_list))
            if len(category_list) > 0:
                thread = threading.Thread(target=self._fetch_all_helper,
                                          args=(category_list,))
                threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()


