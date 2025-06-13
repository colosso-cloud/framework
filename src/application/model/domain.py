domain = (
    {'name': 'id', 'type': 'string', 'default': 'gen_random_uuid()', 'required': True, 'primary_key': True},
    {'name': 'description', 'type': 'string', 'default': None},
    {'name': 'status', 'type': 'string', 'default': 'pending', 'required': True, 'regex': r'^(pending|active|inactive|suspended)$'},
    {'name': 'ssl_enabled', 'type': 'boolean', 'default': True},
    {'name': 'dns_records', 'type': 'jsonb', 'default': []},
    {'name': 'server', 'type': 'string', 'default': None, 'foreign_key': {'table': 'servers', 'column': 'id'}, 'on_delete': 'set null'},
    {'name': 'container', 'type': 'string', 'default': None, 'foreign_key': {'table': 'containers', 'column': 'id'}, 'on_delete': 'set null'},
    {'name': 'service', 'type': 'string', 'default': None, 'foreign_key': {'table': 'services', 'column': 'id'}, 'on_delete': 'set null'},
    {'name': 'created_at', 'type': 'timestamp', 'default': 'now()'},
    {'name': 'updated_at', 'type': 'timestamp', 'default': 'now()'},
    {'name': 'domain', 'type': 'string', 'required': True, 'unique': True},
    {'name': 'owner', 'type': 'string', 'default': 'gen_random_uuid()', 'foreign_key': {'table': 'auth.users', 'column': 'id'}},
)