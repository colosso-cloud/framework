from kink import di
import importlib
import tomli
import sys
import os
from jinja2 import Environment
import asyncio
import ast
import re
import fnmatch
from datetime import datetime, timezone
import uuid
import json

from cerberus import Validator, TypeDefinition

class CustomBuilderValidator(Validator):
    _definition_schema = {
        'default_generate_identifier': {'type': 'string', 'allowed': ['generate_identifier']},
        'default_time_now_utc': {'type': 'string', 'allowed': ['time_now_utc']},
    }

    def _normalize_default_generate_identifier(self, definition):
        return generate_identifier()

    def _normalize_default_time_now_utc(self, definition):
        return time_now_utc()

    # Se vuoi, puoi definire un custom coercer per forzare il tipo a lista
    # Questo è un esempio, la regola 'type: list' + 'default: []' è già robusta
    def _normalize_coerce_to_list_if_none(self, field, value):
        if value is None:
            return []
        if not isinstance(value, list):
            return [value]
        return value
    
async def schema(schema_definition, value=None, lang=None):
    """
    Genera e/o valida un dizionario basato sullo schema Cerberus specificato.
    Popola i valori di default dinamici e normalizza il documento.
    """
    value = value or {} # Assicura che value sia un dizionario

    # Gestione del caricamento dinamico dello schema come stringa
    if isinstance(schema_definition, str):
        try:
            # Questa parte dovrebbe caricare lo schema effettivo.
            # Per questo esempio, usiamo una mappatura diretta.
            if schema_definition == 'transaction':
                loaded_schema = globals().get('transaction_schema_definition') # Ottieni dallo scope globale
                if not loaded_schema:
                    raise AttributeError(f"Schema '{schema_definition}' non definito.")
                schema_definition = loaded_schema
            else:
                # Qui potresti implementare la logica per load_module da un path effettivo
                # Per semplicità, in questo esempio specifico, gestiamo solo 'transaction'
                raise NotImplementedError(f"Caricamento di schema da '{schema_definition}' non supportato per questo esempio minimale.")

            # Ricorsione con lo schema caricato
            return await builder(schema_definition, value, lang)
        except Exception as e:
            print(f"Errore durante il caricamento dello schema '{schema_definition}': {e}")
            raise # Rilancia l'eccezione dopo averla loggata
    
    if not isinstance(schema_definition, dict):
        raise TypeError("Lo schema deve essere un dizionario o una stringa che punta a uno schema definito.")

    # Inizializza il validatore con il nostro CustomBuilderValidator
    # Questo permette a Cerberus di gestire i default dinamici
    validator = CustomBuilderValidator(schema_definition)

    # Valida e normalizza il documento.
    # Il metodo 'validate' applica i default e le coercizioni prima di validare.
    if not validator.validate(value):
        print(f"❌ Errori di validazione Cerberus: {validator.errors}")
        raise ValueError("Errore di validazione Cerberus: i dati non sono conformi allo schema.")
    
    # Restituisce il documento pulito e normalizzato da Cerberus
    return validator.normalized(value)


def extract_params(s):
    """
    Estrae i parametri da una stringa, assumendo che i parametri siano
    formattati come un oggetto JSON valido all'interno delle parentesi.

    Esempio: "funzione(param1: 'valore', param2: 123, param3: [1,2,3])"
    Verrà convertito in "{'param1': 'valore', 'param2': 123, 'param3': [1,2,3]}"
    e poi valutato come JSON.

    Args:
        s (str): La stringa da cui estrarre i parametri.

    Returns:
        dict: Un dizionario dei parametri estratti, o un dizionario vuoto in caso di errore.
    """
    match = re.search(r"\w+\((.*)\)", s)
    if not match:
        return {}

    content = match.group(1).strip()

    if not content: # Se non ci sono parametri
        return {}

    json_content = re.sub(r'(\b\w+)\s*:', r'"\1":', content)
    
    json_content = re.sub(r"'(.*?)'", r'"\1"', json_content)

    # In Python, True/False/None sono maiuscoli, in JSON sono lowercase.
    json_content = json_content.replace("True", "true").replace("False", "false").replace("None", "null")

    # Avvolgi il contenuto in parentesi graffe per renderlo un oggetto JSON completo
    final_json_string = "{" + json_content + "}"

    try:
        # Usa json.loads per analizzare la stringa JSON
        return json.loads(final_json_string)
    except json.JSONDecodeError as e:
        print(f"Errore di decodifica JSON: {e}")
        print(f"Stringa JSON tentata: {final_json_string}")
        return {} # Ritorna un dizionario vuoto in caso di errore di parsing JSON


