import nltk
from nltk.corpus import wordnet

#download the dataset
nltk.download('wordnet')

#filter by adjectives
# adjectives_set = set(wordnet.all_synsets(pos='a'))

"""
with open('test_adj.txt', 'w') as f:
    for adj_synset in adjectives_set:
        lemmas = adj_synset.lemmas()
        for lemma in lemmas:
            f.write(lemma.name() + '\n')

            """
#filter by nouns
nouns_set = set(wordnet.all_synsets(pos='n'))

with open('test_noun.txt', 'w') as f:
    for adj_synset in nouns_set:
        lemmas = adj_synset.lemmas()
        for lemma in lemmas:
            f.write(lemma.name() + '\n')