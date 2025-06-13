file = (
    {'name':'name','type':'sting','default':'None','regex':r'^[a-zA-Z0-9_-]+$'},
    {'name':'message','type':'string','default':'main:','regex':r'^[a-zA-Z0-9_-]+$'},
    {'name':'path','type':'string','default':'main:','required':True,'regex':r'^[a-zA-Z0-9_-]+$'},
    {'name':'location','type':'string','default':'None','required':True},
    {'name':'content','type':'string','default':'None','required':True},
    {'name':'sha','type':'string','default':'None','regex':r'^[a-zA-Z0-9_-]+$'},
    {'name': 'tree', 'type': 'list', 'default': []},
)