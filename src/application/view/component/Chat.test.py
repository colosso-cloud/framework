import unittest
import asyncio

# La tua classe repository modificata per usare self.language invece di language globale
modules = {'flow': 'framework.service.flow'}

class Test(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.component = {
            'id': 'tesssst',
            'view':'application/view/component/Chat.xml',
            'attributes': {'domain':'casa','view':'Chat'},
            'messenger':[
                {"location": "SERVER", "message": " Ciao!", "domain": ["debug"], "operation": "read", "sender": "user", "receiver": "anonym", "timestamp": "2025-05-13 13:46:02.659000", "identifier": "fe75f943-8107-4ecc-8b20-dd3080408907", "priority": "normal"},
                {"location": "SERVER", "message": " Ciao , come stai oggi ?", "domain": ["debug"], "operation": "read", "sender": "anonym", "receiver": "anonym", "timestamp": "2025-05-13 13:46:02.659000", "identifier": "fe75f943-8107-4ecc-8b20-dd3080408907", "priority": "normal"}
            ]
        }

        return self.component
        
    def tearDown(self):
        pass

    def test_valid(self):
        self.assertTrue(False)