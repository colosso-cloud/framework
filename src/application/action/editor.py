modules = {'flow':'framework.service.flow'}

import js
from js import ace,console, setTimeout, clearTimeout
import pyodide
import asyncio
from pyodide.ffi import create_proxy


import re

def xml_tag_to_dict(tag_str):
    # Rimuovi spazi extra e assicura che ci sia una sola riga
    tag_str = tag_str.strip()

    # Match del nome del tag e della stringa di attributi
    tag_match = re.match(r"<(\w+)(.*?)\/?>", tag_str)
    if not tag_match:
        return {}

    tag_name = tag_match.group(1)
    attr_string = tag_match.group(2)

    # Supporta anche attributi con trattini: alignment-vertical, data-id, aria-label, ecc.
    attr_pattern = re.findall(r'([\w\-]+)\s*=\s*"([^"]*)"', attr_string)

    attrs = {k: v for k, v in attr_pattern}
    attrs["tag"] = tag_name
    return attrs

'''def find_opening_tag_at_cursor(text, offset):
    # Match di tag aperti, con attributi opzionali, ma non chiusi
    tag_pattern = re.compile(r"<(?P<name>\w+)(?P<attrs>[^>]*)>", re.DOTALL)

    matches = list(tag_pattern.finditer(text))

    open_stack = []
    for match in matches:
        start, end = match.span()
        tag_name = match.group("name")

        if start > offset:
            break  # siamo oltre il cursore

        # Stack per gestire annidamenti
        if text[end - 2:end] == "/>":
            continue  # tag autochiuso
        else:
            open_stack.append((tag_name, match.group(0), start, end))

        # Ora cerchiamo se c'è una chiusura dopo
        closing_tag = f"</{tag_name}>"
        close_pos = text.find(closing_tag, end)
        if close_pos != -1 and close_pos < offset:
            open_stack = open_stack[:-1]  # chiuso prima del cursore

    return open_stack[-1][1] if open_stack else None'''

def find_opening_tag_at_cursor(text, offset):
    tag_pattern = re.compile(r"<(?P<name>\w+)(?P<attrs>[^>]*)\/?>", re.DOTALL)

    matches = list(tag_pattern.finditer(text))
    open_stack = []

    for match in matches:
        start, end = match.span()
        tag_name = match.group("name")
        tag_str = match.group(0)

        if offset < start:
            break  # oltre il cursore

        if tag_str.endswith("/>"):
            # Tag autoconclusivo → controlla se offset è dentro
            if start <= offset <= end:
                return tag_str  # es. <Input id="email" />
        else:
            # Stack per gestire apertura/chiusura normale
            open_stack.append((tag_name, tag_str, start, end))

            # Cerca chiusura
            closing_tag = f"</{tag_name}>"
            close_pos = text.find(closing_tag, end)
            if close_pos != -1 and close_pos < offset:
                open_stack.pop()

    return open_stack[-1][1] if open_stack else None


from lxml import etree as ET  # Usa lxml invece di xml.etree.ElementTree

'''def build_xml_tree_dict(xml_string):
    parser = ET.XMLParser(recover=True)
    # Se la stringa contiene dichiarazione di encoding, passa bytes
    if xml_string.lstrip().startswith("<?xml"):
        xml_string = xml_string.encode("utf-8")
    root_elem = ET.fromstring(xml_string, parser=parser)

    def parse_element(elem):
        node = {
            "type": elem.tag,
            "name": elem.attrib.get('id', elem.tag),
            "lineno": elem.sourceline if hasattr(elem, 'sourceline') and elem.sourceline else 0,
            "col_offset": elem.position[1] if hasattr(elem, 'position') else 0,
            "children": [parse_element(child) for child in elem]
        }
        return node

    root_dict = {
        "type": "xml_string",
        "name": 'name',
        "children": [parse_element(root_elem)]
    }

    return root_dict'''

