from django import forms
from .models import Student_Info

class studform ( forms . ModelForm):

    class Meta:
        model = Student_Info
        fields = [ 'First_Name', 'Last_Name', 'Registration_No', 'Branch', 'Email', 'Parents_Email']
        widgets = {
            'First_Name': forms.TextInput(attrs={'class': 'form-control input-block', 'placeholder': 'First Name'}),
            'Last_Name': forms.TextInput(attrs={'class': 'form-control input-block', 'placeholder': 'Last Name'}),
            'Registration_No': forms.TextInput(attrs={'class': 'form-control input-block', 'placeholder': 'Registration No'}),
            'Branch': forms.Select(attrs={'class': 'form-control input-block'}),
            'Email': forms.TextInput(attrs={'class': 'form-control input-block', 'placeholder': 'Your Email'}),
            'Parents_Email': forms.TextInput(attrs={'class': 'form-control input-block', 'placeholder': 'Parents Email'}),
        }