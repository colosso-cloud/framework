import uuid
import asyncio
from html import escape
import json
from datetime import datetime

modules = {'flow': 'framework.service.flow','presentation': 'framework.port.presentation'}

html_layout = """
<!DOCTYPE html>
<html class="h-100" data-navigation-type="default" data-navbar-horizontal-shape="default" lang="it" dir="ltr">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta http-equiv='cache-control' content='no-cache'>
        <meta http-equiv='expires' content='0'>
        <meta http-equiv='pragma' content='no-cache'>
        <!-- ===============================================-->
        <!--    Document Title-->
        <!-- ===============================================-->
        <title>{{ title or '@Title' }}</title>
  
        <!-- ===============================================-->
        <!--    Favicons-->
        <!-- ===============================================-->
        <meta name="theme-color" content="#ffffff">
        <link rel="icon" type="image/x-icon" href="static/logo.png">
  
        <!-- ===============================================-->
        <!--    Stylesheets-->
        <!-- ===============================================-->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/dragula/3.7.3/dragula.css" integrity="sha512-gGkweS4I+MDqo1tLZtHl3Nu3PGY7TU8ldedRnu60fY6etWjQ/twRHRG2J92oDj7GDU2XvX8k6G5mbp0yCoyXCA==" crossorigin="anonymous" referrerpolicy="no-referrer" />
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
        {% block style %}
        {% endblock %}
        <link rel="stylesheet" href="https://unpkg.com/xterm/css/xterm.css" />
        <script src="https://unpkg.com/xterm/lib/xterm.js"></script>
        <script src="https://unpkg.com/xterm-addon-fit/lib/xterm-addon-fit.js"></script>
        <!-- ===============================================-->
        <!--    Javascript-->
        <!-- ===============================================-->
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/dragula/3.7.3/dragula.min.js" integrity="sha512-NgXVRE+Mxxf647SqmbB9wPS5SEpWiLFp5G7ItUNFi+GVUyQeP+7w4vnKtc2O/Dm74TpTFKXNjakd40pfSKNulg==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
        {% block head_script %}
        {% endblock %}
                
    </head>
    <body id="body" class="d-flex h-100 flex-column">
        <!-- ===============================================-->
        <!--    Main Content-->
        <!-- ===============================================-->
        <!-- Body -->
        {% block main %}
        {% endblock %}
        <!-- ===============================================-->
        <!--    JavaScripts-->
        <!-- ===============================================-->
        {% block body_script %}
        {% endblock %}
    </body>
</html>
"""

try:
    from starlette.applications import Starlette
    from starlette.requests import Request
    from starlette.responses import JSONResponse,HTMLResponse,RedirectResponse
    from starlette.routing import Route,Mount,WebSocketRoute
    from starlette.middleware import Middleware
    from starlette.websockets import WebSocket
    from starlette.middleware.sessions import SessionMiddleware
    from starlette.middleware.cors import CORSMiddleware
    #from starlette.middleware.csrf import CSRFMiddleware
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.staticfiles import StaticFiles

    import os
    import uuid
    #import uvicorn
    from uvicorn import Config, Server

    # Auth 
    #from starlette.middleware.sessions import SessionMiddleware
    from datetime import timedelta
    import secrets
    #from starlette_login.middleware import AuthenticationMiddleware

    #
    from starlette.requests import HTTPConnection
    from starlette.types import ASGIApp, Message, Receive, Scope, Send

    from starlette.datastructures import MutableHeaders
    import http.cookies
    import markupsafe
    from bs4 import BeautifulSoup
    import paramiko
    import asyncio
    import xml.etree.ElementTree as ET
    from xml.sax.saxutils import escape
    import untangle

    class NoCacheMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            response = await call_next(request)
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            response.headers["Server"] = "Starlette-Test"
            return response

except Exception as e:
    #import starlette
    import untangle
    import markupsafe
    from bs4 import BeautifulSoup
    
    import xml.etree.ElementTree as ET
    from xml.sax.saxutils import escape

