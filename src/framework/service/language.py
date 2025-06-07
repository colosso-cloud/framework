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

def extract_params2(s):
            match = re.search(r"\w+\((.*)\)", s)
            if not match:
                return {}

            content = match.group(1)

            # Split sicuro che tiene conto di {}
            pairs = []
            temp = ''
            depth = 0
            for char in content:
                if char == ',' and depth == 0:
                    pairs.append(temp.strip())
                    temp = ''
                else:
                    if char == '{':
                        depth += 1
                    elif char == '}':
                        depth -= 1
                    temp += char
            if temp:
                pairs.append(temp.strip())

            result = {}
            for pair in pairs:
                if ':' not in pair:
                    continue
                key, value = pair.split(':', 1)
                key = key.strip()
                value = value.strip()
                # Se è una stringa con apici singoli, rimuovili
                if value.startswith("'") and value.endswith("'"):
                    result[key] = value[1:-1]
                else:
                    result[key] = eval(value)  # valore grezzo

            return result

def extract_params(s):
    match = re.search(r"\w+\((.*)\)", s)
    if not match:
        return {}

    content = match.group(1)

    # Split sicuro che tiene conto di {} e []
    pairs = []
    temp = ''
    depth_curly = 0
    depth_square = 0
    in_string = False
    string_char = ''

    for char in content:
        if char in ("'", '"'):
            if not in_string:
                in_string = True
                string_char = char
            elif string_char == char:
                in_string = False
        if not in_string:
            if char == '{':
                depth_curly += 1
            elif char == '}':
                depth_curly -= 1
            elif char == '[':
                depth_square += 1
            elif char == ']':
                depth_square -= 1

        if char == ',' and depth_curly == 0 and depth_square == 0 and not in_string:
            pairs.append(temp.strip())
            temp = ''
        else:
            temp += char
    if temp:
        pairs.append(temp.strip())

    result = {}
    for pair in pairs:
        if ':' not in pair:
            continue
        key, value = pair.split(':', 1)
        key = key.strip()
        value = value.strip()
        if value.startswith("'") and value.endswith("'"):
            result[key] = value[1:-1]
        elif value.startswith('"') and value.endswith('"'):
            result[key] = value[1:-1]
        else:
            try:
                result[key] = eval(value)
            except Exception:
                result[key] = value  # fallback, ritorna come stringa grezza

    return result


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
                    if isinstance(target, ast.Name) and target.id == "modules":
                        extracted_modules = ast.literal_eval(node.value)
                        break
    except Exception as e:
        print(f"Errore durante l'analisi dei moduli richiesti: {e}")
    return extracted_modules if extracted_modules is not None else {}


def get_module_os(path, lang):
    try:
        # Apriamo il file per la lettura
        with open(path, 'r') as file:
            aa = file.read()  # Leggi il contenuto del file

        # Rimuoviamo l'estensione .py
        nettt = path.split('/')
        module_name = last(nettt).replace('.py','')
        # Otteniamo il nome del modulo dall'ultima parte del percorso

        # Creiamo il modulo dinamicamente
        spec = importlib.util.spec_from_loader(module_name, loader=None)
        module = importlib.util.module_from_spec(spec)

        # Aggiungiamo l'attributo 'language' al modulo
        setattr(module, 'language', lang)

        # Eseguiamo il codice Python contenuto nel file
        exec(aa, module.__dict__)

        return module
    except Exception as e:
        print(f"Error loading 'infrastructure module': {str(e)}")


def get_var(accessor_string, input_dict, default=None):
    """Gets data from a dictionary using a dotted accessor-string"""
    current_data = input_dict
    for chunk in accessor_string.split('.'):
        if isinstance(current_data, list):
            try:
                current_data = current_data[int(chunk)]
            except (IndexError, ValueError, TypeError):
                return default if default is not None else None
        elif isinstance(current_data, dict):
            if chunk in current_data:
                current_data = current_data[chunk]
            else:
                return default if default is not None else None
        else:
            return default if default is not None else None
    return current_data if current_data is not None else default


if sys.platform != 'emscripten':
    async def backend(**constants):
        area, service, adapter = constants["path"].split(".")
        f = open(f"src/{area}/{service}/{adapter}.py", "r")
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
    

