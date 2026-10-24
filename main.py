import securescaffold
import os
from insert_ghost_names import insert_ghost_names
from google.cloud import ndb
from flask import jsonify, url_for, session, redirect, abort, request, render_template
from models import Ghost, User, update_ghost_name
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import random

load_dotenv()

app = securescaffold.create_app(__name__)
client = ndb.Client()
oauth = OAuth(app)

CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"
google = oauth.register(
    name="google",
    server_metadata_url=CONF_URL,
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    client_kwargs={"scope": "openid email profile"},
)


@app.get("/login")
def login():
    redirect_uri = url_for("auth", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.get("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


@app.get("/auth")
def auth():
    token = oauth.google.authorize_access_token()
    session["user"] = token["userinfo"]
    return redirect("/")


@app.get("/")
def index():
    user = session.get("user")

    with client.context():
        users = User.query(User.ghost_key > "").fetch()

        ghost_keys = [ndb.Key(Ghost, user.ghost_key) for user in users]
        ghosts = ndb.get_multi(ghost_keys)

        allocated = []
        for user, ghost in zip(users, ghosts):
            if ghost is None:
                continue
            allocated.append(
                {
                    "ghost_name": ghost.ghost_name,
                    "first_name": ghost.first_name,
                    "last_name": ghost.last_name,
                    "email": user.email,
                }
            )

    return render_template("index.html", ghosts=allocated, user=user)


@app.get("/form")
def form():
    user = session.get("user")

    return render_template("form.html", user=user)


@app.post("/form")
def ghosts():
    user = session.get("user")

    with client.context():
        query = Ghost.query()
        ghosts = query.fetch()

        options = []
        while len(options) < 3:
            i = random.randint(0, len(ghosts))
            if ghosts[i].ghost_name in options:
                continue

            options.append(ghosts[i].ghost_name)

        name = (request.form.get("first_name"), request.form.get("last_name"))

        return render_template("form.html", user=user, ghosts=options, name=name)


@app.post("/ghost")
def ghost():
    selected = request.form.get("ghost")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")

    if not selected or not first_name or not last_name:
        return abort(400, "No name selected")

    user = session.get("user")
    if not user:
        return abort(401)

    user_id = user["sub"]

    with client.context():
        try:
            update_ghost_name(user_id, selected, first_name, last_name)
        except Exception as e:
            print(e)
            return abort(500)

    return redirect(url_for("index"))
