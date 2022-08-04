from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
import os
import tempfile
from PIL import Image
from rest_framework.test import APIClient
from rest_framework import status

from decimal import Decimal
from core.models import (Recipe,Tag,Ingredient)
from recipe.serializers import (RecipeSerializer, RecipeDetailSerializer)

RECIPE_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """ create and return recipe details url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])

def create_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00,
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)

def create_user( **params):
    """ create and return new user """
    return get_user_model().objects.create_user(**params)

def image_upload_url(recipe_id):
    """ create and return image upload url """
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


class PubicTestRecipe(TestCase):
    """ test public url for recipe """
    
    def setUp(self):
        self.client = APIClient()
        
    def test_auth_requeird(self):
        """ test for un authorized request  """
        res = self.client.get(RECIPE_URL)
        
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
class PrivateRecipeTest(TestCase):
    """ test private api """
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email = 'user@example.com',
            password ='password123!',
        )
        self.client.force_authenticate(user=self.user)
        
        
    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_recipe_for_limited_user(self):
        """ each user just access to their recipe """
        other_user = create_user(
           email= 'other_user',
           password= 'other_userP@aas'
        )
        
        create_recipe(other_user)
        create_recipe(user=self.user)
        
        res = self.client.get(RECIPE_URL)
        
        recipes = Recipe.objects.filter(user=self.user)
        serializers = RecipeSerializer(recipes,many=True)
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializers.data)
    
    def test_recipe_detail(self):
        """ test for get recipe detail by id"""
        payload = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00,
        'description':'description',
        }
        recipe = create_recipe(user=self.user,**payload)
        
        recipe_url= detail_url(recipe.id)
        res = self.client.get(recipe_url)
        serializers = RecipeDetailSerializer(recipe)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializers.data)
    
    def test_create_recipe(self):
        payload = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': Decimal('5.5'),
        }
        res = self.client.post(RECIPE_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key,value in payload.items():
            self.assertEqual(getattr(recipe,key),value)
        self.assertEqual(recipe.user,self.user)
    
    def test_partial_update(self):
        original_link="https://example.com/recipe"
        recipe = create_recipe(user=self.user,title="test3title",link=original_link)
        
        payload={'title':'new title 4'}
        
        recipe_url= detail_url(recipe.id)
        res = self.client.patch(recipe_url,payload)
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        recipe.refresh_from_db()
        
        self.assertEqual(recipe.title,payload['title'])
        self.assertEqual(recipe.link,original_link)
        self.assertEqual(recipe.user,self.user)
    
    def test_update_full(self):
        recipe = create_recipe(
            user=self.user,
            title="test3title",
            link="https://example.com/recipe",
            description="some de\]",
            )
        payload = {"title":"new 5",
                   "link":"https://example.com/new-recipe",
                   "description":"edited desc",
                   'time_minutes': 10,
                   'price': 5.00,
                   }
        
        recipe_url= detail_url(recipe.id)
        res = self.client.put(recipe_url,payload)
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        recipe.refresh_from_db()
        
        for key,value in payload.items():
            self.assertEqual(getattr(recipe,key),value)
        self.assertEqual(recipe.user,self.user)
        
    def test_update_user_return_error(self):
        """ check while updating recipe user wont update """
        new_user= create_user(email="example@example.com" , password="example")
        recipe = create_recipe(user=self.user)
        
        payload ={'user':new_user.id}
        url= detail_url(recipe.id)
        self.client.patch(url,payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user,self.user)
        
    def test_delete_recipe(self):
        """ test for deleting a recipe """
        recipe = create_recipe(user=self.user)
        url= detail_url(recipe.id)
        res= self.client.delete(url)
        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())
        
    def test_delete_other_user_recipe(self):
        """ test for deleting other user recipe """
        new_user= create_user(email="example@example.com" , password="example")
        recipe = create_recipe(new_user)
        
        url= detail_url(recipe.id)
        res= self.client.delete(url)
        
        self.assertEqual(res.status_code,status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
    
    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tag': [{'name': 'Thai'}, {'name': 'Dinner'}],
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tag.count(), 2)
        for tag in payload['tag']:
            exists = recipe.tag.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tag(self):
        """Test creating a recipe with existing tag."""
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'tag': [{'name': 'Indian'}, {'name': 'Breakfast'}],
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tag.count(), 2)
        self.assertIn(tag_indian, recipe.tag.all())
        for tag in payload['tag']:
            exists = recipe.tag.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)
    
    def test_update_recipe_with_tags(self):
        """ test for adding tag to existed recipe """
        recipe = create_recipe(user=self.user)
        payload= {
            'tag':[{'name':'new1'}]
        }
        url= detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user,name='new1')
        self.assertIn(new_tag,recipe.tag.all())
    
    def test_update_recipe_with_existed_tag(self):
        """ update recipe with existed tag """
        recipe = create_recipe(user=self.user)
        breakfast_tag= Tag.objects.create(user=self.user,name="breakfast")
        recipe.tag.add(breakfast_tag)
         
        tag_lunch= Tag.objects.create(user=self.user,name="launch")
        payload = {'tag':[{'name':'launch'}]}
        url= detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        self.assertIn(tag_lunch,recipe.tag.all())
        self.assertNotIn(breakfast_tag,recipe.tag.all())
    
    def test_clear_recipe_tags(self):
        recipe = create_recipe(user=self.user)
        breakfast_tag= Tag.objects.create(user=self.user,name="breakfast")
        recipe.tag.add(breakfast_tag)
        
        payload = {'tag':[]}
        url= detail_url(recipe.id)
        
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        self.assertEqual(recipe.tag.count(), 0)
        
    def test_create_recipe_with_new_ingredients(self):
        """Test creating a recipe with new ingredients."""
        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'ingredients': [{'name': 'Thai'}, {'name': 'Dinner'}],
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredients(self):
        """Test creating a recipe with existing ingredients."""
        rice = Ingredient.objects.create(user=self.user, name='rice')
        payload = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'ingredients': [{'name': 'rice'}, {'name': 'Breakfast'}],
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(rice, recipe.ingredients.all())
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)
    
    def test_update_recipe_with_ingredients(self):
        """ test for adding ingredients to existed recipe """
        recipe = create_recipe(user=self.user)
        payload= {
            'ingredients':[{'name':'new1'}]
        }
        url= detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredients = Ingredient.objects.get(user=self.user,name='new1')
        self.assertIn(new_ingredients,recipe.ingredients.all())
    
    def test_update_recipe_with_existed_ingredients(self):
        """ update recipe with existed ingredients """
        recipe = create_recipe(user=self.user)
        breakfast_ingredients= Ingredient.objects.create(user=self.user,name="breakfast")
        recipe.ingredients.add(breakfast_ingredients)
         
        ingredients_lunch= Ingredient.objects.create(user=self.user,name="launch")
        payload = {'ingredients':[{'name':'launch'}]}
        url= detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        self.assertIn(ingredients_lunch,recipe.ingredients.all())
        self.assertNotIn(breakfast_ingredients,recipe.ingredients.all())
    
    def test_clear_recipe_ingredients(self):
        recipe = create_recipe(user=self.user)
        breakfast_ingredients= Ingredient.objects.create(user=self.user,name="breakfast")
        recipe.ingredients.add(breakfast_ingredients)
        
        payload = {'ingredients':[]}
        url= detail_url(recipe.id)
        
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        self.assertEqual(recipe.ingredients.count(), 0)
    def test_filter_by_tags(self):
        """Test filtering recipes by tags."""
        r1 = create_recipe(user=self.user, title='Thai Vegetable Curry')
        r2 = create_recipe(user=self.user, title='Aubergine with Tahini')
        tag1 = Tag.objects.create(user=self.user, name='Vegan')
        tag2 = Tag.objects.create(user=self.user, name='Vegetarian')
        r1.tag.add(tag1)
        r2.tag.add(tag2)
        r3 = create_recipe(user=self.user, title='Fish and chips')

        params = {'tag': f'{tag1.id},{tag2.id}'}
        res = self.client.get(RECIPE_URL, params)

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

    def test_filter_by_ingredients(self):
        """Test filtering recipes by ingredients."""
        r1 = create_recipe(user=self.user, title='Posh Beans on Toast')
        r2 = create_recipe(user=self.user, title='Chicken Cacciatore')
        in1 = Ingredient.objects.create(user=self.user, name='Feta Cheese')
        in2 = Ingredient.objects.create(user=self.user, name='Chicken')
        r1.ingredients.add(in1)
        r2.ingredients.add(in2)
        r3 = create_recipe(user=self.user, title='Red Lentil Daal')

        params = {'ingredients': f'{in1.id},{in2.id}'}
        res = self.client.get(RECIPE_URL, params)

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)
        
class ImageUploadTestCase(TestCase):
    """ all test for upload image for recipe API """
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email = 'user@example.com',
            password ='password123!',
        )
        self.client.force_authenticate(user=self.user)
        self.recipe = create_recipe(self.user)
    
    def tearDown(self):
        self.recipe.image.delete()
    def test_upload_image(self):
        """Test uploading an image to a recipe."""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image."""
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'notanimage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)