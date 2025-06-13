modules = {'flow':'framework.service.flow'}

import js
@flow.asynchronous(managers=('messenger','presenter','storekeeper'),model=('table',))
async def model(messenger,presenter,storekeeper,**constants):
    
    target = constants.get('id','')
    component = await presenter.component(name=target)
    
    component |= await language.builder('table',constants,{},'full',language)
    component['loading'] = True
    

    