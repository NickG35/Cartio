from django import forms 
from django.forms import ModelForm
from .models import Listing, Bid, Comments

class CreateListing(ModelForm):
    class Meta:
        model = Listing
        fields = ('listing_name', 'listing_image', 'listing_price', 'listing_description','listing_category')

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['listing_name'].label = "Name"
        self.fields['listing_image'].label = "Image"
        self.fields['listing_price'].label = "Price"
        self.fields['listing_description'].label = "Description"
        self.fields['listing_category'].label = "Category"

class CategoryForm(ModelForm):
    class Meta:
        model = Listing
        fields = ('listing_category',)
    
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['listing_category'].label = "Category"

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ('bidding_price',)
    
    def _init_(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['bidding_price'].label = ""

class CommentForm(ModelForm):
    class Meta:
        model = Comments
        fields = ('comment_comment',)
    
    def _init_(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields('comment_comment').label = ""


    