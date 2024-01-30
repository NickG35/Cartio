from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    pass

categories = (
    ('technology', 'Technology'),
    ('art', 'Art'),
    ('tools', 'Tools'),
    ('home', 'Home'),
    ('auto', 'Auto'),
    ('memorabilia', 'Memorabilia'),
    ('sports', 'Sports'),
    ('fitness', 'Fitness'),
    ('clothing', 'Clothing'),
    ('health', 'Health'),
    ('beauty', 'Beauty'),
    ('travel', 'Travel'),
    ('pet', 'Pet')
)
class Listing(models.Model):
    listing_name = models.CharField(max_length = 50, blank=False)
    listing_image = models.ImageField(blank=False)
    listing_price = models.IntegerField(blank=False)
    listing_date = models.DateTimeField(blank=False)
    listing_description = models.CharField(max_length = 50, blank=False)
    listing_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listing_user')
    listing_category = models.CharField(max_length=12, choices=categories, blank=False)
    listing_wishlist = models.ManyToManyField(User, related_name='wisher', blank=True)

class Bid(models.Model):
    bidding_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bidding_user')
    bidding_price = models.IntegerField(blank=False)
    bidding_listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bid_listing')

class Comments(models.Model):
    comment_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_user')
    comment_comment = models.CharField(max_length = 300)



