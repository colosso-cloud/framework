modules = {'flow':'framework.service.flow'}

import js
import asyncio
@flow.asynchronous(managers=('messenger','presenter','storekeeper'),)
async def ide(messenger,presenter,storekeeper,**constants):
    
    target = constants.get('id','')
    component = await presenter.component(name=target)
    #print('target',target)
    print('component',constants)
    for key in constants:
        print(key)
        component[key] = constants[key]
        #language.put(component,constants[key])
        print('component',constants)

    if 'loading' not in component:
        component |= await language.builder('ide',constants,{},'full',language)
    
    
    view = await presenter.builder(url=component.get('view'),component=component)

                
    element = js.document.getElementById(target)

    element.innerHTML = ''
    element.appendChild(view)