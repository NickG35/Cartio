from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from .models import User, Listing
from .forms import CreateListing, CategoryForm
from datetime import datetime 

# Create your views here.
def index(request):
    active_listings = Listing.objects.filter(listing_user=request.user).all()
    return render(request, 'Commerce/index.html', {
          'active_listings': active_listings
    })

def create_listing(request):
     if request.method == "POST":
          form = CreateListing(request.POST, request.FILES)
          if form.is_valid():
               new_listing = form.save(commit=False)
               new_listing.listing_date = datetime.now()
               new_listing.listing_user = request.user.id
               new_listing.save()
               return HttpResponseRedirect(reverse("index"))
     else:
          form = CreateListing()         
     return render(request, 'Commerce/create.html', {
          'form': form
     })

def listing_detail(request, listing_id):
     current_user = request.user
     listing_details = Listing.objects.filter(id=listing_id).all()
     wishlist_user = Listing.objects.get(id=listing_id)
     if request.method == 'POST' and 'add_wishlist' in request.POST:
          wishlist_user.listing_wishlist.add(current_user)
          return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
     elif request.method == 'POST' and 'remove_wishlist' in request.POST:
          wishlist_user.listing_wishlist.remove(current_user)
          return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
     else:     
          return render(request, 'Commerce/listing.html', {
                'listings': listing_details,
          })

# working on how to add listings to user's wishlist by submitting form
def wishlist(request):
     wishes = Listing.objects.filter(listing_wishlist=request.user.id).all()
     return render(request, 'Commerce/wishlist.html', {
          'wishes': wishes
     })

def category(request):
     if request.method == 'POST':
          form = CategoryForm
          category = request.POST['listing_category']
          categories = Listing.objects.filter(listing_category=category).all()
          return render(request, 'Commerce/categories.html', {
               'form': form,
               'categories':categories
          })

     else: 
          form = CategoryForm
          return render(request, 'Commerce/categories.html', {
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
