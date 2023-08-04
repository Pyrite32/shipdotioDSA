from os import listdir, getcwd
import os
from csv import reader, writer
# get all image links from all characters with character names, and put it in a csv.

link_dict = {}

tensors_dir = os.path.abspath(os.path.join(getcwd(),"tensors"))

# get the image links from every tensor
for item in listdir(tensors_dir):
    path = os.path.abspath(os.path.join(os.path.join(getcwd(),"tensors", item)))
    name = os.path.basename(path).removesuffix(".csv")
    if os.path.isfile(path) and str(path).endswith('.csv'): # if this is a tensor
        first_part = name
        second_part = ""
        with open(path, 'r') as f:
            csv_reader = reader(f)
            for _, row in enumerate(csv_reader):
                if row[0] == "IMAGE_LINK":
                    second_part = row[1] # get the link
        link_dict[first_part] = second_part

# save the data to a file.
abs_path = os.path.abspath(os.path.join(getcwd(),"image_links.csv"))
with open(abs_path, 'w', newline='', encoding='ansi') as f:
    csv_writer = writer(f)
    for _, (k,v) in enumerate(link_dict.items()):
        try:
            csv_writer.writerow([k,v])
        except Exception:
            continue


                    
