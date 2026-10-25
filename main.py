import securescaffold
import os
from seed_database import insert_ghost_names, insert_dummy_users
from google.cloud import ndb
from flask import jsonify, url_for, session, redirect, abort, request, render_template
from models import Ghost, User, update_ghost_name
from authlib.integrations.flask_client import OAuth
from authlib.integrations.base_client.errors import OAuthError
from dotenv import load_dotenv
import random

load_dotenv()

app = securescaffold.create_app(__name__)
client = ndb.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
oauth = OAuth(app)

# insert_ghost_names(client)
# insert_dummy_users(client)

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
    if not os.environ.get("GOOGLE_CLIENT_ID") or not os.environ.get(
        "GOOGLE_CLIENT_SECRET"
    ):
        return abort(503, "Google authentication is not configured")
    redirect_uri = url_for("auth", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.get("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("form"))


@app.get("/auth")
def auth():
    try:
        token = oauth.google.authorize_access_token()
    except OAuthError:
        return abort(401, "Google authentication failed")

    user_info = token.get("userinfo")
    if not user_info or not user_info.get("sub"):
        return abort(401, "Google profile is incomplete")

    session["user"] = {
        "sub": user_info["sub"],
        "email": user_info.get("email", ""),
        "name": user_info.get("name", ""),
    }
    return redirect("/")


@app.get("/")
def index():
    auth_user = session.get("user")

    with client.context():
        ghosts = Ghost.query().fetch()
        owner_keys = [
            ndb.Key(User, ghost.owner_user_id)
            for ghost in ghosts
            if ghost.owner_user_id
        ]
        owners = {
            user.key.id(): user
            for user in ndb.get_multi(owner_keys)
            if user is not None
        }

        allocated = [
            {
                "ghost_name": ghost.ghost_name,
                "description": ghost.description,
                "first_name": owners[ghost.owner_user_id].first_name,
                "last_name": owners[ghost.owner_user_id].last_name,
                "email": owners[ghost.owner_user_id].email,
            }
            for ghost in ghosts
            if ghost.owner_user_id in owners
        ]

        current_user = None
        if auth_user:
            current_user = ndb.Key(User, auth_user["sub"]).get()

    return render_template(
        "index.html",
        ghosts=allocated,
        user=auth_user,
        has_ghost=bool(current_user and current_user.ghost_key),
    )


@app.get("/form")
def form():
    user = session.get("user")
    return render_template("form.html", user=user, name=("", ""))


@app.post("/form")
def ghosts():
    user = session.get("user")
    if not user:
        return abort(401)

    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    if not first_name or not last_name:
        return abort(400, "First and last name are required")

    with client.context():
        available = Ghost.query(Ghost.owner_user_id == None).fetch()
        options = [
            ghost.ghost_name
            for ghost in random.sample(available, min(3, len(available)))
        ]

        session["ghost_options"] = options
        session["ghost_name"] = [first_name, last_name]

        return render_template(
            "form.html",
            user=user,
            ghosts=options,
            name=(first_name, last_name),
            available_count=len(available),
        )


@app.post("/ghost")
def ghost():
    selected = request.form.get("ghost")
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()

    if not selected or not first_name or not last_name:
        return abort(400, "No name selected")

    user = session.get("user")
    if not user:
        return abort(401)

    expected_name = session.pop("ghost_name", [])
    if [first_name, last_name] != expected_name:
        return abort(400, "The form has expired")

    if selected not in session.pop("ghost_options", []):
        return abort(400, "Invalid or expired ghost name")

    user_id = user["sub"]

    with client.context():
        try:
            update_ghost_name(
                user_id,
                selected,
                first_name,
                last_name,
                user.get("email", ""),
            )
        except ValueError as error:
            return abort(409, str(error))

    return redirect(url_for("index"))
