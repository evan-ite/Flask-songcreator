"""
Document to initialize all data and tables for app.py

By: Elise van Iterson
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Song(db.Model):
    __tablename__ = "songs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    key = db.Column(db.String, nullable=False)
    genre = db.Column(db.String, nullable=False)
    mood = db.Column(db.String, nullable=False)
    subject = db.Column(db.String, nullable=False)
    chords = db.Column(db.String, nullable=False)
    lyrics = db.Column(db.String, nullable=False)
    json_data = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String, nullable=False)
    hashed = db.Column(db.String, nullable=False)


