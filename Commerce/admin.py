from django.contrib import admin
from django.contrib.auth.models import User
from .models import User, Listing, Wishlist
# Register your models here.
class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username"]

admin.site.register(User, UserAdmin)
admin.site.register(Listing)
admin.site.register(Wishlist)