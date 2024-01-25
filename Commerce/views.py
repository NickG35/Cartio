from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from .models import User
from .forms import CreateListing
import datetime 

# Create your views here.
def index(request):
    return render(request, 'Commerce/index.html')

def create_listing(request):
     if request.method == "POST":
          form = CreateListing(request.POST)
          if form.is_valid():
               new_listing = form.save(commit=False)
               new_listing.listing_date = datetime.datetime.now()
               new_listing.listing_user = request.user.username
               new_listing.save()
               return HttpResponseRedirect(reverse("index"))
     else:
          form = CreateListing         
          return render(request, 'Commerce/create.html', {
               'form': form,
          })

def register(request):
     if request.method == "POST":
          username = request.POST["username"]
          email = request.POST["email"]
          password = request.POST["password"]
          confirmation = request.POST["confirmation"]
          if password != confirmation:
               return render(request, "Commerce/register.html", {
                    "message": "Passwords do not match"
               })
          
          try:
               user = User.objects.create_user(username, email, password)
               user.save()
          except IntegrityError:
               return render(request, "Commerce/register.html", {
                    "messagey": "Username already taken."
               })
          login(request, user)
          return HttpResponseRedirect(reverse("index"))
     else:
          return render(request,"Commerce/register.html")

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username,password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "Commerce/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "Commerce/login.html")

def logout_view(request):
     logout(request)
     return render(request, "Commerce/login.html")
