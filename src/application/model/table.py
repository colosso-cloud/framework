'''
{
    'id': 'asdasd',                 # Identificativo unico
    'model': 'ttt',                 # Modello o tipo di tabella
    'selected': [],                 # Elementi selezionati
    'pageCurrent': 1,               # Pagina corrente
    'pageRows': 10,                  # Numero di righe per pagina
    'sortField': 'CardName',        # Campo per l'ordinamento
    'sort': 'asc',                # Ordinamento ascendente o discendente
    'filters': {},                  # Filtri applicati (ad es. {'status': 'active'})
    'columns': [],                  # Elenco delle colonne visualizzate (ad es. ['CardName', 'CardType'])
    'totalRows': 0,                 # Numero totale di righe nella tabella
    'loading': False,               # Stato di caricamento della tabella
    'actions': [],                  # Azioni disponibili (ad es. ['edit', 'delete'])
    'searchQuery': '',              # Query di ricerca
    'rowActions': {},               # Azioni specifiche per riga (ad es. {'rowId1': ['view', 'edit']})
    'paginationOptions': [10, 25, 50, 100]  # Opzioni di paginazione disponibili
}'''

table = (
    {'name':'id','type':'string','default':'None'},
    {'name':'repository','type':'string','default':'None'},
    {'name':'model','type':'string','default':'None'},
    {'name':'view','type':'string','default':'None'},
    {'name':'selected','type':'list','default':[]},
    {'name':'pageCurrent','type':'int','default':1},
    {'name':'pageRows','type':'int','default':5},
    {'name':'sortField','type':'string','default':'full_name'},
    {'name':'sortDirection','type':'string','default':'asc'},
    {'name':'filters','type':'dict','default':{}},
    {'name':'columns','type':'list','default':[]},
    {'name':'totalRows','type':'int','default':100},
    {'name':'loading','type':'bool','default':False},
    {'name':'actions','type':'list','default':[]},
    {'name':'searchQuery','type':'string','default':''},
    {'name':'rowActions','type':'dict','default':{}},
    {'name':'paginationOptions','type':'list','default':[5,10,15,20,25,30,50,100]}
)