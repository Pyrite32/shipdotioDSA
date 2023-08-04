import requests
from csv import reader, DictReader
from PIL import Image
from os import listdir, getcwd, path
from io import BytesIO
link_dict = {}

LIMIT = 10000
LOWER_LIMIT = 8200
abs_base =  path.abspath(path.join(getcwd()))

def download_image(character, link):
    if (link == ''): return
    try:
        response = requests.get(link)
    except Exception:
        return
    if response.status_code == 200:
        image = None
        try:
            image = Image.open(BytesIO(response.content))
        except Exception:
            return
        
        aspect_ratio = image.width / image.height
        if aspect_ratio > 1.2:
            reduced_space = image.width - image.height
            crop_start_x = reduced_space / 2
            crop_end_x = crop_start_x + image.height
            crop_start_y = 0
            crop_end_y = image.height
            image_crop_box = (crop_start_x, crop_start_y, crop_end_x, crop_end_y)
            cropped_image = image.crop(image_crop_box)

            downscaled_image_size = (128,128)
            final_image = cropped_image.resize(downscaled_image_size)
            try:
                final_image.save(path.join(abs_base,"images",character+".png"))
            except Exception:
                return
            pass # landscape
        elif aspect_ratio < 0.8:
            reduced_space = image.height - image.width
            crop_start_x = 0
            crop_end_x = image.width
            crop_start_y = 0
            crop_end_y = image.width
            image_crop_box = (crop_start_x, crop_start_y, crop_end_x, crop_end_y)
            cropped_image = image.crop(image_crop_box)
            downscaled_image_size = (128,128)
            
            final_image = cropped_image.resize(downscaled_image_size)
            try:
                final_image.save(path.join(abs_base,"images",character+".png"))
            except Exception:
                return
            pass # portrait
        else:
            final_image = image.resize((128,128))
            try:
                final_image.save(path.join(abs_base,"images",character+".png"))
            except Exception:
                return
            pass # close enough to a square so it can be resized without much distortion.

        
    else:
        print("failed to get image. status code is",response.status_code)

image_number = 0
abs_ref = path.abspath(path.join(abs_base,"image_links.csv"))
with open(abs_ref, 'r', newline='', encoding='ansi') as f:
    csv_reader = reader(f)
    for row in csv_reader:
        if image_number < LOWER_LIMIT:
            image_number += 1
            print("catching up:", image_number)
            continue
        download_image(row[0],row[1])
        image_number += 1
        if image_number >= LIMIT+2000:
            exit()
