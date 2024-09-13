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
import json
from django.http import JsonResponse
from django.middleware.csrf import CsrfViewMiddleware
from django.views.decorators.csrf import csrf_protect
from django.contrib.humanize.templatetags.humanize import naturaltime


def index(request):
    # display all listings that were created by all users
    active_listings = Listing.objects.filter(listing_closed=False).order_by('-listing_date').all()
    return render(request, 'Commerce/index.html', {
          'active_listings': active_listings,
    })

def notifications(request):
     active_notif = Notifications.objects.filter(noti_user=request.user.profile).all()
     return render(request, 'Commerce/layout.html', {
          'notifs': active_notif
     })

def noti_click(request, user_id):
     if request.method == "POST":
          notif_user = Notifications.objects.filter(noti_user=request.user.profile).all()
          for notification in notif_user:
               if notification.noti_count:
                    notification.noti_count = 0
                    notification.save()
               else:
                    pass
          return JsonResponse({"data": {"notifs":notification.noti_count}})

def noti_change(request, noti_id):
     if request.method == "POST":
          notifs = Notifications.objects.filter(id=noti_id)
          for notif in notifs:
               notif.noti_read = True
               notif.save()
          return JsonResponse({"data": {"notifs":notif.noti_read}})

def noti_page(request):
     active_notif = Notifications.objects.filter(noti_user=request.user.profile).all()
     button_disabled = True
     noti_page = True
     return render(request, 'Commerce/notifications.html', {
          'notifs': active_notif,
          'button_disabled': button_disabled,
          'noti_page': noti_page
     })

