
"""
Tests for the ingredients API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (Ingredient,Recipe,)
from recipe.serializers import (IngredientSerializer)

INGREDIENT_URL = reverse('recipe:ingredient-list')

def detail_url(ingredient_id):
    """ create and return ingredient details url"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])

def create_user(email="test@example.com", password="testpassword"):
    """ create user and return it """
    return get_user_model().objects.create_user(email,password)

class PubicTestIngredient(TestCase):
    """ test public url for Ingredient """
    
    def setUp(self):
        self.client = APIClient()
        
    def test_auth_requeird(self):
        """ test for un authorized request  """
        res = self.client.get(INGREDIENT_URL)
        
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
class PrivateTestIngredient(TestCase):
    """ test authenticated user for private Ingredient """
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)
    
    def test_ingredient_list(self):
        """ test for retriving ingredient """
        Ingredient.objects.create(user=self.user,name="rice")
        Ingredient.objects.create(user=self.user,name="meet")
        
        res = self.client.get(INGREDIENT_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializers = IngredientSerializer(ingredients,many=True)
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializers.data)
        
    def test_limited_ingredients(self):
        """ test ingredientss are shown for the user that created that ingredients """
        
        new_user = create_user(email="use222r@example.com")
        
        Ingredient.objects.create(user=new_user,name="rice")
        ingredients2 =Ingredient.objects.create(user=self.user,name="meet")
        res = self.client.get(INGREDIENT_URL)
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'],ingredients2.name)
        self.assertEqual(res.data[0]['id'],ingredients2.id)
    
    def test_update_ingredient(self):
        """ test for updating a ingredient """
        ingredient =Ingredient.objects.create(user=self.user,name="meet")
        
        payload = {'name':'indianFood'}
        url= detail_url(ingredient.id) 
        res = self.client.patch(url,payload)
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        ingredient.refresh_from_db()
        
        self.assertEqual(ingredient.name,payload['name'])
    
    def test_delete_ingredient(self):
        """ test for deleting ingredients """
        ingredient =Ingredient.objects.create(user=self.user,name="meet2")
        
        url= detail_url(ingredient.id) 
        res = self.client.delete(url)
        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(user=self.user).exists())
    def test_filter_ingredients_assigned_to_recipes(self):
        """Test listing ingedients to those assigned to recipes."""
        in1 = Ingredient.objects.create(user=self.user, name='Apples')
        in2 = Ingredient.objects.create(user=self.user, name='Turkey')
        recipe = Recipe.objects.create(
            title='Apple Crumble',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe.ingredients.add(in1)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients returns a unique list."""
        ing = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentils')
        recipe1 = Recipe.objects.create(
            title='Eggs Benedict',
            time_minutes=60,
            price=Decimal('7.00'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='Herb Eggs',
            time_minutes=20,
            price=Decimal('4.00'),
            user=self.user,
        )
        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)