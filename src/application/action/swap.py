modules = {'flow':'framework.service.flow'}

import js
@flow.asynchronous(managers=('messenger','presenter'))
async def swap(messenger,presenter,**constants):
    """
    Scambia il contenuto interno di due elementi DOM.
    :param messenger: Oggetto per comunicazioni (non usato direttamente qui).
    :param presenter: Oggetto per aggiornamenti visivi (non usato direttamente qui).
    :param constants: Dizionario con i dettagli degli elementi.
                      - 'target': ID del primo elemento.
                      - 'place': ID del secondo elemento.
    """
    try:
        target = js.document.getElementById(constants['target'])
        place = js.document.getElementById(constants['place'])

        # Verifica che entrambi gli elementi esistano
        if not target or not place:
            raise ValueError("Uno o entrambi gli elementi non esistono nel DOM.")

        # Scambia il contenuto interno dei due elementi
        '''swap_content = place.innerHTML  # Salva il contenuto del primo elemento
        place2 = target.parentNode
        place.appendChild(target)  # Assegna il contenuto del secondo al primo
        target.parentNode.appendChild(swap_content)'''
        # Recupera il nodo padre di `target`
        target_parent = target.parentNode
        target_next_sibling = target.nextSibling  # Per mantenere la posizione di `place`

        # Salva il contenuto di `place`
        place_content = place.childNodes

        
        target_parent.appendChild(place_content)

        # Svuota `place` e sposta `target` dentro `place`
        #place.innerHTML = ""
        place.appendChild(target)
        '''if not element1 or not element2:
            raise ValueError("Uno o entrambi gli elementi non esistono nel DOM.")

        parent1 = element1.parentNode
        sibling1 = element1.nextSibling

        parent2 = element2.parentNode
        sibling2 = element2.nextSibling

        if sibling1 is not None:
            parent1.insertBefore(element2, sibling1)
        else:
            parent1.appendChild(element2)

        if sibling2 is not None:
            parent2.insertBefore(element1, sibling2)
        else:
            parent2.appendChild(element1)'''

        # Notifica il successo
        '''if messenger:
            await messenger.send("Scambio completato con successo!")

        # Aggiorna la vista
        if presenter:
            await presenter.update_view()'''

    except Exception as e:
        print(f"Errore durante lo scambio: {e}")
        '''if messenger:
            await messenger.send(f"Errore durante lo scambio: {e}")
        raise'''