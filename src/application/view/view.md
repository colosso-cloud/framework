# 📄 Scopo del file

Questo documento definisce le regole e le linee guida per scrivere file `.xml` nella cartella `/view`, affinché possano essere interpretati correttamente dalla funzione asincrona `mount_view(self, root, data, storekeeper, messenger)`.

I file XML devono rappresentare una struttura di interfaccia utente e componenti interattivi. Ogni nodo XML rappresenta un componente visuale o logico.

---

## 🧩 Tag supportati

Ogni tag corrisponde a un tipo di elemento da costruire. Ecco i tag principali:

| Tag         | Descrizione                                                                 |
|-------------|-----------------------------------------------------------------------------|
| Messenger   | Componente dinamico che carica un file `.xml` da un altro percorso.         |
| Storekeeper | Inizializza un'interazione con un repository dati.                          |
| Icon        | Visualizza un'icona da librerie come Bootstrap Icons.                       |
| Media       | Per contenuti multimediali concreti: immagini, video, audio, embeddati      |
| Visual      | Per rappresentazioni grafiche astratte o generate: grafici, canvas, SVG     |
| View        | Rende una vista interna, eventualmente usando dati da storekeeper.          |
| Input       | Elementi input HTML: testo, select, radio, checkbox, range, ecc.            |
| Action      | Pulsanti, form, dropdown e altri trigger.                                   |
| Window      | Finestre modali, offcanvas, iframe, ecc.                                    |
| Text        | Elementi testuali, statici o dinamici (es. editable, code, etc).            |
| Group       | Contenitori: liste, nav, tab, accordion, input-group, ecc.                  |
| Layout      | `div` generico per layout e contenimento.                                   |

---

## 🛠️ Attributi comuni

- `id`: Identificatore univoco del componente.  
- `type`: Specifica la variante o funzione del componente (es. tipo input, tipo grafico).  
- `value`: Valore iniziale o di default.  
- `placeholder`: Testo guida nei campi input.  
- `view`: Percorso del file `.xml` da caricare (per Messenger).  
- `repository`, `payload`, `method`: Parametri specifici per Storekeeper.

---

## 🔁 Gerarchia e annidamento

Ogni tag può contenere altri tag (elementi figli), a seconda della logica della UI. Ad esempio:

- `<Group>` può contenere `<Input>`, `<Text>, `<Action>`, ecc.
- `<Visual type="table.body">` richiede una riga di riferimento (type="table.row") come figlio.
- `<Action type="form">` può contenere `<Input>` ed elementi `<Text>`.

---

## 🧠 Comportamento dinamico

- Se è presente `storekeeper` i dati verranno iniettati dinamicamente.
- Il campo text può essere elaborato da una funzione language.get().
- Se un `tag` non è riconosciuto, viene considerato generico e trasformato in un `<div>` con contenuto dinamico.

---

## ⚠️ Attenzione

- Non usare nomi di `tag` inventati: saranno trattati come generici e potrebbero non essere montati correttamente.
- Assicurati che gli `id` siano univoci nel file XML.
- Gli `attributi` sono case-sensitive.
- Gli elementi `Messenger` possono richiamare altre viste `.xml`, creando componenti annidati.
- L'attributo `type` in `<Icon>` serve per supportare diverse librerie (es. `fas` per Font Awesome)

---

## 📚 Best Practice

- Usa tag semantici ove possibile (es. `<Group type="list">` invece di un semplice `<div>`).
- Separare logicamente `UI` e `dati`: usa `Storekeeper` per ottenere `dati`, e `Graph` o `Text` per mostrarli.
- Usa Messenger per componibilità modulare della UI.

---

## Attributi Supportati

Il metodo `att(self, element, attributes)` gestisce una vasta gamma di attributi, classificabili in queste categorie:

### ✅ Attributi Generali

| Attributo           | Descrizione                                                                |
|---------------------|----------------------------------------------------------------------------|
| `id`                | Imposta l'ID dell'elemento                                                 |
| `class`             | Aggiunge classi CSS                                                        |
| `style`             | Applica uno stile inline                                                   |
| `width`, `height`   | Imposta dimensioni (anche max)                                             |
| `padding`, `margin` | Gestione tramite classi o separazione con `;`                              |
| `expand`            | Layout responsive (es. `vertical`, `full`, `col-auto`, `col`)              |
| `collapse`          | Nasconde l'elemento (`full`, `visibility`)                                 |
| `flow`              | Controllo overflow (`auto`, `hidden`, `scroll`, `visible`)                 |

### 🎨 Attributi di Stile

| Attributo               | Descrizione                                                  |
|-------------------------|--------------------------------------------------------------|
| `background`            | Colore di sfondo (es. `#fff`, `primary`, ecc.)               |
| `background-opacity`    | (placeholder, non implementato)                              |
| `shadow`                | Applica ombre (`none`, `sm`, `md`, `lg`)                     |
| `text-size`             | Font-size (`px`, `fs-{0-5}`)                                 |
| `text-color`            | Colore testo (usa classi Bootstrap)                          |
| `border`                | Aggiunge bordo con classe `border-{value}`                   |
| `border-position`       | Top, bottom, left, right, outer                              |
| `border-thickness`      | Valori da 0 a 5                                              |
| `border-radius`         | `pill`, `circle`, `top`, `bottom`, `right`, `left`           |
| `border-radius-size`    | `rounded-{0-5}`                                              |
| `border-color`          | Usa classi Bootstrap                                         |

### 📐 Attributi di Allineamento

