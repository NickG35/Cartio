from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save

# Create your models here.
class User(AbstractUser):
    pass

class Profile(models.Model):
    # each user has a profile
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # one profile can follow other profiles, symettrical is set to false because the user doesnt have to follow back their followers, and it is blank because they dont have to follow anyone
    follow = models.ManyToManyField("self",
                                    related_name="followed_by",
                                    symmetrical=False,
                                    blank=True)
    def __str__(self):
        return self.user.username
    
    # automatically create profile when user signs up 
    def create_profile(sender, instance, created, **kwargs):
        if created:
            user_profile = Profile(user=instance)
            user_profile.save()
    post_save.connect(create_profile, sender=User)

categories = (
    ('', 'Select a category'),
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
    listing_image = models.ImageField(blank=False, upload_to="images/")
    listing_price = models.IntegerField(blank=False)
    listing_date = models.DateTimeField(blank=False)
    listing_description = models.CharField(max_length = 50, blank=False)
    listing_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listing_user')
    listing_category = models.CharField(max_length=12, choices=categories, blank=False)
    listing_wishlist = models.ManyToManyField(User, related_name='wisher', blank=True)
    listing_closed = models.BooleanField(default=False)
    listing_bid_price = models.IntegerField(blank=True, null=True)
    listing_bid_winner = models.ForeignKey(User, related_name='bid_winner', blank=True, null=True, on_delete=models.PROTECT)
    bidding_count = models.IntegerField(default=0)
    

    def __str__(self):
        return f"{self.listing_name}"


class Bid(models.Model):
    bidding_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bidding_user')
    bidding_price = models.IntegerField(blank=False)
    bidding_listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bid_listing')

    def __str__(self):
        return f"{self.bidding_listing}"



class Comments(models.Model):
    comment_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_user')
    comment_comment = models.CharField(max_length = 300)
    comment_listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='listing_comment', blank=True, null=True)

    def __str__(self):
        return f"{self.comment_comment}"



