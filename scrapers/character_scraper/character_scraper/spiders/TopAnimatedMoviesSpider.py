from pathlib import Path

import scrapy
from html import unescape
import pandas as pd
from os import path, remove 

page_file_name = "page.txt"

class TopAnimatedMoviesSpider(scrapy.Spider):
    name = "movies"
    movie_dict = {}

    def start_requests(self):
        self.start = 0
        if path.exists(page_file_name):
            with open(page_file_name, 'r') as f:
                self.start = int(f.read())
        print("current start is : " , self.start)
        urls = [
            f"https://www.imdb.com/search/title/?genres=animation&start={self.start}&explore=title_type,genres&ref_=adv_nxt"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.get_movies_links(response)

        df = pd.Series(self.movie_dict).to_frame('data')
        df.to_csv('output.csv', mode='a')
        if path.exists(page_file_name):
            remove(page_file_name)
        with open(page_file_name, 'w') as f:
            f.write(str(len(self.movie_dict) + self.start))

    def get_movies_links(self, response):
        list_items = response.xpath("//div[@class='lister-list']")[0].xpath("//div[@class='lister-item mode-advanced']")
        print("movies:::")
        for li in list_items:
            html : str = li.xpath("div[@class='lister-item-content']//h3").css("a")[0].get()
            innerHTML = html[html.find('>')+1:html.rfind('<')]
            print(innerHTML)
            link_str = html[html.find('"/')+1:html.rfind('/"')]
            print(link_str)
            if (link_str != '' or innerHTML != ''):
                self.movie_dict[unescape(innerHTML).lower()] = link_str

