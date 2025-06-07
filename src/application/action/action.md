# 📂 `src/application/action`

Questa cartella contiene **azioni applicative asincrone** che rappresentano comportamenti specifici del sistema all'interno di flussi di lavoro coordinati dal framework.

Ogni file in `action/` definisce una o più funzioni asincrone decorate con `@flow.asynchronous(...)`, che orchestrano l’interazione tra componenti logici (chiamati **manager**) come `messenger`, `presenter`, `storekeeper`, `executor`, `tester`, `defender`. Queste azioni permettono al sistema di reagire dinamicamente a eventi o richieste e rappresentano l’**application layer** secondo un’architettura DDD (Domain-Driven Design).

---

## ✨ Scopo

Le azioni in questa directory gestiscono operazioni ad alto livello e coordinano la logica di business del dominio. Sono progettate per:

- processare richieste asincrone
- mediare tra il dominio e l’infrastruttura

---

## 📌 Struttura tipica

Ogni azione:

- è **asincrona**
- è decorata con `@flow.asynchronous(managers=(...))`, che registra il flusso
- dichiara esplicitamente i **manager** richiesti
- accetta un dizionario `constants` con parametri dinamici

---

## 🧰 Manager supportati

Ecco i principali manager utilizzabili nei flussi:

| Manager      | Descrizione                                                                 |
|--------------|-----------------------------------------------------------------------------|
| `messenger`  | Canale di messaggistica tra componenti. Usato per inviare/ricevere prompt, richieste, risposte, comandi. |
| `presenter`  | Interfaccia verso UI. Può richiedere componenti visuali o dati formattati per la presentazione. |
| `storekeeper`| Gateway per accedere a file, documentazione, knowledge base persistenti. Legge/scrive documenti da repository. |
| `executor`   | Esegue codice dinamico generato (es. codice Python, script, Task).|
| `tester`     | Valuta automaticamente l’output rispetto a requisiti, test, validazioni. |
| `defender`   | Verifica la sicurezza o integrità di contenuti, modelli o output generati. |

---

## 🧪 Esempio completo: `create.py`

```python
modules = {'flow': 'framework.service.flow'}

import asyncio
import re

@flow.asynchronous(managers=('messenger', 'storekeeper','presenter'),inputs='note')
async def note(messenger, storekeeper, presenter, **constants):
    print(f"Note: {constants}")
    

    response = await storekeeper.store(repository='notes', payload=constants)
    print(f"Response: {response}")
    # Notifica il risultato del salvataggio
    if response.get('state', False):
        await messenger.post(domain='success', message=f"Create {constants.get('path', '')}{constants.get('name', '')}")
    else:
        await messenger.post(domain='error', message=f"Error: {constants.get('path', '')}{constants.get('name', '')}")
```