def build_xml_tree_dict(xml_string):
    parser = ET.XMLParser(recover=True)
    if xml_string.lstrip().startswith("<?xml"):
        xml_string = xml_string.encode("utf-8")
    root_elem = ET.fromstring(xml_string, parser=parser)
    lines = xml_string.decode("utf-8").splitlines() if isinstance(xml_string, bytes) else xml_string.splitlines()

    def parse_element(elem):
        row = elem.sourceline if hasattr(elem, 'sourceline') and elem.sourceline else 0
        col = 0
        if row > 0:
            tag = f"<{elem.tag}"
            line = lines[row-1]
            col = line.find(tag)
            if col == -1:
                col = 0
        node = {
            "type": elem.tag,
            "name": elem.attrib.get('id', elem.tag),
            "lineno": row,
            "col_offset": col,
            "children": [parse_element(child) for child in elem]
        }
        return node

    root_dict = {
        "type": "xml_string",
        "name": 'name',
        "children": [parse_element(root_elem)]
    }
    return root_dict

import ast

def build_python_tree_dict(file_path):
    source = file_path
    tree = ast.parse(source)
    filename = 'python'

    def get_node_name(node):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return node.name
        elif isinstance(node, ast.ClassDef):
            return node.name
        elif isinstance(node, ast.Import):
            return ", ".join([alias.name for alias in node.names])
        elif isinstance(node, ast.ImportFrom):
            return f"from {node.module} import " + ", ".join([alias.name for alias in node.names])
        elif isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            return ", ".join(targets)
        return "unknown"

    root = {
        "type": "module",
        "name": filename,
        "path": "",
        "children": []
    }

    categories = {
        "imports": [],
        "classes": [],
        "functions": [],
        "async_functions": [],
        "constants": []
    }

    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            categories["imports"].append({
                "type": "import",
                "name": get_node_name(node),
                "lineno": node.lineno,
                "col_offset": node.col_offset,
                "source": ast.get_source_segment(source, node)
            })
        elif isinstance(node, ast.ClassDef):
            class_node = {
                "type": "class",
                "name": node.name,
                "lineno": node.lineno,
                "col_offset": node.col_offset,
                "source": ast.get_source_segment(source, node),
                "children": []
            }
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    class_node["children"].append({
                        "type": "method",
                        "name": item.name,
                        "lineno": item.lineno,
                        "col_offset": item.col_offset,
                        "source": ast.get_source_segment(source, item)
                    })
                elif isinstance(item, ast.AsyncFunctionDef):
                    class_node["children"].append({
                        "type": "async_method",
                        "name": item.name,
                        "lineno": item.lineno,
                        "col_offset": item.col_offset,
                        "source": ast.get_source_segment(source, item)
                    })
            categories["classes"].append(class_node)
        elif isinstance(node, ast.FunctionDef):
            categories["functions"].append({
                "type": "function",
                "name": node.name,
                "lineno": node.lineno,
                "col_offset": node.col_offset,
                "source": ast.get_source_segment(source, node)
            })
        elif isinstance(node, ast.AsyncFunctionDef):
            categories["async_functions"].append({
                "type": "async_function",
                "name": node.name,
                "lineno": node.lineno,
                "col_offset": node.col_offset,
                "source": ast.get_source_segment(source, node)
            })
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    categories["constants"].append({
                        "type": "constant",
                        "name": target.id,
                        "lineno": node.lineno,
                        "col_offset": node.col_offset,
                        "source": ast.get_source_segment(source, node)
                    })

    for key, items in categories.items():
        if items:
            root["children"].append({
                "type": key,
                "name": key.replace("_", " ").capitalize(),
                "children": items
            })

    return root

# Funzione asincrona Python da chiamare dopo debounce
@flow.asynchronous(managers=('messenger','presenter','storekeeper'),)
async def on_editor_change(ace_editor,messenger,presenter,storekeeper):
    await asyncio.sleep(0.1)
    content = ace_editor.getValue()
    mode_obj = ace_editor.session.getMode()
    mode = getattr(mode_obj, "$id", None)
    
    match mode:
        case 'ace/mode/python':
            code = build_python_tree_dict(content)
        case 'ace/mode/xml':
            code = build_xml_tree_dict(content)
            cursor = ace_editor.getCursorPosition()
            row, column = cursor.row, cursor.column
            lines = content.splitlines()
            offset = sum(len(line) + 1 for line in lines[:row]) + column

            tag = find_opening_tag_at_cursor(content, offset)
            print("➡️ Sei dentro il tag:", tag)
            info = xml_tag_to_dict(tag)
            await presenter.rebuild(id='editor-property',view='application/view/component/Editor.xml',data={'info':info})
        case _:
            return None
        
    await presenter.rebuild(id='preview-content',view='application/view/component/Tru.xml',data={'info':code})

