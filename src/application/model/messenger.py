messenger = (
    {
        "name": "message",
        "type": "string",
        "required": True,
        "description": "Testo del messaggio da inviare"
    },
    {
        "name": "domain",
        "type": "list",
        "required": True,
        "description": "Topic MQTT/Redis su cui pubblicare. Deve iniziare con un prefisso come info|error|debug...",
        'force_type': 'str',
        #"regex": r"^(info|error|debug|warning|event|alert|critical|fatal|success|notice)(\..+)?$"
    },
    {
        "name": "operation",
        "type": "string",
        "default": "read",
        "description": "Tipo di operazione o routing del messaggio",
        "regex": r"^(m2m|p2p|read|multicast|anycast|unicast|broadcast)$"
    },
    {
        "name": "sender",
        "type": "string",
        "required": False,
        "default": "anonym",
        "description": "Identificativo del mittente del messaggio (es. servizio, device, utente)"
    },
    {
        "name": "receiver",
        "type": "string",
        "required": False,
        "default": "anonym",
        "description": "Identificativo del destinatario (necessario per operazioni p2p/unicast)"
    },
    {
        "name": "timestamp",
        "type": "string",
        "required": False,
        "default": "now",
        "description": "Data e ora di invio del messaggio",
        "function": "time_now_utc",
    },
    {
        "name": "identifier",
        "type": "string",
        "required": False,
        "description": "ID univoco del messaggio (es. UUID per tracciabilità)",
        "function": "generate_identifier",
    },
    {
        "name": "priority",
        "type": "string",
        "required": False,
        "default": "normal",
        "description": "Priorità del messaggio",
        "regex": r"^(low|normal|high|critical)$"
    }
)