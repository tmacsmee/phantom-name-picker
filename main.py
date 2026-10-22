import securescaffold
import os
from insert_ghost_names import insert_ghost_names
from google.cloud import ndb
from flask import jsonify
from models import GhostName

STATIC_FOLDER = "frontend/dist"

app = securescaffold.create_app(__name__)
app.static_folder = STATIC_FOLDER
app.static_url_path = "/"

client = ndb.Client()


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
