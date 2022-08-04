from rest_framework import serializers
from core.models import (Recipe,Tag,Ingredient)

class TagSerializer(serializers.ModelSerializer):
    """ serializers for tags """
    
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class IngredientSerializer(serializers.ModelSerializer):
    """ serializers for tags """
    
    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']
        
class RecipeSerializer(serializers.ModelSerializer):
    """ serializers for Recipes """
    tag= TagSerializer(many=True, required=False)
    ingredients= IngredientSerializer(many=True, required=False)
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link','tag','ingredients']
        read_only_fields = ['id']
        
    def _get_or_create_tag(self, tag,recipe):
        auth_user = self.context['request'].user
        for t in tag:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **t,
            )
            recipe.tag.add(tag_obj)
    
    def _get_or_create_ingredients(self, ingredients,recipe):
        auth_user = self.context['request'].user
        for t in ingredients:
            ingredients_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **t,
            )
            recipe.ingredients.add(ingredients_obj)     
    def create(self, validated_data):
        """Create a recipe."""
        tag = validated_data.pop('tag', [])
        ingredients= validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tag(tag,recipe)
        self._get_or_create_ingredients(ingredients,recipe)
        return recipe
    
    def update(self, instance ,validated_data):
        """ update recipe """
        tag = validated_data.pop('tag', None)
        ingredients= validated_data.pop('ingredients', None)
        
        if tag is not None:
            instance.tag.clear()
            self._get_or_create_tag(tag,instance)
            
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients,instance)
                
        for attr, value in validated_data.items():
            setattr(instance,attr,value)
           
        instance.save() 
        return instance
        
  
class RecipeDetailSerializer(RecipeSerializer):
    """ serializers for recipes details """
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description','image'] 
        

class ImageSerializer(serializers.ModelSerializer):
    """ serializers for uploading images """
    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs={'image':{'required':'True'}}