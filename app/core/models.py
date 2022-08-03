from re import T
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.conf import settings
# Create your models here.

class UserManger(BaseUserManager):
    """ Manager for user """
    
    def create_user(self,email,password=None , **extra_feilds):
        "create , save user and return"
        if not email:
            raise ValueError('user must have a valid email address')
        
        user = self.model(email=self.normalize_email(email), **extra_feilds)
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self,email,password):
        """ create and save superuser """
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        
        return user
        

class User(AbstractBaseUser ,PermissionsMixin ):
    """ user in systems """
    
    email = models.EmailField(max_length=255 , unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManger()
    
    USERNAME_FIELD = 'email'
    
    
class Recipe(models.Model):
    """ recipe model """
    user= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title= models.CharField(max_length=255)
    description= models.TextField(blank=True)
    time_minutes= models.IntegerField()
    price= models.DecimalField(max_digits=5, decimal_places=2)
    link= models.CharField(max_length=255,blank=True)
    tag= models.ManyToManyField('Tag')
    
    def __str__(self):
        return self.title

class Tag(models.Model):
    user= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name= models.CharField(max_length=255)
    
    def __str__(self):
        return self.name