async def load_module(lang, **constants):
    try:
        if 'code' in constants:
            module_code = constants['code']
            adapter = 'Test'
        else:
            # Estrae il nome del modulo
            area, service, adapter = constants["path"].split(".")
            
            # Recupera il codice del modulo dal backend
            module_code = await backend(**constants)
            if not module_code or not isinstance(module_code, str):
                raise ValueError(f"⚠️ Codice del modulo '{adapter}' non valido o vuoto.")
        
        
            

        # Controlla le dipendenze del modulo
        modules_to_install = await extract_modules_from_code(module_code)

        # Crea un nuovo modulo dinamico
        spec = importlib.util.spec_from_loader(adapter, loader=None)
        module = importlib.util.module_from_spec(spec)
        module.language = lang

        # Carica i moduli richiesti ricorsivamente
        for module_name, module_path in modules_to_install.items():
            setattr(module, module_name, await load_module(lang, path=module_path))

        # Esegue il codice nel contesto del modulo
        exec(module_code, module.__dict__)

        # Registra il modulo in sys.modules per permettere future importazioni
        #sys.modules[adapter] = module

        print(f"✅ Modulo '{adapter}' caricato con successo.")
        return module

    except Exception as e:
        print(f"❌ Errore durante il caricamento del modulo '{adapter}': {e}")
        return None

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
    
def loader_provider_test(**constants):

        
        adapter = constants['adapter'] if 'adapter' in constants else ''
        service = constants['service'] if 'service' in constants else ''
        payload = constants['payload'] if 'payload' in constants else ''
        area = constants['area'] if 'area' in constants else 'application'
            
        req = js.XMLHttpRequest.new()
        req.open("GET", f"{area}/{service}/{adapter}.py", False)
        req.send()

        req2 = js.XMLHttpRequest.new()
        req2.open("GET", f"framework/service/language.py", False)
        req2.send()

        spec2 = importlib.util.spec_from_loader('language', loader=None)
        module2 = importlib.util.module_from_spec(spec2)
        exec(req2.response, module2.__dict__)
        
        spec = importlib.util.spec_from_loader(adapter, loader=None)
        module = importlib.util.module_from_spec(spec)
        module.language = module2
        exec(req.response, module.__dict__)

        

        return module

def ttt(**constants):
    adapter = constants['adapter'] if 'adapter' in constants else ''
    service = constants['service'] if 'service' in constants else ''
    area = constants['area'] if 'area' in constants else ''
    payload = constants['payload'] if 'payload' in constants else ''

    spec=importlib.util.spec_from_file_location(adapter,f"src/{area}/{service}/{adapter}.py")
 
    # creates a new module based on spec
    foo = importlib.util.module_from_spec(spec)

    spec_lang=importlib.util.spec_from_file_location('language','src/framework/service/language.py')
    foo_lang = importlib.util.module_from_spec(spec_lang)
    spec_lang.loader.exec_module(foo_lang)
    setattr(foo,'language',foo_lang)
    
    # executes the module in its own namespace
    # when a module is imported or reloaded.
    spec.loader.exec_module(foo)

    return foo

def load_main(lang,**c):
    
    if sys.platform == 'emscripten':
        a = loader_provider_test(**c)
        return a
    else:
        return ttt(**c)

# Definizione dei campi richiesti in base all'adapter
ADAPTER_FIELDS = {
    "wasm": ["host", "port", "view", "routes"],
    "starlette": ["host", "port", "view", "routes"],
    "logging": ["host", "port", "persistence"],
    "websocket": ["url"],
    "api": ["url",'authorization','accept',],
    "flow": [],
    "mqtt": ["url", "port", "username", "password"],
    'oauth': ['url','id','secret'],
    "jwt": ["url", "app_id", "installation_id", "key", "autologin"],
    "supabase": ["url", "key"],
    "fs": [],
    "flutter": [],
    "ansible": ['playbook_path','inventory_file','extra_vars','timeout'],
    "log": ['format','level','file'],
    "console": ['format','level','file'],
    "redis": ['host','port','database','password'],
}


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
            required_fields = ADAPTER_FIELDS.get(adapter)

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
    jinjaEnv.filters['get'] = get_safe
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

def get(domain,dictionary={}):
        output = None
        lista = [] 
        
        piec = domain.split('.')
        puntatore = dictionary.copy()
        for idx,key in enumerate(piec):
            if key.isnumeric():
                key = int(key)
            
            if key == '*':
                arr = get('.'.join(piec[:idx]),dictionary)
                for x in range(len(arr)):
                    aa = piec
                    aa[idx] = str(x)
                    nnnome = '.'.join(aa)
                    #print(nnnome)
                    lista.append(get(nnnome,dictionary))
                return lista

            if type(key) == type(10):
                if key > len(puntatore):
                    return None
            else:
                if not key in puntatore:
                    return None
            
            
            if idx == len(piec)-1:
                return puntatore[key]
            else:
                if len(puntatore) != 0:
                    puntatore = puntatore[key]

def get_safe(dictionary, domain, default=None):
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


def put(domain,value,data=dict()):
        #print(domain)
        if type(domain) == type(list()):
            subdomain = domain[0].split('.')
        else:
            subdomain = domain.split('.')
        
        work = data.copy()
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

def translationold2(data, values, mapper, input='MODEL', output='MODEL'):
    try:
        lista = []
        for deta in data:
            lista.append(translation(deta, values, mapper, input, output))
        return lista
    except Exception as e:
        print(f"Errore translation: {type(e).__name__}: {e}")
    return []

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