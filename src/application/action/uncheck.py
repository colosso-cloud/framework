

async def uncheck(presentation,event,**data):
    target = event.target.getAttribute('data-bs-target')
    #toggle = event.target.getAttribute('data-bs-toggle')
    selected = presentation.components[target]['selected']
    
    checkboxes = presentation.document.querySelectorAll(f'[data-bs-target="{target}"]')
    
    for checkbox in checkboxes:
        checkbox.checked = False
    
    selected.clear()