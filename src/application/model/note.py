note = (
    {'name': 'id', 'type': 'string', 'default': 'gen_random_uuid()'},
    {'name': 'owner', 'type': 'string', 'required': True},
    {'name': 'location', 'type': 'string', 'required': True},
    {'name': 'type', 'type': 'string', 'required': True},
    {'name': 'text', 'type': 'string', 'required': True},
    {'name': 'color', 'type': 'string', 'default': '#fffaa8'},
    {'name': 'parent_note_id', 'type': 'string', 'default': None},
    {'name': 'created_at', 'type': 'string', 'default': "timezone('utc', now())"},
    {'name': 'updated_at', 'type': 'string', 'default': "(now() AT TIME ZONE 'utc')"},
    {'name': 'description', 'type': 'string', 'default': None},
)