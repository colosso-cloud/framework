modules = {'flow':'framework.service.flow'}

import pyodide
import js
import asyncio
import json
from js import Terminal,FitAddon,console,eval
@flow.asynchronous(managers=('messenger','presenter','storekeeper'))
async def terminal(messenger,presenter,storekeeper,**constants):
    
    target = constants.get('target','')
    #terminal = Terminal()
    terminal = eval("new Terminal({fontFamily: 'monospace', experimentalCharAtlas: 'none',})")
    #fitAddon = eval("new FitAddon.FitAddon()")
    fitAddon = js.FitAddon.FitAddon.new()
    terminal.loadAddon(fitAddon)
    element = js.document.getElementById(target)
    terminal.open(element)
    await asyncio.sleep(3)
    
    fitAddon.fit()
    #session = js.window.sessionStorage.getItem('session_state')
    socket = js.WebSocket.new('wss://app.colosso.cloud/ssh')
    def on_message(event):
        #print(f"Message received: {event.data}")
        terminal.write(event.data)
    def on_open(event):
        params  = {
            'username': constants.get('username','username'),
            'password': constants.get('password','password'),
            'host': constants.get('host','host'),
        }
        print(params)
        socket.send(json.dumps(params))
    def on_data(event,data):
        #print(data,event)
        socket.send(event)
    socket.onmessage = on_message
    socket.onopen = on_open
    #terminal.ondata = on_data

    #await messenger.post(msg='Terminal is ready',type='info')
    #pyodide.create_proxy(self.route)
    #socket.addEventListener('message', pyodide.create_proxy(on_message))
    #socket.addEventListener('open', pyodide.create_proxy(on_open))
    
    #terminal.addEventListener('data', pyodide.create_proxy(on_data))
    terminal.onData(pyodide.ffi.create_proxy(on_data))