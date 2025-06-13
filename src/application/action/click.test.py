
import unittest
import asyncio

# La tua classe repository modificata per usare self.language invece di language globale
modules = {'flow': 'framework.service.flow'}

class Test(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def test_valid(self):
        self.assertTrue(True)
        #self.assertEqual(count, 2)