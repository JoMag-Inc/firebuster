import unittest
from app.example_module.example_function import  get_some_text

class TestExample(unittest.TestCase):
    def test_example(self):
        txt = get_some_text()
        self.assertEqual("this is an example",txt)
        
        
