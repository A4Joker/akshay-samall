import unittest
from check_semiprime import isSemiprime, find_semiprimes

class TestSemiprime(unittest.TestCase):
    def test_is_semiprime(self):
        """Test individual semiprime numbers"""
        # Known semiprimes
        self.assertTrue(isSemiprime(4))   # 2 x 2
        self.assertTrue(isSemiprime(6))   # 2 x 3
        self.assertTrue(isSemiprime(25))  # 5 x 5
        self.assertTrue(isSemiprime(91))  # 7 x 13
        
        # Known non-semiprimes
        self.assertFalse(isSemiprime(1))   # Not semiprime by definition
        self.assertFalse(isSemiprime(2))   # Prime, not semiprime
        self.assertFalse(isSemiprime(12))  # 2 x 2 x 3 (three factors)
        self.assertFalse(isSemiprime(16))  # 2 x 2 x 2 x 2 (four factors)
        
    def test_find_semiprimes(self):
        """Test finding semiprimes in a range"""
        # Test first few semiprimes
        result = find_semiprimes(1, 10)
        self.assertEqual(result, {4, 6, 9})
        
        # Test empty range
        self.assertEqual(find_semiprimes(1, 3), set())
        
        # Test invalid range
        with self.assertRaises(ValueError):
            find_semiprimes(-1, 10)
        with self.assertRaises(ValueError):
            find_semiprimes(10, 5)

    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Test zero and negative numbers
        self.assertFalse(isSemiprime(0))
        self.assertFalse(isSemiprime(-4))
        
        # Test large numbers
        self.assertTrue(isSemiprime(143))  # 11 x 13
        self.assertTrue(isSemiprime(299))  # 13 x 23

if __name__ == '__main__':
    unittest.main()