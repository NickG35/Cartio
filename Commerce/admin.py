from django.contrib import admin
from django.contrib.auth.models import User
from .models import User
# Register your models here.
class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username"]

admin.site.register(User, UserAdmin)