# 📦 Modelli - `src/application/model`

Questa cartella contiene la definizione dei **modelli dati** utilizzati all'interno del framework. I modelli rappresentano le entità logiche e strutturali dell'applicazione e sono definiti come tuple di dizionari Python.

Ogni dizionario descrive un campo del modello con attributi che ne definiscono tipo, valore predefinito, comportamento e altre proprietà opzionali.

---

## 🧱 Struttura di un modello

Un modello è definito come una variabile Python (ad esempio `transaction`, `user`, ecc.) che contiene una tupla di campi. Ogni campo è un dizionario con la seguente struttura:

### 🔑 Attributi disponibili per ciascun campo

| Attributo     | Tipo        | Obbligatorio | Descrizione                                                                 |
|---------------|-------------|--------------|-----------------------------------------------------------------------------|
| `name`        | `string`    | ✅            | Nome del campo.                                                             |
| `type`        | `string`    | ❌           | Tipo base del campo (`string`, `boolean`, `dict`, `list`, ecc.).           |
| `default`     | qualsiasi   | ❌           | Valore predefinito.                                                         |
| `model`       | riferimento | ❌           | Riferimento a un altro modello (per campi relazionali).                    |
| `function`    | `string`    | ❌           | Funzione da eseguire per ottenere il valore (es. `time_now_utc`).          |
| `force_type`  | `string`    | ❌           | Impone il tipo degli elementi (utile per liste).                            |
| `iterable`    | `boolean`   | ❌           | Se `True`, il campo rappresenta una lista di elementi dello stesso tipo.   |

---

## 📄 Esempio: `transaction`

```python
transaction = (
    {'name': 'identifier', 'type': 'string', 'default': ''},
    {'name': 'state', 'type': 'boolean', 'default': False},
    {'name': 'action', 'type': 'string', 'default': 'unknown'},
    {'name': 'time', 'type': 'string', 'default': 'yyyy-mm-dd hh:mm:ss', 'function': 'time_now_utc'},
    {'name': 'user', 'model': user.user},
    {'name': 'remark', 'type': 'string', 'default': ''},
    {'name': 'worker', 'type': 'string', 'default': 'unknown'},
    {'name': 'parameters', 'type': 'dict', 'default': {}},
    {'name': 'transaction', 'type': 'list', 'default': [], 'iterable': True},
    {'name': 'result', 'type': 'list', 'force_type': 'dict', 'iterable': True, 'default': []},
)
```