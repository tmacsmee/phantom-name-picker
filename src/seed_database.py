from src.models import Ghost, User
from google.cloud import ndb
import csv
import os


def normalise(name: str) -> str:
    return name.lower().replace(" ", "_")


def insert_ghost_names(client: ndb.Client):
    with client.context():
        with open("ghost-names.csv", mode="r") as file:
            dict_reader = csv.DictReader(file)

            ghost_names = []
            for row in dict_reader:
                name = row["Ghost name"]
                key = ndb.Key(Ghost, normalise(name))
                ghost = key.get()

                if ghost is None:
                    ghost = Ghost(key=key)
                ghost.ghost_name = name
                ghost.description = row["Description"]
                ghost_names.append(ghost)

            ndb.put_multi(ghost_names)


def insert_dummy_users(client: ndb.Client):
    dummy_users = [
        ("dummy-alice", "alice@example.com", "Alice", "Carter", "Betelgeuse"),
        ("dummy-ben", "ben@example.com", "Ben", "Miller", "Bhoot"),
        ("dummy-cora", "cora@example.com", "Cora", "Nguyen", "Bloody Mary"),
    ]

    with client.context():
        entities = []
        for user_id, email, first_name, last_name, ghost_name in dummy_users:
            ghost_key = normalise(ghost_name)
            ghost = ndb.Key(Ghost, ghost_key).get()
            if ghost is None:
                raise ValueError(f"Ghost does not exist: {ghost_name}")

            ghost.owner_user_id = user_id

            user = User(
                key=ndb.Key(User, user_id),
                email=email,
                ghost_key=ghost_key,
                first_name=first_name,
                last_name=last_name,
            )
            entities.extend([ghost, user])

        ndb.put_multi(entities)


if __name__ == "__main__":
    seed_client = ndb.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
    insert_ghost_names(seed_client)
