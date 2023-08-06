import pickle
from csv import writer

entire_dataset = []

with open('characters_processed.bin', 'rb') as f:
    entire_dataset = pickle.load(f)

DATA_SIZE = len(entire_dataset)
UPDATE_INTERVAL = 100
interval_counter = 0
processed = 0

with open('unpacked.csvt', 'w', encoding='ansi') as f:
    csv_writer = writer(f,lineterminator='\n')
    for line in entire_dataset:
        csv_writer.writerow(line)
        interval_counter += 1
        processed = 0
        if interval_counter % UPDATE_INTERVAL == 0:
            with open('progress.txt', 'w') as f:
                f.write(f'{str(processed)}/{DATA_SIZE}')