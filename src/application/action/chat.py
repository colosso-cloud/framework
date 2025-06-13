modules = {'flow': 'framework.service.flow','create': 'application.action.create'}

import os
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
                await create.note(text=voce['text'],location=constants.get('location'),type="backlog.product",owner=constants.get('owner',''))
        print(codice_estratto)
    else:
        print("Nessun blocco di codice trovato.")

@flow.asynchronous(managers=('messenger', 'presenter', 'storekeeper'))
async def chat(messenger, presenter, storekeeper, **constants):
    print(f"Create: {constants}")
    receiver = constants.get('receiver', 'producer')
    match receiver:
        case 'programmer':
            pass
        case 'producer':
            asyncio.create_task(handle_response(messenger,constants))
            await messenger.post(domain='backlog.producer', message=f"Rispondimi come se fossi un product owner che utilizza metologie agile framework SCRUM da parte stakeholder ! commando : creami una lista Product Backlog sottoforma di una lista dizionario con i seguneti campi (text,title,) in python  per :{constants.get('message', '')}")

    # Salva il file principale
    #await messenger.post(domain='chat', message=f"Usa il seguente documento come base per rispondere alle domande dell'utente:\n\n{doc} Utente msg:{message}")

@flow.asynchronous(managers=('messenger', 'presenter', 'storekeeper'))
async def programmer(messenger, presenter, storekeeper, **constants):
    component = await presenter.component(name='chat-ai')
    file = constants.get('file', '')
    location = constants.get('location', '')
    message = constants.get('message', '')

    doc = ''
    paths = [file]
    directory = os.path.dirname(file.replace('src/application/', ''))
    path = 'src/application'
    for x in directory.split('/'):
        path = f"{path}/{x}"
        paths.append(path+f'/{x}.md')
    
    print('paths:', paths)

    for path in paths:
        payload = {'location': location, 'path': path}
        result = await storekeeper.gather(repository='file', payload=payload)
        doc += ''.join(f['content'] for f in result.get('result', []))

    component.setdefault('messenger', []).append(constants)
    print(doc,'component:',constants)
    await messenger.post(domain='chat', message=f"Usa il seguente documento come base per rispondere alle domande dell'utente:\n\n{doc} Utente msg:{message}")