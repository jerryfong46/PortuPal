document.addEventListener('DOMContentLoaded', function () {

    // Variables
    let currentMode = 'practice';

    // Event listeners for the mode toggles
    document.getElementById('learn').addEventListener('click', function () {
        currentMode = 'learn';
        fetchNewWord();
    });

    document.getElementById('practice').addEventListener('click', function () {
        currentMode = 'practice';
        fetchNewWord();
    });

    function fetchNewWord() {
        let display = document.getElementById('word-display');
        let sentenceDisplay = document.getElementById('sentence-display');  // Assuming you'll have a dedicated element for the sentence
        let endpoint = '/get-random-word' + '?mode=' + currentMode;

        fetch(endpoint)
            .then(response => response.json())
            .then(data => {
                display.dataset.english = data.english;
                display.dataset.portuguese = data.portuguese;
                display.dataset.wordID = data.wordID; // Store wordId data
                display.dataset.sentence = data.sentence; // Store sentence data

                display.textContent = data.english;
                sentenceDisplay.textContent = ''; // Clear sentence initially
            })
            .catch(error => {
                console.error('There was an error fetching the word:', error);
            });
    }

    function markWordAsDifficult() {
        let display = document.getElementById('word-display');
        let currentWordId = display.dataset.wordID; // Assuming you've stored the wordId in the dataset

        // Skip if there's no word displayed
        if (!currentWordId) return;

        // Call backend endpoint to add wordId to difficult_words.csv
        fetch('/mark-as-difficult', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ wordID: currentWordId })
        })
            .then(response => response.json())
            .then(data => {
                // Maybe display a message that word was added successfully
                if (data.status === "success") {
                    console.log("Word marked as difficult");
                } else {
                    console.error("There was an error marking the word as difficult:", data.message);
                }
            })
            .catch(error => {
                console.error('There was an error:', error);
            });
    }


    document.getElementById('flip-btn').addEventListener('click', function () {
        let display = document.getElementById('word-display');
        let sentenceDisplay = document.getElementById('sentence-display');

        if (display.textContent === "Press 'Enter' to start!" || !display.dataset.english) {
            fetchNewWord();
        } else {
            if (display.textContent === display.dataset.english) {
                display.textContent = display.dataset.portuguese;
                sentenceDisplay.textContent = display.dataset.sentence;  // Show the sentence
            } else {
                display.textContent = display.dataset.english;
                sentenceDisplay.textContent = '';  // Clear the sentence when showing English word
            }
        }
    });

    // Event listener for the next button
    document.getElementById('next-btn').addEventListener('click', function () {
        fetchNewWord();
    });

    // Event listener for the right arrow key
    document.addEventListener('keydown', function (event) {
        if (event.code === "ArrowRight") {
            fetchNewWord();
        } else if (event.code === "ArrowDown") {
            // Trigger the flip button's click event
            document.getElementById('flip-btn').click();
        } else if (event.code === "Enter") {
            markWordAsDifficult();
        }
    });


});
