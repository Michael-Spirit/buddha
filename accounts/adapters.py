from django import forms

from allauth.account.adapter import DefaultAccountAdapter
from accounts.models import User
from allauth.utils import email_address_exists


class AccountAdapter(DefaultAccountAdapter):
    def respond_user_inactive(self, request, user):
        pass

    def clean_email(self, email):
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            if email_address_exists(email):
                raise forms.ValidationError(self.error_messages['email_taken'])
        else:
            return email

        return super().clean_email(email)
