
from sklearn.decomposition import PCA
import numpy as np
import pandas as pd
import csv
import os

from sklearn.metrics import euclidean_distances

# determine the MAX dimension
# determine which dimensions are included.

usable_nums = set()
character_names = []
USAGE_LOWER_LIMIT = 10
USAGE_UPPER_LIMIT = 100

LIMIT = 5000
limit_counter = 0
DIM_MAX = 0
with open('the_words_filtered.csv', 'r') as f:
     csv_reader = csv.reader(f)
     for _, row in enumerate(csv_reader):
         current_id = int(row[1])
         usable_nums.add(current_id)
         DIM_MAX = max(DIM_MAX, current_id)
DIM_MAX += 2 
print("dim max : ", DIM_MAX)

# determine the number of character files.
CHARACTER_COUNT = 0
for item in os.listdir("tensors"):
     path = os.path.join("tensors", item)
     if os.path.isfile(path):
          CHARACTER_COUNT += 1

# create the mega matrix
#mega_input = np.zeros((DIM_MAX, CHARACTER_COUNT), dtype=float)
MAX_ROWS = int(DIM_MAX)
MAX_COLUMNS = LIMIT
mega_input = np.zeros((MAX_ROWS, MAX_COLUMNS+1), dtype=float)

print(len(mega_input))
# load entries into matrix
file_index = 0
for item in os.listdir("tensors"):
    path = os.path.join("tensors", item)
    if os.path.isfile(path) and str(path).endswith('.csv'):
        character_names.append(path[8:path.find('_')])
        with open(path, 'r') as f:
            csv_reader = csv.reader(f)
            for _, row in enumerate(csv_reader):
                if (row[0] == 'IMAGE_LINK'):
                    break
                id = int(row[0])
                if id < MAX_ROWS:
                    mega_input[int(row[0]), file_index] = float(row[1])
        file_index += 1
    if file_index > MAX_COLUMNS:
        break



print(len(mega_input))
components = 2

print("delonelify")
# remove lonely or blank entries (a row with only one entry in all of the vectors.)
usage_amounts = np.sum(mega_input, axis=1)
mega_input = mega_input[USAGE_LOWER_LIMIT < usage_amounts]

usage_amounts = np.sum(mega_input, axis=1)
mega_input = mega_input[USAGE_UPPER_LIMIT > usage_amounts]
print("delonelified size",len(mega_input))
print(mega_input)


# normalize data
min_values = np.min(mega_input)
max_values = np.max(mega_input)

normalized = (mega_input - min_values) / (max_values - min_values)

# center data
mean_values = np.mean(normalized, axis=0)
normalized = normalized - mean_values

# transpose
normalized = np.transpose(normalized)

# covariance
# how much of one word exists in each of the characters 

covariance = np.cov(normalized)
data_array = np.asarray(covariance)

pca = PCA(n_components=30, svd_solver='randomized')
approximated_data = pca.fit_transform(data_array)


print("Now, you should be able to compare characters to each other.")
option = '0'
while option != 'exit':
    print("1. compare")
    option = input("enter an option: ")
    if option == "1":
        valid1 = False
        valid2 = False
        while not valid1:
            char1 = input("enter char 1")
            if char1 in character_names:
                idx1 = character_names.index(char1)
                valid1 = True
        print("valid")
        while not valid2:
            char2 = input("enter char 2")
            if char2 in character_names:
                idx2 = character_names.index(char2)
                valid2 = True
        vec1 = approximated_data[idx1]
        vec2 = approximated_data[idx2]
        cosine_similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1)*np.linalg.norm(vec2))
        euclidean_similarity = np.linalg.norm(vec1 - vec2)
        correlation_coefficient = np.corrcoef(vec1, vec2)[0,1]
        manhattan_similarity = np.sum(np.abs(vec2 - vec1))
        print("Likeness using cosine similarity: ",abs(cosine_similarity * 100.0),'%')
        print("Likeness using euclidean distance: ",1 - abs(euclidean_similarity * 100.0),'%')
        print("Likeness using correlation coefficient:", 1 - abs(correlation_coefficient * 100.0),'%')
        print("Likeness using manhattan distance:", 1 - abs(manhattan_similarity * 100.0),'%')
        print(char1,"data:",vec1)
        print(char2,"data:",vec2)


#print("covariance : ",covariance)

# eigenvalues and eigenvectors for some reason
#eigenvals, eigenvectors = np.linalg.eigh(covariance)

# sort the eigenvalues and eigenvectors for yet even less of a good reason
#sorted_indices = np.argsort(eigenvals)[::-1] # reverse order
#sorted_eigenvalues = eigenvals[sorted_indices]
#sorted_eigenvectors = eigenvectors[:, sorted_indices]
#print("eigenvectors: ",sorted_eigenvectors)

# only get the best of the eigenvectors
#mm_yess_gimme_the_eigenvectors = sorted_eigenvectors[:, 0:components]




# apply PCA

# save each column as a new_edition tensor