modules = {'flow':'framework.service.flow'}

import js

@flow.asynchronous(managers=('defender',))
async def logout(defender,**constants):
    
    await defender.logout(ip='1111',identifier='asdasd',**constants)
    js.location.reload()