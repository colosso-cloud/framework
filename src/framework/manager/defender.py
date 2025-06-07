from secrets import token_urlsafe
from typing import Dict, Any

class defender:
    def __init__(self, **constants):
        """
        Inizializza la classe Defender con i provider specificati.

        :param constants: Configurazioni iniziali, deve includere 'providers'.
        """
        self.sessions = {}
        self.providers = constants.get('providers', [])

    #@flow.asynchronous(managers=('messenger',))
    async def unionsession(self,**constants):
        id = constants.get('identifier', '')
        if id not in self.sessions:
            self.sessions[id] = constants.get('session', {})
        else:
            self.sessions[id] |= constants.get('session', {})

        print(self.sessions,'session.updated')
    
    '''async def authenticate(self,**constants):
        """
        Autentica un utente utilizzando i provider configurati.

        :param constants: Deve includere 'identifier', 'ip' e credenziali.
        :return: Token di sessione se l'autenticazione ha successo, altrimenti None.
        """
        identifier = constants.get('identifier', '')
        ip = constants.get('ip', '')
        if identifier not in self.sessions:
            self.sessions[identifier] = {'ip': ip,}

        for backend in self.providers:
            session = await backend.authenticate(**constants)
            print(session,backend,'auth.defender')
            if session:
                self.sessions[identifier] |= {backend.config.get('profile',''): session}
        return self.sessions[identifier]'''
    
    async def authenticate(self, **constants):
        """
        Autentica un utente utilizzando i provider configurati.

        :param constants: Deve includere 'identifier', 'ip' e credenziali.
        :return: Dizionario di sessione aggiornato se l'autenticazione ha successo, altrimenti None.
        """
        identifier = constants.get('identifier')
        ip = constants.get('ip')

        if not identifier or not ip:
            print("Errore: 'identifier' e 'ip' sono obbligatori per l'autenticazione.")
            return None

        # Inizializza la sessione se non esiste
        session = self.sessions.setdefault(identifier, {'ip': ip})

        authenticated = False
        for backend in self.providers:
            try:
                backend_session = await backend.authenticate(**constants)
                print(f"[auth.defender] Risultato: {backend_session} | Provider: {backend}",constants)
                if backend_session:
                    profile = backend.config.get('profile', '')
                    if profile:
                        session[profile] = backend_session
                    else:
                        session.update(backend_session)
                    authenticated = True
            except Exception as e:
                print(f"Errore durante l'autenticazione con {backend}: {e}")

        if authenticated:
            self.sessions[identifier] = session
            return session
        else:
            print(f"Autenticazione fallita per identifier: {identifier}")
            return None

    async def registration(self, **constants) -> Any:
        """
        Autentica un utente utilizzando i provider configurati.

        :param constants: Deve includere 'identifier', 'ip' e credenziali.
        :return: Token di sessione se l'autenticazione ha successo, altrimenti None.
        """
        identifier = constants.get('identifier', '')
        ip = constants.get('ip', '')
        for backend in self.providers:
            token = await backend.registration(**constants)
            if token:
                self.sessions[identifier] = {'token': token, 'ip': ip}
                return token
        return None

    async def authenticated(self, **constants) -> bool:
        """
        Verifica se una sessione è autenticata.

        :param constants: Deve includere 'session'.
        :return: True se la sessione è valida, altrimenti False.
        """
        session_token = constants.get('session', '')
        return session_token in {session['token'] for session in self.sessions.values()}

    async def authorize(self, **constants) -> bool:
        """
        Controlla se un'azione è autorizzata in base all'indirizzo IP.

        :param constants: Deve includere 'ip'.
        :return: True se l'IP è autorizzato, altrimenti False.
        """
        ip = constants.get('ip', '')
        return any(session.get('ip') == ip for session in self.sessions.values())

    async def whoami(self, **constants) -> Any:
        """
        Determina l'identità dell'utente associato a un determinato indirizzo IP.

        :param constants: Deve includere 'ip'.
        :return: Identificatore dell'utente se trovato, altrimenti None.
        """
        ip = constants.get('ip', '')
        for identifier, session in self.sessions.items():
            if session.get('ip') == ip:
                return identifier
        return None
    
    async def whoami2(self, **constants) -> Any:
        
        for backend in self.providers:
            identity = await backend.whoami(token=constants.get('token', ''))
            return identity

    async def detection(self, **constants) -> bool:
        """
        Placeholder per il rilevamento di minacce.

        :param constants: Parametri opzionali per il rilevamento.
        :return: True come comportamento predefinito.
        """
        return True

    async def protection(self, **constants) -> bool:
        """
        Placeholder per la protezione attiva.

        :param constants: Parametri opzionali per la protezione.
        :return: True come comportamento predefinito.
        """
        return True

    async def logout(self, **constants) -> bool:
        """
        Termina la sessione di un utente specificato.

        :param constants: Deve includere 'identifier'.
        :return: True se la sessione è stata terminata, False se l'utente non esiste.
        """
        identifier = constants.get('identifier', '')

        for backend in self.providers:
            await backend.logout()

        if identifier in self.sessions:
            del self.sessions[identifier]

    def cleanup_expired_sessions(self, **constants) -> None:
        """
        Placeholder per rimuovere sessioni scadute o non più valide.

        Questo metodo potrebbe essere implementato con controlli di scadenza basati su timestamp.

        :param constants: Parametri opzionali per la pulizia.
        """
        pass