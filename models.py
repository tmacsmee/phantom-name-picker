from google.cloud import ndb


class GhostName(ndb.Model):
    ghost_name = ndb.StringProperty()
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()


class User(ndb.Model):
    ghostNameKey = ndb.StringProperty()
    email = ndb.StringProperty()
