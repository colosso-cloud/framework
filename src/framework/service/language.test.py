import asyncio
import types

resources = {
    'factory': 'framework/service/factory.py',
    'flow': 'framework/service/flow.py',
    'test': 'framework/service/test.py',
    'model': 'framework/schema/model.json',
}

class Test(test.test):
    def setUp(self):
        print("Setting up the test environment...")

    async def test_resource(self):
        """Verifica che language.get recuperi correttamente i valori da percorsi validi."""
        success = [
            {'args':(language),'kwargs':{'path':"framework/service/run.py"},'type':types.ModuleType},
            {'args':(language),'kwargs':{'path':"framework/schema/model.json"},'equal':model},
        ]

        failure = [
            {'args':(language),'kwargs':{'path':"framework/service/NotFound.py"}, 'error': FileNotFoundError},
        ]

        await self.check_cases(language.resource, success)
        await self.check_cases(language.resource, failure)

        

    async def test_schema(self):
        cases = [
            {'args':(language),'kwargs':{'path':"framework/service/run.py"},'type':types.ModuleType},
            {'args':(language),'kwargs':{'path':"framework/schema/model.json"},'equal':model},
        ]


        a = {'name': 'test', 'version': '1.0.0', 'description': 'Test schema','url':{'path':'/', 'query': {'test': 'test'},}}
        cc = language.get(a,'name')
        path = language.get(a, 'url.path')
        self.assertEqual(cc, 'test')
        self.assertEqual(path, '/')
        nn = language.get(a, 'url.stringa',123)
        self.assertEqual(nn, 123)
        #self.assertTrue(False)

    async def test_put(self):
        a = {}

        cases = [
            {'args':(a,'name','mario'),'equal':{'name': 'mario'}},
        ]

        await self.check_cases(language.put, cases)

    async def test_extract_params(self):
        success = [
            {'args':("func(name: 'Alice', age: 30, city: 'New York')"),'equal':{'name': 'Alice', 'age': 30, 'city': 'New York'}},
            {'args':("process(id: 123, options: {'mode': 'fast', 'verbose': True})"),'equal':{'id': 123, 'options': {'mode': 'fast', 'verbose': True}}},
            {'args':("analyze(data: [1, 2, 3, {'x': 10}], threshold: 0.5)"),'equal':{'data': [1, 2, 3, {'x': 10}], 'threshold': 0.5}},
            {'args':("send(message: \"Hello, world!\", priority: 5)"),'equal':{'message': "Hello, world!", 'priority': 5}},
            {'args':("empty_func()"),'equal':{}}, # Funzione senza parametri
            {'args':("some_action(status: None, debug: False)"),'equal':{'status': None, 'debug': False}},
            {'args':("another_func(data: [1, 'two', 3], complex: {'a': [1,2], 'b': 'nested'})"),'equal':{'data': [1, 'two', 3], 'complex': {'a': [1, 2], 'b': 'nested'}}},
        ]

        failure_cases = [
            # Caso 1: Stringa JSON/Python malformata (es. virgole, apici mancanti)
            {'args':("bad_syntax(param: {'key': value)"), 'error': SyntaxError}, # Assumi che un parsing fallito dia SyntaxError o ValueError
            {'args':("incomplete(param: 'value'"), 'error': SyntaxError}, # Mancanza di chiusura parentesi
            {'args':("simple(name: Bob)"), 'error': ValueError}, # Valore non quotato che non è un tipo Python valido (int, float, bool, None)

            # Caso 2: Nomi di parametri invalidi
            # {'args':("invalid(0name: 'value')"), 'error': ValueError}, # Se la tua funzione convalida i nomi
            
            # Caso 3: Input non previsto per la funzione (es. non una stringa)
            {'args': (123,), 'error': TypeError}, # Se 'extract_params' si aspetta una stringa come input
            {'args': ({'a':1},), 'error': TypeError},
        ]

        failure = [
            {'args':("problematic(key: 'value with , comma', another: {nested_key: 'value, inside'})"),'equal':{'key': 'value with , comma', 'another': {'nested_key': 'value, inside'}}},
            {'args':("simple(name: Bob)"),'equal':{}}, # Chiave non quotata e valore non quotato non stringa   
        ]

        await self.check_cases(language.extract_params, success)
        await self.check_cases(language.extract_params, failure)

    async def test_get_success_cases(self):
        """Verifica che language.get recuperi correttamente i valori da percorsi validi."""
        success_cases = [
            # (data, accessor_string, default, expected_output)
            ({'name': 'test_name'}, 'name', None, 'test_name'),
            ({'url': {'path': '/api'}}, 'url.path', None, '/api'),
            ({'a': {'b': 1}}, 'a.b', None, 1), # Esiste, default non usato
            ({'list_data': [10, 20]}, 'list_data.0', None, 10),
            ({'list_data': [{'item': 'val'}]}, 'list_data.0.item', None, 'val'),
            ({'a': None}, 'a', None, None), # Verifica None esplicito come valore
        ]

        for i, (data, accessor_string, default, expected_output) in enumerate(success_cases):
            with self.subTest(msg=f"Success Case {i+1}: get({data}, '{accessor_string}', {default})"):
                result = language.get(data, accessor_string, default)
                self.assertEqual(result, expected_output)

    async def test_get_failure_cases(self):
        """Verifica che language.get gestisca correttamente i percorsi non validi o inesistenti."""
        failure_cases = [
            # (data, accessor_string, default, expected_output_on_failure)
            ({}, 'a.b', 'def', 'def'), # Percorso inesistente, restituisce default
            ({'a': {'b': 1}}, 'a.c', 123, 123), # Chiave inesistente in dict, restituisce default
            ({'a': None}, 'a.b', 'fallback', 'fallback'), # Accesso su None, restituisce default
            ({'list': [1,2,3]}, 'list.5', 'not found', 'not found'), # Indice fuori range, restituisce default
            ({'list': [1,2,3]}, 'list.abc', 'invalid index', 'invalid index'), # Indice non numerico, restituisce default
            ({'numeric_val': 123}, 'numeric_val.sub', 'no_sub', 'no_sub'), # Accesso su tipo non iterabile, restituisce default
        ]

        for i, (data, accessor_string, default, expected_output_on_failure) in enumerate(failure_cases):
            with self.subTest(msg=f"Failure Case {i+1}: get({data}, '{accessor_string}', {default})"):
                result = language.get(data, accessor_string, default)
                self.assertEqual(result, expected_output_on_failure)