@flow.asynchronous(managers=('messenger','presenter'))
async def editor(messenger,presenter,**constants):
    target = constants.get('target','')
    field = constants.get('field','editor')
    file = constants.get('path','')
    await asyncio.sleep(0.5)
    # Mappatura delle estensioni ai moduli di modalità di ACE
    mode_mapping = {
        'py': 'ace/mode/python',
        'xml': 'ace/mode/xml',
        'js': 'ace/mode/javascript',
        'html': 'ace/mode/html',
        'css': 'ace/mode/css',
        'json': 'ace/mode/json',
        'txt': 'ace/mode/text',
        'toml': 'ace/mode/toml',
        'yaml': 'ace/mode/yaml',
        'yml': 'ace/mode/yaml',
        'md': 'ace/mode/markdown',
        'java': 'ace/mode/java',
        'c': 'ace/mode/c_cpp',
        'cpp': 'ace/mode/c_cpp',
        'h': 'ace/mode/c_cpp',
        'hpp': 'ace/mode/c_cpp',
        'cs': 'ace/mode/csharp',
        'php': 'ace/mode/php',
        'rb': 'ace/mode/ruby',
        'go': 'ace/mode/golang',
        'rs': 'ace/mode/rust',
        'sh': 'ace/mode/sh',
        'sql': 'ace/mode/sql',
        'swift': 'ace/mode/swift',
        'ts': 'ace/mode/typescript',
        'tsx': 'ace/mode/typescript',
        'vue': 'ace/mode/vue',
        'scss': 'ace/mode/scss',
        'less': 'ace/mode/less',
        'ini': 'ace/mode/ini',
        'bat': 'ace/mode/batchfile',
        'dockerfile': 'ace/mode/dockerfile',
        'makefile': 'ace/mode/makefile',
        'perl': 'ace/mode/perl',
        'pl': 'ace/mode/perl',
        'lua': 'ace/mode/lua',
        # Aggiungi altre estensioni se necessario
    }
    
    # Estrai l'estensione del file
    mode = mode_mapping.get(file.split('.')[-1], 'ace/mode/text')
    

    # Inizializza l'editor ACE sull'elemento
    ace_editor = ace.edit(field+target, {
        # Imposta la modalità dinamicamente
    })
    
    ace_editor.setTheme("ace/theme/github")
    ace_editor.session.setMode(mode)
    
    component = await presenter.component(name=target)
    component[field] = ace_editor

    # Variabile per debounce timer (salvata in JS globale)
    js.debounce_timer = None

    # Wrapper sincrono per il debounce (usato in .on)
    def debounced_wrapper(*args, **kwargs):
        if js.debounce_timer is not None:
            clearTimeout(js.debounce_timer)
        js.debounce_timer = setTimeout(
            create_proxy(lambda: asyncio.ensure_future(on_editor_change(ace_editor))),
            1000
        )

    # Crea proxy della funzione e collegalo a Ace
    change_proxy = create_proxy(debounced_wrapper)
    ace_editor.session.on("change", change_proxy)
    #ace_editor.getSession().selection.on("changeCursor", change_proxy)
    ace_editor.session.selection.on("changeCursor", change_proxy)
    def printEditorDetails():
        print('printEditorDetails')
        '''cursorPosition = ace_editor.getCursorPosition()

        cursorPosition = ace_editor.getCursorPosition()

        # Ottieni il numero di spazi per l'indentazione
        tabSize = ace_editor.session.getTabSize()

        # Ottieni il formato di carattere di a capo
        # "unix" (LF) o "windows" (CRLF)
        newLineMode = ace_editor.session.getNewLineMode()  

        # Ottieni il contenuto della riga attuale
        currentLine = ace_editor.session.getLine(cursorPosition.row)

        # Conta gli spazi iniziali della riga attuale
        #leadingSpaces = currentLine.match('/^\s*/')[0].length

        # Stampa le informazioni
        console.log("Riga: " + (cursorPosition.row + 1))
        console.log("Colonna: " + (cursorPosition.column + 1))
        console.log("Numero di spazi per indentazione: " + tabSize)
        console.log("Tipo di carattere di a capo: " + newLineMode)
        #console.log("Spazi effettivi sulla riga corrente: " + leadingSpaces)'''
    try:
        #cursor = ace_editor.getCursorPosition()
        #print(cursor)
        #aaa = pyodide.create_proxy(ttt)
        #component['proxy'] = aaa
        #component['editor'].addEventListener('click',presenter.info)
        #ace_editor.session.selection.on("changeCursor",component['proxy'])
        pass
    except Exception as e:
        print('Errore',e)
        console.log(e)

