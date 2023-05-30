// Javascript file to accompany the flask app
// this code implements the download button for generated songs.

document.addEventListener("DOMContentLoaded", function(event) {
    const button = document.querySelector(".download-button");
    const song_id = SONG_ID;

    async function downloadSong(song_id) {
        try {
            const response = await fetch("/download", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ id: song_id }),
            });
            if (response.ok) {
                const blob = await response.blob();

                // Create a temporary URL for the downloaded file
                const url = URL.createObjectURL(blob);

                // Create a temporary link element to initiate the download
                const link = document.createElement("a");
                link.href = url;
                link.download = "mysong.pdf";

                // Simulate a click on the link to start the download
                link.click();

                // Clean up the temporary URL
                URL.revokeObjectURL(url);
            } else {
                throw new Error("Failed to download file");
            }
        } catch (error) {
            console.error("Error:", error);
        }
    }

    button.addEventListener("click", function(event) {
        if (LOGGED_IN) {
            downloadSong(song_id);
        }
        else {
            window.location.href = '/login';
        }

    });
});
