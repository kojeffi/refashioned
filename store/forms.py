
from django import forms
from .models import Review
from django.contrib.auth.models import User
from .models import Product

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image', 'category']


from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating > 5:
            raise forms.ValidationError("Rating cannot exceed 5.")
        return rating


from django import forms
from .models import BlogPost

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content']


from django import forms

class ImageUploadForm(forms.Form):
    image = forms.ImageField()


from django import forms
from .models import SupplyChainForecast

class SupplyChainForecastForm(forms.ModelForm):
    class Meta:
        model = SupplyChainForecast
        fields = ['forecast_date', 'forecast_data']
        widgets = {
            'forecast_date': forms.DateInput(attrs={'type': 'date'}),
        }


from django import forms
from .models import Transaction

from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'product']
