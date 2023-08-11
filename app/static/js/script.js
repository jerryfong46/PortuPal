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


    var ctx = document.getElementById('myChart').getContext('2d');

    // Sample data
    var dates = ["2023-08-01", "2023-08-02", "2023-08-03"];  // X-axis data
    var learnedWords = [5, 10, 15];  // Y-axis data

    var chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Total Learned Words',
                data: learnedWords,
                fill: false,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.3  // This gives the soft curves
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day',
                        displayFormats: {
                            day: 'MMM D'
                        }
                    }
                },
                y: {
                    beginAtZero: true
                }
            }
        }
    });


});
