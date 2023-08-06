def modded_msd_sort(dataset): # O(N) (best case)  to O(N * W) (worst case), W: average length of strings
    R = 256
    aux = [None] * len(dataset)

    def sort(dataset, low, high, d):
        if low >= high or d >= len(dataset[low][0]):
            return

        count = [0] * (R + 2)
        for i in range(low, high + 1):
            char_index = ord(dataset[i][0][d] if d < len(dataset[i][0]) else -1)
            count[char_index + 2] += 1

        for r in range (R + 1):
            count[r + 1] += count[r]

        for j in range(low, high + 1):
            char_index = ord(dataset[i][0][d] if d < len(dataset[i][0]) else -1)
            aux[count[char_index + 1] - 1] = dataset[i]
            count[char_index + 1] += 1

        for i in range (low, high + 1):
            dataset[i] = aux[i - low]

        for r in range(R):
            sort(dataset, low + count[r], low + count[r + 1] - 1, d + 1)

    sort(dataset, 0, len(dataset) - 1, 0)
    return dataset


dataset = []
with open('lexical-data-rand.txt', 'r', encoding='ansi') as f:
    dataset = f.readlines()

modded_msd_sort(dataset)
