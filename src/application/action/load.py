modules = {'flow':'framework.service.flow'}

import js
@flow.asynchronous(managers=('messenger','presenter','storekeeper'))
async def load(messenger,presenter,storekeeper,**constants):
    url = f'application/view/component/editor.xml'
    #print(constants)
    component = await presenter.component(name='ide')
    payload = {'location':f"{component.get('repository')['owner']}/{component.get('repository')['name']}",'path':constants.get('url','')}
    print(payload,'##########3')
    transaction = await storekeeper.gather(repository="file",payload=payload)
    print(component)
    print(transaction)
    #text = await presenter.description(url=constants['url'])
    view = await presenter.builder(url=url,storekeeper=transaction)
    element = js.document.getElementById(constants['target'])
    element.appendChild(view)