PROJECT="python-app"

# Set --host-port to work around a bug with NDB unable to connect to ::1.
gcloud beta emulators datastore start \
    --project "$PROJECT" \
    --host-port localhost:8081 &
EMULATOR_PID=$!

trap 'kill "$EMULATOR_PID"' EXIT

eval "$(gcloud beta emulators datastore env-init)"

wait "$EMULATOR_PID"