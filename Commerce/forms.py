from django import forms 
from django.forms import ModelForm
from .models import Listing, Bid, Comments

class CreateListing(ModelForm):
    class Meta:
        model = Listing
        fields = ('listing_name', 'listing_image', 'listing_price', 'listing_description','listing_category')

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['listing_name'].widget.attrs["placeholder"] = "Enter name"
        self.fields['listing_price'].widget.attrs["placeholder"] = "Enter price"
        self.fields['listing_description'].widget.attrs["placeholder"] = "Write a description"
        self.fields['listing_name'].label = ""
        self.fields['listing_image'].label = ""
        self.fields['listing_price'].label = ""
        self.fields['listing_description'].label = ""
        self.fields['listing_category'].label = ""
        self.fields['listing_name'].widget.attrs['id'] = "inputs"
        self.fields['listing_image'].widget.attrs['id']  = "image-input"
        self.fields['listing_price'].widget.attrs['id']  = "inputs"
        self.fields['listing_description'].widget.attrs['id']  = "inputs"
        self.fields['listing_category'].widget.attrs['id']  = "inputs"

class CategoryForm(ModelForm):
    class Meta:
        model = Listing
        fields = ('listing_category',)
    
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['listing_category'].label = ""
        self.fields['listing_category'].widget.attrs['id'] = "inputs"

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ('bidding_price',)
    
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['bidding_price'].widget.attrs["placeholder"] = "Enter bid amount"
        self.fields['bidding_price'].widget.attrs['class'] = "form-bid"
        self.fields['bidding_price'].label = ""

class CommentForm(ModelForm):
    class Meta:
        model = Comments
        fields = ('comment_comment',)
    
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['comment_comment'].widget.attrs["placeholder"] = "Leave a comment..."
        self.fields['comment_comment'].label = ""


    