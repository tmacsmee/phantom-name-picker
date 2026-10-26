# Phantom Name Picker

Flask application for assigning unique Phantom names using Google OAuth and
Cloud Datastore in Datastore mode.

## Local setup

Requires Python 3.13+, `uv`, Node.js, `pnpm`, and the Google Cloud SDK.

```sh
uv sync
pnpm install
touch .env
```

Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`. Add
`http://localhost:5000/auth` as an authorized redirect URI in the Google OAuth
client.

Start the Datastore emulator and Flask server:

```sh
./run-datastore.sh
```

```sh
./run-flask.sh
```

Seed the database with the emulator environment active:

```sh
uv run python seed_database.py
```

## Deployment

The GitHub Actions workflow deploys `app.yaml` and injects these GitHub
repository or environment secrets through the App Engine action:

- `GCP_PROJECT_ID`
- `GCP_WIF_PROVIDER`
- `GCP_DEPLOY_SERVICE_ACCOUNT`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