def profile(request, profile_id):
     profile_user = Profile.objects.get(user_id=profile_id)
     profile_listings = Listing.objects.filter(listing_user=profile_user).all()
     listing_wins = Listing.objects.filter(listing_bid_winner=profile_user).all()
     followers = profile_user.follow.all()
     following = profile_user.followed_by.all

     if request.method == 'POST':
        # Use request.FILES and request.POST together
        form = EditProfileForm(request.POST, request.FILES, instance=profile_user)
        if form.is_valid():
            form.save()
            return redirect(request.META.get('HTTP_REFERER'))
     else:
          editprofileform = EditProfileForm(instance=profile_user)
          profile = Profile.objects.get(user_id=profile_id)
          return render(request, 'Commerce/profile.html', {
               'profile': profile,
               'editprofileform': editprofileform,
               'listings': profile_listings,
               'wins': listing_wins,
               'followers': followers,
               'followings': following
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
     comments = Comments.objects.filter(comment_listing=listing_object).order_by('-comment_time').all()
     if request.method == 'POST':
          # organizing post requests by form and passing variables to bid and comment views
          if 'bid' in request.POST:
               errors = process_bid(request, listing_object, starting_price, bid_price)
               if errors:
                    form = BidForm
                    formy = CommentForm   
                    return render(request, 'Commerce/listing.html', {
                         'listing_object': listing_object,
                         'listings': listing_details,
                         'formy' : formy,
                         'form': form,
                         'comments': comments,
                         'starting_price': starting_price,
                         'bid_count': listing_object.bidding_count,
                         'errors': errors
          })
          elif 'close' in request.POST:
               listing_object.listing_closed = True
               if current_bidder is not None:
                    listing_object.listing_bid_winner = current_bidder.bidding_user
                    existing_count = Notifications.objects.filter(noti_user = current_bidder.bidding_user).values_list('noti_count', flat=True).last()
                    if existing_count is None:
                          Notifications.objects.create(noti_user = current_bidder.bidding_user, noti_winner = current_bidder.bidding_user, noti_listing=listing_object,  noti_count = 1, noti_time=datetime.now())
                    else:
                         Notifications.objects.create(noti_user = current_bidder.bidding_user, noti_winner = current_bidder.bidding_user, noti_listing=listing_object,  noti_count = existing_count + 1, noti_time=datetime.now())
               else:
                    listing_object.listing_bid_winner = listing_object.listing_user
               listing_object.save()
               return HttpResponseRedirect(reverse("index"))
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
     errors = {}
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
                    errors['firstBid'] = 'First bid must be equal or greater than listed price'
          # if there are bids posted, subsequent bids must be greater
          else:
               if current_bid > listing_object.listing_bid_price:
                    listing_object.listing_bid_price = current_bid
                    listing_object.bidding_count += 1
               else:
                    errors['otherBid'] = 'Bids following the first bid must be greater than the previous bid'
          # save the listing object once form is submitted to update listing price
          listing_object.save()
          # update user bid information when form is submitted
          if not errors:
               new_bid.save()

               existing_count = Notifications.objects.filter(noti_user=listing_object.listing_user).values_list('noti_count', flat=True).last()
               if existing_count is None:
                    Notifications.objects.create(noti_user=listing_object.listing_user, noti_bid=request.user.profile, noti_listing=listing_object, noti_count = 1, noti_time=datetime.now())
               else:
                    Notifications.objects.create(noti_user=listing_object.listing_user, noti_bid=request.user.profile, noti_listing=listing_object, noti_count = existing_count + 1, noti_time=datetime.now())
               
          return errors
          
def comment(request, listing_id):
     # comment form allows users to post their comments on a listing
     #add to database properly because html is only replacing the one comment instead of adding multiple
     if request.method == "POST":
          data = json.loads(request.body)
          listing = Listing.objects.get(id=listing_id)
          new_comment = Comments.objects.create(
               comment_listing = listing,
               comment_user = request.user.profile,
               comment_comment = (data["comment_text"]),
               comment_time = datetime.now()
          )
          return JsonResponse({"data": {"comment_pic":new_comment.comment_user.profile_pic.url, "comment_user": new_comment.comment_user.user.username, "comment_comment": new_comment.comment_comment, "comment_time": naturaltime(new_comment.comment_time), "likes":new_comment.comment_likes.count(), "comment_id":new_comment.id, "user_id":request.user.id},})

def follow(request, profile_id):
     if request.method == "POST":
          profile_user = Profile.objects.get(user_id=profile_id)
          follower_id = request.user.profile
          follow_id = request.user.profile.user_id
          profile_user.followed_by.add(follower_id)
          follower_profile = Profile.objects.get(user_id=follow_id)
          profile_user.save()
          existing_count = Notifications.objects.filter(noti_user=profile_user).values_list('noti_count', flat=True).last()
          if existing_count is None:
               Notifications.objects.create(noti_user=profile_user, noti_follower=request.user.profile, noti_count = 1, noti_time=datetime.now())
          else:
               Notifications.objects.create(noti_user=profile_user, noti_follower=request.user.profile,noti_count = existing_count + 1, noti_time=datetime.now())
          if follower_profile.profile_pic and follower_profile.profile_pic.url:
               return JsonResponse({
                    "data": {
                         "followers": profile_user.followed_by.count(),
                         "following": profile_user.follow.count(),
                         "follower_id": follower_profile.user_id,
                         "follower_pfp": follower_profile.profile_pic.url,
                         "follow_user": follower_profile.user.username
                    }
               })
          else:
               return JsonResponse({
                    "data": {
                         "followers": profile_user.followed_by.count(),
                         "following": profile_user.follow.count(),
                         "follower_id": follower_profile.user_id,
                         "follower_pfp": "../media/images/default_profile.png",
                         "follow_user": follower_profile.user.username
                    }
               })

def unfollow(request, profile_id):
     if request.method == "POST":
          profile_user = Profile.objects.get(user_id=profile_id)
          follower_id = request.user.profile
          follow_id = request.user.profile.user_id
          profile_user.followed_by.remove(follower_id)
          follower_profile = Profile.objects.get(user_id=follow_id)
          profile_user.save()
          follower_filter = Notifications.objects.filter(noti_user=profile_user, noti_follower=request.user.profile)
          follower_filter.delete()
          if follower_profile.profile_pic and follower_profile.profile_pic.url:
               return JsonResponse({
                    "data": {
                         "followers": profile_user.followed_by.count(),
                         "following": profile_user.follow.count(),
                         "follower_id": follower_profile.user_id,
                         "follower_pfp": follower_profile.profile_pic.url,
                         "follow_user": follower_profile.user.username
                    }
               })
          else:
               return JsonResponse({
                    "data": {
                         "followers": profile_user.followed_by.count(),
                         "following": profile_user.follow.count(),
                         "follower_id": follower_profile.user_id,
                         "follower_pfp": "../media/images/default_profile.png",
                         "follow_user": follower_profile.user.username
                    }
               })

@csrf_protect
def like_toggle(request, comment_id):
     if request.method == "POST":
          user = request.user.profile.id
          comments = Comments.objects.get(id=comment_id)
          comments.comment_likes.add(user)
          comments.save()
          return JsonResponse({"data": {"likes":comments.comment_likes.count()}})

@csrf_protect
def unlike_toggle(request, comment_id):
     if request.method == "POST":
          user = request.user.profile.id
          comments = Comments.objects.get(id=comment_id)
          comments.comment_likes.remove(user)
          comments.save()
          return JsonResponse({"data": {"likes":comments.comment_likes.count()}})

def delete_comment(request, comment_id):
     if request.method == "POST":
          comments = Comments.objects.get(id=comment_id)
          commentListing = comments.comment_listing
          comments.delete()
          comment_count = Comments.objects.filter(comment_listing=commentListing).count()
          no_comments = comment_count == 0
          return JsonResponse({"data": {"comment": comments.comment_comment, "no_comments":no_comments}})
     
def add_wish(request, user_id):
          if request.method == "POST":
               data = json.loads(request.body)
               listing_id = (data["listingId"])
               listing = Listing.objects.get(id=listing_id)
               user = Profile.objects.get(id=user_id)
               listing.listing_wishlist.add(user)
               listing.save()
               return JsonResponse({"data": {"user":request.user.username}})

def remove_wish(request, user_id):
          if request.method == "POST":
               data = json.loads(request.body)
               listing_id = (data["listingId"])
               listing = Listing.objects.get(id=listing_id)
               user = Profile.objects.get(id=user_id)
               listing.listing_wishlist.remove(user)
               listing.save()
               return JsonResponse({"data": {"user":request.user.username}})


def wishlist(request):
     # display wishlist items of the specific user signed in 
     wishes = Listing.objects.filter(listing_wishlist=request.user.profile.id,listing_closed=False).all()
     return render(request, 'Commerce/wishlist.html', {
          'wishes': wishes
     })

def category(request, category_name):
     # the category selected and submitted will display all listings that are under that specific category
     categories = Listing.objects.filter(listing_category=category_name, listing_closed=False ).all()
     return render(request, 'Commerce/categories.html', {
          'categories':categories,
          'category_name': category_name
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
          loggin = True
          errors = {}

          if not email:
               errors['email'] = "Please enter an email"

           # if username not entered, raise an error
          if not username:
               errors['username'] = "Please enter a username"
          else:
               try:
                    user = User.objects.create_user(username, email, password)
                    user.save()
               except IntegrityError:
                    errors['username'] = "Username already taken"
          
          #if password is not entered, raise an error
          if not password:
               errors['password'] = "Please enter a password"

          # if password doesn't match, raise an error message
          if password != confirmation:
               errors['confirmation'] = "Passwords do not match"

          if not errors:
                # if not log the user in immediately
               login(request, user)
               return HttpResponseRedirect(reverse("index"))   
          else:
               return render(request, "Commerce/register.html", {
                    "errors": errors,
                    'loggin': loggin
               })
     else:
          loggin = True
          return render(request,"Commerce/register.html", {
               'loggin': loggin
          })

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
            loggin = True
            return render(request, "Commerce/login.html", {
                "message": "Invalid username and/or password.",
                'loggin': loggin
            })
    else:
        loggin = True
        return render(request, "Commerce/login.html", {
             'loggin': loggin
        })

def logout_view(request):
     # log user out of site
     logout(request)
     return HttpResponseRedirect(reverse("login"))
