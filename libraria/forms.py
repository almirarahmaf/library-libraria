from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile, ReviewWeb, category, booklist, review_user

# Review Web
class ReviewWebForm(forms.ModelForm):
    class Meta:
        model = ReviewWeb
        fields = ['review_field']

# Signup
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists. Please choose another one.")
        return username
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match. Please try again.") 

        return password2
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'style': 'width: 100%;' 'padding-top: 5px;' 'padding-bottom: 5px;' 'border-radius: 5px;',
            'placeholder': 'Enter Username',
        })
        self.fields['email'].widget.attrs.update({
            'style': 'width: 100%;' 'padding-top: 5px;' 'padding-bottom: 5px;' 'border-radius: 5px;',
            'placeholder': 'Enter Email',
        })
        self.fields['password1'].widget.attrs.update({
            'id': 'password-field',
            'style': 'width: 100%; padding-top: 5px; padding-bottom: 5px; border-radius: 5px;',
            'placeholder': 'Enter password',
            'pattern': '(?=.*\d).{8,}',
            'title': 'Must contain at least one number and at least 8 or more characters',
        })
        self.fields['password2'].widget.attrs.update({
            'id': 'confirm-password-signup',
            'style': 'width: 100%;' 'padding-top: 5px;' 'padding-bottom: 5px;' 'border-radius: 5px;',
            'placeholder': 'Confirm password',
        })

# Profile
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'bio', 'profile_picture', 'address', 'phone', 'account']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'name': 'Enter your name',
            'bio': 'Short bio (e.g. Student, Book lover)',
            'profile_picture': '',  # biasanya input file tidak perlu placeholder
            'address': 'Enter your address',
            'phone': 'Enter phone number (e.g. 081234567890)',
            'account': 'Enter your account number',
        }

# Add Book
class addbookForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=category.objects.all(),
        empty_label="Select a category", 
        widget=forms.Select(attrs={
            'class': 'form-control select-placeholder',
        })
    )

    years = forms.ChoiceField(
        choices=[('', 'Select a publication year')] + [(year, year) for year in range(1990, 2026)],
        widget=forms.Select(attrs={
            'class': 'form-control select-placeholder',
        })
    )


    class Meta:
        model = booklist
        fields = [
            'title', 'author', 'publisher', 'number_of_pages', 'years', 
            'category', 'synopsis', 'price', 'cover_image', 'stock',
        ]

        labels = {
            'number_of_pages': 'Number of Page',
            'years': 'Publication Year',
            'cover_image': 'Book Cover',
        }

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control input-detail',
                'placeholder': 'Enter the book title'
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control input-detail',
                'placeholder': 'Enter the author name'
            }),
            'publisher': forms.TextInput(attrs={
                'class': 'form-control input-detail',
                'placeholder': 'Enter the publisher name'
            }),
            'number_of_pages': forms.NumberInput(attrs={
                'class': 'form-control input-detail',
                'placeholder': 'Enter the number of pages'
            }),
            'synopsis': forms.Textarea(attrs={
                'class': 'form-control synopsis',
                'placeholder': 'Write a short synopsis',
                'rows': 5
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control input-detail',
                'placeholder': 'Enter the price'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control',
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control input-detail',
                'placeholder': 'Enter stock quantity'
            }),
        }

class ReviewAccountForm(forms.ModelForm):
    class Meta:
        model = review_user
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'placeholder': 'Rate the librender (1-5)',
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your review here',
                'rows': 4,
            }),
        }