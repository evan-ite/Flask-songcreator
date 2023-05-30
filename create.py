"""
Document to create all data and tables from models.py

By: Elise van Iterson
"""

import os

from flask import Flask
from models import *

# set the DATABASE_URL environment variable
os.environ["DATABASE_URL"] = "postgresql://localhost/songs"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():
    db.create_all()

if __name__ == "__main__":
    with app.app_context():
        main()
