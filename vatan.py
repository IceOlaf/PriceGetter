#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import argparse
from item import *
import os
from item_db import *
from tqdm import *
import proxy
from random import choice

NAME_LEN = 50

#url = "https://www.vatanbilgisayar.com/ekran-kartlari/"
url = "https://www.vatanbilgisayar.com/"
vatan = "https://www.vatanbilgisayar.com"

categories = []
proxies = proxy.working_proxies()
next_page = "?page="
i = 1

def get_name(item):
    name = item.find("div", {"class":"ems-prd-name"})
    if name == None:
        return None
    return name.text.strip()

def get_url(item):
    url = item.find("div", {"class":"ems-prd-name"})
    if url == None:
        return None
    if url.find("a") == None:
        return None
    return url.find("a")["href"]

def create_item_objects(products, category):
    list_of_items = []

    for soup in products:
        url, name = get_url(soup), get_name(soup)

        if name == None or url == None: # Unnecessary items in page
            continue

        item = Item(vatan + url, name, price=0, soup=soup)
        item.extract_info()
        list_of_items.append(item)
        ItemDb.create(url=item.url, name=item.name, price=item.price, category=category)
    return list_of_items

def prettify_name(name):
    name = name[:NAME_LEN]
    return name + " " * (NAME_LEN - len(name))

def print_items(pages_dict):
    for key, values in pages_dict.items():
        print("Page No: ", key)
        for item in values:
            print("\t", item.name, item.price)

def find_last_page(page):
    soup = BeautifulSoup(page.text, 'html.parser')
    last_page = soup.find("a", {"class": "emos_invisible lastPage"})
    if last_page == None:
        return 2
    return int(last_page["href"].split("page=")[1])

def parse_page(page, category):
    soup = BeautifulSoup(page.text, 'html.parser')
    products = soup.find_all("div", {"class":"ems-prd-inner"})
    return create_item_objects(products, category)

def handle_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--category", help="Fetch the prices from given category")
    args = parser.parse_args()
    return args

def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def save_results(pages_dict, category):
    path = "vatan"
    create_dir(path)
    path = path + "/" + category + "/"
    create_dir(path)

    day = datetime.datetime.now().strftime("%d-%m-%Y")
    price_out = open(path + "/" + day + ".txt", "w+")
    url_out = open(path + "/" + "url_" + day  + ".txt", "w+")
    for key, values in pages_dict.items():
        for item in values:
            price_out.write(item.name + ":" + item.price + "\n")
            url_out.write(vatan + item.url + "\n")
    price_out.close()
    url_out.close()

def get_categories():
    categories = []
    page = requests.get(vatan)
    soup = BeautifulSoup(page.text, 'html.parser')
    cats = soup.find_all("div", {"class":"cat-name"})
    for category in cats:
        categories.append(category.find("a")["href"])
    return categories

def fetch_page(page_url):
    try:
        page = requests.get(page_url)
        return page
    except:
        pass
    for url, val in proxies.items():
        print("Trying with new proxy:", url)
        try:
            page = requests.get(page_url, proxies= {val[0]: url}, timeout=1)
            return page
        except Exception as e:
            print(e)
            continue
        break
    return None

def get_category_page(category, *args):
    category_url = url + category + "/"
    if args:
        category_url = category_url + args[0]
    page = fetch_page(category_url)
    if page == None:
        print("All proxies are dead")
    return page

def fetch_items_in_category(category):
    print("Fetching Category: {}".format(category))
    page = get_category_page(category)
    last_page = find_last_page(page)

    pages[1] = parse_page(page, category)
    for i in range(2, last_page+1):
        try:
            page = get_category_page(category, next_page+str(i))
        except Exception as e:
            print(e)
            break
        pages[i] = parse_page(page, category)

if __name__ == '__main__':
    args = handle_args()
    pages = {}

    if args.category == None:
        print("Provide category")
        exit(0)

    if args.category == "all":
        categories = get_categories()

    else:
        categories.append(args.category)

    for category in tqdm(categories):
        fetch_items_in_category(category)
       #save_results(pages, category)

