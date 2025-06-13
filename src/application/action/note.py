modules = {'flow': 'framework.service.flow'}

@flow.asynchronous(managers=('messenger', 'storekeeper','presenter'),)
async def note(messenger, storekeeper, presenter, **constants):
    print(f"Note: {constants}")
    if 'target' in constants:
        target = constants.get('target', '')
        component = await presenter.component(name=target)
        print(f"Component: {component}")
        id = language.get('attributes.identifier', component)
        filters = {
            'eq': {'id':id},
            #'neq': [('age', '30')],
            #'like': [('email', '%example.com')],
            #'ilike': [('city', '%rome%')]
        }
    
    
    
    response = await storekeeper.change(repository='notes', filter=filters, payload={'type':constants.get('data', '')})
    #if 'target' in constants and 'data' not in constants:
        #response = await storekeeper.delete(repository='notes', filter=filters)
    #else:
        #if 'action' in constants:
            #constants.pop('action')
        #response = await storekeeper.store(repository='notes',payload=constants)
    '''response = await storekeeper.store(repository='notes', payload=constants)

    # Notifica il risultato del salvataggio
    if response.get('state', False):
        await messenger.post(domain='success', message=f"Creato {constants.get('path', '')}{constants.get('name', '')}")
    else:
        await messenger.post(domain='error', message=f"Errore creazione {constants.get('path', '')}{constants.get('name', '')}")'''