| Attributo               | Valori                              |
|-------------------------|-------------------------------------|
| `alignment-horizontal`  | `start`, `end`, `center`, `between`, `around`, `evenly` |
| `alignment-vertical`    | `start`, `end`, `center`, `baseline`, `stretch`         |
| `alignment-content`     | `vertical`, `horizontal` (definisce `d-flex` con direzione) |

---

### ⚙️ Eventi e Interazioni

| Attributo     | Azione                                                                        |
|---------------|-------------------------------------------------------------------------------|
| `click`       | Registra evento `click`                                                       |
| `onchange`    | Evento onchange                                                               |
| `init`        | Avvia un task asincrono                                                       |
| `hide`        | `data-bs-dismiss` per modali o offcanvas                                      |
| `show`        | Imposta `data-bs-toggle` e `data-bs-target`                                   |
| `route`       | Link dinamico o toggle                                                        |
| `link`        | Aggiunge href diretto                                                         |
| `ddd`         | Aggiunge listener al click destro                                             |

---

### 🧩 Drag & Drop

| Attributo             | Comportamento                                                            |
|-----------------------|--------------------------------------------------------------------------|
| `draggable`           | Abilita trascinamento base                                               |
| `droppable`           | Accetta drop, imposta eventi `dragover`, `drop`, `dragleave`             |
| `draggable-component` | Identifica un componente come trascinabile                               |

---

## 1. `<Messenger>`

### Attributi supportati:
- `id`: identificatore univoco (opzionale)
- `type`: modello da utilizzare (default: `flesh`)
- `title`, `domain`, `view`

### 📌 Esempio base

```xml
<Messenger id="main-chat" type="flesh" title="Chat" domain="chat" view="Chat"/>
```

### Comportamento:
Inietta un componente dinamico da `application/view/component/{view}.xml` e lo monta nel contesto corrente.

---

## 2. `<Storekeeper>`

### Attributi supportati:
- `method`: `overview`, `gather`, ecc.
- `payload`: parametri passati
- `repository`: sorgente dei dati

### Comportamento:
Interagisce con una fonte dati tramite il metodo indicato e rende gli elementi figli con i dati ottenuti.

---

## 3. `<Visual>`

### Tipi supportati (`type`):
- `table`, `table.head`, `table.body`, `table.row`
- `carousel`

### Comportamento:
Genera rappresentazioni grafiche dinamiche: icone, tabelle, immagini, caroselli.

### 📌 Esempio base

```xml
<Storekeeper method="overview" payload="id={{user.id}}" repository="users">
    <Visual type="table.body">
        <Visual type="table.row">
            <Text storekeeper="name"/>
            <Text storekeeper="email"/>
        </Visual>
    </Visual>
</Storekeeper>
```

---

## 4. `<View>`

### Attributi opzionali:
- `storekeeper`: se presente, il testo può essere derivato da un oggetto dati.

### Comportamento:
Wrapper generico che costruisce una vista con `builder()`.

---

## 5. `<Input>`

### Tipi HTML supportati:
- Standard HTML: `text`, `checkbox`, `radio`, `range`, `color`, ecc.
- Speciali: `select`, `textarea`, `switch`

### Comportamento:
Costruisce un controllo di input compatibile con Bootstrap.

---

## 6. `<Action>`

### Tipi supportati:
- `form`
- `button`
- `submit`
- `dropdown`

### Comportamento:
Costruisce azioni utente (bottoni, form, menu).

---

## 7. `<Window>`

### Tipi supportati:
- `canvas`, `modal`, `window` (iframe)

### Attributi:
- `id`, `type`, `action`, `size`, `url`

### Comportamento:
Crea finestre modali, canvas laterali o iframe.

---

## 8. `<Text>`

### Tipi supportati:
- `editable`: contenuto modificabile
- `code`: blocco di codice
- `default`: paragrafo testuale

---

## 9. `<Group>`

### Tipi supportati:
- `button`, `list`, `pagination`, `breadcrumb`, `card`
- `tab`, `nav`, `tree`, `input`, `node`, `accordion`

### Comportamento:
Struttura e raggruppa elementi visivi correlati (liste, tab, gruppi input...).

---

## 10. `<Layout>`

### Comportamento:
Container generico, restituisce un `div` con attributi personalizzati.

---

## 🆕 11. `<Icon>` - Componente per icone

### Attributi supportati:
- `name` (obbligatorio): Nome dell'icona (es. `bi-image-alt`)
- `type`: Prefisso della libreria (default: `bi` per Bootstrap Icons)
- Tutti gli attributi generici di stile/allineamento

### 📌 Esempi:
```xml
<!-- Icona base -->
<Icon name="bi-check-circle" />

<!-- Icona con stile personalizzato -->
<Icon name="bi-exclamation-triangle" type="bi" color="danger" size="fs-3"/>

<!-- Icona cliccabile -->
<Icon name="bi-trash" click="deleteItem()" class="cursor-pointer"/>
```

### Best practice:
1. Usare sempre il prefisso della libreria (es. `bi-` per Bootstrap Icons)
3. Aggiungere `click` o altri eventi per interattività

---

## 12. `<Media>`

### Tipi supportati (`type`):
- `image`: immagini
- `video`: video player
- `audio`: audio player
- `embed`: contenuti esterni (iframe, YouTube, ecc.)

### Attributi principali:
- `src`: percorso o URL del media
- `alt`, `title`, `controls`, `autoplay`, `loop`, `muted`, ecc.

### 📌 Esempio

```xml
<!-- Esempio Media -->
<Media type="img" src="logo.png" alt="Logo"/>
```

### Comportamento:
Gestisce la visualizzazione di contenuti multimediali concreti come immagini, video, audio o embed esterni.

---