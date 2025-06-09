
'''
ID della Transazione: Un identificatore unico per la transazione.
Timestamp: La data e l’ora in cui la transazione è stata avviata.
Utente: L’utente che ha avviato la transazione.
Tipo di Operazione: Il tipo di operazione eseguita (ad esempio, inserimento, aggiornamento, cancellazione).
Stato della Transazione: Lo stato corrente della transazione (ad esempio, in corso, completata, annullata).
Dettagli delle Operazioni: Le specifiche operazioni eseguite durante la transazione, come le query SQL.
Log delle Modifiche: Un registro delle modifiche apportate ai dati durante la transazione.
Durata: Il tempo totale impiegato per completare la transazione.'''

transaction = (
    {'name':'identifier','type':'string','default':''},
    {'name':'state','type':'boolean','default':False},
    {'name':'action','type':'string','default':'unknown'},
    {'name':'time','type':'string','default':'yyyy-mm-dd hh:mm:ss',"function": "time_now_utc",},
    #{'name':'user','model':user.user},
    {'name':'remark','type':'string','default':''},
    {'name':'worker','type':'string','default':'unknown'},
    #{'name':'event','model':event.event},
    {'name':'parameters','type':'dict','default':{}},
    #{'name':'transaction','type':'list','default':[],'iterable':True},
    {'name':'result','type':'list','force_type':'dict','iterable':True,'default':[]},
)