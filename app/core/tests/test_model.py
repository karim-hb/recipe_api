""" test for models """

from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTestCase(TestCase):
    """ test models """
    
    def test_create_user_with_email_successfully(self):
        """ test for create user with email successfully"""
        email = 'email@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(email=email, password=password)
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        
    def test_for_normalize_email_(self):
        """ test for check unique emial """
        
        sample_email =[
            ["email@EXAMPLE.com" ,'email@example.com'],
            ["email2@Example.com" ,'email2@example.com'],
            ["Email3@EXAMPLE.com" ,'Email3@example.com'],
            ["email4@example.com" ,'email4@example.com'],
        ]
        
        for email, excepted in sample_email:
            user = get_user_model().objects.create_user(email=email)
            self.assertEqual(user.email, excepted)
            
    def test_for_create_superuser(self):
        """ test for create superuser """
        
        user = get_user_model().objects.create_superuser(
            email='email@example.com',
            password='password'
        )
        
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)