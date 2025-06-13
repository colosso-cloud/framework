modules = {'flow':'framework.service.flow'}

import js
@flow.asynchronous(managers=('messenger','presenter'))
async def tab(messenger, presenter, **constants):
    
    tab_id = constants['id']  # ID della nuova tab da mostrare
    print(constants)
    
    # Mostra la nuova tab
    tab = js.document.getElementById(f'{tab_id}')
    parent = tab.parentElement

    # Rimuovi 'active' e 'show' dagli altri figli
    for sibling in parent.children:
        sibling.classList.remove('active', 'show')
        
        # Trova l'elemento con href corrispondente e rimuovi 'active'
        if sibling.id:
            link = js.document.querySelectorAll(f'[href="#{sibling.id}"]')
            
            for l in link:
                if l.getAttribute('href') == '#'+tab_id:
                    l.classList.add('active')
                else:
                    l.classList.remove('active')
        

    # Aggiungi 'active' e 'show' al tab corrente
    tab.classList.add('active', 'show')