def generate_identifier():
    return str(uuid.uuid4())

def time_now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")

def wildcard_match(check, pattern):
    """
    Restituisce il primo elemento in `check` che corrisponde al `pattern` con wildcard (*),
    oppure None se non c'è corrispondenza.
    """
    
    check = list(check)  # Conversione da dict_keys se necessario
    r = []
    for item in check:
        if fnmatch.fnmatch(item, pattern):
            r.append(item)
    print(f"Wildcard match: {pattern} {check} -> {r}")
    return r

async def extract_modules_from_code(code):
    """Copia il contenuto della variabile 'modules' dal codice senza eseguire exec e lo restituisce."""
    extracted_modules = None
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "resources":
                        extracted_modules = ast.literal_eval(node.value)
                        break
    except Exception as e:
        print(f"Errore durante l'analisi dei moduli richiesti: {e}")
    return extracted_modules if extracted_modules is not None else {}


if sys.platform != 'emscripten':
    async def backend(**constants):
        
        path = constants["path"]
        f = open(f"src/{path}", "r")
        ok = f.read()
        f.close() 
        return ok
    
else:
    import js

    async def backend(**constants):
        area, service, adapter = constants["path"].split(".")

        module_url = f"{area}/{service}/{adapter}.py"

        """Effettua una richiesta HTTP asincrona e restituisce il contenuto della risposta."""
        response = await js.fetch(module_url,{'method':'GET'})
        a = await response.text()
        return a
    

async def json_to_pydict(content: str, adapter_name: str):
    """Parsa il contenuto di un file JSON e restituisce un dizionario."""
    try:
        parsed_json = json.loads(content)
        print(f"✅ Risorsa JSON '{adapter_name}' caricata con successo.")
        return parsed_json
    except json.JSONDecodeError as e:
        raise ValueError(f"⚠️ Errore durante il parsing del JSON per '{adapter_name}': {e}")
    
async def resource(lang, **constants):
    """
    Carica una risorsa (modulo Python o file JSON) dinamicamente.
    """
    path = constants.get("path", "")
    adapter = constants.get("adapter", 'NaM').replace('.test', '')
    
    try:
        if 'code' in constants:
            # Caso in cui il codice è fornito direttamente
            resource_content = constants['code']
            adapter_name_for_logging = 'Test_Code'
        else:
            # Recupera il contenuto della risorsa dal backend
            resource_content = await backend(**constants)
            adapter_name_for_logging = adapter

        if not resource_content:
            raise FileNotFoundError(f"⚠️ Contenuto della risorsa '{adapter_name_for_logging}' non valido o vuoto.")

        # Determina il tipo di risorsa basandosi sull'estensione del path
        if path.endswith('.json'):
            adapter_name = constants.get("adapter", "default_adapter")
            content = await backend(**constants)
            return await json_to_pydict(content, adapter_name)
        elif path.endswith('.py'):
            # Se è un file Python, continua con la logica esistente
            module_code = resource_content
            
            # Controlla le dipendenze del modulo (solo per codice Python)
            # Ho adattato il nome della tua funzione per coerenza
            modules_to_install = await extract_modules_from_code(module_code)

            # Crea un nuovo modulo dinamico
            spec = importlib.util.spec_from_loader(adapter, loader=None)
            module = importlib.util.module_from_spec(spec)
            module.language = lang

            # Carica le risorse richieste ricorsivamente
            # Qui usiamo load_resource (la funzione corrente) per gestire sia .py che .json
            for resource_name, resource_path in modules_to_install.items():
                # Passa l'adapter originale se non specificato, altrimenti il nome della risorsa
                setattr(module, resource_name, await resource(lang, path=resource_path, adapter=resource_name))

            # Esegue il codice nel contesto del modulo
            exec(module_code, module.__dict__)

            print(f"✅ Modulo Python '{adapter_name_for_logging}' caricato con successo.")
            return module
        else:
            # Gestisci altri tipi di file o un tipo non riconosciuto
            print(f"⚠️ Tipo di risorsa non supportato per '{adapter_name_for_logging}': '{os.path.splitext(path)[1]}'. Restituzione del contenuto grezzo.")
            return resource_content # O solleva un errore, a seconda della tua politica

    except Exception as e:
        print(f"❌ Errore durante il caricamento della risorsa '{adapter}': {e}")
        #raise FileNotFoundError(f"⚠️ Contenuto della risorsa  non valido o vuoto.")

async def load_provider(lang,**constants):
        adapter = constants.get('adapter', '')
        service = constants.get('service', '')
        payload = constants.get('payload', '')

        if service not in di:
            di[service] = lambda di: list([])

        try:
            module = await load_module(lang,**constants)
            # Ottiene il provider e lo registra
            provider = getattr(module, 'adapter')
            di[service].append(provider(config=payload))

        except Exception as e:
            print(f"❌ Error: loading 'infrastructure.{service}.{adapter}': {repr(e)}")

