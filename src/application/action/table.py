modules = {'flow':'framework.service.flow'}

import js
import asyncio
@flow.asynchronous(managers=('messenger','presenter','storekeeper'),model=('table',))
async def table(messenger,presenter,storekeeper,**constants):
    
    target = constants.get('id','')
    component = await presenter.component(name=target)
    print(f"Component: {component}")
    
    for key in constants:
        value = constants[key]
        if key != 'selected':
            component[key] = value
        else:
            selected = component.get('selected', [])
            if value not in selected:
                selected.append(value)
            component['selected'] = selected

    if 'loading' not in component:
        component |= await language.builder('table',constants,{},'full',language)
        component['loading'] = True
    
    print('@@@@@@:',constants,component)
    #print('loading' not in component,'######:',component)
    
    transaction = await storekeeper.gather(**component)
    view = await presenter.builder(storekeeper=transaction,text=component.get('inner'))

                
    element = js.document.getElementById(target)

    element.innerHTML = ''
    element.appendChild(view)