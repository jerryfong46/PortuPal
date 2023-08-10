document.addEventListener('DOMContentLoaded', function () {

    // Variables
    let currentMode = 'learn';

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
                display.dataset.sentence = data.sentence; // Store sentence data

                display.textContent = data.english;
                sentenceDisplay.textContent = ''; // Clear sentence initially
            })
            .catch(error => {
                console.error('There was an error fetching the word:', error);
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
        }
    });

    const tabs = document.querySelectorAll('.tab-link');
    tabs.forEach(tab => {
        tab.addEventListener('click', function (event) {
            event.preventDefault();

            // Remove 'selected' class from all tabs
            tabs.forEach(innerTab => innerTab.classList.remove('selected'));

            // Add 'selected' class to the clicked tab
            tab.classList.add('selected');
        });
    });

});