@flow.asynchronous(managers=('messenger','presenter','storekeeper'),)
async def ide(messenger,presenter,storekeeper,**constants):
    
    
    component = await presenter.component(name='ide')
    #print('target',target)
    print('component',constants)
    for key in constants:
        print(key)
        component[key] = constants[key]
        #language.put(component,constants[key])
        print('component',constants)

    '''if 'selected' in constants:
        component = await presenter.component(name=constants.get('selected'))
        
        code = component['block-editor-'].getValue()
        code = build_python_tree_dict(code)
        await presenter.rebuild(id='preview-content',view='application/view/component/Tru.xml',data={'info':code})'''

@flow.asynchronous(managers=('messenger','presenter'))
async def move(messenger,presenter,**constants):
    row = constants.get('row', 0)
    col = constants.get('col', 0)
    print('move',constants)
    component = await presenter.component(name='ide')
    selected = component.get('selected', None)
    #target = constants.get('targetr','ide')
    component = await presenter.component(name=selected)
    print('move component:',component)
    component['block-editor-'].gotoLine(int(row), int(col), True)
    #component['block-editor-'].moveCursorTo(int(row), int(col))
    component['block-editor-'].focus()

    #on_editor_change(component['block-editor-'])

    '''# Forza il movimento del cursore per scatenare l'evento
    cursor = component['block-editor-'].getCursorPosition()
    component['block-editor-'].moveCursorTo(cursor.row, cursor.column + 1)
    component['block-editor-'].moveCursorTo(cursor.row, cursor.column)
    #component['block-editor-'].getSession().selection._emit("changeCursor")
    component['block-editor-'].session.selection._emit("changeCursor")
    #component['block-editor-'].selection.selectLine()
    #view=component.get('view','')'''


def build_combined_input_tag2(self_closing=True):
    """
    Costruisce il tag combinato usando tutti gli input/select/textarea dentro un contenitore.
    Unisce width e width-unit (es: width="100px"), e ignora width-unit come attributo separato.
    Stesso discorso per height/height-unit.
    Per i radio button, prende solo quello checked.
    """
    container = js.document.getElementById('editor-property')
    if container is None:
        return ""

    elements = container.querySelectorAll("input, select, textarea")
    values = {}
    tag_name = "Input"
    attrs = []

    # Prima raccogli tutti i valori
    for el in elements:
        name = el.name or el.id or ""
        value = el.value
        # Solo radio checked
        if hasattr(el, "type") and el.type == "radio":
            if not el.checked:
                continue
        values[name] = value
        # Gestione tag dinamico
        if name == "tag" or el.id == "editor-property-tag":
            tag_name = value or "Input"

    # Poi costruisci gli attributi, gestendo le coppie
    for name, value in values.items():
        if value == '' or value == '#808080':
            continue
        # Unisci width + width-unit
        if name == "width":
            unit = values.get("width-unit", "")
            if unit:
                attrs.append(f'width="{value}{unit}"')
            else:
                attrs.append(f'width="{value}"')
        # Unisci height + height-unit
        elif name == "height":
            unit = values.get("height-unit", "")
            if unit:
                attrs.append(f'height="{value}{unit}"')
            else:
                attrs.append(f'height="{value}"')
        # Ignora width-unit e height-unit come attributi separati
        elif name in ("width-unit", "height-unit"):
            continue
        else:
            attrs.append(f'{name}="{value}"')

    if self_closing:
        return f'<{tag_name} {" ".join(attrs)} />'
    else:
        return f'<{tag_name} {" ".join(attrs)}>'

