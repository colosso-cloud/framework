

async def pagination(presentation,event,**data):
    target = event.target.getAttribute('data-bs-target')
    #toggle = event.target.getAttribute('data-bs-toggle')
    component = presentation.components[target]
    component['pageCurrent'] = int(data['data'][0])

    aaa = await presentation.rebuild(target,'Table')
    #print(data)
    #component['pageCurrent']
    #component['pageRow']
    #['sortField']
    #['sortAsc']

    