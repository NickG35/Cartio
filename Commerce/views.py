from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from .models import User, Listing, Comments, Bid, Profile, Notifications
from .forms import CreateListing, CategoryForm, BidForm, CommentForm, EditProfileForm
from datetime import datetime 
from django.core.exceptions import ValidationError

def index(request):
    # display all listings that were created by all users
    active_listings = Listing.objects.filter(listing_closed=False).all()
    return render(request, 'Commerce/index.html', {
          'active_listings': active_listings,
    })

def notifications(request):
     active_notif = Notifications.objects.filter(noti_user=request.user.profile).order_by('-time').all()
     return render(request, 'Commerce/layout.html', {
          'notifs': active_notif
     })

def profile(request, profile_id):
     profile_user = Profile.objects.get(user_id=profile_id)
     profile_listings = Listing.objects.filter(listing_user=profile_user).all()
     listing_wins = Listing.objects.filter(listing_bid_winner=profile_user).all()

     

     if request.method == 'POST':
          if 'profile_pic' in request.FILES:
               editprofileform = EditProfileForm(request.FILES)
               if editprofileform.is_valid():
                    profile_pic_file = request.FILES['profile_pic']
                    profile_user.profile_pic = profile_pic_file
                    profile_user.save()
          elif 'bio' in request.POST:
               editprofileform = EditProfileForm(request.POST)
               if editprofileform.is_valid():
                    bio = editprofileform.cleaned_data['bio']
                    profile_user.bio = bio
                    profile_user.save()

          elif 'unfollow' in request.POST:
               follower_id = request.POST['follower']
               follower_profile = Profile.objects.get(user_id=request.user.id)
               profile_user.followed_by.remove(follower_id)
               Notifications.objects.filter(noti_user=profile_user, noti_follower=follower_profile).delete()
          elif 'follow' in request.POST:
               follower_id = request.POST['follower']
               follower_profile = Profile.objects.get(user_id=request.user.id)
               profile_user.followed_by.add(follower_id)
               Notifications.objects.create(noti_user=profile_user, noti_follower=follower_profile)
               
               # add notification user by getting noti_user = profile_user and noti_follower = follower

              
          return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
     else:
          editprofileform = EditProfileForm(instance=profile_user)
          profile = Profile.objects.get(user_id=profile_id)
          return render(request, 'Commerce/profile.html', {
               'profile': profile,
               'profile_user': profile_user,
               'editprofileform': editprofileform,
               'listings': profile_listings,
               'wins': listing_wins
          })

def comment(request, comment_id):
     comment_info = Comments.objects.filter(id=comment_id).all()
     return render(request, 'Commerce/comment.html', {
          'comments': comment_info
     })

def create_listing(request):
     if request.method == "POST":
          # form that allows user to create their own listings
          form = CreateListing(request.POST, request.FILES)
          if form.is_valid():
               new_listing = form.save(commit=False)
               new_listing.listing_date = datetime.now()
               new_listing.listing_user = request.user.profile
               new_listing.save()
               return HttpResponseRedirect(reverse("index"))
     else:
          form = CreateListing()         
     return render(request, 'Commerce/create.html', {
          'form': form
     })

def listing_detail(request, listing_id):
     # variables used to pass through bids and comments forms
     listing_details = Listing.objects.filter(id=listing_id).all()
     listing_object = get_object_or_404(Listing, id=listing_id)
     starting_price = listing_object.listing_price
     bid_price = listing_object.listing_bid_price
     current_bidder = Bid.objects.filter(bidding_listing=listing_object).last()
     comments = Comments.objects.filter(comment_listing=listing_object).order_by('comment_time').all()
     if request.method == 'POST':
          # organizing post requests by form and passing variables to bid and comment views
          if 'bid' in request.POST:
               process_bid(request, listing_object, starting_price, bid_price)
          elif 'comment' in request.POST:
               process_comment(request, listing_object)
          elif 'close' in request.POST:
               listing_object.listing_closed = True
               if current_bidder is not None:
                    listing_object.listing_bid_winner = current_bidder.bidding_user
               else:
                    listing_object.listing_bid_winner = listing_object.listing_user
               listing_object.save()
               return HttpResponseRedirect(reverse("index"))
          # add listing to wishlist
          elif 'add_wishlist' in request.POST:
               listing_object.listing_wishlist.add(request.user.profile.id)
          # remove listing from wishlist
          elif 'remove_wishlist' in request.POST:
               listing_object.listing_wishlist.remove(request.user.profile.id)
          return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
     else:
          # presents bid and comment forms
          form = BidForm
          formy = CommentForm     
          return render(request, 'Commerce/listing.html', {
               # converting variables to html template to display on listing page
                    'listings': listing_details,
                    'form' : form,
                    'formy' : formy,
                    'comments': comments,
                    'starting_price': starting_price,
                    'bid_count': listing_object.bidding_count
          })