def build_combined_input_tag(self_closing=True):
    """
    Costruisce il tag combinato usando tutti gli input/select/textarea dentro un contenitore.
    Per i radio button, prende solo quello checked.
    """
    container = js.document.getElementById('editor-property')
    if container is None:
        return ""

    elements = container.querySelectorAll("input, select, textarea")
    attrs = []
    tag_name = "Input"
    for el in elements:
        name = el.name or el.id or ""
        value = el.value
        # Gestione radio: solo quello checked
        if hasattr(el, "type") and el.type == "radio":
            if not el.checked:
                continue
        # Usa il campo 'tag' per il nome del tag
        if name == "tag" or el.id == "editor-property-tag":
            tag_name = value or "Input"
        elif value == '' or value == '#808080' or value == '0' or value == 'None':
            continue
        else:
            attrs.append(f'{name}="{value}"')
    if self_closing:
        return f'<{tag_name} {" ".join(attrs)} />'
    else:
        return f'<{tag_name} {" ".join(attrs)}>'
    


@flow.asynchronous(managers=('messenger','presenter'))
async def replace_tag(messenger,presenter,**constants):
    component = await presenter.component(name='ide')
    selected = component.get('selected', None)
    component = await presenter.component(name=selected)
    editor = component['block-editor-']
    session = editor.getSession()
    cursor = editor.getCursorPosition()
    lines = session.getDocument().getAllLines()

    # Calcola offset assoluto
    offset = 0
    for i in range(cursor.row):
        offset += len(lines[i]) + 1  # +1 per newline
    offset += cursor.column

    full_text = "\n".join(lines)

    # Cerca tutti i tag (aperti o autochiusi)
    tag_pattern = re.compile(r"<(\w+)([^<>]*)\/?>", re.DOTALL)
    matches = list(tag_pattern.finditer(full_text))

    for match in matches:
        start, end = match.span()
        if start <= offset <= end:
            tag_text = match.group(0)
            # Verifica se il tag è autochiuso
            self_closing = tag_text.strip().endswith("/>")
            # Costruisci il nuovo tag in base al tipo
            new_tag = build_combined_input_tag(self_closing)
            # Sostituisci il tag trovato con quello nuovo
            new_text = full_text[:start] + new_tag + full_text[end:]
            session.setValue(new_text)
            # Riporta il cursore dov’era
            editor.moveCursorToPosition(cursor)
            return True

    return False  # Nessun tag trovato

'''@flow.asynchronous(managers=('messenger','presenter'))
async def replace_tag(messenger,presenter,**constants):
    def build_combined_input_tag():
        """
        ids: lista di id degli input da combinare
        Ritorna una stringa tipo: <TagName name1="val1" name2="val2" ... />
        Il nome del tag viene preso dal valore di 'editor-property-tag'
        """
        ids = ['editor-property-tag', 'editor-property-width', 'editor-property-height', 'editor-property-id']
        attrs = []
        tag_name = "Input"
        for input_id in ids:
            el = js.document.getElementById(input_id)
            if el is not None:
                name = el.name or input_id
                value = el.value
                if input_id == 'editor-property-tag':
                    tag_name = value or "Input"
                else:
                    attrs.append(f'{name}="{value}"')
        return f'<{tag_name} {" ".join(attrs)} />'

    component = await presenter.component(name='ide')
    selected = component.get('selected', None)
    component = await presenter.component(name=selected)
    editor = component['block-editor-']
    session = editor.getSession()
    cursor = editor.getCursorPosition()
    lines = session.getDocument().getAllLines()

    new_tag = build_combined_input_tag()

    # Calcola offset assoluto
    offset = 0
    for i in range(cursor.row):
        offset += len(lines[i]) + 1  # +1 per newline
    offset += cursor.column

    full_text = "\n".join(lines)

    # Cerca tutti i tag (aperti o autochiusi)
    tag_pattern = re.compile(r"<(\w+)([^<>]*)\/?>", re.DOTALL)
    matches = list(tag_pattern.finditer(full_text))

    for match in matches:
        start, end = match.span()
        if start <= offset <= end:
            # Sostituisce il tag trovato con quello nuovo
            new_text = full_text[:start] + new_tag + full_text[end:]
            session.setValue(new_text)

            # Riporta il cursore dov’era
            editor.moveCursorToPosition(cursor)
            return True

    return False  # Nessun tag trovato'''