document.addEventListener('DOMContentLoaded', function () {

    document.getElementById("new-story-btn").addEventListener("click", function () {
        const selectedGenre = document.getElementById("story-type").value;

        fetch('/generate_story', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                genre: selectedGenre
            })
        })
            .then(response => response.json())
            .then(data => {
                // document.getElementById("english-story").textContent = data.english_story;
                // document.getElementById("portuguese-story").textContent = data.portuguese_story;
                document.getElementById("english-story").innerHTML = data.english_story.replace(/\n/g, '<br>');
                document.getElementById("portuguese-story").innerHTML = data.portuguese_story.replace(/\n/g, '<br>');
            });
    });

    document.getElementById('continue-btn').addEventListener('click', function () {
        const selectedGenre = document.getElementById("story-type").value;
        // let currentStory = document.getElementById('english-story').textContent;
        let currentStory = document.getElementById('english-story').innerHTML.replace(/<br\s*\/?>/mg, '\n');


        // Construct the request body
        let requestData = {
            story: currentStory,
            genre: selectedGenre
        };

        fetch('/continue-story', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
            .then(response => response.json())
            .then(data => {
                // Update the story on the page or handle the returned data
                // document.getElementById('english-story').textContent = data.english_story;
                // document.getElementById("portuguese-story").textContent = data.portuguese_story;
                document.getElementById("english-story").innerHTML = data.english_story.replace(/\n/g, '<br>');
                document.getElementById("portuguese-story").innerHTML = data.portuguese_story.replace(/\n/g, '<br>');

            })
            .catch(error => {
                console.error('There was an error:', error);
            });
    });

});