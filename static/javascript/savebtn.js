// Javascript file to accompany the flask app
// this code implements the save/delete button for generated songs.

document.addEventListener("DOMContentLoaded", function(event) {
    const button = document.querySelector(".save-button");

    const data = { id: SONG_ID };

    async function save_song(data) {
        try {
            const response = await fetch("/save-song", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
            });

            const result = await response.json();
            id = result.id
            button.innerHTML = "<img class='delete-icon' src='../static/images/delete.png' alt='Delete Song'>";
        } catch (error) {
            console.error("Error:", error);
        }
    }

    async function delete_song(data) {
        try {

            const response = await fetch("/delete-song", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
            });

            const result = await response.json();
            button.innerHTML = "<img class='save-icon' src='../static/images/save.png' alt='Save Song'>";
        } catch (error) {
            console.error("Error:", error);
        }
    }

    button.addEventListener("click", function(event) {
        if (LOGGED_IN) {
            if (button.querySelector(".save-icon")) {
                save_song(data);
            }
            else {
                delete_song(data);
            }
        }
        else {
            window.location.href = '/login';
        }
    });
})
