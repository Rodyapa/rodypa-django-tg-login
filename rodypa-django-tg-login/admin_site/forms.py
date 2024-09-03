from django import forms
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class LinkTGForm(forms.Form):
    """
    A form that lets a user link their Telegram id to Django account.
    """
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self["tg_id"].css_classes = "telegram_id_input"

    tg_id = forms.IntegerField(
        label='Your Telegram ID',
        required=True,
        widget=forms.PasswordInput(
            attrs={"autofocus": True, }
        ),
    )

    def save(self, commit=True):
        tg_id = self.cleaned_data["tg_id"]
        self.user.tg_id = tg_id
        if commit:
            self.user.save()
        return self.user


class UnLinkTGForm(forms.Form):
    """
    A form that question if user want to unlick his telegram.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["tg_id"].css_classes = "telegram_id_input"

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.user.tg_id = None
        if commit:
            self.user.save()
        return self.user
