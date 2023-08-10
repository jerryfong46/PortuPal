import pandas as pd
import random

WORDS_FILE = "data/raw/dictionary/words.csv"


def get_random_word():
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(WORDS_FILE)  # assuming tab-separated
    df = df[0:300]

    # Randomly select a row (word)
    random_row = df.sample()

    # Extract the English and Portuguese words from the row
    english_word = random_row["lemma"].values[0]
    portuguese_word = random_row["Portuguese"].values[0]

    # Randomly decide which side to show
    if random.choice(["english", "portuguese"]) == "english":
        return english_word, "English"
    else:
        return portuguese_word, "Portuguese"


if __name__ == "__main__":
    word, side = get_random_word()
    print(f"Showing {side} side: \n {word.upper()}")
