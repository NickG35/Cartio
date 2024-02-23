from django.contrib import admin
from django.contrib.auth.models import User
from .models import User, Listing, Comments, Bid, Profile
# Register your models here.

class ProfileInline(admin.StackedInline):
    model= Profile

class ListingInline(admin.StackedInline):
    model = Listing
    fk_name = 'listing_user'

class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username"]
    inlines = [ProfileInline, ListingInline]

admin.site.register(User, UserAdmin)
admin.site.register(Listing)
admin.site.register(Comments)
admin.site.register(Bid)