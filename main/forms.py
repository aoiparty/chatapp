from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm  # 便利機能

from .models import User,Talk


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email",)


class LoginForm(AuthenticationForm):
    pass


# ...

class TalkForm(forms.ModelForm):
    class Meta:
        model = Talk
        fields = ("message",)

# 以下を追加
class UsernameChangeForm(forms.ModelForm):
    class Meta:
        model = User  #変更する人
        fields = ("username",) #変更する所
        labels = {"username": "新しいユーザー名"}
        help_texts = {"username": ""} #下の説明文がいらないので空白にする

class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = {"email",}
        labels = {"email" : "新しいメールアドレス"}
        

