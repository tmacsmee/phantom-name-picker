import securescaffold
import os
from insert_ghost_names import insert_ghost_names
from google.cloud import ndb
from flask import jsonify, url_for, session, redirect, abort
from models import GhostName
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

load_dotenv()

STATIC_FOLDER = "frontend/dist"

app = securescaffold.create_app(__name__)
app.static_folder = STATIC_FOLDER
app.static_url_path = "/"

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


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    if path and os.path.exists(os.path.join(STATIC_FOLDER, path)):
        return app.send_static_file(path)
    return app.send_static_file("index.html")


@app.route("/api/ghosts")
def api():
    with client.context():
        query = GhostName.query()
        ghosts = query.fetch()
        return jsonify([ghost.ghost_name for ghost in ghosts])


@app.route("/api/login")
def login():
    # redirect_uri = url_for("auth", _external=True)
    redirect_uri = "http://localhost:5173/api/auth"
    return oauth.google.authorize_redirect(redirect_uri)


@app.route("/api/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


@app.route("/api/auth")
def auth():
    token = oauth.google.authorize_access_token()
    session["user"] = token["userinfo"]
    return redirect("/")


@app.route("/api/user")
def user():
    user = session["user"]
    if user is None:
        return abort(404, "Not logged in")
    return jsonify(user)
