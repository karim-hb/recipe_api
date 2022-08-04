from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal

from rest_framework.test import APIClient
from rest_framework import status

from core.models import (Tag,Recipe,)
from recipe.serializers import (TagSerializer)

TAG_URL = reverse('recipe:tag-list')

def detail_url(tag_id):
    """ create and return tag details url"""
    return reverse('recipe:tag-detail', args=[tag_id])

def create_user(email="test@example.com", password="testpassword"):
    """ create user and return it """
    return get_user_model().objects.create_user(email,password)

class PubicTestTag(TestCase):
    """ test public url for Tag """
    
    def setUp(self):
        self.client = APIClient()
        
    def test_auth_requeird(self):
        """ test for un authorized request  """
        res = self.client.get(TAG_URL)
        
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
class PrivateTestTag(TestCase):
    """ test authenticated user for private tag """
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)
    
    def test_tag_list(self):
        """ test for retriving tag """
        Tag.objects.create(user=self.user,name="vegen")
        Tag.objects.create(user=self.user,name="meet")
        
        res = self.client.get(TAG_URL)
        tags = Tag.objects.all().order_by('-name')
        serializers = TagSerializer(tags,many=True)
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializers.data)
        
    def test_limited_tag(self):
        """ test tags are shown for the user that created that tag """
        
        new_user = create_user(email="use222r@example.com")
        
        Tag.objects.create(user=new_user,name="fastFood")
        tag2 =Tag.objects.create(user=self.user,name="seaFood")
        res = self.client.get(TAG_URL)
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'],tag2.name)
        self.assertEqual(res.data[0]['id'],tag2.id)
    
    def test_update_tag(self):
        """ test for updating a tag """
        tag =Tag.objects.create(user=self.user,name="seaFood")
        
        payload = {'name':'indianFood'}
        url= detail_url(tag.id) 
        res = self.client.patch(url,payload)
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        tag.refresh_from_db()
        
        self.assertEqual(tag.name,payload['name'])
    
    def test_delete_tag(self):
        """ test for deleting tags """
        tag =Tag.objects.create(user=self.user,name="seaFood2")
        
        url= detail_url(tag.id) 
        res = self.client.delete(url)
        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(user=self.user).exists())
    def test_filter_tags_assigned_to_recipes(self):
        """Test listing tags to those assigned to recipes."""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='Green Eggs on Toast',
            time_minutes=10,
            price=Decimal('2.50'),
            user=self.user,
        )
        recipe.tag.add(tag1)

        res = self.client.get(TAG_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags returns a unique list."""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Dinner')
        recipe1 = Recipe.objects.create(
            title='Pancakes',
            time_minutes=5,
            price=Decimal('5.00'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='Porridge',
            time_minutes=3,
            price=Decimal('2.00'),
            user=self.user,
        )
        recipe1.tag.add(tag)
        recipe2.tag.add(tag)

        res = self.client.get(TAG_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)