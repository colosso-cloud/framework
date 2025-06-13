import js
import asyncio

modules = {'flow': 'framework.service.flow'}

@flow.asynchronous(managers=('messenger', 'presenter', 'storekeeper'),)
async def iframe(messenger, presenter, storekeeper, **constants):
    target = constants.get('id', 'myIframe')  # ID dell'iframe
    iframe_url = constants.get('src', '')     # URL da caricare
    if 'target' in constants:
        gg = constants['target']
        v = js.document.getElementById(gg)
        iframe_url = v.value

    print(f"Updating iframe '{target}' to load: {iframe_url}")
    
    iframe_element = js.document.getElementById(target)
    iframe_element.setAttribute('src', iframe_url)
    #iframe_element.src = iframe_url
    
    
    