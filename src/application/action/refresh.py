

async def refresh(presentation,event,**data):
    #target = event.target.getAttribute('data-bs-target')
    #component = presentation.components[target]
    #print("ok",data['data'])
    
    await presentation.rebuild(data['data'][1],data['data'][0])

    