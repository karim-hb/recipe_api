""" test for admin panel """


from unicodedata import name
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

class AdminPanelTests(TestCase):
    """ test for django admin panel """
    
    def setUp(self):
        """test for create user and client """
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email = 'admin@example.com',
            password = 'adminpassword'
        )
        
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email = 'user@example.com',
            password = 'userpassword',
            name = "user"
        )
        
    def test_user_list(self):
        """ test for user listed on page """
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)
        
        self.assertContains(res,self.user.email)
        self.assertContains(res,self.user.name)
        
    def test_edit_user_page(self):
        """ test for edit user page """
        url = reverse('admin:core_user_change' , args=[self.user.id])
        res = self.client.get(url)
        
        self.assertEqual(res.status_code , 200)
        
    def test_add_user_page(self):
        """ test for add user to the page """
        url = reverse('admin:core_user_add')
        res = self.client.post(url)
        
        self.assertEqual(res.status_code, 200)