from models import Ghost, User
from google.cloud import ndb
import csv


def normalise(name: str) -> str:
    return name.lower().replace(" ", "_")


def insert_ghost_names(client: ndb.Client):
    with client.context():
        with open("ghost-names.csv", mode="r") as file:
            dict_reader = csv.DictReader(file)

            ghostNames = []
            for row in dict_reader:
                name = row["Ghost name"]
                description = row["Description"]

                key = ndb.Key(Ghost, normalise(name))

                ghostName = Ghost(key=key, ghost_name=name)
                ghostNames.append(ghostName)

            ndb.put_multi(ghostNames)


client = ndb.Client(project="python-app")
insert_ghost_names(client)
