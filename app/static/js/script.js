document.addEventListener('DOMContentLoaded', function () {

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
                display.dataset.eng_sentence = data.eng_sentence;  // Set the English sentence
                display.dataset.port_sentence = data.port_sentence;  // Set the Portuguese sentence

                display.textContent = data.english;
                sentenceDisplay.textContent = data.eng_sentence;
                // sentenceDisplay.textContent = ''; // Clear sentence initially
            })
            .catch(error => {
                console.error('There was an error fetching the word:', error);
            });
    }

    function markWordAsDifficult() {
        let display = document.getElementById('word-display');
        let currentWordId = display.dataset.wordID; // Assuming you've stored the wordId in the dataset
        let currentWord = display.textContent;

        // Show alert
        showAlert(currentWord);

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

    function showAlert(word) {
        let customAlert = document.getElementById('customAlert');

        // Update the alert message with the word
        customAlert.innerHTML = `<strong>${word.toUpperCase()}</strong> added to difficult words!`;

        // Remove hidden class to display the alert
        customAlert.classList.remove('hidden');

        // Use setTimeout to add the hidden class after 0.5 seconds
        setTimeout(() => {
            customAlert.classList.add('hidden');
        }, 1000);
    }

    document.getElementById('flip-btn').addEventListener('click', function () {
        let display = document.getElementById('word-display');
        let sentenceDisplay = document.getElementById('sentence-display');

        if (display.textContent === "Press 'Enter' to start!" || !display.dataset.english) {
            fetchNewWord();
        } else {
            if (display.textContent === display.dataset.english) {
                display.textContent = display.dataset.portuguese;
                sentenceDisplay.textContent = display.dataset.port_sentence;  // Show the Portuguese sentence
            } else {
                display.textContent = display.dataset.english;
                sentenceDisplay.textContent = display.dataset.eng_sentence;  // Show the English sentence
            }
        }
    });


    // Event listener for the next button
    document.getElementById('next-btn').addEventListener('click', function () {
        fetchNewWord();
    });

});
