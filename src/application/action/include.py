
async def include(presentation,event,**data):
    target = event.target.getAttribute('data-bs-target')
    toggle = event.target.getAttribute('data-bs-toggle')
    selected = presentation.components[target]['selected']
    
    if event.target.checked and toggle not in selected:
        selected.append(toggle)
    elif not event.target.checked and toggle in selected:
        selected.remove(toggle)