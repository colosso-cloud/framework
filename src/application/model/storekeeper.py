
storekeeper = (
    # Identificatore univoco dell'operazione o della risorsa
    {'name': 'provider', 'type': 'string', 'default': 'unknown','regex': r'^[a-zA-Z0-9_-]+$'},
    
    {'name': 'location', 'type': 'string', 'default': ''},

    # Tipo di operazione CRUD: create, read, update, delete
    {'name': 'operation', 'type': 'string','default': 'read', 'regex': r'^(create|read|update|delete|view)$'},

    # Nome della tabella/collezione in caso di database
    {'name': 'repository', 'type': 'string', 'default': None},
    
    # Query o filtro per le operazioni READ/UPDATE/DELETE
    {'name': 'filter', 'type': 'dict', 'default': {}},
    
    # Dati da inserire o aggiornare
    {'name': 'payload', 'type': 'dict', 'default': {}},
)