from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'password1', 'password2')
        labels = {
            'username': 'Имя пользователя',
            'phone': 'Телефон',
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Этот email уже используется')
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'phone', 'address')
        labels = {
            'email': 'Email',
            'phone': 'Телефон',
            'address': 'Адрес',
        }


User = get_user_model()


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Имя пользователя или Email',
        widget=forms.TextInput(attrs={'autofocus': True})
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # Пытаемся понять, кто это
            user_obj = None
            if '@' in username:
                try:
                    user_obj = User.objects.get(email=username)
                except User.DoesNotExist:
                    pass
            if user_obj is None:
                try:
                    user_obj = User.objects.get(username=username)
                except User.DoesNotExist:
                    pass

            if user_obj is None:
                raise ValidationError(
                    'Неверное имя пользователя или пароль.',
                    code='invalid_login',
                )

            self.user_cache = authenticate(
                self.request,
                username=user_obj.username,
                password=password,
            )

            if self.user_cache is None:
                raise ValidationError(
                    'Неверное имя пользователя или пароль.',
                    code='invalid_login',
                )

        return self.cleaned_data

    def get_user(self):
        return self.user_cache