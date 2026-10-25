# PHQ Studios Ghost Name Picker

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

Start the Datastore emulator in one terminal:

```sh
./run-datastore.sh
```

Then start Flask in another terminal:

```sh
./run-flask.sh
```

Seed the catalog with the emulator environment active:

```sh
uv run python seed_database.py
```

The seed module exposes import functions; use a short Python command or the
Datastore console to invoke them with an `ndb.Client` for the selected project.

## Deployment

Create a Google Cloud project with App Engine and Firestore in Datastore mode
enabled. Configure the OAuth client with the production redirect URI:
`https://PROJECT_ID.uc.r.appspot.com/auth`.

Set production secrets through the deployment environment or Secret Manager,
then deploy:

```sh
gcloud app deploy app.yaml --project PROJECT_ID
```

The GitHub Actions workflow deploys `app.yaml` and injects these GitHub
repository or environment secrets through the App Engine action:

- `GCP_PROJECT_ID`
- `GCP_WIF_PROVIDER`
- `GCP_DEPLOY_SERVICE_ACCOUNT`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

The workflow then runs `cloudbuild.seed.yaml` to seed the catalog. The GitHub
deployment service account needs App Engine Admin, Cloud Build Editor, Storage
Admin, Artifact Registry Reader, and Service Account User. The Cloud Build
service account needs `roles/datastore.user` on the project.

Push to `main` or start the workflow manually from the Actions tab. The seed
job is idempotent and preserves existing ghost ownership.

Production OAuth secrets must not be committed to `.env` or this repository.

## Design notes

`Ghost` stores the immutable catalog name and description plus `owner_user_id`.
`User` stores the authenticated email, entered first and last names, and the
selected ghost key. Selection and name changes update both entities in one
cross-group NDB transaction, preventing duplicate ownership and releasing the
previous name.

The brief requires the overview to display the email address and entered name
for taken ghosts. This is intentionally implemented as specified, but it is a
privacy consideration for a public deployment.

## Limitations

The application requires a configured Google OAuth client and Datastore. If
fewer than three names are available, it shows the available choices rather
than duplicating or inventing names. The current catalog overview uses normal
Datastore queries, so newly written records can take a short time to appear in
eventually consistent query results.
