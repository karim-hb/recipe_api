from django.test import SimpleTestCase

from app import calc

class TestCalculator(SimpleTestCase):
    def test_calculator(self):
        res = calc.add(5,6)
        
        self.assertEqual(res,11)
    def test_calculator2(self):
        res = calc.minus(100,2)
        
        self.assertEqual(res,98)