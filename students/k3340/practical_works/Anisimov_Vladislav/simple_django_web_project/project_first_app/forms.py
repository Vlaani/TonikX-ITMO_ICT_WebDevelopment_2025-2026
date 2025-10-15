from django import forms
from .models import Owner, Car

class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = ['username', 'first_name', 'last_name', 'email', 'passport_number', 
                 'address', 'nationality', 'birthday']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'password': forms.PasswordInput(),
        }

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['license_plate', 'brand', 'model', 'color']