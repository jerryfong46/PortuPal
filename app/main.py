from flask import Flask, render_template, jsonify, request

import random
import csv
import os
import pandas as pd
import datetime

app = Flask(__name__)


def read_csv(file_path):
    words = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            words.append(row)
    return words


def write_to_csv(file_path, words):
    with open(file_path, "w", encoding="utf-8") as f:
        # Assuming the wordID is an additional field in the CSV.
        writer = csv.DictWriter(f, fieldnames=["wordID", "english", "portuguese"])
        writer.writeheader()
        for word in words:
            writer.writerow(word)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/home")
def homepage():
    # Your logic for the home page, for example, displaying stats
    return render_template("home.html")


@app.route("/flashcards")
def flashcards_page():
    # Your logic for the flashcards
    return render_template("flashcards.html", active_page="flashcards")


@app.route("/stats")
def stats_page():
    # Your logic for displaying stats
    return render_template("stats.html")


@app.route("/stories")
def stories_page():
    # Your logic for displaying stories
    return render_template("stories.html")


@app.route("/get-random-word", methods=["GET"])
def get_random_word():
    USER_ID = 1  # hardcoded user ID for now

    mode = request.args.get("mode", "practice")  # default mode is 'practice'

    # Read the learned words
    learned_words_df = pd.read_csv("data/user/learned_words.csv")
    learned_words_df = learned_words_df[learned_words_df["user_id"] == USER_ID]
    learned_word_ids = learned_words_df["word_id"].tolist()

    # Retrieve words from the main dictionary
    all_words = pd.read_csv("data/raw/dictionary/words.csv")
    cols = ["wordID", "lemma", "Portuguese", "Sentence"]
    all_words = all_words[cols]
    all_words.columns = ["wordID", "english", "portuguese", "sentence"]

    if mode == "practice":
        # Filter the main dictionary to get only learned words
        practiced_words = all_words[all_words["wordID"].isin(learned_word_ids)]
        chosen_word = random.choice(practiced_words.to_dict("records"))

        # Update date_last_accessed for the chosen word
        update_last_accessed_date(USER_ID, chosen_word["wordID"])

        return jsonify(chosen_word)

    else:  # mode == 'learn'
        unlearned_words = all_words[~all_words["wordID"].isin(learned_word_ids)]
        if not unlearned_words.empty:
            first_unlearned_word = unlearned_words.iloc[0]
            add_learned_word(USER_ID, first_unlearned_word["wordID"])
            return jsonify(first_unlearned_word.to_dict())

    return jsonify({"message": "No new words to learn."})


def update_last_accessed_date(user_id, word_id):
    today = datetime.date.today().isoformat()
    learned_words_df = pd.read_csv("data/user/learned_words.csv")

    # Update last_accessed date for the word
    learned_words_df.loc[
        (learned_words_df["user_id"] == user_id)
        & (learned_words_df["word_id"] == word_id),
        "date_last_accessed",
    ] = today
    learned_words_df.to_csv("data/user/learned_words.csv", index=False)


def add_learned_word(user_id, word_id):
    today = datetime.date.today().isoformat()  # Get today's date in YYYY-MM-DD format
    try:
        learned_words_df = pd.read_csv("data/user/learned_words.csv")

        # Check if word_id is already present for the user
        existing_entry = learned_words_df[
            (learned_words_df["user_id"] == user_id)
            & (learned_words_df["word_id"] == word_id)
        ]

        if existing_entry.empty:  # If word is not already learned
            with open("data/user/learned_words.csv", "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(
                    [user_id, word_id, today, today]
                )  # first_accessed and last_accessed are both today
        else:  # If word is already learned, then update last_accessed
            learned_words_df.loc[
                (learned_words_df["user_id"] == user_id)
                & (learned_words_df["word_id"] == word_id),
                "date_last_accessed",
            ] = today
            learned_words_df.to_csv("data/user/learned_words.csv", index=False)

        return jsonify({"message": "Word added/updated successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/learn-new-words")
def learn_new_words():
    all_words = read_csv("data/raw/dictionary/words.csv")
    learned_word_ids = [
        word["wordID"] for word in read_csv("data/user/learned_words.csv")
    ]
    new_words = [word for word in all_words if word["wordID"] not in learned_word_ids][
        :5
    ]
    return jsonify(new_words)


@app.route("/mark-learned/<wordID>")
def mark_as_learned(wordID):
    learned_words = read_csv("data/user/learned_words.csv")
    # Using wordID to identify the word
    new_word = next(
        item
        for item in read_csv("data/raw/dictionary/words.csv")
        if item["wordID"] == wordID
    )
    learned_words.append(new_word)
    write_to_csv("data/user/learned_words.csv", learned_words)
    return jsonify({"status": "success", "learned": wordID})


if __name__ == "__main__":
    app.run(debug=True)
