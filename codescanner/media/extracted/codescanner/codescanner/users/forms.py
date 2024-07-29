from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# from .models import Files

# class for register from creation. 
class createUserForm(UserCreationForm):
    class Meta:
        model = User
        fields =['username', 'email', 'password1','password2']
