import app21.py
import unittest
import coverage
import MySQLdb

cov = coverage.Coverage()
cov.start()

class TestPasswordValidation(unittest.TestCase):

    def test_short_password(self):
        self.assertFalse(app21.is_password_valid("abc123"))  # length < 8

    def test_long_password(self):
        self.assertFalse(app21.is_password_valid("abcdefghij1234567890klmnopqrstu"))  # length > 25

    def test_alpha_password(self):
        self.assertFalse(app21.is_password_valid("abcdefghijklmnopqrstuvwxyz"))  # alphabetic only

    def test_numeric_password(self):
        self.assertFalse(app21.is_password_valid("1234567890"))  # numeric only

    def test_valid_password(self):
        self.assertTrue(app21.is_password_valid("abc123xyz"))  # valid password

if __name__ == '__main__':
    cov.start()
    unittest.main()
    cov.stop()
    cov.save()
    cov.report()
