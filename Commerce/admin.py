from django.contrib import admin
from django.contrib.auth.models import User
from .models import User, Listing, Comments, Bid, Profile, Notifications
# Register your models here.

class ProfileInline(admin.StackedInline):
    model= Profile

class CommentInline(admin.StackedInline):
    model= Comments

class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username"]
    inlines = [ProfileInline]

class ListingAdmin(admin.ModelAdmin):
    model = Listing
    list_display = ('listing_name', 'listing_description', 'listing_price', 'listing_category', 'listing_closed', 'bidding_count', 'listing_user', 'listing_date')
    inlines = [CommentInline]

class BidAdmin(admin.ModelAdmin):
    model = Bid
    list_display = ('bidding_listing', 'bidding_price', 'bidding_user')

admin.site.register(User, UserAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Notifications)