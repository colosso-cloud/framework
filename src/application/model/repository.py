
repository = (
    {'name': 'id', 'type': 'integer', 'default': 0,'force_type':'str'},
    {'name': 'name', 'type': 'string', 'default': None, 'required': True, 'regex': r'^[\w\-]+$'},
    {'name': 'branch', 'type': 'string', 'default': 'main', 'regex': r'^[\w\-]+$'},
    {'name': 'description', 'type': 'string', 'default': '', 'regex': r'^[\w\s\-]*$'},
    {'name': 'visibility', 'type': 'bool', 'default': False,},
    {'name': 'owner', 'type': 'string', 'default': '', 'regex': r'^[\w\-]+$'},
    {'name': 'location', 'type': 'string', 'default': '0000', 'regex': r'^[a-zA-Z0-9_-]+$'},
    {'name': 'updated', 'type': 'string', 'default': None, 'regex': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?$'},
    {'name': 'created', 'type': 'string', 'default': None, 'regex': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?$'},
    {'name': 'stars', 'type': 'integer', 'default': 0},
    {'name': 'forks', 'type': 'integer', 'default': 0},
    #{'name': 'commits', 'type': 'integer', 'default': 0},
    {'name': 'tree', 'type': 'list', 'default': []},
    {'name': 'sha', 'type': 'string', 'default': ''},
)