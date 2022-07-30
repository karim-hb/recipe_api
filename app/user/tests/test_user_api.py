""" test for user api """

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_API = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL =  reverse('user:me')


def create_user(**params):
    """ create and return new user"""
    return get_user_model().objects.create_user(**params)

class PublicUserAPITest(TestCase):
    """ test for user pubilc api """
    
    def setUp(self):
        self.client = APIClient()
        
    def test_create_user(self):
        payload = {
          'email': 'test@example.com',
          'password': 'password',
          'name': 'testname'
        }
        
        res = self.client.post(CREATE_USER_API , payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        
        self.assertTrue(user.check_password(payload['password']))
        
        """ check the password not inside response"""
        self.assertNotIn('password', res.data)
        
    def test_user_with_email_exist_error(self):
        """ test for check all email are unique """
        payload = {
          'email': 'test@example.com',
          'password': 'password',
          'name': 'testname'
        }
        
        create_user(**payload)
        
        res = self.client.post(CREATE_USER_API, payload)
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST) 
        
    def test_short_password(self):
        payload = {
          'email': 'test@example.com',
          'password': '1',
          'name': 'testname'
        }
        
        res = self.client.post(CREATE_USER_API, payload)
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST) 
        
        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()
        
        self.assertFalse(user_exists)
        
    def test_token(self):
        payload = {'email': 'test@londonappdev.com', 'password': 'testpass'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_token_bad_credentials(self):
        """test for check user login inputs are invalid as a result token should not generate"""
        create_user(email='test@londonappdev.com', password="testpass")
        payload = {'email': 'test@londonappdev.com', 'password': 'wrong'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_blank_password(self):
        payload = {'email': 'example@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
    def get_test_unAuthorized(self):
        """ test for check un authorized users """
        res = self.client.post(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
class PrivateUserApiTestCase(TestCase):
    """ test private api """
    def setUp(self):
        self.user = create_user(
            email = 'user@example.com',
            password = 'password123!',
            name="test name"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_retrive_profile_success(self):
        """ test retrieving profile for loggin users"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data,{
            'name':self.user.name,
            'email':self.user.email
        })
        
    def test_post_not_allowed_me(self):
        """ test for not allowed post request to me endpoint"""
        res = self.client.post(ME_URL,{})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
    def test_update_user_information(self):
        """ test for update user information """
        payload = {'name':"new test name" , 'password': "new T@ST password"}
        res = self.client.patch(ME_URL,payload)
        
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name , payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))