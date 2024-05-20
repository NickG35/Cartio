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
    path('add_wish/<int:user_id>', views.add_wish, name='add_wish'),
    path('remove_wish/<int:user_id>', views.remove_wish, name='remove_wish'),
    path('wishlist', views.wishlist, name='wishlist'),
    path('categories', views.category, name='category'),
    path('closed_listings', views.closed_listing, name='closed_listing'),
    path('follow/<int:profile_id>', views.follow, name='follow'),
    path('unfollow/<int:profile_id>', views.unfollow, name='unfollow'),
    path("like_toggle/<int:comment_id>", views.like_toggle, name= "like_toggle"),
    path("unlike_toggle/<int:comment_id>", views.unlike_toggle, name= "unlike_toggle"),
    path("delete_comment/<int:comment_id>", views.delete_comment, name="delete_comment"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("noti_click/<int:user_id>", views.noti_click, name="noti_click"),
    path("noti_change/<int:noti_id>", views.noti_change, name="noti_change"),
    path('notifications', views.noti_page, name="noti_page")
]