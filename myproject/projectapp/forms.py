# forms.py

# projectapp/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Restaurant

class RestaurantAdminRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    # Restaurant info
    restaurant_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    restaurant_address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists. Please choose a different username.")
        return username

    def clean_restaurant_name(self):
        restaurant_name = self.cleaned_data['restaurant_name']
        if Restaurant.objects.filter(name=restaurant_name).exists(): 
            raise forms.ValidationError("Restaurant name already exists. Please choose a different restaurant name.")
        return restaurant_name


    def save(self):
        # Create user
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )

        # Create restaurant
        restaurant = Restaurant.objects.create(
            name=self.cleaned_data['restaurant_name'],
            address=self.cleaned_data['restaurant_address']
        )

        # Link to UserProfile
        profile = UserProfile.objects.create(
            user=user,
            is_admin=True,
            restaurant=restaurant
        )

        return profile
    
    
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
