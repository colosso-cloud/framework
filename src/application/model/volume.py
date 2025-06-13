volume = (
    {'name': 'id', 'type': 'uuid', 'default': 'gen_random_uuid()', 'required': True, 'primary_key': True},
    {'name': 'name', 'type': 'string', 'required': True},
    {'name': 'description', 'type': 'string', 'default': None},
    {'name': 'size', 'type': 'integer', 'required': True, 'check': lambda x: x > 0},
    {'name': 'type', 'type': 'string', 'required': True, 'check': ['SSD', 'HDD', 'NFS', 'Object Storage']},
    {'name': 'mount', 'type': 'string', 'required': True},
    {'name': 'state', 'type': 'string', 'default': 'detached', 'required': True, 'check': ['attached', 'detached', 'error']},
    {'name': 'encrypted', 'type': 'boolean', 'default': False},
    {'name': 'backup_enabled', 'type': 'boolean', 'default': False},
    {'name': 'created_at', 'type': 'timestamp', 'default': 'now()'},
    {'name': 'updated_at', 'type': 'timestamp', 'default': 'now()'},
    {'name': 'owner', 'type': 'uuid', 'default': 'gen_random_uuid()', 'foreign_key': {'table': 'auth.users', 'column': 'id'}},
)