from flask import Flask, request, redirect, render_template, flash, session, jsonify, g
from flask_debugtoolbar import DebugToolbarExtension
import os
import requests
import random

CURR_USER_KEY = "curr_user"
BASE_URL = "https://api.jikan.moe/v4"

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'qwerty')

debug = DebugToolbarExtension(app)

def get_info_from_show_data(data):
    """Given a response from jikanapi at /seasons extract the ids form the first page (25)"""
    genres = []
    for genre in data.get('genres'):
        genres.append(genre.get('name'))
    return {
        'id': data.get('mal_id'),
        'image_url': data.get('images').get('jpg').get('image_url'),
        'title': data.get('title'),
        'synopsis': data.get('synopsis'),
        'rating': data.get('rating'),
        'genres': genres,
        'type': data.get('type')
    }

def get_info_from_charas_data(data, *role):
    """
    Given a response from jikanapi at /anime/{id}/characters grab the characters' info
    type is used to specify the role of the character either with 'm' (Main roles), or 's' (Supporting roles).
    Not specifying type will grab all the characters.
    """
    characters = []
    for character in data:
        if (role[0] == None or character.get('role')[0].lower() == role[0]):
            characters.append({
                'chara_id': character.get('mal_id'),
                'chara_name': character.get('character').get('name'),
                'chara_image_url': character.get('character').get('images').get('jpg').get('image_url'),
                'role': character.get('role'),
                'seiyuu_id': character.get('voice_actors')[0].get('mal_id'),
                'seiyuu_name': character.get('voice_actors')[0].get('name'),
                'seiyuu_image_url': character.get('voice_actors')[0].get('person').get('images').get('jpg').get('image_url')
            })
    return characters

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        #get user later and add to flask global g
        return

    else:
        g.user = None

@app.route("/")
def root():
    """Homepage."""

    seasonals_req = requests.get(f"{BASE_URL}/seasons/now").json()
    show_info = get_info_from_show_data(random.choice(seasonals_req.get('data')))
    charas_req = requests.get(f"{BASE_URL}/anime/{show_info.get('id')}/characters").json()
    charas_info = get_info_from_charas_data(charas_req.get('data'), 'm')
    return render_template('home.html')