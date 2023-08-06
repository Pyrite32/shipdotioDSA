from genericpath import exists
import random
from exceptiongroup import catch
from numpy import char
import pandas as pd
from scipy.__config__ import show
import selenium.webdriver as wd
from selenium.webdriver.common.by import By
import base64
from os import mkdir, path, remove
from csv import reader, writer
import csv
import fandom
from re import sub
import json
from pathlib import Path
import random
import logging
from selenium.webdriver.remote.remote_connection import LOGGER

CHAR_START = "char_start.txt"
CSV_FILE = "characters.csv"
UNIQUE_SET_FILE = "the_words.csv"
POS_SAV = "sav.txt"
google_USER = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
google_USER_OBJ = { "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36' }
CHECKPOINT_SAVE_FREQUENCY = 50
SET_SIZE = 0
PARCEL_INDEX = 0

IGNORE = ['Gallery']
main_map = {}

def start_webscraper():
    
    c_options = wd.ChromeOptions();
    c_options.add_argument('--ignore-certificate-errors')
    c_options.add_argument('--ignore-ssl-errors')
    c_options.add_argument('-headless')
    c_options.add_argument('--log-level=25')
    c_options.add_argument(f'user_agent={google_USER}')
    LOGGER.setLevel(logging.CRITICAL)
    logging.getLogger('lxml').setLevel(logging.CRITICAL)
    driver = wd.Chrome(options=c_options)
    
    return driver

def google_search(webscraper:wd.Chrome, character_names:str, show_name:str):
    global PARCEL_INDEX

    # search for a fandom article to latch onto.
    google_url = f"https://www.google.com/search?q={show_name.replace(' ', '+')}+fandom"
    try:
        webscraper.get(google_url) # access the page
    except Exception:
        PARCEL_INDEX += 1
        print("oopsies! failed to get the website!")
        return
    search_results = webscraper.find_elements(By.CSS_SELECTOR, ".yuRUbf") # find all search result objects

    
    links = []
    titles = []
    for result in search_results:
        link: str
        title = result.find_element(By.CSS_SELECTOR, "h3").get_attribute('innerHTML') # get the title
        #if title.lower().find('fandom') != -1 or title.lower().find('wiki') != -1: # we are imposing a stricter rule.
        link = result.find_element(By.TAG_NAME, 'a').get_attribute('href') # get the link
        subdomain = get_subdomain_from_url(link)
        if (link.find("fandom") != -1):
            links.append(link)
            titles.append(title)

    highest_similarity_count = -1
    best_matches_stack = []
    found_fandom = False
    for i in range(len(links)):
        link = links[i]
        title = titles[i]

        subdomain = get_subdomain_from_url(link)
        if title.lower().find("database") != -1:
            print("## Error! this is a database fandom, which may not contain enough info. Skipping.")
            continue
        try:
            fandom.set_wiki(subdomain)
            print("Fandom link :",link)
            found_fandom = True
            break
        except Exception:
            print("## Error! ## subdomain parsed wrongly:",subdomain)
    if found_fandom == False:
        print("The show",show_name,"doesn't have a Fandom. They should get a fanbase already!")
        return

    print("Loaded ",show_name,"'s fandom.",sep='')

    for character_name in character_names:
        # go get the google search results!
        print("\tInvestigating:", character_name)
        valid_parcel, tensor_params_map, image_link = fondue_search(character_name, show_name, webscraper)
        if valid_parcel:
            save_current_parcel_to_disk(tensor_params_map, character_name, show_name, image_link)
        PARCEL_INDEX += 1
    
    # check if we should save a checkpoint.
    print("saving position")
    save_position(PARCEL_INDEX)
    save_big_as_heck_csv()

def fondue_search(character:str, show_name:str, webscraper:wd.Chrome):
    # attempt to get straight to the article
    page : None
    try:
        page = fandom.page(character)
    except Exception:
        top_result_name = ''
        try:
            top_result_name, _ = fandom.search(character, results=1)[0]
        except Exception:
            print("\t\t Error!", character, "from", show_name, "doesn't have an article on this fandom.")
            return False, {}, ""
        page = fandom.page(top_result_name)
    image = ""
    images = []
    try:
        print("\t\twill I has portrait??")
        webscraper.get(page.url)
        image_link = webscraper.find_element(By.CLas_heck_NAME, "pi-image-thumbnail").get_attribute('src')
        image = image_link
        print("\t\ti has portrait!")
    except Exception:
        print("\t\t Warning! This character doesn't have a portrait. using first-image instead")
        try:
            images = page.images
            if len(images) == 0:
                # throw 
                image = images[1]
            image = images[0]
        except Exception:
            print("\t\t No images at all!")
    categories = []
    try:
        categories = page.sections
    except Exception:
        print("\t\t Warning! This page doesn't have any sections")

    # process categories
    tensor_params_map = {}
    for cat in categories:
        possible_categories = ["features", "personality", "description", "desc", "traits", "concept", "appearance"]
        valid_cat = False
        cat_words = cat.split()
        for word in cat_words:
            if word.lower() in possible_categories:
                valid_cat = True
                break
        if not valid_cat:
            continue
        text = ""
        try:
            text = page.section(cat)
        except Exception:
            continue
        process_words(text.replace('\n', ' ').split(' '), character, show_name, tensor_params_map)
    summary = ""
    try:
        summary = page.summary
    except Exception:
        print("\t\t Warning! this page does not have a summary! lets see if it has any structure.")
        content = {}
        try:
            content = page.content
        except Exception:
            print("\t\t This article aint got nothing. Returning.")
            return False, {}, ""
        string_dict = str(content)
        process_words(string_dict.replace('\n', ' ').split(' '), character, show_name, tensor_params_map)
    if summary != "":
        process_words(summary.replace('\n', ' ').split(' '), character, show_name, tensor_params_map)

    return True, tensor_params_map, image

def process_words(words:list[str], character:str, show_name:str, tensor_params_map):
    global SET_SIZE
    new_words_count = 0
    for word in words:
        word = remove_spaces_and_non_alphanumeric(word).lower()
        dimension = main_map.get(word)
        if dimension is not None:
            if tensor_params_map.get(dimension) is None: # if this is the first encounter of an already-existing word.
                tensor_params_map[dimension] = 1
            else:
                tensor_params_map[dimension] += 1 # if it's already a part of the current tensors.
            pass
        else:
            main_map[word] = SET_SIZE
            tensor_params_map[SET_SIZE] = 1
            new_words_count += 1
            SET_SIZE += 1
    print("\t\t # new words :", new_words_count)
    #save_current_parcel_to_disk(tensor_params_list, character, show_name)
            
def save_current_parcel_to_disk(contents, character:str, show_name:str, image_link:str):
    file_path = f"tensors/{remove_unusable_chars(f'{character}_{show_name}')}.csv"
    
    with open(file_path, 'w') as f:
        csv_writer = writer(f, lineterminator='\n')
        for k, v in contents.items():
            csv_writer.writerow([k,v])
        if image_link is not None:
            print("\t\t ## Writing image link!")
            f.write(f"IMAGE_LINK,{image_link}")
    pass

def remove_spaces_and_non_alphanumeric(input_string):
    # Use regular expression to remove spaces and non-alphanumeric characters
    cleaned_string = sub(r'[^a-zA-Z0-9]', '', input_string)
    return cleaned_string

def remove_unusable_chars(filename):
    # Define a regular expression pattern to match unusable characters
    pattern = r'[\\/:*?"<>|]'
    
    # Use the re.sub() function to replace unusable characters with an empty string
    cleaned_filename = sub(pattern, '', filename)
    
    return cleaned_filename
    
def get_subdomain_from_url(url:str):
    return url[url.find("https://")+8:url.find('.fandom')]
    # if the article name contains fandom??

def get_characters_after(pos:int):
    pos = pos * 2 # because of the horsenothing with the empty entries
    entries = []
    with open(CSV_FILE, 'r', encoding='ansi') as f:
        csv_reader = reader(f)
        for i, row in enumerate(csv_reader):
            if i < pos:
                continue
            if row[0] != '':
                entries.append(row)
    return entries

def save_position(pos:int):
    remove(POS_SAV)
    with open(POS_SAV, 'w') as f:
        f.write(f'{str(pos)},{str(SET_SIZE)}')

def load_position():
    if not path.exists(POS_SAV):
        return 0
    with open(POS_SAV, 'r') as f:
        strings = f.read().split(',')
        if len(strings) != 2:
            return 0
        SET_SIZE = int(strings[1])
        return int(strings[0])

def load_big_as_heck_csv():
    word_count = 0
    with open(UNIQUE_SET_FILE, 'rt') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            for k, v in row.items():
                main_map[k] = v
                word_count += 1
    return word_count

def save_big_as_heck_csv():
    list_representation = list(main_map.items())
    with open(UNIQUE_SET_FILE, 'w', newline='') as f:
        csv_writer = writer(f)
        for k, v in list_representation:
            csv_writer.writerow([k, v])
    # save the words with their indices


if __name__ == '__main__':
    webscraper = start_webscraper()
    index = load_position()
    if index > 0:
        SET_SIZE = load_big_as_heck_csv()
    lines = get_characters_after(index)
    i = 0
    print("there are ", len(lines) ,"lines to read")
    for line in lines:
        i += 1
        #convert next line to array
        arr = eval(line[1])
        google_search(webscraper, arr, line[0])
            
        save_position(index)
