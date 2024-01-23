from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    pass

class Listing(models.Model):
    listing_name = models.CharField(max_length = 50, blank=False)
    listing_image = models.ImageField(blank=False)
    listing_price = models.IntegerField(blank=False)
    listing_date = models.DateTimeField(blank=False)
    listing_description = models.CharField(max_length = 50, blank=False)
    listing_user = models.ForeignKey(User, on_delete=models.CASCADE)

class Wishlist(models.Model):
    wishlist_user = models.ForeignKey(User, on_delete=models.CASCADE)
    wishlist_name = models.CharField(max_length = 50, blank=False)
    wishlist_image = models.ImageField(blank=False)
    wishlist_date = models.DateTimeField(blank=False)


