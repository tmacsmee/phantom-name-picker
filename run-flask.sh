FLASK_APP="src/main:app"

# Start your local development server.
export FLASK_SETTINGS_FILENAME="settings.py"
export DATASTORE_EMULATOR_HOST="localhost:8081"
FLASK_APP="$FLASK_APP" uv run flask run --debug