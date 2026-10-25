from google.cloud import ndb


class Ghost(ndb.Model):
    ghost_name = ndb.StringProperty()
    description = ndb.TextProperty()
    owner_user_id = ndb.StringProperty()


class User(ndb.Model):
    ghost_key = ndb.StringProperty()
    email = ndb.StringProperty()
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()


@ndb.transactional(xg=True)
def update_ghost_name(
    user_id: str,
    ghost_name: str,
    first_name: str,
    last_name: str,
    email: str = "",
):
    ghost_id = ghost_name.lower().replace(" ", "_")
    ghost_key = ndb.Key("Ghost", ghost_id)
    ghost = ghost_key.get()
    if not ghost:
        raise ValueError("Ghost does not exist")

    user_key = ndb.Key(User, user_id)
    user = user_key.get() or User(key=user_key)

    if ghost.owner_user_id and ghost.owner_user_id != user_id:
        raise ValueError("Ghost is already taken")

    previous_ghost = None
    if user.ghost_key and user.ghost_key != ghost_id:
        previous_ghost = ndb.Key(Ghost, user.ghost_key).get()
        if previous_ghost:
            previous_ghost.owner_user_id = None

    ghost.owner_user_id = user_id
    user.ghost_key = ghost_id
    user.email = email or user.email
    user.first_name = first_name
    user.last_name = last_name

    entities = [ghost, user]
    if previous_ghost:
        entities.append(previous_ghost)
    ndb.put_multi(entities)
