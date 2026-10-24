from google.cloud import ndb


class Ghost(ndb.Model):
    ghost_name = ndb.StringProperty()
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()


class User(ndb.Model):
    ghost_key = ndb.StringProperty()
    email = ndb.StringProperty()


@ndb.transactional()
def update_ghost_name(user_id: str, ghost_name: str, first_name: str, last_name: str):
    ghost_id = ghost_name.lower().replace(" ", "_")
    ghost_key = ndb.Key("Ghost", ghost_id)
    ghost = ghost_key.get()
    if not ghost:
        raise ValueError("Ghost does not exist")

    user = User.get_or_insert(user_id)

    ghost.first_name = first_name
    ghost.last_name = last_name
    user.ghost_key = ghost_id

    ndb.put_multi([ghost, user])
