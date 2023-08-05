def modded_lsd_sort(dataset): # O(N * W) N: number of characters W: max string size

    # find max length string
    max_length = 0
    for character in dataset:
        if len(character[0]) > max_length:
            max_length = len(character[0])

    # Pad shorter strings
    dataset = [character[0].ljust(max_length, '\0') for character in dataset]

    # lsd radix sort
    for i in range(max_length - 1, -1, -1):
        dataset = sorted(dataset, key=lambda s: s[i][0])

    # Remove padding
    dataset = [character[0].rstrip() for character in dataset]
    return dataset