def process_bid(request, listing_object, starting_price, bid_price):      
     form = BidForm(request.POST)
     # bid form to allow users to post bids
     if form.is_valid():
          new_bid = form.save(commit=False)
          new_bid.bidding_user = request.user.profile
          new_bid.bidding_listing = listing_object
          current_bid = new_bid.bidding_price
          # if no bids are posted, the first bid can be greater or equal to the original price
          if bid_price is None:
               if current_bid >= starting_price:
                    listing_object.listing_bid_price = current_bid
                    listing_object.bidding_count += 1
               else:
                    raise ValueError('bid is invalid')
          # if there are bids posted, subsequent bids must be greater
          else:
               if current_bid > listing_object.listing_bid_price:
                    listing_object.listing_bid_price = current_bid
                    listing_object.bidding_count += 1
               else:
                    raise ValueError('bid is invalid')
          # save the listing object once form is submitted to update listing price
          listing_object.save()
          # update user bid information when form is submitted
          new_bid.save()
          Notifications.objects.create(noti_user=listing_object.listing_user, noti_bid=request.user.profile, noti_listing=listing_object)
          
def process_comment(request, listing_object):
     # comment form allows users to post their comments on a listing
     formy = CommentForm(request.POST)
     if formy.is_valid():
          new_comment = formy.save(commit=False)
          new_comment.comment_user = request.user.profile
          new_comment.comment_listing = listing_object
          new_comment.comment_time = datetime.now()
          new_comment.save()

def like_comment(request, comment_id):
     if request.method == "POST":
          comment = Comments.objects.get(id=comment_id)
          comment_liker = request.POST['like']
          comment.comment_likes.add(comment_liker)
          comment.save()
          liker_profile = Profile.objects.get(user_id=request.user.id)
          Notifications.objects.create(noti_user=comment.comment_user, noti_like=liker_profile, noti_time = datetime.now(), noti_comment=comment)
          return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
     
def unlike_comment(request, comment_id):
     if request.method == "POST":
          comment = Comments.objects.get(id=comment_id)
          comment_unliker = request.POST['unlike']
          comment.comment_likes.remove(comment_unliker)
          comment.save()
          liker_profile = Profile.objects.get(user_id=request.user.id)
          Notifications.objects.filter(noti_user=comment.comment_user, noti_like=liker_profile).delete()
          return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



def wishlist(request):
     # display wishlist items of the specific user signed in 
     wishes = Listing.objects.filter(listing_wishlist=request.user.profile.id,listing_closed=False).all()
     return render(request, 'Commerce/wishlist.html', {
          'wishes': wishes
     })

def category(request):
     if request.method == 'POST':
          # display category form on page
          form = CategoryForm
          # the category selected and submitted will display all listings that are under that specific category
          category = request.POST['listing_category']
          categories = Listing.objects.filter(listing_category=category, listing_closed=False ).all()
          return render(request, 'Commerce/categories.html', {
               'form': form,
               'categories':categories
          })

     else: 
          form = CategoryForm
          return render(request, 'Commerce/categories.html', {
               'form': form,
          })

def closed_listing(request):
     closed_listings = Listing.objects.filter(listing_closed=True).all()
     return render(request, 'Commerce/closed_listings.html', {
          'closed_listings': closed_listings 
     })

def register(request):
     # allow a user to register for the site
     if request.method == "POST":
          username = request.POST["username"]
          email = request.POST["email"]
          password = request.POST["password"]
          confirmation = request.POST["confirmation"]
          # if password doesn't match, raise an error message
          if password != confirmation:
               return render(request, "Commerce/register.html", {
                    "message": "Passwords do not match"
               })
          # if user already exists, raise error message
          try:
               user = User.objects.create_user(username, email, password)
               user.save()
          except IntegrityError:
               return render(request, "Commerce/register.html", {
                    "messagey": "Username already taken."
               })
          # if not log the user in immediately
          login(request, user)
          return HttpResponseRedirect(reverse("index"))
     else:
          return render(request,"Commerce/register.html")

def login_view(request):
    # allow user to log in with their username and password
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username,password=password)
        # if the user exists in database, allow user to log in
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        # if not provide error message
        else:
            return render(request, "Commerce/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "Commerce/login.html")

def logout_view(request):
     # log user out of site
     logout(request)
     return HttpResponseRedirect(reverse("index"))
