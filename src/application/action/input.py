import js

modules = {'flow': 'framework.service.flow'}

@flow.asynchronous(managers=('messenger', 'presenter', 'storekeeper'),)
async def input(messenger, presenter, storekeeper, **constants):
    value = constants.get('value', '')
    inputs = constants.get('inputs', [])
    
    for id in inputs:
        input = js.document.getElementById(id)
        input.value = value
    #print(constants,'WOW22')
    
    
    