async def load_manager(lang,**constants):
        area, service, adapter = constants["path"].split(".")

        if service not in di:
            di[service] = lambda di: list([])

        try:
            module = await load_module(lang,**constants)

            # Ottiene il provider e lo registra
            provider = getattr(module, adapter)
            
            providers = constants["provider"]
            if providers is list:
                providers = [di[provider] for provider in providers ]
            else:
                if providers not in di:
                    di[providers] = lambda di: list([])
                providers = di[providers]

            di[constants["name"]] = lambda _di: provider(providers=providers)
        except Exception as e:
            print(constants)
            print(f"❌ Error: loading 'infrastructure.{service}.{adapter}': {repr(e)}")
    

def validate_toml(content):
    

    # Caricare il TOML processato
    config = tomli.loads(content)

    errors = []
    for section, zone in config.items():
        if section in ['project','tool']:
            continue
        for name in zone:
            fields = zone[name]
            full_name = f"{section}.{name}"
            if "adapter" not in fields:
                errors.append(f"⚠️  Nessun adapter specificato nella sezione [{full_name}]")
                continue  # Saltiamo la validazione se non c'è un adapter

            adapter = fields["adapter"]
            #required_fields = ADAPTER_FIELDS.get(adapter)
            required_fields = {}

            if required_fields is None:
                errors.append(f"❌ Adapter sconosciuto '{adapter}' nella sezione [{full_name}]")
                continue  # Se l'adapter non è riconosciuto, segnaliamo l'errore e saltiamo

            # Verifica che tutti i campi richiesti dall'adapter siano presenti
            for field in required_fields:
                if field not in fields:
                    errors.append(f"❌ Campo mancante in [{full_name}] per adapter '{adapter}': {field}")

    # Output dei risultati della validazione
    if errors:
        print("⛔ Errore di validazione:")
        for error in errors:
            print(f"  - {error}")
        exit(1)
    else:
        print("✅ Il file TOML è valido!")

def get_confi(**constants):
    jinjaEnv = Environment()
    jinjaEnv.filters['get'] = get
    if sys.platform != 'emscripten':
        with open('pyproject.toml', 'r') as f:
            text = f.read()
            template = jinjaEnv.from_string(text)
            content = template.render(constants)
            config = tomli.loads(content)
            validate_toml(content)
            return config
    else:
        req = js.XMLHttpRequest.new()
        req.open("GET", "pyproject.toml", False)
        req.send()
        text = str(req.response)
        template = jinjaEnv.from_string(text)
        content = template.render(constants)
        validate_toml(content)
        config = tomli.loads(content)
        return config

def get_2(dictionary, domain, default=None):
    """
    Safe access to nested dict/list structures using dot notation.
    Supports wildcard '*' to map over lists.
    """
    def _get(domain, d):
        output = None
        lista = []

        parts = domain.split('.')
        current = d

        for idx, key in enumerate(parts):
            if key.isnumeric():
                key = int(key)

            if key == '*':
                arr = _get('.'.join(parts[:idx]), d)
                if not isinstance(arr, list):
                    return default
                for i in range(len(arr)):
                    new_parts = parts.copy()
                    new_parts[idx] = str(i)
                    lista.append(_get('.'.join(new_parts), d))
                return lista

            try:
                if isinstance(current, list) and isinstance(key, int):
                    current = current[key]
                elif isinstance(current, dict):
                    current = current.get(key)
                else:
                    return default
            except (KeyError, IndexError, TypeError):
                return default

        return current if current is not None else default

    return _get(domain, dictionary)

def get(dictionary, domain, default=None):
    """Gets data from a dictionary using a dotted accessor-string, returning default only if path not found."""
    current_data = dictionary
    for chunk in domain.split('.'):
        if isinstance(current_data, list):
            try:
                index = int(chunk)
                current_data = current_data[index]
            except (IndexError, ValueError, TypeError):
                # Se l'indice non è valido o current_data non è una lista
                return default
        elif isinstance(current_data, dict):
            if chunk in current_data:
                current_data = current_data[chunk]
            else:
                # Se la chiave non è presente nel dizionario
                return default
        else:
            # Se current_data non è né un dizionario né una lista nel mezzo del percorso
            return default
    
    # Restituisce il valore trovato. Se il valore trovato è None, lo restituisce così com'è.
    return current_data 


