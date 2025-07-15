resources = {
    'starlette': 'infrastructure/presentation/starlette.py',
    'flow': 'framework/service/flow.py',
    'test': 'framework/service/test.py',
    #'model': 'framework/schema/model.json',
}

class AdapterTest(test.test):

    def setUp(self):
        """
        Questo metodo viene eseguito prima di ogni test.
        Serve per inizializzare l'ambiente di test.
        """
        test_config = {
            #'route': 'test_route',
            'host': '127.0.0.1',
            'port': 8000
        }

        self.adapter = starlette.adapter(config=test_config)

    def tearDown(self):
        """
        Questo metodo viene eseguito dopo ogni test.
        Serve per pulire l'ambiente di test.
        """
        # Qui puoi aggiungere codice per pulire l'ambiente di test, se necessario
        pass

    async def test_mount_widget(self):
        
        success = [
            #1 Recupera il modello
            {'args':('video',[],{}),'equal': '<video  ></video>'},
        ]

        '''failure = [
            #1 Campo mancante
            {'args':(self.schema,{'user': {'ok':'m','name':'marco','items': [{'id': 123, 'name': 'Prodotto A'}]}}),'error': ValueError},
        ]'''
        await self.check_cases(self.adapter.mount_widget, success)
        #await self.check_cases(language.model, failure)