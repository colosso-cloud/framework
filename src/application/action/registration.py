modules = {'flow':'framework.service.flow'}

import js

@flow.asynchronous(managers=('defender',))
async def registration(defender,**constants):
    
    token = await defender.registration(ip='1111',identifier='asdasd',**constants)

    if token:
        js.location.reload()