def put(dictionary, domain, value):
        #print(domain)
        if type(domain) == type(list()):
            subdomain = domain[0].split('.')
        else:
            subdomain = domain.split('.')
        
        work = dictionary.copy()
        puntatore = work
        
        for idx,key in enumerate(subdomain):
            #print(key,idx)
            if idx == len(subdomain)-1:
                #print(key,value)
                puntatore[key] = value
            else:
                if not key in puntatore:
                    if subdomain[idx+1].isnumeric():
                        puntatore[key] = []
                        puntatore = puntatore[key]
                    else:
                        if type(puntatore) == type([]):
                            #print(puntatore)
                            if 0 <= int(key) < len(puntatore):
                               puntatore = puntatore[int(key)]
                            else:
                                puntatore.insert(int(key), {})
                                puntatore = puntatore[int(key)]
                        else:
                            puntatore[key] = {}
                            puntatore = puntatore[key]

                else:
                    puntatore = puntatore[key]
        
        return work

async def builder(schema, value=None, spread={}, mode='full', lang=None):
    """Genera un dizionario basato sullo schema specificato, rispettando l'ordine delle operazioni."""
    
    value = value or {}  # Assicura che value sia un dizionario
    
    if isinstance(schema, tuple):
        return {
            row.get('name', '@'): await builder(row, value, spread)
            for row in schema if mode != 'filtered' or (value and row.get('name', '@') in value)
        }

    if isinstance(schema, str):
        try:
            module = await load_module(lang, path=f'application.model.{schema}')
            model = getattr(module, schema, None)
            if not model:
                raise AttributeError(f"⚠️ '{schema}' non trovato.")
            return await builder(model, value, spread, mode, lang)
        except Exception as e:
            print(f"Errore durante il caricamento dello schema '{schema}': {e}")
            

    name = schema.get('name', spread.get('name', ''))
    output = {}

    # Ordine di esecuzione delle operazioni
    operation_order = ["required", "force_type","default","function", "type", "regex"]
    expected_types = {
        "string": str,
        "integer": int,
        "boolean": bool,
        "dict": dict,
        "list": list
    }

    for operation in operation_order:
        if operation not in schema:
            continue
        
        match operation:
            case "force_type":
                var_type = type(value.get(name)).__name__
                expected_type = expected_types.get(schema.get("type")).__name__
                #print(var_type, expected_type)
                #print(f"⚠️ Forzando il tipo per '{name}'",str(type(value.get(name))), schema["force_type"])
                match expected_type:
                    case 'list':
                        #value[name] = [value[name]]
                        if var_type == schema["force_type"]:
                            #value[name] = [list(item.items()) if isinstance(item, dict) else item for item in value[name]]
                            value[name] = [value[name]]
                        if var_type == 'NoneType':
                            value[name] = []
                    case 'int':
                        if var_type == schema["force_type"]:
                            value[name] = int(value[name])
                
            case "required":
                if schema["required"] and name not in value:
                    raise ValueError(f"⚠️ Campo obbligatorio mancante: {name}")

            case "default":
                if name not in value:
                    value[name] = schema["default"]

            case "function":
                match schema["function"]:
                    case 'generate_identifier':
                        value[name] = generate_identifier()
                    case 'time_now_utc':
                        value[name] = time_now_utc()

            case "type":
                
                expected_type = expected_types.get(schema.get("type"))
                if expected_type and not isinstance(value.get(name), expected_type):
                    raise TypeError(f"❌ Tipo non valido per '{name}': atteso {expected_type.__name__}, ricevuto {type(value.get(name)).__name__}")

            case "regex":
                if name in value and not re.match(schema["regex"], str(value[name])):
                    raise ValueError(f"⚠️ Regex mismatch per '{name}': {value[name]}")

    output[name] = value.get(name)
    
    return output[name] if len(output) == 1 else output


def translation(data_dict, fields,mapper, values, input='MODEL', output='MODEL'):
    
    """ Trasforma un set di costanti in un output mappato. """
    translated = {}
    for key in fields:
        if key in mapper:
            mapping = mapper[key]
            key_input = mapping.get(input, key)
            key_output = mapping.get(output, key)
        else:
            key_input = key
            key_output = key
        #print("translation44",key_input,key_output)
        value = get(key_input, data_dict)

        if key in values and output in values[key]:
            if value is not None:
                    value = values[key][output](value)           
            else:
                pass
        #print("translation2",key_input,key_output,value,mapping)
        translated |= put(key_output, value, translated)

    return translated


def filter(self):
        pass

def first(self):
        pass

def last(iterable):
    return iterable[-1] if iterable else None

def keys(self):
        pass

def map(self):
        pass

def reduce(self):
        pass

def replace(self):
        pass

def slice(self):
        pass