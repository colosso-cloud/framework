modules = {'flow': 'framework.service.flow'}


@flow.asynchronous(managers=('messenger', 'storekeeper'))
async def delete(messenger, storekeeper, **constants):
    print(f"Delete: {constants}")
    model = constants.get('type', 'repository')
    

    match model:
        case 'file':
            #payload = await file(**constants)
            pass
        case 'repository':
            await repository(**constants)
        case 'note':
            pass

@flow.asynchronous(managers=('messenger', 'storekeeper'),inputs='repository')
async def repository(messenger, storekeeper, **constants):

    await storekeeper.remove(repository='repository', filter={'eq': {'owner': constants.get('owner', ''), 'name': constants.get('name', '')}})

@flow.asynchronous(managers=('messenger', 'storekeeper'))
async def file(messenger, storekeeper, **constants):
    """
    Funzione asincrona per eliminare un file e il relativo file di test, se esiste.

    Args:
        messenger: Servizio di messaggistica per notifiche.
        storekeeper: Servizio di archiviazione per gestire i file.
        **constants: Dizionario di parametri costanti.
    """
    path = constants.get('path', '')
    name = constants.get('name', '')

    # Rimuove il file di test associato, se applicabile
    if name.endswith('.py') and not name.endswith('.test.py'):
        test_file_constants = constants | {'name': name.replace('.py', '.test.py')}
        await _remove_file(storekeeper, messenger, test_file_constants)

    # Rimuove il file principale
    await _remove_file(storekeeper, messenger, constants)


async def _remove_file(storekeeper, messenger, file_constants):
    """
    Funzione di supporto per rimuovere un file e notificare il risultato.

    Args:
        storekeeper: Servizio di archiviazione per gestire i file.
        messenger: Servizio di messaggistica per notifiche.
        file_constants: Dizionario con i dettagli del file da rimuovere.
    """
    response = await storekeeper.remove(repository='file', payload=file_constants)
    file_path = f"{file_constants.get('path', '')}{file_constants.get('name', '')}"

    if response.get('state', False):
        await messenger.post(domain='success', message=f"Rimosso {file_path}")
    else:
        await messenger.post(domain='error', message=f"Errore rimozione {file_path}")