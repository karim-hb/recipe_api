from rest_framework import (viewsets,mixins,)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from recipe import serializers
from core.models import (Recipe,Tag,Ingredient)

class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')
    
    def get_serializer_class(self):
        """ return serializer class for each request """
        
        if self.action == "list":
            return serializers.RecipeSerializer
        
        return self.serializer_class
    
    def perform_create(self,serializer):
        """ create a new recipe """
        serializer.save(user=self.request.user)
        

class BaseView(mixins.DestroyModelMixin,
               mixins.UpdateModelMixin,
               mixins.ListModelMixin,
               viewsets.GenericViewSet):
    """ base viewset """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')
        
class TagViewSet(BaseView):
    """ view for tag API """
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
   
    

class IngredientViewSet(BaseView):
    """ view for ingredient API """
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
   