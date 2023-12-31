from flask import Flask, render_template, jsonify, request

import random
import numpy as np
import csv
import os
import pandas as pd
from datetime import datetime, timedelta
import requests
import openai

app = Flask(__name__)


# Helper Functions
def is_word_difficult(userID, wordID):
    """Check if a word is marked as difficult for a user."""
    userID = int(userID)
    wordID = int(wordID)

    file_path = "data/user/difficult_words.csv"
    if not pd.io.common.file_exists(file_path):
        return False
    df = pd.read_csv(file_path)
    return df[(df["user_id"] == userID) & (df["word_id"] == wordID)].any().any()


def remove_word_from_difficult(userID, wordID):
    """Remove a word from the difficult list for a user."""
    userID = int(userID)
    wordID = int(wordID)

    file_path = "data/user/difficult_words.csv"
    df = pd.read_csv(file_path)
    df = df[~((df["user_id"] == userID) & (df["word_id"] == wordID))]
    df.to_csv(file_path, index=False)


def add_word_to_difficult(userID, wordID, DIFFICULT_WEIGHT=2):
    """Add a word to the difficult list for a user."""
    file_path = "data/user/difficult_words.csv"
    new_row_df = pd.DataFrame(
        {
            "user_id": [userID],
            "word_id": [wordID],
            "difficulty_weight": [DIFFICULT_WEIGHT],
        }
    )

    if not pd.io.common.file_exists(file_path):
        new_row_df.to_csv(file_path, index=False)
    else:
        df = pd.read_csv(file_path)
        updated_df = pd.concat([df, new_row_df], ignore_index=True)
        updated_df.to_csv(file_path, index=False)


# Endpoint
@app.route("/toggle-difficulty", methods=["POST"])
def toggle_difficulty():
    userID = 1  # hardcoded user ID for now
    data = request.json
    wordID = data.get("wordID")

    if is_word_difficult(userID, wordID):
        remove_word_from_difficult(userID, wordID)
        return jsonify(
            status="success",
            action="removed",
            message="Word removed from difficult list.",
        )
    else:
        add_word_to_difficult(userID, wordID)
        return jsonify(
            status="success", action="added", message="Word marked as difficult."
        )


@app.route("/get-words-learned-data", methods=["GET"])
def get_words_learned_data():
    USER_ID = 1

    # Calculate learned words
    learned_words_df = pd.read_csv("data/user/learned_words.csv")
    learned_words_df = learned_words_df[learned_words_df["user_id"] == USER_ID]

    # Generate a complete date range from the start to the end of your data
    min_date = learned_words_df["date_first_accessed"].min()
    max_date = learned_words_df["date_first_accessed"].max()
    all_dates = pd.DataFrame(
        {"date_first_accessed": pd.date_range(start=min_date, end=max_date)}
    )
    all_dates["date_first_accessed"] = all_dates["date_first_accessed"].dt.strftime(
        "%Y-%m-%d"
    )

    cumulative_learned = (
        learned_words_df.groupby("date_first_accessed")
        .agg({"word_id": "count"})
        .reset_index()
        .rename({"word_id": "wordsLearnedDay"}, axis=1)
    )

    # Merge with the complete date range
    cumulative_learned = all_dates.merge(
        cumulative_learned, on="date_first_accessed", how="left"
    ).fillna(0)

    cumulative_learned["wordsLearned"] = cumulative_learned["wordsLearnedDay"].cumsum()
    cumulative_learned["date"] = cumulative_learned["date_first_accessed"]
    data = cumulative_learned[["date", "wordsLearned", "wordsLearnedDay"]].to_dict(
        "records"
    )

    return jsonify(data)


def get_keys():
    # Define the path to the file containing API keys and descriptions
    api_key_file = os.path.join("config", "api_keys.txt")

    # Read the file and split the lines by newline
    with open(api_key_file, "r") as f:
        api_key_lines = f.read().split("\n")

    # Parse the lines into a dictionary
    api_keys = {}
    for line in api_key_lines:
        if line.strip():
            key_description, api_key = line.split()
            api_keys[key_description.strip("[]")] = api_key

    # API Keys
    openai.api_key = api_keys["openai"]


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
    all_words_df["perMil"] = all_words_df["perMil"].astype(float)
    spoken_pct = round(all_words_df["perMil"].sum() / 1000000 * 100, 1)

    return render_template(
        "index.html",
        words_learned=words_learned,
        words_reviewed=words_reviewed,
        words_learned_today=words_learned_today,
        spoken_pct=spoken_pct,
    )


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
    timeframe = request.args.get("timeframe", default="All", type=str)
    practiceType = request.args.get("practiceType", default="vocabulary", type=str)

    # Read the learned words
    learned_words_df = pd.read_csv("data/user/learned_words.csv")
    difficult_words_df = pd.read_csv("data/user/difficult_words.csv")

    learned_words_df = learned_words_df[learned_words_df["user_id"] == USER_ID]
    difficult_words_df = difficult_words_df[difficult_words_df["user_id"] == USER_ID][
        "word_id"
    ].tolist()

    learned_word_ids = learned_words_df["word_id"].tolist()

    # Retrieve words from the main dictionary

    all_words = pd.read_csv("data/raw/dictionary/words.csv")
    all_verbs = pd.read_csv("data/raw/dictionary/verbs_present_tense.csv")

    if practiceType == "conjugations":
        # Select random conjugations from list
        conj_perm = len(all_verbs["eng_conjugations"][0].split(";"))
        randConj = random.randint(0, conj_perm - 1)

        cols = [
            "wordID",
            "eng_conjugations",
            "port_conjugations",
            "eng_sentence",
            "port_sentence",
        ]

        all_words = all_verbs[cols]
        all_words = all_words.dropna()  # Drop rows with NaN values

        # Only keep randomly selected conjugation
        all_words["eng_conjugations"] = [
            i.split(";")[randConj] for i in all_words["eng_conjugations"]
        ]
        all_words["port_conjugations"] = [
            i.split(";")[randConj] for i in all_words["port_conjugations"]
        ]
        all_words["eng_sentence"] = [
            i.split(";")[randConj] for i in all_words["eng_sentence"]
        ]
        all_words["port_sentence"] = [
            i.split(";")[randConj] for i in all_words["port_sentence"]
        ]

        all_words.columns = [
            "wordID",
            "english",
            "portuguese",
            "eng_sentence",
            "port_sentence",
        ]
    else:
        cols = [
            "wordID",
            "lemma",
            "Portuguese",
            "Sentence",
            "port_sentence",
            "eng_sentence",
        ]
        all_words = all_words[cols]
        all_words.columns = [
            "wordID",
            "english",
            "portuguese",
            "sentence",
            "port_sentence",
            "eng_sentence",
        ]

    if mode == "practice":
        # Filter the main dictionary to get only learned words
        chosen_word_id = get_random_word_by_weight(USER_ID, timeframe, practiceType)
        print(f"THE WORD IS {chosen_word_id}")
        chosen_word = all_words[all_words["wordID"].isin([chosen_word_id])].to_dict(
            "records"
        )[0]

        # Check if chosen word is difficult word
        if chosen_word_id in difficult_words_df:
            chosen_word["is_difficult"] = True
        else:
            chosen_word["is_difficult"] = False

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