class adapter(presentation.port):

    def widget_video(self, tag, inner, props):
        return self.code('video',{},inner)

    def widget_videomedia(self, tag, inner, props):
        pass
    
    def widget_column(self ,tag, inner, props):
        return self.code('div',{'class':'d-flex flex-row'},inner)
    
    def widget_row(self, tag, inner, props):
        return self.code('div',{'class':'d-flex flex-row'},inner)
    
    def widget_container(self, tag, inner, props):
        return self.code('div',{'class':'container-fluid'},inner)
    
    def widget_button(self, tag, inner, props):
        return self.code('button',{'class':'btn btn-primary','type':'button'},inner)
    
    def widget_list(self, tag, inner, props):
        return self.code('ul',{'class':'list-group'},inner)
    
    def widget_tree(self, tag, inner, props):
        return self.code('ul',{'class':'list-group'},inner)
    
    def widget_image(self, tag, inner, props):
        return self.code('image',{},inner)
    
    def widget_table(self, tag, inner, props):
        return self.code('table',{},inner)
    
    def widget_modal(self, tag, inner, props):
        return self.code('div', {'class': 'modal'}, inner)
    
    def widget_drawer(self, tag, inner, props):
        return self.code('div', {'class': 'modal'}, inner)
    
    def widget_window(self, tag, inner, props):
        return self.code('div', {'class': 'modal'}, inner)
    
    def widget_map(self, tag, inner, props):
        return self.code('div', {'class': 'modal'}, inner)
    
    def widget_chart(self, tag, inner, props):
        return self.code('div', {'class': 'modal'}, inner)
    
    def widget_tab(self, tag, inner, props):
        return self.code('div', {'class': 'modal'}, inner)
    
    def widget_scroll(self, tag, inner, props):
        return self.code('div', {'class': 'modal'}, inner)
    
    def widget_toast(self, tag, inner, props):
        return self.code('div', {'class': 'modal'}, inner)
    
    def widget_alert(self, tag, inner, props):
        return self.code('div', {'class': 'modal'}, inner)
    
    def widget_card(self, tag, inner, props):
        return self.code('div', {'class': 'card'}, inner)
    
    def widget_breadcrumb(self, tag, inner, props):
        return self.code('div', {'class': 'modal'}, inner)
    
    def widget_pagination(self, tag, inner, props):
        return self.code('div', {'class': 'modal'}, inner)
    
    def widget_carousel(self, tag, inner, props):
        return self.code('div', {'class': 'modal'}, inner)
    
    def widget_navigationbar(self, tag, inner, props):
        return self.code('div', {'class': 'modal'}, inner)
    
    def widget_navigationrail(self, tag, inner, props):
        return self.code('div', {'class': 'modal'}, inner)
    
    def widget_navigationapp(self, tag, inner, props):
        return self.code('div', {'class': 'modal'}, inner)
    
    def widget_navigationmenu(self, tag, inner, props):
        return self.code('div', {'class': 'modal'}, inner)
    
    def widget_text(self, tag, inner, props):
        return self.code('p', {'class': 'text'}, inner)
    
    def widget_input(self, tag, inner, props):
        ttype = props.get('type','text')
        match ttype:
            case 'text':
                return self.code('input', {'type': 'text'}, inner)
            case 'password':
                return self.code('input', {'type': 'text'}, inner)
            case _:
                return self.code('input', {'type': 'text'}, inner)
        return widget

    @flow.synchronous(managers=('defender',))
    def __init__(self,defender,**constants):
        self.config = constants['config']
        self.initialize()
        self.views = dict({})
        self.ssh = {}
        cwd = os.getcwd()

        routes=[
            Mount('/static', app=StaticFiles(directory=f'{cwd}/public/'), name="static"),
            Mount('/framework', app=StaticFiles(directory=f'{cwd}/src/framework'), name="y"),
            Mount('/application', app=StaticFiles(directory=f'{cwd}/src/application'), name="z"),
            Mount('/infrastructure', app=StaticFiles(directory=f'{cwd}/src/infrastructure'), name="x"),
            WebSocketRoute("/messenger", self.websocket, name="messenger"),
            WebSocketRoute("/ssh", self.websocketssh, name="ssh"),
        ]

        middleware = [
            Middleware(SessionMiddleware, session_cookie="session_state",secret_key=self.config['project']['key']),
            Middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*']),
            Middleware(NoCacheMiddleware),
            #Middleware(CSRFMiddleware, secret=self.config['project']['key']),
            #Middleware(AuthorizationMiddleware, manager=defender)
        ]

        loop = asyncio.get_event_loop()
        async def main():
            file = await self.host({'url':'application/policy/presentation/'+self.config.get('route','')})
            self.mount_route(file)
            self.mount_routes_from_list(routes)
            self.app = Starlette(debug=True,routes=routes,middleware=middleware)

            
            if 'ssl_keyfile' in self.config and 'ssl_certfile' in self.config:
                print('SSL')
                config = Config(app=self.app,host=self.config['host'], port=int(self.config['port']),ssl_keyfile=self.config['ssl_keyfile'],ssl_certfile=self.config['ssl_certfile'],use_colors=True,reload=True)
            else:
                config = Config(app=self.app, loop=loop,host=self.config['host'], port=int(self.config['port']),use_colors=True,reload=True)
            server = Server(config)

            loop.create_task(server.serve())
        loop.create_task(main())
    
    async def mount_css(self,constants):
        pass
        
    @flow.asynchronous(managers=('defender',))
    async def logout(self,request,defender) -> None:
        assert request.scope.get("app") is not None, "Invalid Starlette app"
        request.session.clear()
        response = RedirectResponse('/', status_code=303)
        response.delete_cookie("session_token")
        return response

    @flow.asynchronous(managers=('storekeeper', 'messenger','defender'))
    async def login(self, request, storekeeper,messenger, defender):
        """Gestisce il login dell'utente con autenticazione basata su IP e sessione."""
        
        client_ip = request.client.host
        session_identifier = request.cookies.get('session_identifier', secrets.token_urlsafe(16))
        
        # Determina le credenziali in base al metodo HTTP
        if request.method == 'GET':
            credentials = dict(request.query_params)
        elif request.method == 'POST':
            credentials = dict(await request.form())
        else:
            return RedirectResponse('/', status_code=400)  # Metodo non supportato

        # Autenticazione tramite defender
        session = await defender.authenticate(ip=client_ip, identifier=session_identifier, **credentials)
        print(session,credentials,'session.defender')
        provider = credentials.get('provider', 'undefined')

        
        # Aggiorna la sessione se l'autenticazione ha avuto successo
        #if session:
        #    request.session.update(session)

        # Crea la risposta di reindirizzamento
        response = RedirectResponse('/', status_code=303)

        # Imposta i cookie della sessione se non già presenti
        if 'session_identifier' not in request.cookies:
            response.set_cookie(key='session_identifier', value=session_identifier)
        
        #response.set_cookie(key='session', value=token, max_age=3600)
        response.set_cookie(key='session', value=session)
        
        await messenger.post(domain=f"error.{client_ip}",message=f"🔑 Login completato per IP: {client_ip} | con provider: {provider} | Session: {session_identifier}")

        return response

    @flow.asynchronous(managers=('messenger',))
    async def websocket(self, websocket, messenger):
        ip = websocket.client.host
        await websocket.accept()
        print(f"🔌 Connessione WebSocket da {ip}")

        #ws_queue = asyncio.Queue()  # Coda per i messaggi WebSocket
        #messenger_queue = asyncio.Queue()  # Coda per i messaggi di Messenger
        stop_event = asyncio.Event()  # Evento per fermare il loop quando necessario

        async def listen_websocket():
            try:
                while not stop_event.is_set():
                    msg = await websocket.receive_text()
                    print(f"📥 Messaggio dal client: {msg}")
                    await websocket.send_text(msg)
            except Exception:
                stop_event.set()  # Ferma il ciclo se il WebSocket si chiude

        async def listen_for_updates():
            while not stop_event.is_set():
                msg = await messenger.read(domain='*',identity=ip)
                print(f"📨 Messaggio dal server: {msg}")
                #await messenger_queue.put(msg)
                await websocket.send_text(msg)
    
    @flow.asynchronous(managers=('defender',))
    async def websocketssh(self, websocket, defender):
        ip = websocket.client.host

        # Sessione di autenticazione
        session = await defender.whoami(ip=ip)
        await websocket.accept()

        try:
            # Riceve parametri iniziali
            initial_message = await websocket.receive_text()
            print(f"Sessione {session} con messaggio iniziale: {initial_message}")
            params = json.loads(initial_message)
            username = params.get("username")
            password = params.get("password")
            host = params.get("host")

            # Connessione SSH
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, username=username, password=password)
            channel = ssh.invoke_shell()

            # Invia la risposta iniziale del terminale (banner, prompt, ecc.)
            if channel.recv_ready():
                initial_response = channel.recv(1024).decode('utf-8')
                await websocket.send_text(initial_response)

            # Lettura dati da SSH → WebSocket
            async def read_from_channel():
                while True:
                    if websocket.client_state.name != "CONNECTED":
                        break
                    if channel.recv_ready():
                        data = channel.recv(1024).decode('utf-8')
                        await websocket.send_text(data)
                    await asyncio.sleep(0.01)

            # Lettura dati da WebSocket → SSH
            async def read_from_websocket():
                while True:
                    data = await websocket.receive_text()
                    if data:
                        channel.send(data)

            await asyncio.gather(read_from_channel(), read_from_websocket())

        except Exception as e:
            print(f"Errore durante la sessione SSH-WebSocket: {e}")
            
        finally:
            try:
                if channel:
                    channel.close()
                if ssh:
                    ssh.close()
                print(f"Sessione SSH chiusa per {session}")
            except Exception as close_err:
                print(f"Errore durante la chiusura SSH: {close_err}")
    
    @flow.asynchronous(managers=('storekeeper','messenger'))
    async def action(self, request, storekeeper, messenger, **constants):
        #print(request.cookies.get('user'))
        match request.method:
            case 'GET':
                query = dict(request.query_params)
                #await messenger.post(identifier=id,name=request.url.path[1:],value=dict(query))
                #data = await messenger.get(identifier=id,name=request.url.path[1:],value=dict(query))
                import application.action.gather as gather
                
                data = await gather.gather(messenger,storekeeper,model=query['model'],payload=query)
                return JSONResponse(data)
                
            case 'POST':
                form = await request.form()
                data = dict(form)
                
                request.scope["user"] = data
                #await messenger.post(name=request.url.path[1:],value={'model':data['model'],'value':data})
                return RedirectResponse('/', status_code=303)

    async def apply_view(self,url):
        url = self.routes.get(url,{}).get('view')
        return await self.builder(url=url)
    
    async def starlette_view(self,request):
        html_body = await self.apply_view(request.url.path)
        layout = 'application/view/layout/base.html'
        file = await self.host({'url':layout})
        css = await self.host({'url':layout.replace('.html','.css').replace('.xml','.css')})
        #template = self.env.from_string(file.replace('{% block style %}','{% block style %}<style>'+css+'</style>'))
        template = self.env.from_string(file)
        content = template.render()
        content = content.replace('<!-- Body -->',html_body)
        return HTMLResponse(content)
    
    def code(self,tag,attr,inner=[]):
        att = ''
        html = ''
        for key in attr:
            att += f' {key}="{attr[key]}"'
        if type(inner) == type([]):
            for item in inner:
                html += item
            return f'<{tag} {att} >{html}</{tag}>'
        elif  type(inner) == type(''):
            return f'<{tag} {att} >{inner}</{tag}>'
        else:
            return f'<{tag} {att} />'

    def code_update(self, view, attr={}, inner=[], position='end'):
        """
        Modifica una vista HTML già esistente (stringa):
        - aggiorna gli attributi secondo 'attr'
        - aggiunge i figli di 'inner' (lista di stringhe HTML/XML) come figli del nodo root
        in base a 'position': 'start' (inizio) o 'end' (fine, default)
        """
        soup = BeautifulSoup(view, 'html.parser')
        root = soup.find()  # Prende il primo nodo root

        # Aggiorna attributi
        if root and attr:
            for key, value in attr.items():
                root[key] = value

        # Aggiungi nuovi figli
        if root and inner:
            if position == 'start':
                for item in reversed(inner):  # reversed per mantenere l'ordine originale
                    child = BeautifulSoup(item, 'html.parser')
                    for c in reversed(child.contents):
                        root.insert(0, c)
            else:  # 'end' (default)
                for item in inner:
                    child = BeautifulSoup(item, 'html.parser')
                    for c in child.contents:
                        root.append(c)

        return str(soup)
         
    async def set_attribute(self, widget, attributes, field, value):
        print(widget, attributes, field, value)
        return self.code_update(widget,{field:value})

    async def get_attribute(self, widget, field):
        
        def extract_attribute(html: str, attribute: str) -> str | None:
            import re
            pattern = fr'{attribute}\s*=\s*["\'](.*?)["\']'
            match = re.search(pattern, html)
            return match.group(1) if match else None
        match field:
            case 'elements':
                a = getattr(widget,'controls',None)
                if a:
                    return a
                a = getattr(widget,'content',None)
                if a:
                    return await self.get_attribute(a,'elements')
            case 'class':
                return getattr(widget,'class_name',None)
            case _:
                return extract_attribute(widget,field)

    async def selector(self, **constants):
        for key in constants:
            value = constants[key]
            match key:
                case 'id':
                    return [self.document[value]]

    async def apply_css(self, *services, **constants):
        
        '''styles = parse_css_tinycss2(ttt)
        #print('style:',styles)
        for key in self.document:
            widget = self.document[key]
            await self.apply_style(widget, styles)'''
        pass

    async def apply_route(self, *services, **constants):
        pass

    def mount_routes_from_list(self, routes):
        for path, data in self.routes.items():
            typee = data.get('type')
            method = data.get('method')
            view = data.get('view')

            # Associa il path alla view (utile per debug o reverse lookup)
            self.views[path] = view

            # Se è una mount statica
            if typee == 'mount' and path == '/static':
                r = Mount(path, app=StaticFiles(directory='/public'), name="static")
                routes.append(r)
                continue

            # Determina l'endpoint
            if typee == 'model':
                endpoint = self.model
            elif typee == 'view':
                endpoint = self.starlette_view
            elif typee == 'action':
                endpoint = self.action
            elif typee == 'login':
                endpoint = self.login
            elif typee == 'logout':
                endpoint = self.logout
            else:
                endpoint = self.default_handler  # fallback o gestione errori

            # Crea la rotta e aggiungila
            r = Route(path, endpoint=endpoint, methods=[method])
            routes.append(r)