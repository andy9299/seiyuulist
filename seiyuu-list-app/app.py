from flask import Flask, request, redirect, render_template, flash, session, jsonify, g
from flask_debugtoolbar import DebugToolbarExtension
import os
import requests
import random
import time

CURR_USER_KEY = "curr_user"
BASE_URL = "https://api.jikan.moe/v4"
WAIT_TIME = .5

app = Flask(__name__)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "qwerty")

debug = DebugToolbarExtension(app)


def get_info_from_show_data(data):
    """Given a response from jikanapi at /seasons extract the ids form the first page (25)"""
    genres = []
    for genre in data.get("genres"):
        genres.append(genre.get("name"))
    return {
        "id": data.get("mal_id"),
        "image_url": data.get("images").get("jpg").get("image_url"),
        "title": data.get("title"),
        "synopsis": data.get("synopsis"),
        "rating": data.get("rating"),
        "genres": genres,
        "type": data.get("type"),
    }


def get_info_from_characters_data(data, role=None):
    """
    Given a response from jikanapi that has a list of characters grab the characters' info
    role is used to specify the role of the character either with 'main' (Main roles), or 'supporting' (Supporting roles).
    Not specifying type will grab all the characters.
    """
    characters = []
    for character in data:
        if role[0] == None or character.get("role").lower() == role.lower():
            curr_character = character.get("character")
            character_info = {
                "character_id": curr_character.get("mal_id"),
                "character_name": curr_character.get("name"),
                "character_image_url": curr_character
                .get("images")
                .get("jpg")
                .get("image_url"),
                "role": character.get("role"),
            }
            if character.get("voice_actors") is not None and character.get(
                "voice_actors"
            ):
                voice_actor = character.get("voice_actors")[0]
                character_info["seiyuu_id"] = (
                    voice_actor.get("person").get("mal_id")
                )
                character_info["seiyuu_name"] = (
                    voice_actor.get("person").get("name")
                )
                character_info["seiyuu_image_url"] = (
                    voice_actor
                    .get("person")
                    .get("images")
                    .get("jpg")
                    .get("image_url")
                )
            if character.get("anime") is not None:
                character_info["title"] = character.get("anime").get("title")
                character_info["anime_id"] = character.get("anime").get("mal_id")
            characters.append(character_info)
    return characters


def get_info_from_person_data(person):
    """
    Given a response from jikanapi that has information about a person grab their info.
    """
    return {
        "id": person.get("mal_id"),
        "name": person.get("name"),
        "jp_name": person.get("family_name") + " " + person.get("given_name"),
        "image_url": person.get("images").get("jpg").get("image_url"),
        "about": person.get("about"),
        "birthday": person.get("birthday"),
        "website_url": person.get("website_url"),
    }

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        # get user later and add to flask global g
        return

    else:
        g.user = None


@app.route("/")
def root():
    """Homepage."""
    seasonals_req = requests.get(f"{BASE_URL}/seasons/now").json()
    anime_info = get_info_from_show_data(random.choice(seasonals_req.get("data")))
    all_seasonals = []
    page = 1
    while True:
        # to prevent rate limiting
        time.sleep(WAIT_TIME)
        for show in seasonals_req.get("data"):
            all_seasonals.append(
                {
                    "id": show.get("mal_id"),
                    "image_url": show.get("images").get("jpg").get("image_url"),
                    "title": show.get("title"),
                }
            )
        page += 1
        seasonals_req = requests.get(
            f"{BASE_URL}/seasons/now", params={"page": page}
        ).json()
        if not seasonals_req.get("pagination").get("has_next_page"):
            break

    characters_req = requests.get(
        f"{BASE_URL}/anime/{anime_info.get('id')}/characters"
    ).json()
    characters_info = get_info_from_characters_data(characters_req.get("data"), "main")

    return render_template(
        "home.html",
        anime_info=anime_info,
        characters_info=characters_info,
        all_seasonals=all_seasonals,
    )


@app.route("/person/<int:person_id>")
def person_info(person_id):
    """View information about a person"""

    person_req = requests.get(f"{BASE_URL}/people/{person_id}/full").json()
    info = get_info_from_person_data(person_req.get("data"))
    main_roles = get_info_from_characters_data(person_req.get("data").get("voices"), "main")
    sup_roles = get_info_from_characters_data(
        person_req.get("data").get("voices"), "supporting"
    )

    return render_template(
        "person.html", info=info, main_roles=main_roles, sup_roles=sup_roles
    )


@app.route("/anime/<int:anime_id>")
def anime_info(anime_id):
    """View information about an anime"""

    anime_req = requests.get(f"{BASE_URL}/anime/{anime_id}/full").json()
    info = get_info_from_show_data(anime_req.get("data"))

    characters_req = requests.get(f"{BASE_URL}/anime/{anime_id}/characters").json()
    main_characters = get_info_from_characters_data(characters_req.get("data"), "main")
    sup_characters = get_info_from_characters_data(characters_req.get("data"), "supporting")
    return render_template(
        "anime.html", info=info, main_characters=main_characters, sup_characters=sup_characters
    )
