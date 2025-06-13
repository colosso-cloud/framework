modules = {'flow': 'framework.service.flow'}

@flow.asynchronous(managers=('messenger', 'storekeeper'))
async def update(messenger, storekeeper, **constants):
    print(f"update: {constants}")
    model = constants.get('type', 'repository')
    

    match model:
        case 'file':
            #payload = await file(**constants)
            pass
        case 'repository':
            #for item in constants.get('items', []):
            await repository(**constants)
            pass
        case 'note':
            pass

@flow.asynchronous(managers=('messenger', 'storekeeper'),inputs='repository')
async def repository(messenger, storekeeper, **constants):

    await storekeeper.change(repository='repository', payload=constants)