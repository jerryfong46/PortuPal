document.addEventListener('DOMContentLoaded', function () {

    const timeframeButton = document.getElementById('timeframe-toggle');

    fetchWordsLearnedData();  // Fetch the words learned data when the page loads

    document.getElementById('timeframe-toggle').addEventListener('click', function () {
        const toggleBtn = document.getElementById('timeframe-toggle');
        if (toggleBtn.innerText === 'All') {
            toggleBtn.innerText = '15';
        } else {
            toggleBtn.innerText = 'All';
        }
        // fetchNewWord();  // Fetch a new word based on the new timeframe
    });

    document.getElementById('learn').addEventListener('click', function () {
        currentMode = 'learn';
        timeframeButton.style.display = 'none';  // Hide the button when in 'Learn' mode
        fetchNewWord();
    });

    document.getElementById('practice').addEventListener('click', function () {
        currentMode = 'practice';
        timeframeButton.style.display = 'block'; // Show the button when in 'Practice' mode
        fetchNewWord();
    });


    // Fetch words learned data from Flask backend
    function fetchWordsLearnedData() {
        fetch('/get-words-learned-data')
            .then(response => response.json())
            .then(data => {
                createChart(data);
            })
            .catch(error => {
                console.error('There was an error fetching the words learned data:', error);
            });
    }

    function createChart(data) {
        const ctx = document.getElementById('wordsLearnedChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',  // This can be a 'bar' type to show bars for daily learned words
            data: {
                labels: data.map(item => item.date),  // Date will be on x-axis
                datasets: [{
                    type: 'line',  // This will force this dataset to be line type
                    label: 'Total Words Learned',
                    data: data.map(item => item.wordsLearned),
                    borderColor: '#007BFF',
                    fill: false,
                    yAxisID: 'y-axis-1'
                }, {
                    type: 'bar', // This will force this dataset to be bar type
                    label: 'Words Learned Daily',
                    data: data.map(item => item.wordsLearnedDay),  // Assuming you have this in your data
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    yAxisID: 'y-axis-2'
                }]
            },
            options: {
                scales: {
                    'y-axis-1': {
                        type: 'linear',
                        position: 'left',
                        beginAtZero: true
                    },
                    'y-axis-2': {
                        type: 'linear',
                        position: 'right',
                        beginAtZero: true,
                        grid: {
                            drawOnChartArea: false  // ensures that the grid lines of this axis don't show up
                        }
                    },
                    x: {
                        type: 'category'
                    }
                }
            }

        });
    }



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
        let timeframe = document.getElementById('timeframe-toggle').textContent; // Get the current value of the toggle

        let endpoint = '/get-random-word' + '?mode=' + currentMode + '&timeframe=' + timeframe;

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

                // Add the logic for displaying "Difficult Word" based on 'is_difficult' field
                if (data.is_difficult) {
                    const indicator = document.createElement('div');
                    indicator.classList.add('difficult-indicator');
                    indicator.textContent = 'Difficult Word';
                    document.querySelector('.flashcard').appendChild(indicator);
                } else {
                    const existingIndicator = document.querySelector('.difficult-indicator');
                    if (existingIndicator) existingIndicator.remove();
                }
            })
            .catch(error => {
                console.error('There was an error fetching the word:', error);
            });
    }

    function markWordAsDifficult() {
        let display = document.getElementById('word-display');
        let currentWordId = display.dataset.wordID; // Assuming you've stored the wordId in the dataset
        let currentWord = display.textContent;

        // Skip if there's no word displayed
        if (!currentWordId) return;

        // Call backend endpoint to toggle word difficulty in difficult_words.csv
        fetch('/toggle-difficulty', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ wordID: currentWordId })
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    if (data.action === "added") {
                        showAlert(`"${currentWord}" was marked as difficult`);
                    } else if (data.action === "removed") {
                        showAlert(`"${currentWord}" was removed from difficult words`);
                    }
                } else {
                    console.error("There was an error toggling the word's difficulty:", data.message);
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
