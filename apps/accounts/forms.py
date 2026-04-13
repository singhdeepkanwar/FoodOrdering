from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RestaurantRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    restaurant_name = forms.CharField(max_length=200, label="Restaurant Name")
    phone = forms.CharField(max_length=20, required=False, label="Phone Number")
    city = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = User.RESTAURANT_ADMIN
        if commit:
            user.save()
        return user
