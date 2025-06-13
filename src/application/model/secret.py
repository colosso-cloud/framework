secret = (
    {'name': 'id', 'type': 'uuid', 'default': 'gen_random_uuid()', 'required': True, 'primary_key': True},
    {'name': 'owner', 'type': 'uuid', 'required': True, 'foreign_key': {'table': 'auth.users', 'column': 'id'}, 'on_delete': 'cascade'},
    {'name': 'field', 'type': 'string', 'default': None},
    {'name': 'secret', 'type': 'string', 'required': True},
    {'name': 'created_at', 'type': 'timestamp', 'default': "timezone('utc', now())"},
    {'name': 'description', 'type': 'string', 'default': None},
    {'name': 'updated_at', 'type': 'timestamp', 'required': True, 'default': "(now() AT TIME ZONE 'utc')"},
)