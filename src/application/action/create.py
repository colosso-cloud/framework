modules = {'flow': 'framework.service.flow'}

import asyncio
import re

async def handle_response(messenger, constants):
    
    print("In attesa di una risposta...")
    response = await messenger.read(domain='backlog.producer')
    print("Risposta ricevuta:", response)
    # Estrae tutto il contenuto tra ```python e ```
    match = re.search(r"```python\n(.*?)```", response.get('message'), re.DOTALL)

    if match:
        codice_estratto = match.group(1)
        # 2. Esegui il codice in un namespace isolato
        namespace = {}
        exec(codice_estratto, {}, namespace)

        # 3. Estrai la variabile
        product_backlog = namespace.get("product_backlog")
        if product_backlog:
            for voce in product_backlog:
                await note(text=voce['text'],location=f"SottoMonte/{constants.get('name')}",type="backlog.product",owner="99938d7a-ec20-4ad2-b319-60b3833be160")
        print(codice_estratto)
    else:
        print("Nessun blocco di codice trovato.")

@flow.asynchronous(managers=('messenger', 'storekeeper'))
async def create(messenger, storekeeper, **constants):
    print(f"Create: {constants}")
    model = constants.get('type', 'repository')
    match model:
        case 'file':
            payload = await file(**constants)
        case 'repository':
            if 'backlog' in constants:
                asyncio.create_task(handle_response(messenger,constants))
                #await asyncio.sleep(3)
                msg = await messenger.post(domain='backlog.producer', message=f"Rispondimi come se fossi un product owner che utilizza metologie agile framework SCRUM ! commando : creami una lista Product Backlog sottoforma di una lista dizionario con i seguneti campi (text,title,) in python  per :{constants.get('description', '')}")
                print('msg:', msg)
            payload = await repository(**constants)
        case 'note':
            payload = await note(**constants)

    # Salva il file principale
    transaction = await storekeeper.store(repository=model, payload=payload)
    # Notifica il risultato del salvataggio
    if transaction.get('state', False):
        await messenger.post(domain='success', message=f"Creato ")
    else:
        await messenger.post(domain='error', message=f"Errore creazione ")

@flow.asynchronous(managers=('messenger', 'storekeeper'),inputs='file')
async def file(messenger, storekeeper, **constants):
    """
    Funzione asincrona per creare un file e gestire la comunicazione con i servizi di archiviazione e messaggistica.

    Args:
        messenger: Servizio di messaggistica per notifiche.
        storekeeper: Servizio di archiviazione per salvare i dati.
        **constants: Dizionario di parametri costanti.
    """
    code_test = """
import unittest
import asyncio

# La tua classe repository modificata per usare self.language invece di language globale
modules = {'flow': 'framework.service.flow'}

class Test(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def test_valid(self):
        self.assertTrue(False)
        #self.assertEqual(count, 2)"""
    # Recupera il nome dal dizionario `constants` o usa un valore predefinito
    name = constants.get('name', '')

    # Aggiunge l'estensione `.py` al nome se non è già presente
    if '.' not in name:
        name = f"{name}.py"
        constants['path'] += name + '/'
        constants['name'] = name

    # Se il file è un file Python ma non un file di test, crea anche un file di test
    if constants.get('name', '').endswith('.py') and not constants.get('name', '').endswith('.test.py'):
        test_file_name = constants['name'].replace('.py', '.test.py')
        test_file_payload = constants | {'name': test_file_name,'content': code_test}

        # Prova a salvare il file di test
        test_response = await storekeeper.store(repository='file', payload=test_file_payload)
        if test_response.get('state', False):
            await messenger.post(domain='success', message=f"Creato {constants.get('path', '')}{test_file_name}")
        else:
            await messenger.post(domain='error', message=f"Errore creazione {constants.get('path', '')}{test_file_name}")

    # Salva il file principale
    response = await storekeeper.store(repository='file', payload=constants)

    # Notifica il risultato del salvataggio
    if response.get('state', False):
        await messenger.post(domain='success', message=f"Creato {constants.get('path', '')}{constants.get('name', '')}")
    else:
        await messenger.post(domain='error', message=f"Errore creazione {constants.get('path', '')}{constants.get('name', '')}")

@flow.asynchronous(managers=('messenger', 'storekeeper'),inputs='repository')
async def repository(messenger, storekeeper, **constants):
    return constants|{"private": False}
    
@flow.asynchronous(managers=('messenger', 'storekeeper','presenter'),inputs='note')
async def note(messenger, storekeeper, presenter, **constants):
    print(f"Note: {constants}")
    

    response = await storekeeper.store(repository='notes', payload=constants)
    print(f"Response: {response}")
    '''# Notifica il risultato del salvataggio
    if response.get('state', False):
        await messenger.post(domain='success', message=f"Creato {constants.get('path', '')}{constants.get('name', '')}")
    else:
        await messenger.post(domain='error', message=f"Errore creazione {constants.get('path', '')}{constants.get('name', '')}")'''