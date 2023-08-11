from flask import Flask, render_template, jsonify, request

import random
import numpy as np
import csv
import os
import pandas as pd
from datetime import datetime

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
    USER_ID = 1

    # Calculate learned words
    learned_words_df = pd.read_csv("data/user/learned_words.csv")
    learned_words_df = learned_words_df[learned_words_df["user_id"] == USER_ID]
    learned_words_list = learned_words_df["word_id"].tolist()

    words_learned = len(
        learned_words_df["word_id"].unique()
    )  # number of unique words learned

    # Calculate words learned today
    today = datetime.today().strftime(
        "%Y-%m-%d"
    )  # Get today's date in YYYY-MM-DD formatsss\\\
    words_reviewed = len(
        learned_words_df[learned_words_df["date_last_accessed"] == today]
    )

    # Calculate words reviewed today
    words_learned_today = len(
        learned_words_df[learned_words_df["date_first_accessed"] == today]
    )

    # Calculate conversational coverage
    all_words_df = pd.read_csv("data/raw/dictionary/words.csv")
    all_words_df = all_words_df[all_words_df["wordID"].isin(learned_words_list)]
    spoken_pct = round(all_words_df["perMil"].sum() / 1000000 * 100, 1)

    return render_template(
        "index.html",
        words_learned=words_learned,
        words_reviewed=words_reviewed,
        words_learned_today=words_learned_today,
        spoken_pct=spoken_pct,
    )


@app.route("/")
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


@app.route("/mark-as-difficult", methods=["POST"])
def mark_as_difficult():
    userID = 1  # hardcoded user ID for now
    DIFFICULT_WEIGHT = 1.5  # hardcoded difficulty weight for now

    data = request.json
    wordID = data.get("wordID")

    # Your data, for example
    data = {
        "userID": [userID],
        "wordID": [wordID],
        "difficulty_weight": [DIFFICULT_WEIGHT],
    }
    new_row_df = pd.DataFrame(data)

    # 1. Read the existing CSV into a DataFrame
    file_path = "data/difficult_words.csv"
    if not pd.io.common.file_exists(file_path):
        # If the file doesn't exist, create an empty DataFrame with the same columns
        existing_df = pd.DataFrame(columns=["userID", "wordID", "difficulty_weight"])
    else:
        existing_df = pd.read_csv(file_path)

    # 2. Check if the combination of userID and wordID already exists
    exists = (
        existing_df[
            (existing_df["userID"] == new_row_df["userID"][0])
            & (existing_df["wordID"] == new_row_df["wordID"][0])
        ].shape[0]
        > 0
    )

    # 3. If the combination doesn't exist, append the new row
    if not exists:
        updated_df = pd.concat([existing_df, new_row_df], ignore_index=True)

        # 4. Write the updated DataFrame back to the difficult_words.csv
        updated_df.to_csv(file_path, index=False)
    else:
        print("The combination of userID and wordID already exists.")

    # Add your logic to write the wordId to difficult_words.csv

    return jsonify(status="success", message="Word marked as difficult.")


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
        chosen_word_id = get_random_word_by_weight(USER_ID)
        chosen_word = all_words[all_words["wordID"].isin([chosen_word_id])].to_dict(
            "records"
        )[0]

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


def get_random_word_by_weight(USER_ID):
    # Read the learned words
    learned_words_df = pd.read_csv("data/user/learned_words.csv")
    learned_words_df = learned_words_df[learned_words_df["user_id"] == USER_ID]

    # Convert columns to datetime objects
    learned_words_df["date_first_accessed"] = pd.to_datetime(
        learned_words_df["date_first_accessed"]
    )
    learned_words_df["date_last_accessed"] = pd.to_datetime(
        learned_words_df["date_last_accessed"]
    )

    # Calculate the number of days since first and last accessed
    today = datetime.today()
    learned_words_df["days_since_first_accessed"] = (
        today - learned_words_df["date_first_accessed"]
    ).dt.days + 1
    learned_words_df["days_since_last_accessed"] = (
        today - learned_words_df["date_last_accessed"]
    ).dt.days + 1

    # Generate weights
    # We inverse the days_since_first_accessed because newer words should have higher weights.
    learned_words_df["weight_first_accessed"] = (
        1 / learned_words_df["days_since_first_accessed"]
    )
    learned_words_df["weight_last_accessed"] = learned_words_df[
        "days_since_last_accessed"
    ]

    # Merge with difficult words
    difficult_words_df = pd.read_csv("data/user/difficult_words.csv")
    difficult_words_df = difficult_words_df[difficult_words_df["user_id"] == USER_ID]
    learned_words_df = pd.merge(
        learned_words_df,
        difficult_words_df[["word_id", "difficulty_weight"]],
        on="word_id",
        how="left",
    )
    learned_words_df["difficulty_weight"] = learned_words_df[
        "difficulty_weight"
    ].fillna(
        1
    )  # Fill NaNs with 1 (baseline weight)

    # Calculate the final weight
    learned_words_df["final_weight"] = (
        learned_words_df["weight_first_accessed"]
        * learned_words_df["weight_last_accessed"]
        * learned_words_df["difficulty_weight"]
    )

    # Sample a word based on the final weight
    chosen_word_id = np.random.choice(
        learned_words_df["word_id"],
        p=learned_words_df["final_weight"] / learned_words_df["final_weight"].sum(),
    )
    return chosen_word_id


def update_last_accessed_date(user_id, word_id):
    today = datetime.today().strftime("%Y-%m-%d")
    learned_words_df = pd.read_csv("data/user/learned_words.csv")

    # Update last_accessed date for the word
    learned_words_df.loc[
        (learned_words_df["user_id"] == user_id)
        & (learned_words_df["word_id"] == word_id),
        "date_last_accessed",
    ] = today
    learned_words_df.to_csv("data/user/learned_words.csv", index=False)


def add_learned_word(user_id, word_id):
    today = datetime.today().strftime(
        "%Y-%m-%d"
    )  # Get today's date in YYYY-MM-DD format
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
    app.run(debug=True, port=5001)
