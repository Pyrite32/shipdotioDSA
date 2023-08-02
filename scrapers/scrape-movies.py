import pandas as pd
import selenium.webdriver as wd
from selenium.webdriver.common.by import By
import base64
from os import path, remove
from csv import reader

CHAR_START = "char_start.txt"

def start_dominic():
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    c_options = wd.ChromeOptions();
    c_options.add_argument('--ignore-certificate-errors')
    c_options.add_argument('--ignore-ssl-errors')
    #c_options.add_argument('-headless')
    c_options.add_argument(f'user_agent={user_agent}')
    driver = wd.Chrome(options=c_options)
    return driver

def run_through_pages(dominic:wd.Chrome):
    char_dict = {}
    checkpoint = load_checkpoint()
    with open("movies.csv", 'r', encoding="utf8") as f:
        csv_reader = reader(f, delimiter=',')
        i = 0 
        for row in csv_reader:
            if row[0] == '' or i < checkpoint : continue
            print(row[0])
            current_movie_name = row[0]
            current_movie_url = row[1]
            characters = []
            url = f'https://www.imdb.com/{current_movie_url}'
            try:
                characters = get_characters_from_link(dominic, url)
            except Exception:
                save_checkpoint(i)
            char_dict[current_movie_name] = characters
            df = pd.Series(char_dict).to_frame()
            df.to_csv('characters.csv', mode='a')
            char_dict = {}
            i += 1
        save_checkpoint(i)

def save_checkpoint(i : int):
    with open(CHAR_START, 'w') as f:
        f.write(str(i))

def load_checkpoint():
    index_start : int = 0
    if path.exists(CHAR_START):
        with open(CHAR_START, 'r') as f:
            index_start = int(f.read())
        remove(CHAR_START)
    return index_start

def get_characters_from_link(dominic:wd.Chrome, movie_link: str):
    dominic.get(movie_link)
    cast_list2 = dominic.find_element(By.CLASS_NAME, 'title-cast__grid')
    if cast_list2 is None: return
    cast_list1 = cast_list2.find_element(By.CLASS_NAME, 'ipc-sub-grid')
    if cast_list1 is None: return
    cast_list = cast_list1.find_elements(By.TAG_NAME, 'div')
    if cast_list is None: return
    result = []
    print("found actors list")
    index = 0
    for actor in cast_list:
        actor_names = actor.find_elements(By.CLASS_NAME, 'title-cast-item__characters-list')
        for _ in actor_names:
            try:
                char_name_txt1 = actor.find_element(By.TAG_NAME, 'ul').find_element(By.TAG_NAME, 'a')
                char_name_txt = char_name_txt1.find_element(By.CSS_SELECTOR, '*').get_attribute('innerHTML')
            except Exception:
                pass
            else:
                if index % 2 == 0:
                    result.append(char_name_txt)
                index += 1
    return result


if __name__ == '__main__':
    dominic = start_dominic()
    run_through_pages(dominic)
