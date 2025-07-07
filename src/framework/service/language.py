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
import copy

from cerberus import Validator, TypeDefinition, errors

class MyCustomValidator(Validator):
    '''def __init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)
        # Puoi anche inizializzare qui altre risorse o configurazioni
        # self.my_custom_setting = kwargs.get('my_setting')
        pass'''
    
    def _normalize_coerce_identifier(self, value):
        return generate_identifier()
    
    def _normalize_setter_identifier(self, mapping, field, value):
            return generate_identifier()
    
    def _check_with_is_odd(self, field, value):
        if not value & 1:
            self._error(field, "Must be an odd number")

    def _validate_is_odd(self, constraint, field, value):
        """ Test the oddity of a value.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if constraint is True and not bool(value & 1):
            self._error(field, "Must be an odd number")

    # Metodo di normalizzazione per gestire le funzioni personalizzate
    # I metodi di normalizzazione iniziano con '_normalize_coerce_'
    # Questa è una delle vie per "trasformare" i dati prima della validazione
    # e permette a Cerberus di riconoscere la chiave 'function' nel tuo schema.
    def _validate_function(self, constraint, field, value):
        """
        Gestisce l'applicazione delle funzioni custom specificate nello schema.
        Questa funzione viene invocata se la regola 'function' è presente per un campo.
        """
        #print(constraint, field, value)
        # 'value' qui è il nome della funzione da eseguire, ad esempio 'generate_identifier'
        if value == 'generate_identifier':
            return generate_identifier()
        elif value == 'time_now_utc':
            return time_now_utc()
        else:
            # Se la funzione non è riconosciuta, potresti voler generare un errore
            # o semplicemente restituire il valore originale o None.
            # Qui restituiamo None, Cerberus poi validerà 'None' in base al tipo.
            self._error(f"Funzione '{value}' sconosciuta o non supportata.")
            return None

async def model(schema, value=None, mode='full', lang=None):
    """
    Convalida, popola, trasforma e struttura i dati utilizzando uno schema Cerberus.

    Args:
        schema (dict): Lo schema Cerberus da applicare ai dati.
        value (dict, optional): I dati da elaborare. Defaults a {}.
        mode (str, optional): Modalità di elaborazione (es. 'full'). Non completamente utilizzato qui,
                              ma mantenuto per coerenza se hai logiche esterne che lo usano.
        lang (str, optional): Lingua per il caricamento dinamico degli schemi (se implementato).

    Returns:
        dict: I dati elaborati e validati.

    Raises:
        ValueError: Se la validazione fallisce.
    """
    value = value or {}

    # Se lo schema è una stringa, prova a caricarlo dinamicamente (come prima)
    # Questa parte deve essere adattata per caricare uno schema Cerberus
    if isinstance(schema, str):
        try:
            # Qui si aspetta che il modulo caricato contenga lo schema Cerberus
            module = await load_module(lang, path=f'application.model.{schema}')
            # Supponiamo che lo schema sia un attributo 'SCHEMA' nel modulo
            cerberus_schema = getattr(module, 'SCHEMA', None)
            if not cerberus_schema:
                raise AttributeError(f"⚠️ Lo schema Cerberus 'SCHEMA' non trovato nel modulo '{schema}'.")
            schema = cerberus_schema # Aggiorna lo schema con quello caricato
        except Exception as e:
            print(f"Errore durante il caricamento dello schema '{schema}': {e}")
            raise # Rilancia l'eccezione o gestiscila diversamente

    if not isinstance(schema, dict):
        raise TypeError("Lo schema deve essere un dizionario valido per Cerberus.")

    # 1. Popolamento e Trasformazione Iniziale (Default, Funzioni)
    # Cerberus gestisce i 'default', ma le 'functions' richiedono un pre-processing
    processed_value = value.copy() # Lavora su una copia per non modificare l'originale

    for field_name, field_rules in schema.items():
        print(f"Processing field: {field_name} with rules: {field_rules}")
        if isinstance(field_rules, dict) and 'function' in field_rules:
            func_name = field_rules['function']
            if func_name == 'generate_identifier':
                # Applica solo se il campo non è già presente
                if field_name not in processed_value:
                    processed_value[field_name] = generate_identifier()
            elif func_name == 'time_now_utc':
                # Applica solo se il campo non è già presente
                if field_name not in processed_value:
                    processed_value[field_name] = time_now_utc()
            # Aggiungi altre funzioni qui

    # Cerberus Validation (Convalida, Tipi, Required, Regex, Default)
    # Crea un validatore Cerberus con lo schema fornito
    v = MyCustomValidator(schema,allow_unknown=False)

    # Permetti a Cerberus di gestire i valori di default durante la validazione
    # Cerberus gestirà 'type', 'required', 'default' e 'regex' direttamente
    if not v.validate(processed_value):
        # La validazione fallisce, Cerberus fornisce i messaggi di errore
        #errors_str = "; ".join([f"{k}: {', '.join(v)}" for k, v in v.errors.items()])
        raise ValueError(f"⚠️ Errore di validazione: {v.errors}")

    final_output = v.document

    return final_output

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
        raise FileNotFoundError(f"⚠️ Contenuto della risorsa  non valido o vuoto.")

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

def get(dictionary, domain, default=None):
    """Gets data from a dictionary using a dotted accessor-string, returning default only if path not found."""
    if not isinstance(dictionary, (dict, list)):
        raise TypeError("Il primo argomento deve essere un dizionario o una lista.")
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

def find_matching_keys2(mapper, schema):
    key = None
    fields = schema.keys()
    number_occurent = {}
    for k, v in mapper.items():
        for kk in v:
            chiave = v.get(kk, None)
            print(f"find_matching_keys: {k} {kk} {v}")
            if chiave in fields:
                print(f"###########################find_matching_keys: {k} {kk} {v} -> {chiave}")
                number_occurent.setdefault(kk,0)
                number_occurent[kk] += 1

    #trovare la chiave con il valore più alto
    max_value = max(number_occurent.values(), default=0)
    r = [k for k, v in number_occurent.items() if v == max_value]
    
    print(f"find_matching_keys: {key}",r)
    return key

def _check_path_in_schema(path: str, schema) -> bool:
    """
    Verifica se un percorso (dot-notation) esiste e punta a un campo definito
    all'interno di uno schema.
    """
    if not isinstance(path, str) or not path:
        return False
    if not isinstance(schema, dict) or not schema:
        return False

    current_schema_node = schema
    path_chunks = path.split('.')

    for i, chunk in enumerate(path_chunks):
        is_last_chunk = (i == len(path_chunks) - 1)
        
        if current_schema_node is None or not isinstance(current_schema_node, dict):
            return False # Il nodo intermedio non è un dizionario o è nullo
        
        next_schema_part = _get_next_schema(current_schema_node, chunk)

        if next_schema_part is None:
            return False # Il chunk non è stato trovato nello schema corrente
        
        if not is_last_chunk:
            current_schema_node = next_schema_part
    
    return True # Il percorso completo è stato trovato nello schema

def find_matching_keys(mapper, schema) :
    """
    Trova la chiave del formato (es. 'API', 'MODEL') nel mapper che ha il maggior numero
    di percorsi di output corrispondenti nello schema fornito.

    Args:
        mapper: Il dizionario mapper completo.
                Esempio: {
                    'product_id': {'MODEL': 'product_id', 'API': 'idProdotto'},
                    'description': {'MODEL': 'desc', 'API': 'descrizioneArticolo'}
                }
        schema: Lo schema completo del dizionario di output.

    Returns:
        La chiave del formato (es. 'API') che ha il maggior numero di corrispondenze
        nello schema, o None se non viene trovata alcuna corrispondenza significativa.
    """
    if not isinstance(mapper, dict) or not mapper:
        print("find_matching_keys: Mapper non valido o vuoto.")
        return None
    if not isinstance(schema, dict) or not schema:
        print("find_matching_keys: Schema non valido o vuoto.")
        return None

    number_occurrences = {} # Dizionario per contare le occorrenze per ogni chiave di formato (es. 'API')

    # Itera su ogni campo nel mapper (es. 'product_id', 'description')
    for original_field_name, format_mappings in mapper.items():
        if not isinstance(format_mappings, dict):
            continue # Salta se le mappature non sono un dizionario

        # Itera sulle mappature per ogni formato (es. 'MODEL': 'product_id', 'API': 'idProdotto')
        for format_key, output_path_in_mapper in format_mappings.items():
            # Verifica se il percorso di output specificato nel mapper esiste nello schema di output
            if _check_path_in_schema(output_path_in_mapper, schema):
                # Se esiste, incrementa il contatore per quella chiave di formato
                number_occurrences.setdefault(format_key, 0)
                number_occurrences[format_key] += 1
                # print(f"MATCH: '{original_field_name}' maps '{format_key}' to '{output_path_in_mapper}', found in schema.")
            # else:
                # print(f"NO MATCH: '{original_field_name}' maps '{format_key}' to '{output_path_in_mapper}', NOT found in schema.")

    #print(f"find_matching_keys: Conteggio occorrenze per formato: {number_occurrences}")

    if not number_occurrences:
        return None # Nessuna corrispondenza trovata

    # Trova la chiave (o le chiavi) con il valore più alto
    max_value = 0
    if number_occurrences: # Assicurati che non sia vuoto prima di chiamare max()
        max_value = max(number_occurrences.values())
    
    # Raccogli tutte le chiavi che hanno il valore massimo
    winning_keys = [k for k, v in number_occurrences.items() if v == max_value]

    # Politica di risoluzione: Se ci sono più chiavi con lo stesso conteggio massimo,
    # puoi scegliere la prima in ordine alfabetico, o la prima che incontri.
    # Per semplicità, restituirò la prima se ce ne sono più.
    if winning_keys:
        return winning_keys[0] 
    
    return None # Dovrebbe essere catturato da 'if not number_occurrences'

def translation(data_dict, mapper, values, input, output):

    """ Trasforma un set di costanti in un output mappato. """

    translated = {}

    if not isinstance(data_dict, dict):
        raise TypeError("Il primo argomento deve essere un dizionario.")

    if not isinstance(mapper, dict):
        raise TypeError("'mapper' deve essere un dizionario.")

    if not isinstance(values, dict):
        raise TypeError("'values' deve essere un dizionario.")
    
    if not isinstance(input, dict):
        raise TypeError("'input' deve essere un dizionario.")
    
    if not isinstance(output, dict):
        raise TypeError("'output' deve essere un dizionario.")

    key = find_matching_keys(mapper,output) or find_matching_keys(mapper,input)
    #print(f"find_matching_keys: {key}######################")
    for k, v in mapper.items():
        
        n1 = get(data_dict, k)
        n2 = get(data_dict, v.get(key, None))
        
        if n1:
            output_key = v.get(key, None)
            value = n1
            translated |= put(translated, output_key, value, output)
        if n2:
            output_key = k
            value = n2
            translated |= put(translated, output_key, value, output)

        #print(f"translation: k:{k},key:{key} = {v},{data_dict}",n1,n2) 

    fieldsData = data_dict.keys()
    fieldsOutput = output.keys()


    for field in fieldsData:
        if field in fieldsOutput:
            value = get(data_dict, field)
            translated |= put(translated, field, value, output)

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

def _get_next_schema(schema, key):
    if isinstance(schema, dict):
        if 'schema' in schema:
            if schema.get('type') == 'list': return schema['schema']
            if isinstance(schema['schema'], dict): return schema['schema'].get(key)
        return schema.get(key)
    return None

def put(data: dict, path: str, value: any, schema: dict) -> dict:
    if not isinstance(data, dict): raise TypeError("Il dizionario iniziale deve essere di tipo dict.")
    if not isinstance(path, str) or not path: raise ValueError("Il dominio deve essere una stringa non vuota.")
    if not isinstance(schema, dict) or not schema: raise ValueError("Lo schema deve essere un dizionario valido.")

    result = copy.deepcopy(data)
    node, sch = result, schema
    chunks = path.split('.')

    for i, chunk in enumerate(chunks):
        is_last = i == len(chunks) - 1
        is_index = chunk.lstrip('-').isdigit()
        key = int(chunk) if is_index else chunk
        next_sch = _get_next_schema(sch, chunk)

        if isinstance(node, dict):
            if is_index:
                raise IndexError(f"Indice numerico '{chunk}' usato in un dizionario a livello {i}.")
            if is_last:
                if next_sch is None:
                    raise IndexError(f"Campo '{chunk}' non definito nello schema.")
                if not MyCustomValidator({chunk: next_sch}, allow_unknown=False).validate({chunk: value}):
                    raise ValueError(f"Valore non valido per '{chunk}': {value}")
                node[key] = value
            else:
                node.setdefault(key, {} if next_sch and next_sch.get('type') == 'dict'
                                     else [] if next_sch and next_sch.get('type') == 'list'
                                     else None)
                if node[key] is None:
                    raise IndexError(f"Nodo intermedio '{chunk}' non valido nello schema.")
                node, sch = node[key], next_sch

        elif isinstance(node, list):
            if not is_index:
                raise IndexError(f"Chiave '{chunk}' non numerica usata in una lista a livello {i}.")
            if not isinstance(next_sch, dict) or 'type' not in next_sch:
                raise IndexError(f"Schema non valido per lista a livello {i}.")

            if key == -1:  # Append mode
                t = next_sch['type']
                new_elem = {} if t == 'dict' else [] if t == 'list' else None
                node.append(new_elem)
                key = len(node) - 1

            if key < 0:
                raise IndexError(f"Indice negativo '{chunk}' non valido in lista.")

            while len(node) <= key:
                t = next_sch['type']
                node.append({} if t == 'dict' else [] if t == 'list' else None)

            if is_last:
                if not MyCustomValidator({chunk: next_sch}, allow_unknown=False).validate({chunk: value}):
                    raise ValueError(f"Valore non valido per indice '{chunk}': {value}")
                node[key] = value
            else:
                if node[key] is None or not isinstance(node[key], (dict, list)):
                    t = next_sch['type']
                    if t == 'dict': node[key] = {}
                    elif t == 'list': node[key] = []
                    else: raise IndexError(f"Tipo non contenitore '{t}' per nodo '{chunk}' in lista.")
                node, sch = node[key], next_sch

        else:
            raise IndexError(f"Nodo non indicizzabile al passo '{chunk}' (tipo: {type(node).__name__})")

    return result