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

ide = (
    {'name':'id','type':'string','default':'None'},
    {'name':'branch','type':'string','default':'main'},
    {'name':'repository','type':'dict','default':{'name':'framework','owner':'SottoMonte'}},
    #{'name':'repository','type':'string','default':'SottoMonte/framework'},
    {'name':'selected','type':'string','default':'None'},
    {'name':'loading','type':'bool','default':True},
)