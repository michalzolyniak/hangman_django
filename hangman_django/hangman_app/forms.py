from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()
START_ATTEMPT = 1
END_ATTEMPT = 10

LANGUAGE_T0_CHOSE = (
    (1, "polish"),
    (2, "english"),
)


class UserCreateForm(forms.Form):
    """
    Create user form
    """
    login = forms.CharField(max_length=150)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()

    def clean(self):
        cd = super().clean()
        password1 = cd.get('password1')
        password2 = cd.get('password2')
        if password1 != password2:
            raise ValidationError('Hasła nie są identyczne.')


class LoginForm(forms.Form):
    """
        Login form
    """
    login = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cd = super().clean()
        login = cd.get('login')
        password = cd.get('password')
        user = authenticate(username=login, password=password)
        if user is None:
            raise ValidationError('Dane logowania nie są prawidłowe')


class GameForm(forms.Form):
    """
        Game form
    """
    word = forms.CharField(max_length=150, label='Type letter or word')


class MainForm(forms.Form):
    """
        main form
    """
    language = forms.ChoiceField(choices=LANGUAGE_T0_CHOSE)
    attempts = forms.ChoiceField(choices=[(i, str(i)) for i in range(START_ATTEMPT, END_ATTEMPT + 1)])
