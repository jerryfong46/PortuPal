import os
import nltk
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, names
from nltk.tag import pos_tag
from nltk.tokenize import RegexpTokenizer
import string
import pandas as pd
import re


def get_sentence(word, text):
    # Split the text into sentences
    sentences = re.split("(?<=[.!?]) +", text)

    # Find the first sentence that contains the word
    for sentence in sentences:
        if word in sentence.split():
            return sentence

    # If no sentence is found that contains the word, return an empty string
    return ""


# Download NLTK data
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("averaged_perceptron_tagger")

# Load stopwords and punctuation
stop_words = set(stopwords.words("english"))
punct = set(string.punctuation)

# Read in corpus files
corpus_dir = "data/corpus_files"
files = os.listdir(corpus_dir)
corpus = ""
for file in files:
    with open(os.path.join(corpus_dir, file), "rb") as f:
        contents = f.read().decode("utf-8", errors="replace")
        corpus += contents


# Use NLTK's regular expression tokenizer
tokenizer = RegexpTokenizer(r"\w+")
tokens = tokenizer.tokenize(corpus.lower())

# Tokenize words
tokens = word_tokenize(corpus.lower())

# Use part-of-speech tagging to label each word
tagged_tokens = pos_tag(tokens)

# Filter out stopwords, punctuation and proper nouns
custom_stop_words = set(
    [
        "harry",
        "ron",
        "potter",
        "hagrid",
        "philosophers",
        "rowling",
        "j.k.",
        "hermione",
        "dumbledore",
        "snape",
        "mr.",
        "malfoy",
        "sirius",
        "mcgonagall",
        "lupin",
        "george",
        "ginny",
        "voldemort",
        "weasley",
        "fred",
        "percy",
        "neville",
        "crabbe",
        "goyle",
        "filch",
        "flitwick",
        "lockhart",
        "moody",
        "quidditch",
        "trelawney",
        "umbridge",
        "winky",
        "wood",
        "zabini",
        "cho",
        "dobby",
        "dudley",
        "fudge",
        "hedwig",
        "luna",
        "mrs.",
        "narcissa",
        "pettigrew",
        "riddle",
        "scabbers",
        "skeeter",
        "slughorn",
        "sprout",
        "tom",
        "trelawney",
        "vernon",
        "wormtail",
    ]
)
stop_words = stop_words.union(custom_stop_words)
filtered_tokens = [
    token
    for token, tag in tagged_tokens
    if token not in stop_words
    and not all(char in punct for char in token)
    and tag != "NNP"
    and tag != "NNPS"
    and token.isalpha()
]

# Get the top 1000 words
freq_dist = Counter(filtered_tokens)
common_words = freq_dist.most_common(2000)

df = pd.DataFrame(common_words, columns=["word", "count"])
total_words = len(filtered_tokens)
df["cumulative_count"] = df["count"].cumsum()
df["cumulative_percent"] = (df["cumulative_count"] / total_words) * 100

# Apply the get_sentence function to each word
df["sentence"] = df["word"].apply(lambda x: get_sentence(x, corpus))
