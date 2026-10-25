PROJECT="python-app"
FLASK_APP="main:app"


# Set --host-port to work around bug with NDB unable to connect to ::1.
gcloud beta emulators datastore start \
    --project "$PROJECT" \
    --host-port localhost

sleep 5
$(gcloud beta emulators datastore env-init)