import securescaffold
import os

STATIC_FOLDER = "frontend/dist"

app = securescaffold.create_app(__name__)
app.static_folder = STATIC_FOLDER
app.static_url_path = "/"


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    if path and os.path.exists(os.path.join(STATIC_FOLDER, path)):
        return app.send_static_file(path)
    return app.send_static_file("index.html")


@app.route("/api")
def api():
    return "Hello, World!"
