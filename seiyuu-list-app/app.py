from flask import Flask, request, redirect, render_template, flash, session, jsonify, g, url_for
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


def get_info_from_anime_data(anime_data):
    """Given a response from jikanapi about an anime, extract the data"""
    genres = []
    if anime_data.get('genres'):
        for genre in anime_data.get("genres"):
            genres.append(genre.get("name"))
    return {
        "id": anime_data.get("mal_id"),
        "image_url": anime_data.get("images").get("jpg").get("image_url"),
        "title": anime_data.get("title"),
        "synopsis": anime_data.get("synopsis"),
        "rating": anime_data.get("rating"),
        "genres": genres,
        "type": anime_data.get("type"),
    }


def get_info_by_role(data, type, role=None):
    """
    Given a response from jikanapi that has a list of characters/anime
    filter the list by role with 'main' (Main roles), 
    or 'supporting' (Supporting roles).
    Not specifying type will grab all the characters.
    """
    info = []
    if type.lower() == "character":
        for character in data:
            if role == None or character.get("role").lower() == role.lower():
                character_info = get_info_from_character_data(character)
                info.append(character_info)

    elif type.lower() == "anime":
        for anime in data:
            if role == None or anime.get("role").lower() == role.lower():
                anime_info = get_info_from_anime_data(anime.get('anime'))
                info.append(anime_info)
    return info

def get_info_from_character_data(character_data):
    """
    Given a response from jikanapi with information on one character
    grab the characters info
    """
    # when getting information about characters from the jikanApi depending on 
    # where it is requested there could be a lot of varying nested/named data

    # requested from /anime/ or /people/
    if character_data.get("character"):
        curr_character = character_data.get("character")
        voice_actor = "voice_actors"
    # requested from /characters/
    else:
        curr_character = character_data
        voice_actor = "voices"

    character_info = {
        "character_id": curr_character.get("mal_id"),
        "character_name": curr_character.get("name"),
        "character_image_url": curr_character
        .get("images")
        .get("jpg")
        .get("image_url"),
        "role": character_data.get("role"),
        'about': character_data.get('about')
    }

    # some characters have no voice actors
    if character_data.get(voice_actor) is not None and character_data.get(voice_actor):
        voice_actor_index = 0
        for i, dict in enumerate(character_data.get(voice_actor)):
            if dict['language'] == 'Japanese':
                voice_actor_index = i
                break
        voice_actor = character_data.get(voice_actor)[voice_actor_index]
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

    # check if it is from /characters if it is we need every anime instead of 1 so we dont need this
    if character_data.get("anime") is not None and not isinstance(character_data.get("anime"), list):
        character_info["title"] = character_data.get("anime").get("title")
        character_info["anime_id"] = character_data.get("anime").get("mal_id")
    return character_info

def get_info_from_person_data(person_data):
    """
    Given a response from jikanapi that has information about a person 
    breakdown their information
    """
    jp_name = ""
    if person_data.get("family_name") is not None:
        jp_name += (person_data.get("family_name") + " ")
    if person_data.get("given_name") is not None:
        jp_name += person_data.get("given_name")
    jp_name = jp_name.strip()
    return {
        "id": person_data.get("mal_id"),
        "name": person_data.get("name"),
        "jp_name": jp_name,
        "image_url": person_data.get("images").get("jpg").get("image_url"),
        "about": person_data.get("about"),
        "birthday": person_data.get("birthday"),
        "website_url": person_data.get("website_url"),
    }

def get_jikan_request(url, params=None):
    """Function to handle jikan requests"""

    request = requests.get(f"{BASE_URL}{url}", params).json()
    if 'error' in request:
        # This means there isn't the correct data in the api request
        raise KeyError
    return request

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
    try:
        seasonals_req = get_jikan_request("/seasons/now")
        anime_info = get_info_from_anime_data(random.choice(seasonals_req.get("data")))
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
            seasonals_req = get_jikan_request("/seasons/now", {"page": page})
            if not seasonals_req.get("pagination").get("has_next_page"):
                break

        characters_req = get_jikan_request(f"/anime/{anime_info.get('id')}/characters")
        characters_info = get_info_by_role(characters_req.get("data"), "character", "main")
        return render_template(
            "home.html",
            anime_info=anime_info,
            characters_info=characters_info,
            all_seasonals=all_seasonals,
        )

    except KeyError:
        flash("Something went wrong with the api request!")
        return render_template("home.html")


@app.route("/person/<int:person_id>")
def person_info(person_id):
    """View information about a person"""

    try:
        person_req = get_jikan_request(f"/people/{person_id}/full")
        info = get_info_from_person_data(person_req.get("data"))
        main_roles = get_info_by_role(person_req.get("data").get("voices"), "character", "main")
        sup_roles = get_info_by_role(person_req.get("data").get("voices"), "character", "supporting")

        return render_template(
            "person.html", info=info, main_roles=main_roles, sup_roles=sup_roles
        )

    except KeyError:
        flash("Something went wrong with the api request!")
        return redirect(url_for('root'))


@app.route("/anime/<int:anime_id>")
def anime_info(anime_id):
    """View information about an anime"""
    try:
        anime_req = get_jikan_request(f"/anime/{anime_id}/full")
        info = get_info_from_anime_data(anime_req.get("data"))

        characters_req = get_jikan_request(f"/anime/{anime_id}/characters")
        main_characters = get_info_by_role(characters_req.get("data"), "character", "main")
        sup_characters = get_info_by_role(characters_req.get("data"), "character", "supporting")
        return render_template(
            "anime.html", info=info, main_characters=main_characters, sup_characters=sup_characters
        )

    except KeyError:
        flash("Something went wrong with the api request!")
        return redirect(url_for('root'))

@app.route("/character/<int:character_id>")
def character_info(character_id):
    """View information about a character"""
    try:
        character_req = get_jikan_request(f"/characters/{character_id}/full")
        character_info = get_info_from_character_data(character_req.get('data'))
        main_character_anime = get_info_by_role(character_req.get('data').get('anime'), 'anime', 'main')
        sup_character_anime = get_info_by_role(character_req.get('data').get('anime'), 'anime', 'supporting')

        return render_template(
            "character.html", 
            character_info=character_info, main_character_anime=main_character_anime, sup_character_anime=sup_character_anime
            )

    except KeyError:
        flash("Something went wrong with the api request!")
        return redirect(url_for('root'))

@app.route("/search/")
def search():
    """Handle Searching"""
    try:
        type = request.args.get('type')
        query = request.args.get('q')
        page = request.args.get('p')
        search_req = get_jikan_request(f"/{type}/", {'q': query, 'page': page, 'sort': 'desc', 'order_by': 'favorites'})
        pages = search_req.get('pagination').get('last_visible_page')
        results = []

        if type == 'anime':
            for anime in search_req.get('data'):
                results.append(get_info_from_anime_data(anime))
        elif type == 'people':
            for person in search_req.get('data'):
                results.append(get_info_from_person_data(person))
        elif type == 'characters':
            results = get_info_by_role(search_req.get('data'), 'character')

        return render_template("search.html", results=results, pages=pages)

    except KeyError:
        flash("Something went wrong with the api request!")
        return redirect(url_for('root'))
