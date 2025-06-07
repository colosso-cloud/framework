from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import sys
import json
try:
    import supabase
except Exception as e:
    import js
    from js import supabase
    import pyodide

modules = {'flow': 'framework.service.flow'}

class adapter:
    def __init__(self, **config):
        """Inizializza il client Supabase con URL e chiave API."""
        self.config = config.get('config', {})
        #print(self.config)
        self.client = supabase.createClient(self.config['url'], self.config['key'])
        self.set_token(self.config.get('token', ''))

        js_code = f"""
  
        globalThis.supabaseClient = supabase.createClient("{self.config.get('url','')}", "{self.config.get('key','')}");

        console.log("✅ Supabase inizializzato!");
        """
        pyodide.code.run_js(js_code)
        

    def set_token(self, token):
        """Imposta il token di autenticazione dell'utente."""
        self.token = token
        self.client.auth.session = {"access_token": token}  # Usa il token per autenticazione

    def generate_query_filter(self, filters):
        """
        Genera una stringa di query Python per Supabase applicando dinamicamente i filtri.
        """
        query = ""

        # Applica i filtri dinamicamente
        if 'eq' in filters:
            for field in filters['eq']:
                query += f'.eq("{field}", "{filters['eq'][field]}")'
        if 'neq' in filters:
            for field, value in filters['neq']:
                query += f'.neq("{field}", "{filters['neq'][field]}")'
        if 'like' in filters:
            for field, value in filters['like']:
                query += f'.like("{field}", "{filters['like'][field]}")'
        if 'ilike' in filters:
            for field, value in filters['ilike']:
                query += f'.ilike("{field}", "{filters['ilike'][field]}")'
        if 'pagination' in filters:
            for field in filters['pagination']:
                start = filters['pagination'][field].get('start', 1)
                end = filters['pagination'][field].get('end', 10)
                start, end = (start - 1) * end, start * end - 1
                query += f'.range({start}, {end})'
        if 'in' in filters:
            for field, value in filters['in']:
                query += f'.in("{field}", {filters['pagination'][field]})'

        return query

    @flow.asynchronous()
    async def query(self, **constants):
        
        """
        Esegue una query su Supabase tramite supabase-js, con supporto per filtri e paginazione.
        """
        payload = constants.get('payload', {}) or "{}"
        method = constants.get('method', '')
        location = constants.get('location', '')
        filter = constants.get('filter', {})
        filter = self.generate_query_filter(filter)
        # Configura la paginazione
        

        # Genera il codice JavaScript per la query
        js_code = f"""
        async function query() {{
            let query = supabaseClient.from("{location}");
            let response;

           
            const payload = {json.dumps(payload)};
            const method = "{method}";
            const location = "{location}";

            switch (method) {{
                case "GET":
                    response = await query.select("*"){filter};
                    break;
                case "POST":
                    response = await query.insert(payload){filter};
                    break;
                case "PUT":
                    response = await query.update(payload){filter};
                    break;
                case "DELETE":
                    response = await query.delete(){filter};
                    break;
                default:
                    return {{ state: false, error: "Invalid method", input: {{ method, payload, location }} }};
            }}

            return response.error 
                ? {{ state: false, error: response.error.message, input: {{ method, payload, location }} }}
                : {{ state: true, result: response.data, input: {{ method, payload, location }} }};
        }}
        query();
        """
        test = await pyodide.code.run_js(js_code)
        #print(test.to_py(),'test....',js_code)
        return test.to_py()
    
    async def query2(self, **constants):
        """Esegue una richiesta a Supabase utilizzando il token di autenticazione."""
        try:
            payload = constants.get('payload', {})
            method = constants.get('method', '')
            tt = constants.get('path', [])[0]

            print(tt)
            print(dir(supabase.fromTable('router')))
            filters = constants.get('filters', [])

        
            if method == 'GET':
                query = self.client.table(tt).select('*')
                for f in filters:
                    query = query.eq(f['field'], f['value'])
                response = query.execute()

            elif method == 'PUT':
                response = self.client.table(tt).update(payload).match(filters).execute()

            elif method == 'POST':
                response = self.client.table(tt).insert(payload).execute()

            elif method == 'DELETE':
                response = self.client.table(tt).delete().match(filters).execute()

            else:
                return {"state": False, "error": "Invalid method"}

           
            return {"state": bool(response.data), "result": response.data if response else "Request failed"}

        except Exception as e:
            print(f"Errore durante la richiesta: {e}")
            return {"state": False, "error": str(e)}

    @flow.asynchronous(outputs='transaction')
    async def create(self, **constants):
        """Inserisce un nuovo record nella tabella Supabase."""
        return await self.query(**constants | {'method': 'POST'})

    @flow.asynchronous(outputs='transaction')
    async def delete(self, **constants):
        """Elimina un record dalla tabella Supabase."""
        return await self.query(**constants | {'method': 'DELETE'})

    @flow.asynchronous(outputs='transaction')
    async def read(self, **constants):
        """Recupera i dati dalla tabella Supabase."""
        return await self.query(**constants | {'method': 'GET'})

    @flow.asynchronous(outputs='transaction')
    async def update(self, **constants):
        """Aggiorna un record nella tabella Supabase."""
        return await self.query(**constants | {'method': 'PUT'})