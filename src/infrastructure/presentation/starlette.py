import uuid
import asyncio
from html import escape
import re
import json
from datetime import datetime
import copy

resources = {'flow': 'framework/service/flow.py','presentation': 'framework/port/presentation.py'}

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
    
    attributes = {
        # Attributi HTML diretti
        'matter': {
            'id', 'type', 'name', 'component', 'draggable-event','height', 'width',
            'draggable-maker', 'droppable-data', 'identifier','draggable-component','src','value'
        },

        # Mappatura eventi
        'event': {
            ''''click': ('click', self.event),
            'change': ('change', self.event),
            'route': ('click', self.route),
            'ddd': ('contextmenu', self.open_dropdown),
            'draggable': ('dragstart', self.on_drag_start),
            'droppable': ('drop', self.on_drop),
            'init': ('init', self.event),'''
        },

        # Mappatura layout
        'layout': {
            'space': lambda v: f"gap-{v}",
            'border': lambda v: f"border-{v}",
            'border-top': lambda v: f"border-top-{v}",
            'border-bottom': lambda v: f"border-bottom-{v}",
            'border-left': lambda v: f"border-start-{v}",
            'border-right': lambda v: f"border-end-{v}",
            'border-radius': lambda v: f"rounded-{v}",

            'margin': lambda v: ' '.join(v.strip() for v in v.split(';')),
            'margin-top': lambda v: 'mt-' + v,
            'margin-bottom': lambda v: 'mb-' + v,
            'margin-left': lambda v: 'ms-' + v,
            'margin-right': lambda v: 'me-' + v,

            'padding-top': lambda v: 'pt-' + v,
            'padding-bottom': lambda v: 'pb-' + v,
            'padding-left': lambda v: 'ps-' + v,
            'padding-right': lambda v: 'pe-' + v,
            'padding': lambda v: ' '.join(v.strip() for v in v.split(';')),

            'position': lambda v: {
                'static': 'position-static',
                'relative': 'position-relative',
                'absolute': 'position-absolute',
                'fixed': 'position-fixed',
                'sticky': 'position-sticky',
            }.get(v,''),
            'expand': lambda v: {
                'vertical': 'h-100',
                'horizontal': 'w-100',
                'full': 'w-100 h-100',
                'auto': 'col-auto',
                'dynamic': 'col'
            }.get(v, f"col-{v}"),
            'collapse': lambda v: 'd-none' if v == 'full' else 'invisible',
            'alignment-horizontal': lambda v: f"justify-content-{v}" if v in ['start', 'end', 'center', 'between', 'around', 'evenly'] else '',
            'alignment-vertical': lambda v: f"align-items-{v}" if v in ['start', 'end', 'center', 'baseline', 'stretch'] else '',
            'alignment-content': lambda v: {
                    'vertical': 'd-flex flex-column',
                    'horizontal': 'd-flex flex-row',
                    'center': 'd-flex justify-content-center align-items-center',
                    'between': 'd-flex justify-content-between align-items-center',
                    'around': 'd-flex justify-content-around align-items-center',
                    'evenly': 'd-flex justify-content-evenly align-items-center',    
                }.get(v, ''),
        },

        # Mappatura classi CSS
        'style': {
            'background': lambda v: f"bg-{v}" if not v.startswith('#') else None,
            'background-color': lambda v: f"bg-{v}" if not v.startswith('#') else None,
            'text-color': lambda v: f"text-{v}",
            'text-size': lambda v: f"fs-{v}" if v.isdigit() else None,
            'shadow': lambda v: {
                '0': 'shadow-none', '1': 'shadow-sm',
                '2': 'shadow', '3': 'shadow-lg'
            }.get(v, ''),
            'opacity': lambda v: f"opacity-{v}" if v.isdigit() else None,
            'border': lambda v: f"border-{v}",
            'border-thickness': lambda v: f"border-{v}",
            'border-radius-size': lambda v: f"rounded-{v}",
            'border-color': lambda v: f"border-{v}",
            'border-radius': lambda v: {
                'pill': "rounded-pill", 'circle': "rounded-circle",
                'top': "rounded-top", 'bottom': "rounded-bottom",
                'right': "rounded-start", 'left': "rounded-end"
            }.get(v, ''),
            'border-position': lambda v: {
                'outer': "border", 'top': "border-top", 'bottom': "border-bottom",
                'right': "border-start", 'left': "border-end"
            }.get(v, ''),
            'class': lambda v: v
        }
    }

    WIDGETS = {
        'accordion': {
            'tag': 'div',
            'attributes': {'class': 'accordion'},
            '!attributes': {'id':['accordion-item']},
            'case': lambda attributes: {
                'accordion': ('div', {'class': 'accordion', 'id': attributes.get('id', 'test')}),
                'accordion-item': ('div', {'class': 'accordion-item'}),
            }.get(attributes.get('type', 'accordion')),
            'inner_overwrite': lambda adapter, attributes, inner: {
                'accordion': ({'class': 'accordion-item'}, ''),
            }.get('accordion'),
            'inner_last': lambda adapter, attributes, inner,father: {
                'accordion-item': ({'class': 'accordion-collapse collapse ','id':attributes.get('id',''),'data-bs-parent':'#test'}, ""),
            }.get(attributes.get('type')),
            'inner_first': lambda adapter, attributes, inner,father: {
                'accordion-item': ({'class': 'accordion-header', 'id':'h'+attributes.get('id')}, adapter.code('button', {'class': 'accordion-button collapsed', 'type': 'button', 'data-bs-toggle': 'collapse', 'data-bs-target': f'#{father.get("id")}', 'aria-expanded': 'false', 'aria-controls': attributes.get('id')}, inner[0])),
            }.get(attributes.get('type')),
        },
        'defender': {
            'tag': 'div',
            'attributes': {'class': 'container-fluid'},
        },
        'storekeeper': {
            'tag': 'div',
            'attributes': {'class': 'container-fluid'},
        },
        'presenter': {
            'tag': 'div',
            'attributes': {'class': 'container-fluid'},
        },
        'view': {
            'tag': 'div',
            'attributes': {'class': 'container-fluid'},
        },
        'divider': {
            'tag': 'div',
            'attributes': {'class': 'container-fluid'},
        },
        'embed': {
            'tag': 'iframe',
        },
        'icon': {
            'tag': 'i',
            'attributes': {'class': 'bi'},
            'case': lambda attributes: {
                'icon': ('i', {'class': f"bi {attributes.get('src', '')}"}),
            }.get(attributes.get('type', 'icon')),
        },
        'badge': {
            'tag': 'span',
            'attributes': {'class': 'badge'},
            'case': lambda attributes: {
                'primary': ('span', {'class': 'badge bg-primary'}),
                'secondary': ('span', {'class': 'badge bg-secondary'}),
                'success': ('span', {'class': 'badge bg-success'}),
                'danger': ('span', {'class': 'badge bg-danger'}),
                'warning': ('span', {'class': 'badge bg-warning'}),
                'info': ('span', {'class': 'badge bg-info'}),
                'light': ('span', {'class': 'badge bg-light text-dark'}),
                'dark': ('span', {'class': 'badge bg-dark'}),
            }.get(attributes.get('type', 'primary')),
        },
        'data': {
            'tag': 'data',
            'attributes': {},
            'case': lambda attributes: {
                'text': ('span', {'class': 'placeholder'}),
                'table': ('table', {'class': 'table table-striped'}),
                'table.row': ('tr', {}),
                'table.cell': ('td', {}),
                'table.header': ('thead', {}),
                'table.body': ('tbody', {'class': 'table-body'}),
            }.get(attributes.get('type')),
            'wrapper_once': lambda adapter, attributes, inner: {
                #'table': lambda adapter, attributes, inner: adapter.code('sadsadsads', {}, inner),
                'table.header': lambda adapter, attributes, inner: adapter.code('tr', {}, inner),
                #'table.row': lambda adapter, attributes, inner: adapter.code('tr', {'class': 'table-row'}, inner),
            }.get(attributes.get('type', 'text')),
            'wrapper_each': lambda adapter, attributes, inner: {
                'table.row': lambda adapter, attributes, inner: adapter.code('td', {}, inner),
                #'table.cell': lambda adapter, attributes, inner: adapter.code('td', {'class': 'table-cell'}, inner),
                #'table.header': lambda adapter, attributes, inner: adapter.code('th', {'class': 'table-header'}, inner),
                #'table.body': lambda adapter, attributes, inner: adapter.code('tbody', {'class': 'table-body'}, inner),
            }.get(attributes.get('type', 'text')),
        },
        'video': {
            'tag': 'video',
        },
        'videomedia': {
            'tag': 'videomedia',
        },
        'column': {
            'tag': 'div',
            'attributes': {'class': 'd-flex flex-column'}
        },
        'row': {
            'tag': 'div',
            'attributes': {'class': 'd-flex flex-row'}
        },
        'container': {
            'tag': 'div',
            'attributes':{'class': 'container-fluid'}
        },
        'list': {
            'tag': 'ul',
            'attributes': {'class': 'list-group'}
        },
        'tree': {
            'tag': 'ul',
            'attributes': {'class': 'list-group'}
        },
        'image': {
            'tag': 'img',
        },
        'table': {
            'tag': 'table',
        },
        'card': {
            'tag': 'div',
            'attributes': {'class': 'card'},
            'wrapper_once':lambda adapter,attributes,inner: {
                'card': lambda adapter,attributes,inner: adapter.code('div', {'class':'card-body'}, inner),
            }.get('card')
        },
        'text': {
            'tag': 'p',
            'attributes': {'class': 'text'}
        },
        'input': {
            'tag': 'input',
            'case': lambda attributes: {
                'select':  ('select', {'class': 'form-select'}),
            }.get(attributes.get('type', 'text'), ('input', {'class': 'form-control', 'type': attributes.get('type','text')})),
            'wrapper_each':lambda adapter,attributes,inner: {
                'select': lambda adapter,attributes,inner: adapter.code('option', {}, inner),
            }.get(attributes.get('type', 'text'))
        },
        'action': {
            'tag': None,  # Determinato dinamicamente
            'case': lambda attributes: {
                'submit':  ('button', {'class': 'btn', 'type': 'submit'}),
                'reset':   ('button', {'class': 'btn', 'type': 'reset'}),
                'link':    ('a',      {'class': 'btn btn-link', 'href': attributes.get('route', '/'),'data-bs-toggle': 'offcanvas' }),
                'button':  ('button', {'class': 'btn', 'type': 'button'}),
                'form':    ('form', {'class': 'form-control', 'method': 'POST'}),
                'dropdown': ('div', {'class': 'dropdown'}),
            }.get(attributes.get('type')),
            'wrapper_each': lambda adapter, attributes, inner: {
                'dropdown': lambda adapter, attributes, inner: adapter.code('li', {}, inner),
            }.get(attributes.get('type')),
            'wrapper_once': lambda adapter, attributes, inner: {
                'dropdown': lambda adapter, attributes, inner: adapter.code('div', {'class': 'dropdown'}, [adapter.code('button', {'class':'btn btn-secondary dropdown-toggle','type':"button", 'data-bs-toggle':"dropdown", 'aria-expanded':"false"}, inner[0]),adapter.code('ul', {'class': 'dropdown-menu'}, inner[1:])]),
            }.get(attributes.get('type')),
            'inner_overwrite': lambda adapter, attributes, inner: {
                'dropdown': ({'class':'dropdown-item'},''),
            }.get(attributes.get('type')),
        },
        'messenger': {
            'tag': 'div',
            'attributes': {},
            'wrapper_once': lambda adapter, attributes, inner: {
                'messenger': lambda adapter, attributes, inner: adapter.code('div', {'class': 'messenger-body'}, inner),
            }.get(attributes.get('type')),
        },
        'message': {
            'case': lambda attributes: {
                'alert':  ('div', {'class': f"alert alert-{attributes.get('type')}", 'role': 'alert'}),
            }.get(attributes.get('mode', 'alert'))
        },
        'group': {
            'case': lambda attributes: {
                'input':  ('div', {'class': 'input-group'}),
                'list': ('ul', {'class': 'list-group'}),
                'card': ('ul', {'class': 'card-group'}),
                'tab': ('div', {'class': 'tab-content'}),
            }.get(attributes.get('type')),
            'wrapper_each':lambda adapter,attributes,inner: {
                'list': lambda adapter,attributes,inner: adapter.code('li', {'class':'list-group-item'}, inner),
                'tab' : lambda adapter,attributes,inner: adapter.code('div', {'class':'tab-pane'}, inner),
            }.get(attributes.get('type'))
        },
        'editor': {
            'tag': 'form',
        },
        'window': {
            'tag': 'div',
            'attributes': {'class': 'window'},
            'case': lambda attributes: {
                'dialog': ('div', {'class': 'modal-dialog'}),
                'offcanvas': ('div', {'class': 'offcanvas'}),
                'root': ('html', {'class': 'h-100', 'data-navigation-type': 'default', 'data-navbar-horizontal-shape': 'default', 'lang': 'it', 'dir': 'ltr'}),
            }.get(attributes.get('type', 'dialog')),
            'wrapper_once': lambda adapter, attributes, inner: {
                'root': lambda adapter, attributes, inner: [
                    adapter.code('head', {}, f"""
                        <meta charset="utf-8">
                        <meta http-equiv="X-UA-Compatible" content="IE=edge">
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <meta http-equiv='cache-control' content='no-cache'>
                        <meta http-equiv='expires' content='0'>
                        <meta http-equiv='pragma' content='no-cache'>
                        <!-- ===============================================-->
                        <!--    Document Title-->
                        <!-- ===============================================-->
                        <title>{attributes.get('title','')}</title>
                
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
                        
                        <link rel="stylesheet" href="https://unpkg.com/xterm/css/xterm.css" />
                        <script src="https://unpkg.com/xterm/lib/xterm.js"></script>
                        <script src="https://unpkg.com/xterm-addon-fit/lib/xterm-addon-fit.js"></script>
                        <!-- ===============================================-->
                        <!--    Javascript-->
                        <!-- ===============================================-->
                        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
                        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
                        <script src="https://cdnjs.cloudflare.com/ajax/libs/dragula/3.7.3/dragula.min.js" integrity="sha512-NgXVRE+Mxxf647SqmbB9wPS5SEpWiLFp5G7ItUNFi+GVUyQeP+7w4vnKtc2O/Dm74TpTFKXNjakd40pfSKNulg==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>  
                    """),
                    adapter.code('body', {'class':"d-flex h-100 flex-column",'id':attributes.get('id')}, inner)
                ]
            }.get(attributes.get('type')),
        },
        'chart': {
            'tag': 'div',
            'attributes': {'class': 'chart'}
        },
        'tab': {
            'tag': 'div',
            'attributes': {'class': 'tab-content'},
            'wrapper_each': lambda adapter, attributes, inner: {
                'tab': lambda adapter, attributes, inner: adapter.code('div', {'class': 'tab-pane fade', 'role': 'tabpanel'}, inner),
            }.get(attributes.get('type')),
            'wrapper_once': lambda adapter, attributes, inner: {
                'tab': lambda adapter, attributes, inner: adapter.code('div', {'class': 'tab-content'}, inner),
            }.get(attributes.get('type')),
            'inner_overwrite': lambda adapter, attributes, inner: {
                'tab': ({'class':'nav-link active', 'data-bs-toggle':'tab', 'role':'tab'},''),
            }.get(attributes.get('type')),
        },
        'scroll': {
            'tag': 'div',
            'attributes': {'class': 'scroll'}
        },
        'offcanvas': {
            'tag': 'div',
            'attributes': {'class': 'offcanvas h-100', 'tabindex': '-1'},
            'wrapper_once': lambda adapter, attributes, inner: {
                'still': lambda adapter, attributes, inner: adapter.code('div',{},[
                    adapter.code('div', {'class': 'offcanvas-header'}, inner),
                    adapter.code('div', {'class': 'offcanvas-body'}, inner),
                    
                ])
            }.get(attributes.get('type')),
        },
        'modal': {
            'tag': 'div',
            'attributes': {'class': 'modal', 'tabindex': '-1', 'role': 'dialog'},
            'wrapper_once': lambda adapter, attributes, inner: {
                'dialog': lambda adapter, attributes, inner: adapter.code('div', {'class': 'modal-dialog'}, [adapter.code('div', {'class': 'modal-content'}, [
                    adapter.code('div', {'class': 'modal-header'}, inner), 
                    adapter.code('div', {'class': 'modal-body'}, inner),
                    adapter.code('div', {'class': 'modal-footer'}, inner)
                ])])
            }.get(attributes.get('type')),
        },
        'toast': {
            'tag': 'div',
            'attributes': {'class': 'toast'}
        },
        'alert': {
            'tag': 'div',
            'attributes': {'class': 'alert'}
        },
        'breadcrumb': {
            'tag': 'nav',
            'attributes': {},
            'wrapper_each': lambda adapter, attributes, inner: {
                'breadcrumb': lambda adapter, attributes, inner: adapter.code('li', {'class': 'breadcrumb-item'}, inner),
            }.get(attributes.get('type')),
            'wrapper_once': lambda adapter, attributes, inner: {
                'breadcrumb': lambda adapter, attributes, inner: adapter.code('ol', {'class': 'breadcrumb'}, inner),
            }.get(attributes.get('type')),
        },
        'pagination': {
            'tag': 'nav',
            'attributes': {'class': 'pagination'},
            'wrapper_each': lambda adapter, attributes, inner: {
                'pagination': lambda adapter, attributes, inner: adapter.code('li', {'class': 'page-item'}, inner),
            }.get(attributes.get('type')),
            'wrapper_once': lambda adapter, attributes, inner: {
                'pagination': lambda adapter, attributes, inner: adapter.code('ul', {'class': 'pagination'}, inner),
            }.get(attributes.get('type')),
            'inner_overwrite': lambda adapter, attributes, inner: {
                'pagination': ({'class':'page-link'},''),
            }.get(attributes.get('type')),
        },
        'carousel': {
            'tag': 'div',
            'attributes': {'data-bs-ride':'carousel','class':'carousel slide'},
            'wrapper_each':lambda adapter,attributes,inner: {
                'carousel': lambda adapter,attributes,inner: adapter.code('div', {'class':'carousel-item w-100 h-100'}, inner),
            }.get(attributes.get('type')),
            'wrapper_once':lambda adapter,attributes,inner: {
                'carousel': lambda adapter,attributes,inner: adapter.code('div', {'class':'carousel-inner w-100 h-100'}, inner),
            }.get(attributes.get('type')),
            'inner_first': lambda adapter, attributes, inner,father: {
                'carousel': ({'class':'carousel-item w-100 h-100 active'},''),
            }.get(attributes.get('type')),
        },
        'bar': {
            'tag': 'div',
            'attributes': {'class': 'navigation'},
            'case': lambda attributes: {
                'horizontal':  ('div', {'class': 'navbar'}),
                'vertical': ('div', {'class': 'sidebar'}),
            }.get(attributes.get('orientation')),
        },
    }

    @flow.synchronous(managers=('defender',))
    def __init__(self,defender,**constants):
        self.config = constants.get('config', {})
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
            Middleware(SessionMiddleware, session_cookie="session_state",secret_key=self.config.get('project',{}).get('key', 'default_key')),
            Middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*']),
            Middleware(NoCacheMiddleware),
            #Middleware(CSRFMiddleware, secret=self.config['project']['key']),
            #Middleware(AuthorizationMiddleware, manager=defender)
        ]

        loop = asyncio.get_event_loop()
        async def main():
            try:
                # Costruisce l'URL per il fetch, gestendo il caso di percorso vuoto
                route_path = self.config.get('route', '')
                resource_url = f"application/policy/presentation/{route_path}"

                file = await self.fetch_resource({'url': resource_url})
                self.parse_route(file)
                self.mount_route(routes) # 'routes' deve essere accessibile qui

            except Exception as e:
                # Logga qualsiasi errore durante il caricamento delle rotte
                print(f"Errore durante il caricamento delle rotte: {e}")
                # Considera di sollevare l'eccezione o terminare se l'app non può partire senza rotte

            # Inizializza l'applicazione Starlette con rotte e middleware
            self.app = Starlette(debug=True, routes=routes, middleware=middleware)

            # Parametri di configurazione base per Uvicorn
            uvicorn_config_params = {
                "app": self.app,
                "host": self.config.get('host', '127.0.0.1'),
                "port": int(self.config.get('port', 8000)),
                "use_colors": True,
                "reload": True, # `reload=True` solo per sviluppo
                "loop": loop
            }

            # Aggiunge i parametri SSL se presenti
            if 'ssl_keyfile' in self.config and 'ssl_certfile' in self.config:
                print("SSL abilitato.")
                uvicorn_config_params['ssl_keyfile'] = self.config['ssl_keyfile']
                uvicorn_config_params['ssl_certfile'] = self.config['ssl_certfile']
            else:
                print("SSL disabilitato.")

            try:
                # Crea e avvia il server Uvicorn come task asyncio
                config = Config(**uvicorn_config_params)
                server = Server(config)
                loop.create_task(server.serve())
                print(f"Server avviato su {uvicorn_config_params['host']}:{uvicorn_config_params['port']}")
            except Exception as e:
                # Logga errori critici all'avvio del server
                print(f"Errore critico durante l'avvio del server Uvicorn: {e}")
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

    async def mount_view(self,url):
        url = self.routes.get(url,{}).get('view')
        return await self.builder(url=url)
    
    async def starlette_view(self,request):
        html = await self.mount_view(request.url.path)
        print(html, "html_body**********************",request.url.path)
        '''layout = 'application/view/layout/base.html'
        file = await self.fetch_resource({'url':layout})
        css = await self.fetch_resource({'url':layout.replace('.html','.css').replace('.xml','.css')})
        #template = self.env.from_string(file.replace('{% block style %}','{% block style %}<style>'+css+'</style>'))
        template = self.env.from_string(file)
        content = template.render()
        content = content.replace('<!-- Body -->',str(html_body))'''
        #return HTMLResponse(content)
        return HTMLResponse('<!DOCTYPE html>'+html)
        
    def code(self, tag, attr, inner=[]):
        att = ''
        html = ''

        '''for key, value in attr.items():
            # Gestione attributi booleani: True o "true" → solo nome attributo
            if value.lower() == "true":
                att += f' {key}'
            else:
                att += f' {key}="{value}"'''
        if isinstance(inner, list):
            for item in inner:
                html += str(item)
            if len(inner) > 0:
                ele = f'<{tag}{att}>{html}</{tag}>'
            else:
                ele = f'<{tag}{att}/>'
        elif isinstance(inner, str):
            ele = f'<{tag}{att}>{inner}</{tag}>'
        else:
            ele = f'<{tag}{att}/>'
        
        return self.att(ele, attr)

    def att(self, element, attributes):
            
            def set_style(css, element):
                style = self.get_attribute(element, 'style')
                if style is not str:
                    style = ''
                
                style += f" {css}"
                element = self.set_attribute(element, 'style', style.strip())
                print(style, 'style',element)
                return element

            def add_class(cls, element, current_classes=''):
                value = self.get_attribute(element, 'class')
                # + f" {cls}" if current_classes else cls
                #if cls is str:
                if value is not str:
                    value = ''
                value += cls
                out = self.set_attribute(element, 'class', current_classes + f" {cls} ")
                #print(f"old:{element}| old: {value} - new: {cls} |return: {out}")
                return out

                

            for key, value in attributes.items():
                #print(key, value, 'key,value')
                if key in self.attributes['matter']:
                    if key == 'width':
                      element = set_style(f'max-width:{value};width:{value};', element)
                    elif key == 'height':
                      element = set_style(f'max-height:{value};height:{value};', element)
                    else:
                      element = self.set_attribute(element, key, value)
                      #element.setAttribute(key, value)

                elif key in self.attributes['event']:
                    if key == 'init':
                        #print(f"[DEBUG] Executor: {executor}",value,key)
                        #asyncio.create_task(executor.act(action=value))
                        pass
                    elif key == 'hide':
                        mode, _ = map(str.strip, value.split(':'))
                        #element.setAttribute('data-bs-dismiss', mode)
                        self.set_attribute(element, 'data-bs-dismiss', mode)
                    elif key == 'show':
                        mode, target = map(str.strip, value.split(':'))
                        element.setAttribute('data-bs-target', f'#{target}')
                        element.setAttribute('data-bs-toggle', mode)
                    elif key == 'route' and ':' in value:
                        mode, target = map(str.strip, value.split(':', 1))
                        if mode == 'link':
                            element.setAttribute('href', target)
                        else:
                            element.setAttribute('data-bs-toggle', mode)
                            element.setAttribute('href', f'#{target}')
                    elif key == 'link':
                        element.setAttribute('href', value)
                    elif key == 'draggable':
                        element.setAttribute(key,'true')
                        element.setAttribute('ondragstart','drag(event)')
                        element.setAttribute('draggable-domain',value)
                        #element.addEventListener('dragstart',pyodide.ffi.create_proxy(self.on_drag_start))
                        #element.addEventListener('dragend',pyodide.ffi.create_proxy(self.on_drag_end))
                    elif key == 'droppable':
                        element.setAttribute('ondragover','allowDrop(event)')
                        element.setAttribute('draggable-domain',value)
                        #element.addEventListener('drop',pyodide.ffi.create_proxy(self.on_drop))
                        #element.addEventListener('dragover',pyodide.ffi.create_proxy(self.on_drag_over))
                        #element.addEventListener('dragleave',pyodide.ffi.create_proxy(self.on_drag_leave))
                    else:
                      event_name, handler_fn = self.attributes['event'][key]
                      #element.setAttribute('event', value)
                      element.setAttribute(key, value)
                      #element.addEventListener(event_name, pyodide.ffi.create_proxy(handler_fn))

                elif key in self.attributes['style']:
                    mapping = self.attributes['style'][key]
                    cls = mapping(value) if callable(mapping) else mapping.get(value, f"{key}-{value}")
                    if cls:
                        element = add_class(cls, element)
                    elif key == 'background-color' and value.startswith('#'):
                        element = set_style(f'background-color:{value};', element)
                    elif key == 'text-size' and 'px' in value:
                        element = set_style(f'font-size: {value};', element)
                    elif key == 'style':
                        element = set_style(value, element)
                elif key in self.attributes['layout']:
                    mapping = self.attributes['layout'][key]
                    cls = mapping(value) if callable(mapping) else mapping.get(value, f"{key}-{value}")
                    #print(cls, 'CLSSSSSSSSSSSSS')
                    #if key == 'class':
                    if cls:
                        old = self.get_attribute(element, 'class')
                        element = add_class(cls,element,old)
                else:
                    # Attributi non riconosciuti, li aggiunge come sono
                    element = self.set_attribute(element, key, value)
                    #element.setAttribute(key, value)
                
            
            return element

    def code2(self, tag, attributes, inner=None):
        """
        Genera HTML a partire da tag, attributi e contenuto,
        applicando le regole definite in self.attributes.
        """
        if attributes is None:
            attributes = {}
        if inner is None:
            inner = []

        rendered_attrs = []

        for key, value in attributes.items():
            # Applica le trasformazioni dal dizionario attributi
            handler = self.attributes.get(key)

            if handler is None:
                transformed = value
            elif callable(handler):
                transformed = handler(value)
            elif isinstance(handler, tuple):
                # Eventi (es: click, change...)
                event_type, callback = handler
                transformed = f"{event_type}:{callback.__name__}"
            elif handler is True:
                # Attributi "matter": usa il valore così com’è
                transformed = value
            else:
                transformed = value

            # Se la trasformazione restituisce None → non renderizzare
            if transformed is None:
                continue

            # Gestione attributi booleani
            if isinstance(transformed, bool) and transformed:
                rendered_attrs.append(f"{key}")
            else:
                rendered_attrs.append(f'{key}="{transformed}"')

        # Costruzione finale degli attributi
        attr_str = " " + " ".join(rendered_attrs) if rendered_attrs else ""

        # Costruzione del contenuto interno
        if isinstance(inner, list):
            html = "".join(str(item) for item in inner)
            if html:
                return f"<{tag}{attr_str}>{html}</{tag}>"
            else:
                return f"<{tag}{attr_str}/>"
        elif isinstance(inner, str):
            return f"<{tag}{attr_str}>{inner}</{tag}>"
        else:
            return f"<{tag}{attr_str}/>"

    def code_update(self, view, attr=None, inner=None, mode=[]):
        """
        Modifies an existing HTML view (string):
        - updates or sets attributes based on 'attr' dictionary.
        - handles 'inner' depending on 'mode':
            * ["append", "end"] (default): adds 'inner' at the end
            * ["append", "start"]: adds 'inner' at the beginning
            * ["replace"]: replaces the innerHTML entirely

        Args:
            view (str): The HTML string to be modified.
            attr (dict, optional): A dictionary of attributes to set or update.
                                If a value is None, the attribute will be removed.
                                Defaults to None.
            inner (list|str, optional): A list (or single string) of HTML/XML to add or replace.
                                        Defaults to None.
            mode (list, optional): Controls behavior of inner insertion.
                                - ["append", "end"] (default)
                                - ["append", "start"]
                                - ["replace"]

        Returns:
            str: The modified HTML string.
        """
        if not isinstance(view, str) or not view.strip():
            return view  

        soup = BeautifulSoup(view, 'html.parser')
        root = soup.find()  

        if not root:
            return view 

        # --- Update/Remove Attributes ---
        if attr:
            for key, value in attr.items():
                if not isinstance(key, str) or not key.strip() or ' ' in key.strip():
                    continue 
                if value is None:
                    if key in root.attrs:
                        del root[key]
                else:
                    root[key] = str(value)

        # --- Normalize mode ---
        if not mode:
            mode = ["append", "end"]
        if isinstance(mode, str):
            mode = [mode]

        # --- Handle Inner Content ---
        if inner is not None:
            if not isinstance(inner, list):
                inner = [inner]

            if "replace" in mode:
                root.clear()
                for item_html in inner:
                    try:
                        child_soup = BeautifulSoup(item_html, 'html.parser')
                        if child_soup.contents:
                            for child_element in child_soup.contents:
                                root.append(child_element)
                    except Exception:
                        continue

            elif "append" in mode:
                pos = "end"
                if len(mode) > 1 and mode[1] in ("start", "end"):
                    pos = mode[1]

                if pos == "start":
                    for item_html in reversed(inner):
                        try:
                            child_soup = BeautifulSoup(item_html, 'html.parser')
                            if child_soup.contents:
                                for child_element in reversed(child_soup.contents):
                                    root.insert(0, child_element)
                        except Exception:
                            continue
                else:  # end
                    for item_html in inner:
                        try:
                            child_soup = BeautifulSoup(item_html, 'html.parser')
                            if child_soup.contents:
                                for child_element in child_soup.contents:
                                    root.append(child_element)
                        except Exception:
                            continue

        return str(soup)

    def set_attribute(self, widget, field, value):
        """
        Sets or updates a single attribute on the root element of an HTML string,
        applying transformation rules from self.attributes when available.
        """
        # Se non è una stringa HTML valida → ritorna direttamente
        if not isinstance(widget, str):
            return widget

        # Campo non valido → ritorno senza modificare
        if not isinstance(field, str) or not field.strip() or ' ' in field.strip():
            return widget

        # Cerca nel dizionario attributi
        handler = self.attributes.get(field)

        transformed_value = None

        if handler is None:
            # Fallback: nessuna regola → usa il valore diretto
            transformed_value = value
        elif callable(handler):
            # Caso: funzione di trasformazione (layout, style, ecc.)
            transformed_value = handler(value)
        elif isinstance(handler, tuple):
            # Caso: mappatura evento -> (event_type, callback)
            event_type, callback = handler
            # qui potresti gestire diversamente, per esempio aggiungere listener
            transformed_value = f"{event_type}:{callback.__name__}"
        elif handler is True:
            # Caso: attributi "matter" → li includo così come sono
            transformed_value = value
        else:
            # Qualsiasi altro caso non previsto
            transformed_value = value

        # Se la trasformazione restituisce None → significa "rimuovi l'attributo"
        if transformed_value is None:
            return self.code_update(widget, {field: None})

        # Aggiorna il widget con il valore trasformato
        return self.code_update(widget, {field: transformed_value})

    def get_attribute(self, widget, field):
        """
        Extracts an attribute's value from an HTML string or a widget object.
        Handles various attribute formats including boolean attributes, case insensitivity,
        and gracefully handles invalid inputs.
        """

        def extract_attribute_from_html(html: str, attribute: str) -> str | None:
            if not isinstance(html, str) or not html.strip():
                return None  # Handle empty or non-string HTML input

            # 1. Validate 'attribute' input: Must be a non-empty string
            if not isinstance(attribute, str) or not attribute.strip():
                return None # Return None if attribute name is invalid (e.g., None, int, empty string)

            if ' ' in attribute.strip():
                return None
            
            # Make the attribute name case-insensitive for regex matching
            attribute_lower = re.escape(attribute.lower())

            # Updated Regex:
            # - Handles attribute="value", attribute='value'
            # - Handles boolean attributes (attribute with no value)
            # - The key change for JSON values is to ensure the non-greedy match (.*?) captures everything
            #   between quotes. Your previous regex should have worked, but let's double-check the pattern.
            #   The problem might be that the quotes within the JSON were ending the match prematurely.
            #   To capture *any* character inside quotes, including other quotes, we can be more specific
            #   about the matching pair of quotes.

            # Pattern breakdown:
            # {attribute_lower}\s*=\s* -> Matches "attribute ="
            # (["\'])                   -> Captures the opening quote (group 1)
            # (.*?)                     -> Non-greedy match for any characters (group 2)
            # \1                        -> Matches the same closing quote as the opening one (from group 1)
            # |{attribute_lower}(?=\s|>) -> Or, matches boolean attribute (followed by space or closing tag)
            
            pattern = fr'{attribute_lower}\s*=\s*(["\'])(.*?)\1|{attribute_lower}(?=\s|>)'
            
            # Ensure we are parsing a valid HTML structure for the attribute extraction.
            # This is a heuristic to catch severely malformed HTML. A full HTML parser
            # would be more robust, but for regex, we can check for basic well-formedness.
            # For simplicity and to match your test's expectation of None for malformed HTML,
            # we can make a basic check for a closing tag.
            if not html.strip().endswith('>'):
                return None # Return None for clearly malformed HTML like '<div width="100px"'

            # Use re.IGNORECASE to match attribute names case-insensitively in the HTML
            match = re.search(pattern, html, re.IGNORECASE)

            if match:
                # If group 2 (the captured value from inside quotes) exists, return it.
                # This group is populated by the `(["\'])(.*?)\1` part of the regex.
                if match.group(2) is not None:
                    return match.group(2)
                # If group 2 doesn't exist, it means the match was for a boolean attribute.
                # In this case, return None as per your test expectation.
                return None
            
            return None # Attribute not found


        # Determine if 'widget' is an HTML string or an object with specific properties
        if isinstance(widget, str):
            html_string = widget
        else:
            # If widget is an object, we need to decide how to get its HTML representation
            # for `extract_attribute_from_html`. For now, we'll assume attributes like
            # 'class' should come directly from HTML if 'widget' is not a string,
            # and 'elements' might still come from object properties if applicable.
            html_string = str(widget) # Fallback, might need refinement based on your widget object structure


        # Handle specific 'field' cases first, then fall back to HTML attribute extraction.
        # This order is important if 'widget' could be a complex object.
        match field:
            case 'elements':
                # This logic assumes 'widget' is an object instance.
                # If 'widget' is an HTML string, getattr will fail here.
                # You need to clarify if 'elements' means parsing child HTML elements
                # or accessing an object's property.
                if not isinstance(widget, str):
                    a = getattr(widget, 'controls', None)
                    if a:
                        return a
                    a = getattr(widget, 'content', None)
                    if a:
                        return self.get_attribute(a, 'elements')
                return None # No elements found or widget is just a string
            case 'class':
                # For 'class', we should extract it from the HTML string directly,
                # as the test case uses a string input: ('<div id="first" class="second"></div>', 'class')
                # If 'widget' is an object that genuinely has a 'class_name' attribute,
                # you might want to prioritize that, but for the provided test, HTML parsing is needed.
                return extract_attribute_from_html(html_string, field)
            case _:
                # For any other 'field', try to extract it as an HTML attribute
                return extract_attribute_from_html(html_string, field)

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

    def mount_route(self, routes):
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