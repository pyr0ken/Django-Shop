from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='password', widget=forms.PasswordInput)  # todo
    password2 = forms.CharField(label='password confirm', widget=forms.PasswordInput)  # todo

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'password')

    def clean_password2(self):
        cd = self.cleaned_data
        password1 = cd['password1']
        password2 = cd['password2']

        if password1 and password2 and password1 != password2:
            raise ValidationError('passwords don\'t match')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password2'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        help_text="you can change password using <a href=\"../password/\">this form</a>")

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'password')


class UserRegistrationsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'password')
        widgets = {
            'password': forms.PasswordInput
        }

    def __init__(self, *args, **kwargs):
        super(UserRegistrationsForm, self).__init__(*args, *kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Please enter your first name:'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Please enter your last name:'
        self.fields['email'].widget.attrs['placeholder'] = 'Please enter your email:'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Please enter your phone number:'
        self.fields['password'].widget.attrs['placeholder'] = 'Please enter your password:'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'input'

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email).exists()
        if user:
            raise ValidationError('This email already exist!')
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone_number']
        user = User.objects.filter(phone_number=phone).exists()
        if user:
            raise ValidationError('This phone number already exist!')
        return phone


class UserLoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'password')
        widgets = {
            'password': forms.PasswordInput
        }

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, *kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'Please enter your email:'
        self.fields['password'].widget.attrs['placeholder'] = 'Please enter your password:'
        for filed in self.fields:
            self.fields[filed].widget.attrs['class'] = 'input'
