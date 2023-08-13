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
                document.getElementById("english-story").textContent = data.english_story;
                document.getElementById("portuguese-story").textContent = data.portuguese_story;
            });
    });

});