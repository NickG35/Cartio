from django import forms 
from django.forms import ModelForm
from .models import Listing, Bid, Comments, Profile

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
        widgets = {
            'comment_comment': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['comment_comment'].widget.attrs["id"] = "comment_form"
        self.fields['comment_comment'].widget.attrs["placeholder"] = "Leave a review..."
        self.fields['comment_comment'].label = ""

class EditProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('profile_pic','bio',)
        widgets = {
            'profile_pic': forms.FileInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['profile_pic'].label = ""
        self.fields['profile_pic'].widget.attrs["id"] = "change_pic" 
        self.fields['bio'].widget.attrs["placeholder"] = "write a bio..."
        self.fields['bio'].widget.attrs["id"] = "bio_field"
        self.fields['bio'].label = ""




    