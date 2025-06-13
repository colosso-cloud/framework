modules = {'flow':'framework.service.flow'}

import js
@flow.asynchronous(managers=('messenger','presenter'))
async def move(messenger,presenter,**constants):
    """
    Sposta `target` dentro `place` e il contenuto di `place` viene spostato
    nella posizione originaria del nodo padre di `target` usando `replaceChild`.
    :param messenger: Oggetto per comunicazioni (non usato direttamente qui).
    :param presenter: Oggetto per aggiornamenti visivi (non usato direttamente qui).
    :param constants: Dizionario con i dettagli degli elementi.
                      - 'target': ID dell'elemento da spostare.
                      - 'place': ID dell'elemento che riceverà `target`.
    """
    try:
        target = js.document.getElementById(constants['target'])
        place = js.document.getElementById(constants['place'])

        # Verifica che entrambi gli elementi esistano
        if not target or not place:
            raise ValueError("Uno o entrambi gli elementi non esistono nel DOM.")

        # Recupera il nodo padre di `target`
        target_parent = target.parentNode
        swap_content = place.firstChild

        # Sostituisci `target` con `place` nel nodo padre
        target_parent.replaceChild(swap_content, target)

        # Sposta `target` dentro `place`
        place.appendChild(target)

    except Exception as e:
        print(f"Errore durante lo scambio: {e}")
        '''if messenger:
            await messenger.send(f"Errore durante lo scambio: {e}")
        raise'''