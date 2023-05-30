"""
Document with functions to support app.py

by: Elise van Iterson
"""

import json
import openai
from models import *
from flask import session, redirect, flash
from functools import wraps
from fpdf import FPDF


def create_song(key, genre, mood, subject):
  """ Transforms input into ChatGPT promt and returns chords and song lyrics. """

  # Prompt for the openai API.
  prompt = ("I will provide you with one chord, a mood and a music genre. "
           "You will then write a chord progression in the key of the given chord, matching the mood and in the style of the provided music genre."
           "Secondly, I want you to write a lyrics matching the chords, matching the genre and matching the mood. "
           "I'll provide you with a subject for the lyrics. "
           "Lastly, the output should only be in JSON format, don't add any text. The structure of the JSON data should be as follows; "
           "{title:..., subject:..., key:..., genre:..., mood:..., chords:..., lyrics: [{line:..., chord:...}, ...]}"
           f'My first request is: Write a {genre} chord progression in {key}, in a {mood} mood and a lyrics about {subject}.')

  # COmmunicate with openai API.
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
          {"role": "system", "content": "You are a music composer and a songwriter."},
          {"role": "user", "content": prompt}
      ]
  )
  return response['choices'][0]['message']['content']


def save(data, save_to_user: bool):
  """ Save created song into database. Input is a song in JSON format.
  The output is a song id if song is succesfully saved. """

  # Check if song was already saved.
  if type(data) is Song:
    song = data

    if save_to_user:
      # Update the user_id field of the song object with the new user_id
      song.user_id = session["user_id"]

      # Save the changes to the database
      db.session.commit()

    else:
       flash("Something went wrong, we couldn't save your song", "error")

    return song.id

  # If song was not previously saved.
  elif type(data) is str:

    # Convert data to JSON.
    song = json.loads(data)

    # Save a chord list from JSON data
    chords = ""
    for chord in song["chords"]:
      chords += chord

    # Save lyrics from JSON data
    lyrics = ""
    for line in song["lyrics"]:
      lyrics += line["line"] + " "

    data = json.dumps(song)

    if save_to_user:
      # Set user id to session id.
      user_id = session.get("user_id")
    else:
      user_id = None

    # create a new song instance.
    new_song = Song(title=song["title"],key=song["key"], genre=song["genre"], mood=song["mood"], subject=song["subject"],
                  chords=chords, lyrics=lyrics, json_data=data, user_id=user_id)

    # add the new song to the database and commit the changes.
    db.session.add(new_song)
    db.session.commit()

    return new_song.id

  else:
    return None


def delete(song_id):
  """ Delete song from database, returns True if song is succesfully deleted """

  # Check if a song with the given id exists in the database.
  song = Song.query.get(song_id)

  if song:
    # If song exists, delete from database.
    db.session.delete(song)
    db.session.commit()
    return True

  else:
    return False


def create_file(song):
  """Creates a PDF file from the inputted song dictionary. """

  # Load data to json.
  song = json.loads(song)

  # Create single chord string.
  chords = " ".join(song["chords"]) + "\n"

  filepath = f"song_files/mysong.pdf"
  filename = f"mysong.pdf"

  # Create a new PDF object
  pdf = FPDF()

  # Set the margins (left, top, right)
  pdf.set_margins(20, 20, 20)

  # Add a page to the PDF
  pdf.add_page()

  # Write the content to the PDF page
  pdf.image("static/images/logo_black.png" , x=10, y=10, h=20)
  pdf.ln(30)  # Add a blank line
  pdf.set_font("Helvetica", '', size=11) # Reset font to normal
  pdf.cell(0, 10 ,txt=f"Key: {song['key']}", ln=True)
  pdf.cell(0, 10, txt=f"Genre: {song['genre']}", ln=True)
  pdf.cell(0, 10, txt=f"Mood: {song['mood']}", ln=True)
  pdf.cell(0, 10, txt=f"All chords: {chords}", ln=True)
  pdf.ln(10)  # Add a blank line
  pdf.set_font('Helvetica', 'B', size=14) # Set the font
  pdf.cell(0, 10, txt=song['title'], ln=True, align='C')
  pdf.ln(5)  # Add a blank line
  for element in song["lyrics"]:
      pdf.set_font("Helvetica", '', size=12) # Reset font to normal
      pdf.cell(0, 10, txt=element["chord"], ln=True)
      pdf.set_font('Helvetica', 'I', 12)  # Set font to italic
      pdf.cell(0, 10, txt=element["line"], ln=True)

  # Save the PDF file
  pdf.output(filepath)

  return {"path": filepath, "filename": filename}


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

