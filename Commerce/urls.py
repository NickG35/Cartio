from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('profile/<int:profile_id>', views.profile, name='profile'),
    path('create_listing', views.create_listing, name='create_listing'),
    path('listing/<int:listing_id>', views.listing_detail, name='listing'),
    path('wishlist', views.wishlist, name='wishlist'),
    path('categories', views.category, name='category'),
    path('closed_listings', views.closed_listing, name='closed_listing'),
]