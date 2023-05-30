"""
Flask app that let's users generate songs and then download and save them.

by: Elise van Iterson
"""

from dotenv import load_dotenv
load_dotenv()

import os
import json
import time

from flask import Flask, session, redirect, render_template, request, send_file, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash


from models import *
from helpers import *


app = Flask(__name__)
app.debug = True

# Configure the Flask app from .env file
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")

# Initialize the SQLAlchemy instance with the Flask app
db.init_app(app)

# set open api key
openai.api_key = os.getenv("API_KEY")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

@app.route("/")
def index():
    """ Render the homepage, let user fill in form to create a song. """

    # List of keys for user to choose from.
    keys = ["A", "B","C", "D", "E", "F", "G", "Am", "Bm", "Cm", "Dm", "Em", "Fm",
            "Gm", "F#/Gb", "C#/Db", "Ab", "Eb", "Bb", "F#m/Gbm", "C#m/Dbm", "G#m",
            "D#m/Ebm", "A#m/Bbm"]

    # List of genres for user to choose from.
    genres = ["Pop", "HipHop", "Country", "R&B", "Jazz", "Soul", "Rock", "Blues", "Indie Rock",
              "Raggae", "EDM", "Heavy Metal", "Bossa Nova", "Folk", "Funk"]

    return render_template("index.html", keys=keys, genres=genres)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username, password and confirmation are submitted
        if not request.form.get("username") or \
           not request.form.get("password") or \
           not request.form.get("confirmation"):
            flash("Please provide a username, password and password confirmation", "error")
        else:
            username = request.form.get("username")

            # Query database for username
            user = User.query.filter_by(username=username).all()

            # Ensure username doesn't exist and password is correct
            if len(user) > 0:
                flash("This username already exists", "error")
            elif request.form.get("password") != request.form.get("confirmation"):
                flash("Password validation went wrong, please try again", "error")
            else:
                password = generate_password_hash(request.form.get("password"))

                # Add user to user database
                new_user = User(username=username, hashed=password)
                db.session.add(new_user)
                db.session.commit()

                # Create new session
                session["user_id"] = new_user.id

                # Redirect user to home page
                return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username") or not request.form.get("password"):
            flash("Please provide a username and password", "error")
        else:
            username = request.form.get("username")
            password = request.form.get("password")

            # Query database for username
            user = User.query.filter_by(username=username).first()
            print(user)

            # Ensure username exists and password is correct
            if not user or not check_password_hash(user.hashed, password):
                flash("Please provide a valid username and/or password", "error")
            else:
                # Remember which user has logged in
                session["user_id"] = user.id

                # Redirect user to home page
                return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/create", methods=["GET", "POST"])
def create():
  """ Function that connects with API to generate a song according to
      users input. """

  if request.method == "GET":
    # Render index if user uses get method.
    return render_template("index.html")

  else:
    # Obtain user input from form.
    key = request.form.get("key")
    genre = request.form.get("genre")
    mood = request.form.get("mood")
    subject = request.form.get("subject")

    # Create song with openai API.
    json_song = create_song(key, genre, mood, subject)

    # # Use this code if you want to test the app without API key
    # time.sleep(5)

    # file_path = 'test/test_output3.txt'

    # with open(file_path, 'r') as file:
    #     json_song = file.read()

    # Load song into json format
    song = json.loads(json_song)

    # Save song to database.
    song_id = save(json_song, False)

    return render_template("created.html", song=song, song_id=song_id)


@app.route("/save-song", methods=(["POST"]))
@login_required
def save_song():
    """ Saves generated song to database. """

    # Get song id.
    data = request.get_json()
    song_id = data["id"]

    # Query database for song and save.
    song = Song.query.get(song_id)
    new_id = save(song, True)

    if id:
        return {"saved": True, "id" : new_id}
    else:
        return {"saved": False, "id": None}


@app.route("/delete-song", methods=(["POST"]))
@login_required
def delete_song():
    """ Deletes generated song from database. """

    # Get song data.
    song = request.get_json()

    if delete(song["id"]):
        # Song is deleted.
        return {"deleted": True}
    else:
        # Song is not deleted.
        return {"deleted": False}


@app.route("/download", methods=(["GET","POST"]))
@login_required
def download():
    """ Let's user download their generated song. """

    # Get song data.
    data = request.get_json()
    song_id = data["id"]

    # Query database for song.
    song = Song.query.get(song_id)

    # Create PDF file
    file_created = create_file(song.json_data)

    return send_file(file_created["path"], as_attachment=True)


@app.route("/mysongs", methods=["GET"])
@login_required
def mysongs():
    """ Let's user see all their saved songs. """

    # Query database for all songs from user.
    my_songs = Song.query.filter_by(user_id=session["user_id"]).all()

    return render_template("mysongs.html", my_songs=my_songs)


@app.route("/song/<id>", methods=["GET"])
@login_required
def song(id):
    """ Show saved song. """

    # Find song in database.
    song_query = Song.query.get(id)

    if not song_query:
        # if song doesn't exist, return error
        return "No song found"

    # Convert data to json.
    json_song = song_query.json_data
    song = json.loads(json_song)

    return render_template("songpage.html", song=song, song_id=id)


@app.route("/about")
def about():
    """ Information about the website. """

    return render_template("about.html")


@app.route("/contact")
def contact():
    """ Contact information. """

    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)