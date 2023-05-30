// Javascript file to accompany the flask app
// this code implements a loading spinner while the API is running.

document.addEventListener("DOMContentLoaded", function(event) {
    document.querySelector(".spinner").style.display = "none";
    document.querySelector(".spinner-spacer").style.display = "none";
    const button = document.querySelector("#create-btn");

    button.addEventListener("click", function(event) {

        document.querySelector(".spinner").style.display = "flex";
        document.querySelector(".spinner-spacer").style.display = "block";
        document.querySelector(".form-body").style.display = "none";

    });

})

