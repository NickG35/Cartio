from django import forms 
from django.forms import ModelForm
from .models import Listing

class CreateListing(ModelForm):
    class Meta:
        model = Listing
        fields = ('listing_name', 'listing_image', 'listing_price','listing_date', 'listing_description', 'listing_user', 'listing_category')

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['listing_name'].label = "Name"
        self.fields['listing_image'].label = "Image"
        self.fields['listing_price'].label = "Price"
        self.fields['listing_description'].label = "Description"
        self.fields['listing_category'].label = "Category"
        #hide date and user categories
        self.fields['listing_date'].widget = forms.HiddenInput()
        self.fields['listing_user'].widget = forms.HiddenInput()