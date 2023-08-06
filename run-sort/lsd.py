def modded_lsd_sort(dataset, radix=256): # O(N * W) N: number of characters W: max string size

    # find max length string
    max_length = 0
    for character in dataset:
        if len(character[0]) > max_length:
            max_length = len(character[0])
    return lsd_radix_sort_helper(dataset, max_length, radix)

def lsd_radix_sort_helper(dataset, max_length, radix):
    for pos in range(max_length - 1, -1, -1):
        count = [0] * (radix + 1)
        aux = [None] * len(dataset)

        for character in dataset:
            idx = ord(character[0][pos]) if pos < len(character[0]) else 0
            count[idx] += 1

        for i in range(1, radix + 1):
            count[i] += count[i - 1]

        for character in reversed(dataset):
            idx = ord(character[0][pos]) if pos < len(character[0]) else 0
            aux[count[idx] - 1] = character
            count[idx] -= 1

        dataset = aux

    return dataset

dataset = []
with open('lexical-data-rand.txt', 'r', encoding='ansi') as f:
    dataset = f.readlines()

dataset = modded_lsd_sort(dataset)

    