def get_random_word_by_weight(USER_ID, timeframe, practiceType):
    # NEED TO ADD SOMETHING HERE TO FILTER FOR ONLY VERBS?

    # Read the learned words
    learned_words_df = pd.read_csv("data/user/learned_words.csv")
    all_words_df = pd.read_csv("data/raw/dictionary/words.csv")

    learned_words_df = learned_words_df[learned_words_df["user_id"] == USER_ID]

    # Filter for verbs
    if practiceType == "conjugations":
        verb_ids = all_words_df[all_words_df["PoS"] == "v"]["wordID"].tolist()
        learned_words_df = learned_words_df[learned_words_df["word_id"].isin(verb_ids)]

    if timeframe == "15":  # Filter
        learned_words_df = learned_words_df.sort_values(
            by="date_first_accessed", ascending=False
        )[0:15]

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

    if timeframe == "D":  # Filter for only difficult words
        if (
            learned_words_df["difficulty_weight"].max() > 1
        ):  # If difficult words exist, filter for them
            learned_words_df = learned_words_df[
                learned_words_df["difficulty_weight"] > 1
            ]
        else:  # Random word returned if no difficult words exist
            print("No difficult words found. Returning random word.")

    print(learned_words_df)
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


@app.route("/generate_story", methods=["POST"])
def generate_story():
    get_keys()
    USER_ID = 1  # Replace with your actual user id

    data = request.json
    genre = data.get("genre")

    # Logic to generate the stories for each language based on the genre.
    stories = create_story(genre, USER_ID, "")  # blank for current story
    english_story = stories[0]
    portuguese_story = stories[1]

    return jsonify(
        {"english_story": english_story, "portuguese_story": portuguese_story}
    )


@app.route("/continue-story", methods=["POST"])
def continue_story():
    get_keys()
    USER_ID = 1  # Replace with your actual user id

    data = request.json
    current_story = request.json.get("story")
    genre = request.json.get("genre")

    # Logic to generate the stories for each language based on the genre.
    stories = create_story(genre, USER_ID, current_story)
    english_story = stories[0]
    portuguese_story = stories[1]

    return jsonify(
        {"english_story": english_story, "portuguese_story": portuguese_story}
    )


def create_story(genre, user_id, back_story):
    user_id = 1

    learned_words_df = pd.read_csv("data/user/learned_words.csv")
    learned_words_df = learned_words_df[learned_words_df["user_id"] == user_id]
    all_words = pd.read_csv("data/raw/dictionary/words.csv")
    usable_words_list = list(
        all_words[all_words["wordID"].isin(learned_words_df["word_id"])]["lemma"]
    )

    # If story exists, continue story
    if back_story == "None":
        back_story = f"Write the first chapter of an exciting novel."
    else:
        back_story = f"Here is the previous chapter of the novel: \n\n + {back_story} \n\n + Write the next chapter."

    prompt = f"""Write the first chapter. \n\n
        {back_story} \n\n
        Keep it to 100 words or less. The genre is {genre}. The reading comprehension level should be that of a 5 year old. Write it in present tense. \n\n 
        The story should be comprised primarily (over 95%) of the following words and their conjugations: [{', '.join(usable_words_list)}] \n\n 
        Write the English version first, followed by the Brazilian Portuguese version. Separate the two with ***.
        """

    print(prompt)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a professional translator and best-selling author.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=750,
        n=1,
        stop=None,
        temperature=1.0,
    )

    response_story = response.choices[0]["message"]["content"]
    english_story = response_story.split("***")[0].strip()
    portuguese_story = response_story.split("***")[1].strip()

    return english_story, portuguese_story


if __name__ == "__main__":
    app.run(debug=True, port=5000)
